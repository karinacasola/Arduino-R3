from pyfirmata2 import Arduino
import time

placa = Arduino("COM4")
led = placa.get_pin('d:9:o')   
ldr = placa.get_pin('a:5:i')   

placa.samplingOn()
ultimo_print = time.time()

def atualizar_luz(nivel_luz):
    global ultimo_print
    
    if nivel_luz is None:
        return

    agora = time.time()
    if agora - ultimo_print >= 0.5:
        
        # Perto de 1.0 = Muito Claro | Perto de 0.0 = Muito Escuro
        luminosidade = round(1.0 - nivel_luz, 2)
        
        # A LÓGICA CERTA (Claro desliga, Escuro liga)
        if luminosidade < 0.5: 
            led.write(1) # Escuro (luz menor que 50%) -> LIGA o LED
            status = "LIGADO (Escuro)"
        else:                  
            led.write(0) # Claro (luz 50% ou mais) -> DESLIGA o LED
            status = "DESLIGADO (Claro)"
            
        print(f"Luminosidade: {luminosidade} -> LED {status}")
        ultimo_print = agora

ldr.register_callback(atualizar_luz)
ldr.enable_reporting()

print("Sistema Ativo. Pressione Ctrl+C para sair.")

try:
    while True:
        time.sleep(0.1)

except KeyboardInterrupt:
    print("\nPrograma finalizado.")
    placa.exit()