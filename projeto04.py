from pyfirmata2 import Arduino
import time

placa = Arduino('COM4')

# Definicao dos Pinos
btn_vermelho = placa.get_pin('d:2:i')
btn_amarelo = placa.get_pin('d:3:i')
btn_verde = placa.get_pin('d:4:i')

led_vermelho = placa.get_pin('d:8:o')
led_amarelo = placa.get_pin('d:9:o')
led_verde = placa.get_pin('d:10:o')

# Na pyfirmata2, isso inicia a leitura dos pinos em segundo plano
placa.samplingOn()

# --- 1. CRIANDO AS FUNÇÕES DE EVENTO (CALLBACKS) ---

def acao_botao_vermelho(valor):
    # O "valor" será 1 (True) quando apertado e 0 (False) quando solto
    if valor:
        print("Botao Vermelho Pressionado: LED ligado por 5s")
        led_vermelho.write(1)
        time.sleep(5)
        led_vermelho.write(0)
        print("LED Vermelho apagado.")

def acao_botao_amarelo(valor):
    if valor:
        print("Botao Amarelo Pressionado: Iniciando sequencia de pisca")
        for _ in range(5):
            led_amarelo.write(1)
            time.sleep(0.5)
            led_amarelo.write(0)
            time.sleep(0.5)
        print("Sequencia Amarela finalizada.")

# --- 2. VINCULANDO OS BOTÕES ÀS FUNÇÕES ---

# Avisa a placa qual função rodar quando o pino 2 mudar
btn_vermelho.register_callback(acao_botao_vermelho)
btn_vermelho.enable_reporting() # Liga o aviso de mudança de estado

# Avisa a placa qual função rodar quando o pino 3 mudar
btn_amarelo.register_callback(acao_botao_amarelo)
btn_amarelo.enable_reporting()

print("Sistema pronto. Pressione os botoes!")

try:
    # --- 3. LOOP PRINCIPAL ---
    # o loop principal não faz nada além de manter o programa vivo.
    # Tudo acontece nas funções lá em cima quando você aperta o botão.
    while True:
        time.sleep(0.1)

except KeyboardInterrupt:
    print("\nEncerrando o sistema...")
    placa.exit()