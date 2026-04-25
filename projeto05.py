from pyfirmata2 import Arduino
import time

placa = Arduino('COM4')

# Veiculos
led_vermelho = placa.get_pin('d:8:o')
led_amarelo = placa.get_pin('d:9:o')
led_verde = placa.get_pin('d:10:o')

# Pedestres
ped_verde = placa.get_pin('d:6:o')
ped_vermelho = placa.get_pin('d:7:o')

print("Semáforo em operação... Pressione Ctrl+C para encerrar.") 

try:
    while True:
        # FASE 1: Verde Veiculos / Vermelho Pedestres
        led_verde.write(1)
        ped_vermelho.write(1)
        time.sleep(5)

        # FASE 2: Amarelo Veiculos
        led_verde.write(0)
        time.sleep(1)
        ped_vermelho.write(0)
        time.sleep(0.2)
        led_amarelo.write(1)
        time.sleep(1)

        # FASE 3: Vermelho Veiculos / Verde Pedestres
        led_amarelo.write(0)
        time.sleep(0.5)
        led_vermelho.write(1)
        ped_verde.write(1)
        time.sleep(5)
        
        # Reset para Reinicio
        led_vermelho.write(0)
        time.sleep(1)
        ped_verde.write(0)

except KeyboardInterrupt:
    print("\nEncerrando o semáforo...")
    placa.exit()