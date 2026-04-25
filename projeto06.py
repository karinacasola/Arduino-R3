from pyfirmata2 import Arduino
import time
import math

placa = Arduino("COM4")

# Definição dos Pinos
sensor = placa.get_pin('a:3:i')  # Pino analógico A3
led_v = placa.get_pin('d:13:o')  # Vermelho
led_a = placa.get_pin('d:9:o')   # Amarelo
led_g = placa.get_pin('d:11:o')  # Verde
buzzer = placa.get_pin('d:2:o')  # Buzzer

# 1. LIGA A LEITURA DA PLACA (Essencial para pinos analógicos)
placa.samplingOn()

def get_celsius(valor_bruto):
    if valor_bruto is None or valor_bruto <= 0 or valor_bruto >= 1:
        return 0
    
    # Adicionado um try/except para evitar erros matemáticos caso o sensor pisque
    try:
        resistencia = (1 / valor_bruto) - 1
        temp = 1 / (math.log(resistencia) / 3950 + 1 / 298.15) - 273.15
        return round(temp, 1)
    except (ValueError, ZeroDivisionError):
        return 0

# Variável auxiliar para não "inundar" o terminal de prints
ultimo_print = time.time()

# 2. FUNÇÃO DE EVENTO (CALLBACK)
def atualizar_sistema(valor_bruto):
    global ultimo_print
    
    t = get_celsius(valor_bruto)
    
    # Controle para imprimir no terminal apenas a cada 1 segundo
    agora = time.time()
    if agora - ultimo_print >= 1.0:
        print(f"Temperatura Atual: {t}°C")
        ultimo_print = agora

    # Lógica dos LEDs e Buzzer
    if t <= 20:  # FRIO
        led_g.write(1)
        led_a.write(0)
        led_v.write(0)
        buzzer.write(0)

    elif t <= 30:  # CONFORTO
        led_a.write(1)
        led_g.write(0)
        led_v.write(0)
        buzzer.write(0)

    elif t >= 31:  # QUENTE
        led_v.write(1)
        buzzer.write(1)
        led_g.write(0)
        led_a.write(0)

# 3. VINCULA O SENSOR À FUNÇÃO
sensor.register_callback(atualizar_sistema)
sensor.enable_reporting()

print("Sistema de Temperatura Iniciado. Pressione Ctrl+C para encerrar.")

try:
    # 4. LOOP PRINCIPAL VAZIO
    # A placa fará todo o trabalho em segundo plano e chamará a função 'atualizar_sistema' sozinha
    while True:
        time.sleep(0.1)

except KeyboardInterrupt:
    print("\nPrograma finalizado.")
    placa.exit()