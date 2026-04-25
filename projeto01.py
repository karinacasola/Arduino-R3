from pyfirmata2 import Arduino
import time

PORTA = 'COM4'  # Altere para a sua porta COM
placa = Arduino(PORTA)
led = 9  # Variável para o pino 9

print("Iniciando Pisca LED... Pressione Ctrl+C para parar.")

# try/except garante fechamento seguro
try:
    while True:  # Loop infinito
        placa.digital[led].write(1)  # HIGH (Liga)
        time.sleep(1)  # Pausa de 1 seg

        placa.digital[led].write(0)  # LOW (Desliga)
        time.sleep(1)  # Pausa de 1 seg

except KeyboardInterrupt:
    placa.exit()  # Encerra a conexão
