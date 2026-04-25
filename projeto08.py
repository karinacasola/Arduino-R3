import pyfirmata2
import time

# << INÍCIO DO PROGRAMA >>

# Configuração da porta (AUTODETECT tenta achar o Arduino automaticamente)
# Caso não funcione, troque por uma string com sua porta, ex: PORTA = "COM3"
PORTA = pyfirmata2.Arduino.AUTODETECT

print("Conectando ao Arduino...")
board = pyfirmata2.Arduino(PORTA)
print("Conectado com sucesso!\n")

# Mapeamento dos pinos (OUTPUT é padrão ao escrever, mas podemos referenciá-los diretamente)
# Correspondentes aos LEDs dos segmentos do DISPLAY
pino_a = board.digital[2]
pino_b = board.digital[3]
pino_c = board.digital[4]
pino_d = board.digital[5]
pino_e = board.digital[6]
pino_f = board.digital[7]
pino_g = board.digital[8]

# Função auxiliar para acionar os pinos e reduzir a repetição de código
def acionar_display(a, b, c, d, e, f, g):
    pino_a.write(a)
    pino_b.write(b)
    pino_c.write(c)
    pino_d.write(d)
    pino_e.write(e)
    pino_f.write(f)
    pino_g.write(g)
    time.sleep(0.1) # delay de 100 milissegundos

# Funções para exibir os números no display
def zero():  acionar_display(0, 0, 0, 0, 0, 0, 1)
def um():    acionar_display(1, 0, 0, 1, 1, 1, 1)
def dois():  acionar_display(0, 0, 1, 0, 0, 1, 0)
def tres():  acionar_display(0, 0, 0, 0, 1, 1, 0)
def quatro():acionar_display(1, 0, 0, 1, 1, 0, 0)
def cinco(): acionar_display(0, 1, 0, 0, 1, 0, 0)
def seis():  acionar_display(0, 1, 0, 0, 0, 0, 0)
def sete():  acionar_display(0, 0, 0, 1, 1, 1, 1)
def oito():  acionar_display(0, 0, 0, 0, 0, 0, 0)
def nove():  acionar_display(0, 0, 0, 0, 1, 0, 0)

# Função para efetuar contagem regressiva (de 9-0)
def contagem_regressiva():
    nove();  time.sleep(0.75)
    oito();  time.sleep(0.75)
    sete();  time.sleep(0.75)
    seis();  time.sleep(0.75)
    cinco(); time.sleep(0.75)
    quatro();time.sleep(0.75)
    tres();  time.sleep(0.75)
    dois();  time.sleep(0.75)
    um();    time.sleep(0.75)
    zero();  time.sleep(0.75)

# Função para efetuar contagem progressiva (de 0-9)
def contagem_progressiva():
    zero();  time.sleep(0.75)
    um();    time.sleep(0.75)
    dois();  time.sleep(0.75)
    tres();  time.sleep(0.75)
    quatro();time.sleep(0.75)
    cinco(); time.sleep(0.75)
    seis();  time.sleep(0.75)
    sete();  time.sleep(0.75)
    oito();  time.sleep(0.75)
    nove();  time.sleep(0.75)

# Loop principal (Equivalente ao void loop() do Arduino)
while True:
    try:
        # Pede entrada do usuário pelo terminal (Equivalente ao Serial.read)
        comando = input("\nDigite um número (0-9), 'c' (prog.) ou 'r' (reg.): ").strip().lower()

        if comando == '0':
            zero()
            print("Você digitou o número 0")
        elif comando == '1':
            um()
            print("Você digitou o número 1")
        elif comando == '2':
            dois()
            print("Você digitou o número 2")
        elif comando == '3':
            tres()
            print("Você digitou o número 3")
        elif comando == '4':
            quatro()
            print("Você digitou o número 4")
        elif comando == '5':
            cinco()
            print("Você digitou o número 5")
        elif comando == '6':
            seis()
            print("Você digitou o número 6")
        elif comando == '7':
            sete()
            print("Você digitou o número 7")
        elif comando == '8':
            oito()
            print("Você digitou o número 8")
        elif comando == '9':
            nove()
            print("Você digitou o número 9")
        elif comando == 'c':
            print("Iniciando contagem progressiva...")
            contagem_progressiva()
        elif comando == 'r':
            print("Iniciando contagem regressiva...")
            contagem_regressiva()
        else:
            print("Comando não reconhecido.")
            
        time.sleep(1) # Pausa de 1 segundo

    except KeyboardInterrupt:
        print("\nPrograma encerrado pelo usuário.")
        board.exit() # Fecha a conexão com a placa de forma segura
        break

# << FIM DO PROGRAMA >>