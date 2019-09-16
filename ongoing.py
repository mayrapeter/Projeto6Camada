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
def forma_envio(com):
    #com imagem
    tipo_mensagem = 1
    if tipo_mensagem == 1:
        objeto_bytearray = bytes([0x00])  
    print("mayra")
    root = Tk()
    print("oiii")
    root.withdraw()
    print("nao")
    objeto = filedialog.askopenfilename()
    print("nao saiu")
    with open(str(objeto), "rb") as image:
        f = image.read()
        objeto_bytearray = bytearray(f)
        #com string
        #objeto_bytearray = bytes([0xff])*5 + bytes([0xF1]) + bytes([0xF2]) + bytes([0xF3]) + bytes([0xff])*10
        #print("Payload antes do stuffing", objeto_bytearray)
        #objeto_bytearray = bytearray(objeto)
        #with open("oi_panda.jpg", "rb") as image:
         #   f = image.read()
          #  txBuffer = bytearray(f)
     
    head_vazio = bytes([0x00]) + bytes([0x00])
    eop = bytes([0xF1]) + bytes([0xF2]) + bytes([0xF3])
    stuffing = bytes([0x00]) + bytes([0xF1]) + bytes([0x00]) + bytes([0xF2]) + bytes([0x00]) + bytes([0xF3])
    objeto_bytearray = objeto_bytearray.replace(eop, stuffing)

    tamanho = len(objeto_bytearray)
    pacotes = [objeto_bytearray[x:x+128] for x in range(0, len(objeto_bytearray), 128)]
    n_pacotes = ceil(len(objeto_bytearray)/128)
    n_pacotes = n_pacotes.to_bytes(3, "little")
    tipo_mensagem_byte = tipo_mensagem.to_bytes(1, "little")
    servidor = 84
    servidor = servidor.to_bytes(1, "little")
    print("tipo", tipo_mensagem)
    print("tipobyte", tipo_mensagem_byte)
    if tipo_mensagem == 1:
        payload2 = head_vazio
        tamanho2 = len(payload2)
        tamanho_bytes2 = tamanho2.to_bytes(3, "little")
        head = tamanho_bytes2 + tipo_mensagem_byte + servidor + n_pacotes + head_vazio
        print("head", head)
        envio = head + payload2 + eop
        com.sendData(envio)
        while(com.tx.getIsBussy()):
            pass
        time.sleep(0.1)
        head_rece, len_head_rece = com.getData(10, time.time(), time.time())
        print("head servidor", head_rece)
        tipo_mensagem = descobrir_tipo(head_rece)
        tamanhoaler = ler_head(head_rece)
        payload,nRx2 = com.getData(tamanhoaler, time.time(), time.time())
        print(tipo_mensagem)
        payload_total = payload
        eop, nRxEnd = com.getData(3, time.time(), time.time())

        if tipo_mensagem == 2:
            print("Servidor pronto para receber mensagem")
            tipo_mensagem = 3

    if tipo_mensagem == 3:
        i = 1
        for each in pacotes:
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
            com.sendData(envio)
            # espera o fim da transmissão
            while(com.rx.getIsEmpty()):
                pass
            head, len_head = com.getData(10, time.time(), time.time())
            tipo_mensagem = descobrir_tipo(head_rece)
            tamanhoaler = ler_head(head_rece)
            payload,nRx2 = com.getData(tamanhoaler, time.time(), time.time())
            payload_total = payload
            print("payload", payload)
            eop, nRxEnd = com.getData(3, time.time(), time.time())
            print(eop)
            print("head servidor", head)

            i += 1
            time.sleep(0.1)
    
          
    #overhead = len(envio)/len(objeto_bytearray)
    #tamanho_total = len(envio)
    #print(envio)
    #print(tamanho)
    #print("conteudo enviado:", envio)
def ler_head(dado):
    tamanhoByte = dado[:3]
    tamanho = int.from_bytes(tamanhoByte, "little")
    return tamanho
def descobrir_tipo(dado):
    tipo_mensagem = dado[3:4]
    tipo_mensagem = int.from_bytes(tipo_mensagem, "little")
    return tipo_mensagem

def tirar_stuffing(dado):
    stuffing = bytes([0x00]) + bytes([0xF1]) + bytes([0x00]) + bytes([0xF2]) + bytes([0x00]) + bytes([0xF3])
    eop = bytes([0xF1]) + bytes([0xF2]) + bytes([0xF3])
    dado = dado.replace(stuffing, eop)
   
    return dado       


# Serial Com Port
#   para saber a sua porta, execute no terminal :
#   python -m serial.tools.list_ports
#serialName = "/dev/ttyACM1"           # Ubuntu (variacao de)
#serialName = "/dev/tty.usbmodem1411" # Mac    (variacao de)
serialName = "COM16"                  # Windows(variacao de)
print("abriu com")
def main():
    # Inicializa enlace ... variavel com possui todos os metodos e propriedades do enlace, que funciona em threading
    com = enlace(serialName) # repare que o metodo construtor recebe um string (nome)
    # Ativa comunicacao
    com.enable()
  
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
    # Transmite dado
   
   
   
   
    # Atualiza dados da transmissão
    #txSize = com.tx.getStatus()
    #print ("Transmitido       {} bytes ".format(txSize))

    #rxBuffer2,nRx2 = com.getData(10)
    #tamanhoaler = ler_head(rxBuffer2)
    #rxBuffer2,nRx2 = com.getData(tamanhoaler)
    #dadoSemStuffing = tirar_stuffing(rxBuffer2)

   
    tempo2 = time.time() - tempo
    #print("Overhead:", overhead)
    #print("Recebido", tamanho_total)
    print("Tempo:", tempo2, "segundos")
    #print("Velocidade:", tamanho_total/tempo2, "bytes por segundos")

   
    # Encerra comunicação
    print("-------------------------")
    print("Comunicação encerrada")
    print("-------------------------")
    com.disable()
    #so roda o main quando for executado do terminal ... se for chamado dentro de outro modulo nao roda
if __name__ == "__main__":
    main()