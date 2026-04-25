import pyfirmata2
import time

# << INÍCIO DO PROGRAMA >>

PORTA = pyfirmata2.Arduino.AUTODETECT
print("Conectando ao Arduino...")
board = pyfirmata2.Arduino(PORTA)

# Iniciando o iterador (obrigatório para ler as entradas do sensor sem travar)
it = pyfirmata2.util.Iterator(board)
it.start()

print("Inicializando a leitura do sensor ultrassônico HC-SR04 e dos LEDs...\n")

# Mapeamento dos Pinos do Sensor Ultrassônico
pino_trigger = board.get_pin('d:8:o')
pino_echo = board.get_pin('d:7:i')

# Mapeamento dos Pinos dos LEDs e Buzzer (como OUTPUT)
led_verde = board.digital[13]
led_amarelo = board.digital[12]
led_vermelho = board.digital[11]
buzzer = board.digital[2]

# Dicionário e Função de Callback para ler o tempo do som (evita erro de polling)
tempo_pulso = {'inicio': 0, 'fim': 0, 'pronto': False}

def callback_echo(valor):
    agora = time.time()
    if valor:
        tempo_pulso['inicio'] = agora
    else:
        tempo_pulso['fim'] = agora
        tempo_pulso['pronto'] = True

# Registra a escuta no pino Echo
pino_echo.register_callback(callback_echo)
pino_echo.enable_reporting()

time.sleep(1) # Aguarda a placa estabilizar

# Função para disparar e calcular a distância do HC-SR04
def ler_distancia():
    tempo_pulso['pronto'] = False
    
    # Dispara pulso
    pino_trigger.write(0)
    time.sleep(0.002)
    pino_trigger.write(1)
    time.sleep(0.00001) 
    pino_trigger.write(0)
    
    # Aguarda o retorno
    limite_tempo = time.time() + 0.2
    while not tempo_pulso['pronto']:
        if time.time() > limite_tempo:
            return None # Timeout
        time.sleep(0.001)
            
    duracao = tempo_pulso['fim'] - tempo_pulso['inicio']
    if duracao <= 0:
        return None
        
    distancia_cm = (duracao * 34300) / 2
    return distancia_cm

# Loop principal
while True:
    try:
        cm = ler_distancia()
        
        if cm is not None:
            pol = cm / 2.54 
            print(f"Distancia em cm --> {cm:.2f} ==== Distancia em polegadas --> {pol:.2f}")
            
            # Converte para número inteiro para fazer as comparações dos LEDs
            leitura_cm = int(cm)
            
            # Lógica do Sensor de Estacionamento
            # Condição 1: Muito perto (<= 10cm) -> Vermelho + Buzzer
            if leitura_cm <= 10:
                buzzer.write(1)
                led_vermelho.write(1)
                led_verde.write(0)
                led_amarelo.write(0)
                
            # Condição 2: Distância média (entre 11 e 20cm) -> Amarelo
            elif leitura_cm >= 11 and leitura_cm <= 20:
                led_amarelo.write(1)
                led_verde.write(0)
                led_vermelho.write(0)
                buzzer.write(0)
                
            # Condição 3: Distância segura (>= 21cm) -> Verde
            elif leitura_cm >= 21:
                led_verde.write(1)
                led_amarelo.write(0)
                led_vermelho.write(0)
                buzzer.write(0)
                
        else:
            print("Aguardando leitura / Objeto muito distante...")
            # Por segurança, desliga tudo se perder o sinal
            buzzer.write(0)
            led_vermelho.write(0)
            led_amarelo.write(0)
            led_verde.write(0)
            
        time.sleep(1) # pausa por 1 segundo

    except KeyboardInterrupt:
        print("\nPrograma encerrado pelo usuário. Desligando componentes...")
        # Desliga todos os atuadores antes de sair
        buzzer.write(0)
        led_vermelho.write(0)
        led_amarelo.write(0)
        led_verde.write(0)
        board.exit()
        break

# << FIM DO PROGRAMA >>