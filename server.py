# -*- coding: utf-8 -*-
"""
Created on Sun Sep 15 19:53:00 2019

@author: Mayra Peter
"""

from enlace import *
import time
from math import ceil

def descobrir_tipo(head):
    tipo_mensagem = head[3:4]
    tipo_mensagem = int.from_bytes(head, "little")

    return tipo_mensagem

def tirarStuffing(payload):
    stuffing = bytes([0x00]) + bytes([0xF1]) + bytes([0x00]) + bytes([0xF2]) + bytes([0x00]) + bytes([0xF3])
    eop = bytes([0xF1]) + bytes([0xF2]) + bytes([0xF3])
    payload = payload.replace(stuffing, eop)

    return dado

def ler_head(head, tipo):
    tamanhoByte = dado[:3]
    tamanho = int.from_bytes(tamanhoByte, "little")

    if tipo == 1:
        numero_servidor = dado[4:5]
        numero_servidor = int.from_bytes(numero_servidor, "little")
        total_pacotes = dado[5:8]
        total_pacotes = int.from_bytes(total_pacotes, "little")
        return tamanho, numero_servidor, total_pacotes

    if tipo == 3:   
        numero_pacote = dado[4:7]
        numero_pacote = int.from_bytes(numero_pacote, "little")
        total_pacotes = dado[7:]
        total_pacotes = int.from_bytes(total_pacotes, "little")
        return tamanho, numero_pacote, total_pacotes
  

def forma_envio(tipo_mensagem, com, ultimo_pct):
    head_vazio = bytes([0x00])
    eop =  bytes([0xF1]) + bytes([0xF2]) + bytes([0xF3])
    if tipo_mensagem == 2:
        tipo_mensagem_byte = tipo_mensagem.to_bytes(1, "little")
        payload = bytes([0x00])
        tamanho = len(payload)
        tamanho_bytes = tamanho.to_bytes(3, "little")
        head = tamanho_bytes + tipo_mensagem_byte + 6*head_vazio
        envio = head + payload + eop 
        com.sendData(envio)
        while(com.tx.getIsBussy()):
            pass
        time.sleep(0.01)

    elif tipo_mensagem == 4:
        tipo_mensagem_byte = tipo_mensagem.to_bytes(1, "little")
        payload = bytes([0x00])
        tamanho = len(payload)
        tamanho_bytes = tamanho.to_bytes(3, "little")
        numero_pacote_bytes = ultimo_pct.to_bytes(3, "little")
        head = tamanho_bytes + tipo_mensagem_byte + numero_pacote_bytes + 3*head_vazio
        envio = head + payload + eop 
        com.sendData(envio)
        while(com.tx.getIsBussy()):
            pass
        time.sleep(0.01)

    elif tipo_mensagem == 5:
        tipo_mensagem_byte = tipo_mensagem.to_bytes(1, "little")
        payload = bytes([0x00])
        tamanho = len(payload)
        tamanho_bytes = tamanho.to_bytes(3, "little")
        head = tamanho_bytes + tipo_mensagem_byte + 6*head_vazio
        envio = head + payload + eop 
        com.sendData(envio)
        while(com.tx.getIsBussy()):
            pass
        time.sleep(0.01)

    elif tipo_mensagem == 6:
        tipo_mensagem_byte = tipo_mensagem.to_bytes(1, "little")
        payload = bytes([0x00])
        tamanho = len(payload)
        tamanho_bytes = tamanho.to_bytes(3, "little")
        numero_pacote_bytes = ultimo_pct.to_bytes(3, "little")
        head = tamanho_bytes + tipo_mensagem_byte + numero_pacote_bytes + 3*head_vazio
        envio = head + payload + eop 
        com.sendData(envio)
        while(com.tx.getIsBussy()):
            pass
        time.sleep(0.01)

def ocioso(com):
    ocioso = True
    server = 84

    while ocioso:
        if com.rx.getIsEmpty():
            print("Esperando mensagem...")
        else:
            print("Mensagem recebida")
            head  = com.getData(10)[0]
            if descobrir_tipo(head) == 1:
                total_pacotes = ler_head(head, 1)[2]
                if ler_head(head, 1)[1] == server:
                    ocioso = False
                    forma_envio(2, com, 0)
                    print("Na escuta!")
                    com.rx.clearBuffer()
                    return total_pacotes
                    
                else:
                    time.sleep(1)
            else:
                time.sleep(1)
            com.rx.clearBuffer()

serialName = "COM17"              
print(f"abriu com {serialName}")

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

    #Fica ocioso até receber uma mensagem tipo 1
    total_pacotes = ocioso(com)
    i = 1


    #comeca a leitura dos pacotes
    payload = b""
    while i <= total_pacotes:
        timer1 = time.time()
        timer2 = time.time()
        head, lenHead = com.getData(10)
        t3 = False
        if descobrir_tipo(head) == 3:
            t3 = True
            tamanho, numero_pacote, total_pacotes = ler_head(head, 3)
            if numero_pacote == i:
                forma_envio(4, com, i)
                payload += com.getData(tamanho)
                eop = com.getData(3)
                i += 1
            else:
                forma_envio(6, com, i)    
                com.rx.clearBuffer()
        else:
            while not t3:
                com.rx.clearBuffer()
                time.sleep(1)
                if timer2 > 20:
                    forma_envio(5, com, i)
                    break
                else:
                    if timer1 > 2:
                        forma_envio(4, com, i)
                        timer1 = time.time()

    if total_pacotes == i: 
        payload_destuffed = tirarStuffing(payload)
        nome = input("Qual é o nome desejado?")

        with open(nome, "wb") as image:
            image.write(payload_destuffed) 

    


    # Encerra comunicação
    print("-------------------------")
    print("Comunicação encerrada")
    print("-------------------------")
    com.disable()

    #so roda o main quando for executado do terminal ... se for chamado dentro de outro modulo nao roda
if __name__ == "__main__":
    main()
    