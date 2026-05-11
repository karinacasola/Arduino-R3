from pyfirmata2 import Arduino
import time
import csv
from datetime import datetime
from collections import deque
import numpy as np
from sklearn.ensemble import IsolationForest
import paho.mqtt.client as mqtt

# --- CONFIGURAÇÕES DA PLACA ---
placa = Arduino("COM4") # Altere para a sua porta
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
print("MQTT Conectado!\n")

# --- VARIÁVEIS DO PIPELINE E IA (MICRO DEGRADAÇÃO) ---
ultimo_print = time.time()

# Buffers: O curto reage rápido, o longo percebe a degradação lenta
buffer_curto = deque(maxlen=10)  # Últimos 5 segundos
buffer_longo = deque(maxlen=60)  # Últimos 30 segundos
dados_historicos_2d = [] 
registro_exportacao = []

# O modelo agora avaliará 2 dimensões: (Luz Atual, Tendência de Degradação)
modelo_ia = IsolationForest(n_estimators=100, contamination=0.05, random_state=42)
modelo_treinado = False
AMOSTRAS_TREINO = 80 # Precisa de um pouco mais de tempo para formar médias

def atualizar_luz(nivel_luz):
    global ultimo_print, modelo_treinado
    
    if nivel_luz is None:
        return

    agora = time.time()
    
    if agora - ultimo_print >= 0.5:
        luminosidade = round(1.0 - nivel_luz, 2)
        timestamp_legivel = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        # Alimenta os buffers
        buffer_curto.append(luminosidade)
        buffer_longo.append(luminosidade)
        
        # Só calcula degradação se os buffers tiverem dados suficientes
        if len(buffer_longo) > 10:
            media_curta = np.mean(buffer_curto)
            media_longa = np.mean(buffer_longo)
            
            # Cálculo da Taxa de Degradação (Tendência)
            # Se for negativo, significa que está escurecendo com o tempo.
            taxa_degradacao = round(media_curta - media_longa, 4)
        else:
            taxa_degradacao = 0.0

        cliente_mqtt.publish(TOPICO_LUZ, luminosidade)
        
        # ---------------------------------------------------------
        # FASE 1: CALIBRAÇÃO (Luz + Degradação)
        # ---------------------------------------------------------
        if not modelo_treinado:
            # Salvamos um par de valores [x, y]
            dados_historicos_2d.append([luminosidade, taxa_degradacao])
            progresso = (len(dados_historicos_2d) / AMOSTRAS_TREINO) * 100
            print(f"[CALIBRAÇÃO] {progresso:.0f}% | Luz: {luminosidade} | Tendência: {taxa_degradacao}")
            
            if luminosidade < 0.5:
                led.write(1)
                estado_led = "LIGADO"
            else:
                led.write(0)
                estado_led = "DESLIGADO"
                
            registro_exportacao.append([timestamp_legivel, luminosidade, taxa_degradacao, "Calibracao", estado_led, "Treinando"])
            
            if len(dados_historicos_2d) >= AMOSTRAS_TREINO:
                print("\n[IA] Treinando Isolation Forest (MULTIVARIADO)...")
                modelo_ia.fit(dados_historicos_2d)
                modelo_treinado = True
                print("[IA] Modelo treinado! Rastreando Micro Degradações.\n")
                
        # ---------------------------------------------------------
        # FASE 2: INFERÊNCIA HÍBRIDA 2D
        # ---------------------------------------------------------
        else:
            # ---> A. CONTROLE OPERACIONAL
            if luminosidade < 0.5:
                led.write(1)
                estado_led = "LIGADO"
            else:
                led.write(0)
                estado_led = "DESLIGADO"
                
            # ---> B. SUPERVISÃO PREDITIVA (Avaliando a foto e o filme)
            predicao = modelo_ia.predict([[luminosidade, taxa_degradacao]])
            
            if predicao[0] == -1:
                # Vamos diferenciar uma queda brusca de uma sujeira lenta
                if taxa_degradacao < -0.05 and luminosidade > 0.3:
                    status_ia = "ALERTA: MICRO DEGRADACAO (Limpeza necessaria?)"
                else:
                    status_ia = "ALERTA: ANOMALIA GRAVE"
            else:
                status_ia = "NORMAL"
            
            cliente_mqtt.publish(TOPICO_LED, estado_led)
            cliente_mqtt.publish(TOPICO_IA, status_ia)
            
            registro_exportacao.append([timestamp_legivel, luminosidade, taxa_degradacao, "Inferencia", estado_led, status_ia])
                
            print(f"Luz: {luminosidade} | Tendência: {taxa_degradacao} | IA: {status_ia}")
            
        ultimo_print = agora

ldr.register_callback(atualizar_luz)
ldr.enable_reporting()

print("Sistema de Rastreamento de Degradação Ativo.")
print("Aguarde a calibração com a luz estável.")
try:
    while True:
        time.sleep(0.1)

except KeyboardInterrupt:
    print("\nEncerrando e salvando log...")
    led.write(0)
    cliente_mqtt.loop_stop() 
    cliente_mqtt.disconnect()
    placa.exit()
    
    if registro_exportacao:
        nome_arquivo = f"log_preditiva_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        with open(nome_arquivo, mode='w', newline='') as arquivo_csv:
            writer = csv.writer(arquivo_csv, delimiter=';')
            writer.writerow(["Timestamp", "Luminosidade", "Taxa_Degradacao", "Fase", "Atuador", "Status_IA"])
            writer.writerows(registro_exportacao)
        print(f" Datalake salvo: {nome_arquivo}")