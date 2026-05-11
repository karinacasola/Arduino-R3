from pyfirmata2 import Arduino
import time
from collections import deque
import numpy as np
from sklearn.ensemble import IsolationForest
import paho.mqtt.client as mqtt 

# --- CONFIGURAÇÕES DA PLACA ---
placa = Arduino("COM4") # Altere para sua porta
led = placa.get_pin('d:9:o')   
ldr = placa.get_pin('a:5:i')   
placa.samplingOn()

# --- CONFIGURAÇÕES MQTT ---
# Para testar online rapidamente, usaremos um broker público.
# Para rodar LOCALMENTE, instale o Mosquitto e mude o BROKER para "localhost" ou "127.0.0.1"
BROKER = "broker.hivemq.com" 
PORTA = 1883
TOPICO_LUZ = "poc_industria/sensor/luminosidade"
TOPICO_IA = "poc_industria/ia/status"

print(f"Conectando ao Broker MQTT ({BROKER})...")
cliente_mqtt = mqtt.Client()
cliente_mqtt.connect(BROKER, PORTA, 60)
cliente_mqtt.loop_start() # Inicia a thread do MQTT em background
print("MQTT Conectado!")

# --- VARIÁVEIS DO PIPELINE E IA ---
ultimo_print = time.time()
dados_historicos = [] 
janela_inferencia = deque(maxlen=20) 
modelo_ia = IsolationForest(n_estimators=100, contamination=0.1, random_state=42)
modelo_treinado = False
AMOSTRAS_TREINO = 60 # 30 segundos (a 2Hz)

def atualizar_luz(nivel_luz):
    global ultimo_print, modelo_treinado
    
    if nivel_luz is None:
        return

    agora = time.time()
    
    if agora - ultimo_print >= 0.5:
        luminosidade = round(1.0 - nivel_luz, 2)
        
        # 1. PUBLICA O DADO BRUTO VIA MQTT SEMPRE QUE LÊ
        cliente_mqtt.publish(TOPICO_LUZ, luminosidade)
        
        # ---------------------------------------------------------
        # FASE 1: CALIBRAÇÃO
        # ---------------------------------------------------------
        if not modelo_treinado:
            dados_historicos.append([luminosidade])
            progresso = (len(dados_historicos) / AMOSTRAS_TREINO) * 100
            print(f"[CALIBRAÇÃO] {progresso:.0f}% | Luz: {luminosidade}")
            
            if len(dados_historicos) >= AMOSTRAS_TREINO:
                print("\n[IA] Treinando modelo Isolation Forest...")
                modelo_ia.fit(dados_historicos)
                modelo_treinado = True
                print("[IA] Modelo treinado! Iniciando Inferência.\n")
                
        # ---------------------------------------------------------
        # FASE 2: INFERÊNCIA E FEEDBACK MQTT
        # ---------------------------------------------------------
        else:
            janela_inferencia.append([luminosidade])
            predicao = modelo_ia.predict([[luminosidade]])
            
            if predicao[0] == -1: 
                led.write(1)
                status_ia = "ANOMALIA"
            else:                  
                led.write(0)
                status_ia = "NORMAL"
            
            # 2. PUBLICA O VEREDITO DA IA VIA MQTT
            cliente_mqtt.publish(TOPICO_IA, status_ia)
                
            print(f"Luminosidade: {luminosidade} -> IA: {status_ia}")
            
        ultimo_print = agora

ldr.register_callback(atualizar_luz)
ldr.enable_reporting()

print("Sistema Ativo. Enviando dados via MQTT...")
try:
    while True:
        time.sleep(0.1)

except KeyboardInterrupt:
    print("\nEncerrando...")
    led.write(0)
    cliente_mqtt.loop_stop() # Para o cliente MQTT
    cliente_mqtt.disconnect()
    placa.exit()