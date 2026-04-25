from pyfirmata2 import Arduino
import time

placa = Arduino("COM4")
led = placa.get_pin('d:9:o')   # LED no pino digital 9
ldr = placa.get_pin('a:5:i')   # Sensor LDR no pino analógico A5

# 1. Liga a leitura da placa (obrigatório para analógicos)
placa.samplingOn()

# Variável de controle para não floodar o terminal
ultimo_print = time.time()

# 2. Cria a função de Callback (Evento)
def atualizar_luz(nivel_luz):
    global ultimo_print
    
    # Ignora leituras nulas que podem acontecer no milissegundo inicial
    if nivel_luz is None:
        return

    # Controla o tempo para rodar a lógica a cada 0.5 segundos
    agora = time.time()
    if agora - ultimo_print >= 0.5:
        print(f"Luminosidade: {round(nivel_luz, 2)}")
        
        # Lógica do LED
        if nivel_luz < 0.5:
            led.write(1)
        else:
            led.write(0)
            
        ultimo_print = agora

# 3. Registra a função no pino do LDR
ldr.register_callback(atualizar_luz)
ldr.enable_reporting()

print("Sistema Ativo. Pressione Ctrl+C para sair.")

try:
    # 4. Loop vazio: o Arduino cuida de chamar a função em segundo plano
    while True:
        time.sleep(0.1)

except KeyboardInterrupt:
    print("\nPrograma finalizado.")
    placa.exit()