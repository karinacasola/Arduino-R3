from pyfirmata2 import Arduino
import time
from collections import deque
import numpy as np
from sklearn.ensemble import IsolationForest

# --- CONFIGURAÇÕES DA PLACA ---
placa = Arduino("COM4") # Altere se necessário
led = placa.get_pin('d:9:o')   
ldr = placa.get_pin('a:5:i')   

placa.samplingOn()

# --- VARIÁVEIS DO PIPELINE E IA ---
ultimo_print = time.time()
dados_historicos = [] # Lista para armazenar dados de treino
janela_inferencia = deque(maxlen=20) # Buffer de 10 seg (20 amostras a 0.5s) [cite: 81, 92]

# Configuração do Modelo Isolation Forest [cite: 90]
# contamination=0.1 significa que esperamos ~10% de anomalias nos dados do mundo real
modelo_ia = IsolationForest(n_estimators=100, contamination=0.1, random_state=42)
modelo_treinado = False

# Tempo de calibração (ex: 60 amostras = 30 segundos coletando dados "normais")
AMOSTRAS_TREINO = 60 

def atualizar_luz(nivel_luz):
    global ultimo_print, modelo_treinado
    
    if nivel_luz is None:
        return

    agora = time.time()
    
    # Taxa de amostragem de 0.5 segundos (2 Hz)
    if agora - ultimo_print >= 0.5:
        
        # Pré-processamento: Normalização [0, 1] [cite: 80]
        luminosidade = round(1.0 - nivel_luz, 2)
        
        # ---------------------------------------------------------
        # FASE 1: COLETA HISTÓRICA E TREINAMENTO (Pipeline)
        # ---------------------------------------------------------
        if not modelo_treinado:
            dados_historicos.append([luminosidade])
            progresso = (len(dados_historicos) / AMOSTRAS_TREINO) * 100
            print(f"[CALIBRAÇÃO] Coletando dados normais... {progresso:.0f}% | Luz atual: {luminosidade}")
            
            # Quando atingir o limite, treina o modelo
            if len(dados_historicos) >= AMOSTRAS_TREINO:
                print("\n[IA] Treinando modelo Isolation Forest com dados históricos...")
                modelo_ia.fit(dados_historicos)
                modelo_treinado = True
                print("[IA] Modelo treinado! Iniciando Inferência Online.\n")
                
        # ---------------------------------------------------------
        # FASE 2: INFERÊNCIA ONLINE E FEEDBACK (Controle)
        # ---------------------------------------------------------
        else:
            # Mantém os últimos 10 segundos de dados no buffer (20 amostras)
            janela_inferencia.append([luminosidade])
            
            # Só toma decisão se o buffer tiver tamanho mínimo (ex: pelo menos 1 amostra, mas podemos usar a média da janela se quisermos)
            # Para este exemplo, a IA avalia a leitura atual comparada ao histórico
            predicao = modelo_ia.predict([[luminosidade]])
            
            # Isolation Forest retorna -1 para anomalias e 1 para dados normais
            if predicao[0] == -1: 
                led.write(1) # IA detecta Anomalia -> Python envia sinal -> Arduino liga Atuador [cite: 116]
                status = "ANOMALIA DETECTADA! (LED LIGADO)"
            else:                  
                led.write(0) # Comportamento normal
                status = "Operação Normal (LED DESLIGADO)"
                
            print(f"Luminosidade: {luminosidade} -> IA: {status}")
            
        ultimo_print = agora

# Registra a função de callback no pino LDR
ldr.register_callback(atualizar_luz)
ldr.enable_reporting()

print("Iniciando PoC Indústria 4.0 - Fase de Ingestão e Pipeline.")
print("Atenção: Deixe o sensor em estado 'normal' durante os primeiros 30 segundos para o treinamento correto.")
print("Pressione Ctrl+C para sair.\n")

try:
    while True:
        # Loop principal livre, o processamento ocorre via callback na thread do pyFirmata
        time.sleep(0.1)

except KeyboardInterrupt:
    print("\nPrograma finalizado pelo usuário.")
    
    # usar pandas para salvar 'dados_historicos' em um arquivo CSV 
    import pandas as pd
    df = pd.DataFrame(dados_historicos, columns=["luminosidade"])
    df.to_csv("dados_treino_ldr.csv", index=False)
    
    placa.exit()