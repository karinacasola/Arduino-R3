from pyfirmata2 import Arduino
import time
import csv
from datetime import datetime
from collections import deque
import numpy as np
from sklearn.ensemble import IsolationForest
import paho.mqtt.client as mqtt

# --- CONFIGURAÇÕES DA PLACA ---
placa = Arduino("COM4") # Altere para a sua porta serial
led = placa.get_pin('d:9:o')   
ldr = placa.get_pin('a:5:i')   

placa.samplingOn()

# --- CONFIGURAÇÕES MQTT ---
BROKER = "broker.hivemq.com" 
PORTA = 1883
TOPICO_LUZ = "poc_industria/sensor/luminosidade"
TOPICO_LED = "poc_industria/atuador/led"
TOPICO_IA  = "poc_industria/ia/status"

print("Conectando ao Broker MQTT...")
cliente_mqtt = mqtt.Client()
cliente_mqtt.connect(BROKER, PORTA, 60)
cliente_mqtt.loop_start() 
print("MQTT Conectado com sucesso!\n")

# --- VARIÁVEIS DO PIPELINE E IA ---
ultimo_print = time.time()
dados_historicos = [] 
janela_inferencia = deque(maxlen=20) 
registro_exportacao = [] # Lista para armazenar o Datalake local

modelo_ia = IsolationForest(n_estimators=100, contamination=0.1, random_state=42)
modelo_treinado = False
AMOSTRAS_TREINO = 60 # 30 segundos de calibração

def atualizar_luz(nivel_luz):
    global ultimo_print, modelo_treinado
    
    if nivel_luz is None:
        return

    agora = time.time()
    
    if agora - ultimo_print >= 0.5:
        luminosidade = round(1.0 - nivel_luz, 2)
        timestamp_legivel = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        # 1. PUBLICA O DADO DO SENSOR VIA MQTT
        cliente_mqtt.publish(TOPICO_LUZ, luminosidade)
        
        # ---------------------------------------------------------
        # FASE 1: CALIBRAÇÃO DA IA
        # ---------------------------------------------------------
        if not modelo_treinado:
            dados_historicos.append([luminosidade])
            progresso = (len(dados_historicos) / AMOSTRAS_TREINO) * 100
            print(f"[CALIBRAÇÃO] {progresso:.0f}% | Luz: {luminosidade}")
            
            if luminosidade < 0.5:
                led.write(1)
                estado_led = "LIGADO"
            else:
                led.write(0)
                estado_led = "DESLIGADO"
                
            # Salva no log local
            registro_exportacao.append([timestamp_legivel, luminosidade, "Calibracao", estado_led, "Treinando_Modelo"])
            
            if len(dados_historicos) >= AMOSTRAS_TREINO:
                print("\n[IA] Treinando modelo Isolation Forest...")
                modelo_ia.fit(dados_historicos)
                modelo_treinado = True
                print("[IA] Modelo treinado! Iniciando Monitoramento Conjunto.\n")
                
        # ---------------------------------------------------------
        # FASE 2: CONTROLE HÍBRIDO (REGRA CLÁSSICA + IA)
        # ---------------------------------------------------------
        else:
            janela_inferencia.append([luminosidade])
            
            # ---> A. CONTROLE OPERACIONAL (Regra de Negócio)
            if luminosidade < 0.5:
                led.write(1)
                estado_led = "LIGADO"
            else:
                led.write(0)
                estado_led = "DESLIGADO"
                
            # ---> B. SUPERVISÃO PREDITIVA (Inteligência Artificial)
            predicao = modelo_ia.predict([[luminosidade]])
            if predicao[0] == -1:
                status_ia = "ALERTA_ANOMALIA"
            else:
                status_ia = "NORMAL"
            
            # 2. PUBLICA O ESTADO DO ATUADOR E O VEREDITO DA IA VIA MQTT
            cliente_mqtt.publish(TOPICO_LED, estado_led)
            cliente_mqtt.publish(TOPICO_IA, status_ia)
            
            # Salva no log local
            registro_exportacao.append([timestamp_legivel, luminosidade, "Inferencia_Hibrida", estado_led, status_ia])
                
            print(f"Luz: {luminosidade} | Atuador: {estado_led} | IA: {status_ia}")
            
        ultimo_print = agora

# Inicia a leitura do sensor
ldr.register_callback(atualizar_luz)
ldr.enable_reporting()

print("Sistema Híbrido Ativo (Regras + IA + MQTT).")
print("Pressione Ctrl+C a qualquer momento para sair e EXPORTAR OS DADOS.\n")

try:
    while True:
        time.sleep(0.1)

except KeyboardInterrupt:
    print("\n\nEncerrando sistema e preparando exportação...")
    
    # Desliga hardware e conexões
    led.write(0)
    cliente_mqtt.loop_stop() 
    cliente_mqtt.disconnect()
    placa.exit()
    
    # --- LÓGICA DE EXPORTAÇÃO PARA CSV ---
    if registro_exportacao:
        nome_arquivo = f"log_industria_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        
        with open(nome_arquivo, mode='w', newline='') as arquivo_csv:
            writer = csv.writer(arquivo_csv, delimiter=';')
            # Novo cabeçalho adaptado para o sistema híbrido
            writer.writerow(["Timestamp", "Luminosidade", "Fase_do_Sistema", "Estado_Atuador_Fisico", "Veredito_IA_Supervisorio"])
            writer.writerows(registro_exportacao)
            
        print(f"Sucesso! {len(registro_exportacao)} registros foram salvos em: {nome_arquivo}")
    else:
        print("Nenhum dado foi coletado para exportação.")