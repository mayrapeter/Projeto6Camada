# -*- coding: utf-8 -*-
"""
Created on Sun Sep 15 19:53:00 2019

@author: Mayra Peter
"""

from enlace import *
import time
import client2
from math import ceil

def descobrir_tipo(head):
    tipo_mensagem = head[3:4]
    tipo_mensagem = int.from_bytes(tipo_mensagem, "little")

    return tipo_mensagem

def tirarStuffing(payload):
    stuffing = bytes([0x00]) + bytes([0xF1]) + bytes([0x00]) + bytes([0xF2]) + bytes([0x00]) + bytes([0xF3])
    eop = bytes([0xF1]) + bytes([0xF2]) + bytes([0xF3])
    payload = payload.replace(stuffing, eop)

    return payload

def ler_head(dado, tipo):
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
        print("Mensagem tipo 5 enviada, encerrando conexão")
        client2.log("Mensagem tipo 5 enviada, encerrando conexão", "server")

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
            client2.log("Esperando mensagem...", "server")
            time.sleep(0.1)
        else:
            print("Mensagem recebida")
            client2.log("Mensagem recebida", "server")
            head  = com.getData(10, 2)[0]
            if head == []:
                print("Esperando mensagem...")
                client2.log("Esperando mensagem...", "server")
                com.rx.clearBuffer()
            elif descobrir_tipo(head) == 1:
                total_pacotes = ler_head(head, 1)[2]
                if ler_head(head, 1)[1] == server:
                    ocioso = False
                    forma_envio(2, com, 0)
                    print("Na escuta!")
                    client2.log("Na escuta!", "server")
                    com.rx.clearBuffer()
                    return total_pacotes
                    
                else:
                    print("Servidor incorreto")
                    client2.log("Servidor incorreto", "server")
                    time.sleep(1)
            else:
                time.sleep(1)
            com.rx.clearBuffer()

serialName = "COM16"              
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
    client2.log("Comunicação inicializada", "server")
    print("  porta : {}".format(com.fisica.name))
    client2.log("  porta : {}".format(com.fisica.name), "server")
    print("-------------------------")

    #Fica ocioso até receber uma mensagem tipo 1
    total_pacotes = ocioso(com)
    i = 1
    j = 1

    #comeca a leitura dos pacotes
    payload = b""
    while i <= total_pacotes:
        timer1 = time.time()
        timer2 = time.time()
        t3 = False
        while not t3:
            head = com.getData(10, 1)[0]
            if head == []:
                print("Esperando dentro do while...")
                client2.log("Esperando dentro do while...", "server")
                com.rx.clearBuffer()
                time.sleep(1)
                if (time.time() - timer2) > 20:
                    forma_envio(5, com, i)
                    i = total_pacotes + 1
                    print("Timer 2 passou de 20 segundos, encerrando") 
                    client2.log("Timer 2 passou de 20 segundos, encerrando", "server")
                    break
                elif (time.time() - timer1) > 2: 
                    print("Timer 1 passou de 2 segundos, reenviando")  
                    client2.log("Timer 1 passou de 2 segundos, reenviando", "server")       
                    forma_envio(4, com, i)
                    timer1 = time.time()
            elif head != [] and descobrir_tipo(head) == 3:
                t3 = True
                tamanho, numero_pacote, total_pacotes = ler_head(head, 3)
                if numero_pacote == i:
                    forma_envio(4, com, i)
                    print(f"Pacote {i} recebido e mensagem tipo 4 enviada")
                    client2.log(f"Pacote {i} recebido e mensagem tipo 4 enviada", "server")
                    payload += com.getData(tamanho, 1)[0]
                    eop = com.getData(3, 1)[0]
                    if i == total_pacotes:
                        i += 1
                        break
                    else:
                        i += 1
                        j = i
                else:
                    forma_envio(6, com, i)   
                    print(f"Pacote {i} esperado, orientando para reenvio com mensagem tipo 6")
                    client2.log(f"Pacote {i} esperado, orientando para reenvio com mensagem tipo 6", "server")
                    com.rx.clearBuffer()
            elif descobrir_tipo(head) == 5:
                print("mensagem tipo 5 recebida, encerrando conexão")
                client2.log("mensagem tipo 5 recebida, encerrando conexão", "server")
                break
            else:
                com.rx.clearBuffer()
                time.sleep(1)
                if (time.time() - timer2) > 20:
                    forma_envio(5, com, i)
                    i = total_pacotes + 1
                    print("Timer 2 passou de 20 segundos, encerrando") 
                    client2.log("Timer 2 passou de 20 segundos, encerrando", "server")
                    break
                elif (time.time() - timer1) > 2:          
                    forma_envio(4, com, i)
                    print("Timer 1 passou de 2 segundos, reenviando") 
                    client2.log("Timer 1 passou de 2 segundos, reenviando", "server")
                    timer1 = time.time()
    print(i)
    print(j)
    if total_pacotes == j: 
        payload_destuffed = tirarStuffing(payload)
        nome = input("Qual é o nome desejado?")

        with open(nome, "wb") as image:
            image.write(payload_destuffed) 

    


    # Encerra comunicação
    print("-------------------------")
    print("Comunicação encerrada")
    client2.log("Comunicação encerrada", "server")
    print("-------------------------")
    com.disable()

    #so roda o main quando for executado do terminal ... se for chamado dentro de outro modulo nao roda
if __name__ == "__main__":
    main()
    