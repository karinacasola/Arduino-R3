from pyfirmata2 import Arduino
import time

# Porta COM correta (verifique no Windows/Linux/Mac)
PORTA = 'COM4'

# Conectando com a placa
board = Arduino(PORTA)
print("Conectado com sucesso!")

# Loop para piscar o LED embutido (Pino 13)
try:
    while True:
        board.digital[13].write(1)  # Liga o LED
        time.sleep(1)
        board.digital[13].write(0)  # Desliga o LED
        time.sleep(1)
except KeyboardInterrupt:
    board.exit()  # Fecha a conexão de forma segura
