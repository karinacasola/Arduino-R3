from pyfirmata2 import Arduino
import time

placa = Arduino("COM4")

# Mapeamento dos Pinos
led_amarelo = 9
led_verde = 11
led_vermelho = 13

print("Comandos: [y] Amarelo | [g] Verde | [r] Vermelho | [s] Sair")

try:
    while True:
        comando = input("Digite um comando: ").lower()

        if comando == 'y':
            placa.digital[led_amarelo].write(1)
            print("LED AMARELO LIGADO. Desligando em 3s...")
            for i in range(3, 0, -1):
                print(f"... {i}")
                time.sleep(1)
            placa.digital[led_amarelo].write(0)
            print("LED AMARELO DESLIGADO")

        elif comando == 'g':
            placa.digital[led_verde].write(1)
            print("LED VERDE LIGADO")
            time.sleep(2)
            placa.digital[led_verde].write(0)
            print("LED VERDE DESLIGADO")

        elif comando == 'r':
            placa.digital[led_vermelho].write(1)
            print("LED VERMELHO LIGADO")
            time.sleep(2)
            placa.digital[led_vermelho].write(0)
            print("LED VERMELHO DESLIGADO")

        elif comando == 's':
            print("Saindo do programa...")
            break

        else:
            print("Comando inválido!")

except KeyboardInterrupt:
    pass

placa.exit()
print("Sistema desativado.")
