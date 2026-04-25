from pyfirmata2 import Arduino
import time

PORTA = 'COM4'  # Verifique sua porta no Gerenciador de Dispositivos
placa = Arduino(PORTA)

# Definição dos pinos
led = 9
buzzer = 4

print("Alarme Ativo! Pressione Ctrl+C para encerrar.")

# try/except garante fechamento seguro
try:
    while True:
        # LIGA os dois componentes simultaneamente
        placa.digital[led].write(1)
        placa.digital[buzzer].write(1)
        time.sleep(1)  # Pausa com ambos ligados

        # DESLIGA os dois componentes simultaneamente
        placa.digital[led].write(0)
        placa.digital[buzzer].write(0)
        time.sleep(1)  # Pausa com ambos desligados

except KeyboardInterrupt:
    placa.exit()  # Encerra a conexão
    print("Sistema desativado.")
