#!/usr/bin/env python3
# -- coding: utf-8 --
#####################################################
# Camada Física da Computação
#Carareto
#17/02/2018
#  Aplicação
####################################################
print("comecou")
from enlace import *
import time
from tkinter import filedialog, Tk
from math import ceil

def empacota(self, data):
    eop = bytes([0xF1]) + bytes([0xF2]) + bytes([0xF3])

    stuffing = bytes([0x00]) + bytes([0xF1]) + bytes([0x00]) + bytes([0xF2]) + bytes([0x00]) + bytes([0xF3])
    objeto_bytearray = data
    objeto_bytearray = objeto_bytearray.replace(eop, stuffing)
    tamanho = len(data)

    pacotes = [objeto_bytearray[x:x+128] for x in range(0, len(objeto_bytearray), 128)]
    n_pacotes = ceil(len(objeto_bytearray)/128)
    n_pacotes = n_pacotes.to_bytes(3, "little")

    i = 1
    lenPayload = []
    pacote_completo = []
    while i <= len(pacotes):
        tipo_mensagem = 3
        each = pacotes[i]
        lenPayload.append(each)

        tipo_mensagem_byte = tipo_mensagem.to_bytes(1, "little")
        n_pacote = i.to_bytes(3, "little")
        tamanho_pacote = len(each)
        tamanho_pacote_bytes = tamanho_pacote.to_bytes(3, "little")

        head = tamanho_pacote_bytes + tipo_mensagem_byte + n_pacote + n_pacotes    

        print("Head envio", head)
        print("Numero do pacote:", int.from_bytes(n_pacote, "little"),"Total de pacotes:", int.from_bytes(n_pacotes, "little"))
        print(" ")
       
        payload = each
        envio = head + payload + eop
        pacote_completo.append(envio)

    return (pacote_completo, lenPayload, n_pacotes, n_pacote)    

def forma_envio(com):
    inicia = False
    eop = bytes([0xF1]) + bytes([0xF2]) + bytes([0xF3])
    servidor = 84
    servidor = servidor.to_bytes(1, "little")
    vazio = 0
    vazio = vazio.to_bytes(5, "little")
    
    root = Tk()
    root.withdraw()
    objeto = filedialog.askopenfilename()

    with open(str(objeto), "rb") as image:
        f = image.read()
        objeto_bytearray = bytearray(f)

    payload = len(objeto_bytearray)
    
    pacote, lenPayload, n_pacotes, n_pacote = com.empacota(objeto_bytearray) 

    ############################ Mensagem tipo 1##################
    tipo_mensagem = 1
    payload1 = vazio
    tipo_mensagem = tipo_mensagem.to_bytes(1, "little")  
    head = tipo_mensagem + servidor + n_pacotes + vazio
    msg1 = head + payload + eop
    com.fisica.flush()
    print('Mandando uma mensagem tipo 1')
    com.sendData(msg1)

    # Espera o fim da transmissão
    while(com.tx.getIsBussy()):
        pass
    
    print ('Aguardando resposta do servidor...')
    time.sleep(5)

    ##################### Mensagem tipo 2########################
    timer01 = timer02 = time.time()
    head2 = com.getData(10, timer01, timer02)

    tipo_mensagem = head2[1] #ver com a Mayra onde ela colocou
    tam = head2[0] #ver com a Mayra onde ela colocou
    leitura = com.getData(tam + len(eop), timer01, timer02)
    if tipo_mensagem == 2:
        inicia = True
        reenvio = False
        time_out = False
        contador = 1

    if inicia:
        while contador <= n_pacotes:
            if time_out:
                tipo_mensagem = 5
                tipo_mensagem = tipo_mensagem.to_bytes(1, "little")
                empty = 0
                empty = empty.to_bytes(4, "little")
                head = tipo_mensagem + vazio + empty
                msg5 = head + payload1 + eop
                print("Enviada mensagem do tipo 5")
                com.fisica.flush()
                com.sendData(msg5)
                while(com.tx.getIsBussy()):
                        pass
                print("------------------------------------------")
                print('Timeout. Encerrando comunicação.')
                print("------------------------------------------")
                break

            # Transmite dados
            print('Enviando uma mensagem tipo 3')
            print('Tentado transmitir .... {} bytes'.format(lenPayload))
            com.fisica.flush()

            print("Numero do pacote:", int.from_bytes(n_pacote, "little"),"Total de pacotes:", int.from_bytes(n_pacotes, "little"))
            timer1 = timer2 = time.time()

            while(com.tx.getIsBussy()):
                    pass

            head_4, lenmsg4, reenvio, time_out = com.getData(16, timer1, timer2) 
            tipo_mensagem = head_4[1]
            tam = head_4[0]

            if tipo_mensagem == 6:
                leitura = com.getData(tam +len(eop), timer1, timer2)
                contador = leitura[0][tam - 1]
            else:
                leitura = com.getData(tam +len(eop), timer1, timer2)
            if tipo_mensagem == 4:
                print("-------------------------------")
                print("Pacote {} enviado com sucesso!".format(contador))
                print("-------------------------------")
                contador = leitura[0][0] + 1

            elif tipo_mensagem == 5:
                reenvio = False
                time_out = True
            else:
                reenvio = True      

# Serial Com Port
#   para saber a sua porta, execute no terminal :
#   python -m serial.tools.list_ports
#serialName = "/dev/ttyACM1"           # Ubuntu (variacao de)
#serialName = "/dev/tty.usbmodem1411" # Mac    (variacao de)
serialName = "COM11"                  # Windows(variacao de)
print("abriu com")
def main():
    # Inicializa enlace ... variavel com possui todos os metodos e propriedades do enlace, que funciona em threading
    com = enlace(serialName) # repare que o metodo construtor recebe um string (nome)
    # Ativa comunicacao
    com.enable()
    com.rx.clearBuffer()

 
    # Log
    print("-------------------------")
    print("Comunicação inicializada")
    print("  porta : {}".format(com.fisica.name))
    print("-------------------------")
    # Carrega dados
    print ("gerando dados para transmissao :")
 

    tempo = time.time()
    #txBuffer, tamanho, overhead, tamanho_total = forma_envio()
    forma_envio(com)

   
    tempo2 = time.time() - tempo
    print("Tempo:", tempo2, "segundos")

   
    # Encerra comunicação
    print("-------------------------")
    print("Comunicação encerrada")
    print("-------------------------")
    com.disable()
    #so roda o main quando for executado do terminal ... se for chamado dentro de outro modulo nao roda
if __name__ == "__main__":
    main()