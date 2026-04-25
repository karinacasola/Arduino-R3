from pyfirmata2 import Arduino
import time

placa = Arduino("COM4")

print("Inicio")
for i in range(10):
    placa.digital[13].write(1)
    time.sleep(1)
    placa.digital[13].write(0)
    time.sleep(1)

placa.exit()  # Fecha a conexão de forma segura