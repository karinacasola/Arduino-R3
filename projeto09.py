import pyfirmata2
import time

# << INÍCIO DO PROGRAMA >>

PORTA = pyfirmata2.Arduino.AUTODETECT
print("Conectando ao Arduino...")
board = pyfirmata2.Arduino(PORTA)

it = pyfirmata2.util.Iterator(board)
it.start()

print("Inicializando a leitura do sensor ultrassônico HC-SR04...\n")

# Mapeamento dos Pinos
pino_trigger = board.get_pin('d:8:o')
pino_echo = board.get_pin('d:7:i')

# Dicionário para armazenar os tempos de ida e volta do som capturados pelo callback
tempo_pulso = {'inicio': 0, 'fim': 0, 'pronto': False}

# Função de Callback: É acionada SOZINHA sempre que o pino Echo liga ou desliga
def callback_echo(valor):
    agora = time.time()
    if valor: # Se o valor for True (nível ALTO), o som acabou de sair
        tempo_pulso['inicio'] = agora
    else:     # Se o valor for False (nível BAIXO), o som bateu no objeto e voltou
        tempo_pulso['fim'] = agora
        tempo_pulso['pronto'] = True

# Registramos a função acima para "escutar" o pino Echo
pino_echo.register_callback(callback_echo)
pino_echo.enable_reporting()

time.sleep(1) # Aguarda a placa estabilizar

def ler_distancia():
    tempo_pulso['pronto'] = False
    
    # Dispara um pulso sonoro
    pino_trigger.write(0)
    time.sleep(0.002)
    pino_trigger.write(1)
    time.sleep(0.00001) 
    pino_trigger.write(0)
    
    # Aguarda o callback avisar que a leitura terminou (com um limite de 0.2 segundos)
    limite_tempo = time.time() + 0.2
    while not tempo_pulso['pronto']:
        if time.time() > limite_tempo:
            return None # Erro: o som não voltou
        time.sleep(0.001) # Pequena pausa para o computador respirar
            
    # Calcula a duração e a distância
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
        else:
            print("Aguardando leitura / Objeto muito distante...")
            
        time.sleep(1) # pausa por 1 segundo

    except KeyboardInterrupt:
        print("\nPrograma encerrado pelo usuário.")
        board.exit()
        break

# << FIM DO PROGRAMA >>