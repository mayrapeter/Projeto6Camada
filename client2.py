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

def descobrir_tipo(head):
    tipo_mensagem = head[3:4]
    tipo_mensagem = int.from_bytes(tipo_mensagem, "little")

    return tipo_mensagem

def ler_head(dado, tipo):
    tamanhoByte = dado[:3]
    tamanho = int.from_bytes(tamanhoByte, "little")

    if tipo == 4:
        numero_pacote = dado[4:7]
        numero_pacote = int.from_bytes(numero_pacote, "little")
        return tamanho, numero_pacote

    elif tipo == 6:   
        numero_pacote = dado[4:7]
        numero_pacote = int.from_bytes(numero_pacote, "little")
        total_pacotes = dado[7:]
        total_pacotes = int.from_bytes(total_pacotes, "little")
        return tamanho, numero_pacote

# Serial Com Port
#   para saber a sua porta, execute no terminal :
#   python -m serial.tools.list_ports

serialName = "COM16"                  # Windows(variacao de)
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

    root = Tk()
    root.withdraw()
    objeto = filedialog.askopenfilename()

    with open(str(objeto), "rb") as image:
        f = image.read()
        objeto_bytearray = bytearray(f)

    eop =  bytes([0xF1]) + bytes([0xF2]) + bytes([0xF3])
    stuffing = bytes([0x00]) + bytes([0xF1]) + bytes([0x00]) + bytes([0xF2]) + bytes([0x00]) + bytes([0xF3])
    objeto_bytearray = objeto_bytearray.replace(eop, stuffing)
    
    pacotes = [objeto_bytearray[x:x+128] for x in range(0, len(objeto_bytearray), 128)]
    n_pacotes = ceil(len(objeto_bytearray)/128)
    n_pacotes_bytes = n_pacotes.to_bytes(3, "little")

    vazio = bytes([0x00])

    servidor = 84
    inicia = False
    while not inicia:
        #Manda mensagem tipo 1 
        tipo_mensagem = 1
        payload = bytes([0x00])
        tamanho = len(payload)
        tamanho_bytes = tamanho.to_bytes(3, "little")
        servidor_bytes = servidor.to_bytes(1, "little")
        tipo_mensagem = tipo_mensagem.to_bytes(1, "little")  
        head = tamanho_bytes + tipo_mensagem + servidor_bytes + n_pacotes_bytes + 2*vazio
        print("head enviado", head)
        envio = head + payload + eop
        print('Mandando uma mensagem tipo 1')
        com.sendData(envio)

        time.sleep(5)
        head = com.getData(10, 2)[0]
        com.rx.clearBuffer()
        if head == []:
            com.rx.clearBuffer()
            print("Esperando...")
        else:
            tipo_mensagem = descobrir_tipo(head)
            if tipo_mensagem == 2: 
                print("Mensagem tipo 2 recebida")
                inicia = True
            
    i = 1
    while i <= n_pacotes:
        tipo_mensagem = 3
        tipo_mensagem_byte = tipo_mensagem.to_bytes(1, "little")
        payload = pacotes[i-1]
        n_pacote = i.to_bytes(3, "little")
        tamanho_pacote = len(payload)
        tamanho_pacote_bytes = tamanho_pacote.to_bytes(3, "little")
        head = tamanho_pacote_bytes + tipo_mensagem_byte + n_pacote + n_pacotes_bytes    
        envio = head + payload + eop

        com.sendData(envio)
        timer1 = time.time()
        timer2 = time.time()
        head_response = com.getData(10, 2)[0]
        com.rx.clearBuffer()
        if head_response == []:
            if time.time() - timer1 > 5:
                com.sendData(envio)
                timer1 = time.time()
            if time.time() - timer2 > 20:
                tipo_mensagem = 5
                tipo_mensagem_byte = tipo_mensagem.to_bytes(1, "little")
                payload = bytes([0x00])
                tamanho = len(payload)
                tamanho_bytes = tamanho.to_bytes(3, "little")
                head = tamanho_bytes + tipo_mensagem_byte + 6*head_vazio
                envio = head + payload + eop 
                com.sendData(envio)
                while(com.tx.getIsBussy()):
                    pass
                break
        else:
            tipo_mensagem = descobrir_tipo(head_response)
            if tipo_mensagem == 4:
                tamanho, numero_pacote = ler_head(head_response, 4)
                if i == n_pacotes:
                    break
                else:
                    i = numero_pacote + 1
            else:
                if time.time() - timer1 > 5:
                    com.sendData(envio)
                    timer1 = time.time()
                if time.time() - timer2 > 20:
                    tipo_mensagem = 5
                    tipo_mensagem_byte = tipo_mensagem.to_bytes(1, "little")
                    payload = bytes([0x00])
                    tamanho = len(payload)
                    tamanho_bytes = tamanho.to_bytes(3, "little")
                    head = tamanho_bytes + tipo_mensagem_byte + 6*head_vazio
                    envio = head + payload + eop 
                    com.sendData(envio)
                    while(com.tx.getIsBussy()):
                        pass
                    break
                elif tipo_mensagem == 6:
                    tamanho, numero_pacote = ler_head(head_response, 6)
                    i = numero_pacote
    print(i)
    print(n_pacotes)
    if i == n_pacotes:
        print("Comunicação realizada com sucesso!")

    else:
        print("Comunicação interrompida :(")


                
                
        


    

   
    # Encerra comunicação
    print("-------------------------")
    print("Comunicação encerrada")
    print("-------------------------")
    com.disable()
    #so roda o main quando for executado do terminal ... se for chamado dentro de outro modulo nao roda
if __name__ == "__main__":
    main()