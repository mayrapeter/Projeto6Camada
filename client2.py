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
from datetime import datetime
now = datetime.now()
# dd/mm/YY H:M:S
dt_string = now.strftime("%d/%m/%Y %H:%M:%S")

def log(message, sender):
    if sender == "client":
        with open('LogClient.txt', 'a') as arquivo:
            arquivo.write("\nMsg: {0} Recebida: {1} – destinatário: Client \n".format(message,dt_string))
    elif sender == "server":
        with open('LogServer.txt', 'a') as arquivo:
            arquivo.write("\nMsg: {0} Recebida: {1} – destinatário: Server \n".format(message,dt_string))
    else:
        with open('LogClient.txt', 'a') as arquivo:
            arquivo.write("\nMsg: {0} Recebida: {1} – destinatário: Client \n".format(message,dt_string))
        with open('LogServer.txt', 'a') as arquivo:
            arquivo.write("\nMsg: {0} Recebida: {1} – destinatário: Server \n".format(message,dt_string))


def analisa_transmissao(throughput):
    if throughput < 0:
        return "Erro, analise não pode ser concluida"
    elif throughput >= 0 and throughput < 400:
        calculo = 2*throughput/400
        if calculo >= 0 and calculo < 0.5:
            return calculo,"muito lento"
        elif calculo >= 0.5 and calculo < 1:
            return calculo,"lento"
        elif calculo >= 1 and calculo < 1.5:
            return calculo,"bom"
        else:
            return calculo,"ótimo"
    else:
        return 2, "excelente"


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

serialName = "COM17"                  # Windows(variacao de)
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
        objeto_bytearray_unstuffed = bytearray(f)

    tempo_throughput = time.time()
    eop =  bytes([0xF1]) + bytes([0xF2]) + bytes([0xF3])
    stuffing = bytes([0x00]) + bytes([0xF1]) + bytes([0x00]) + bytes([0xF2]) + bytes([0x00]) + bytes([0xF3])
    objeto_bytearray = objeto_bytearray_unstuffed.replace(eop, stuffing)
    
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
        envio = head + payload + eop
        print('Mandando uma mensagem tipo 1')
        log("Mandando uma mensagem tipo 1", "client")
        com.sendData(envio)

        time.sleep(5)
        head = com.getData(10, 2)[0]
        com.rx.clearBuffer()
        if head == []:
            com.rx.clearBuffer()
            print("Esperando...")
            log("Esperando...", "client")
        else:
            tipo_mensagem = descobrir_tipo(head)
            if tipo_mensagem == 2: 
                print("Mensagem tipo 2 recebida")
                log("Mensagem tipo 2 recebida", "client")
                inicia = True
    terminou = False
    i = 1
    j = 1
    while i <= n_pacotes:
        recebido_t4 = False
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
        while not recebido_t4 and not terminou:
            head_response = com.getData(10, 2)[0]
            com.rx.clearBuffer()
            if head_response == []:
                if time.time() - timer1 > 5:
                    print("Timer 1 passou de 5 segundos, reenviando")
                    log("Timer 1 passou de 5 segundos, reenviando", "client")
                    com.sendData(envio)
                    while(com.tx.getIsBussy()):
                        pass
                    timer1 = time.time()
                if time.time() - timer2 > 20:
                    i = n_pacotes + 1
                    print("Timer 2 passou de 20 segundos, encerrando conexão")
                    log("Timer 2 passou de 20 segundos, encerrando conexão", "client")
                    tipo_mensagem = 5
                    tipo_mensagem_byte = tipo_mensagem.to_bytes(1, "little")
                    payload = bytes([0x00])
                    tamanho = len(payload)
                    tamanho_bytes = tamanho.to_bytes(3, "little")
                    head = tamanho_bytes + tipo_mensagem_byte + 6*vazio
                    envio = head + payload + eop 
                    com.sendData(envio)
                    while(com.tx.getIsBussy()):
                        pass
                    break
                    
            else:
                tipo_mensagem = descobrir_tipo(head_response)
                if tipo_mensagem == 4:
                    recebido_t4 = True
                    tamanho, numero_pacote = ler_head(head_response, 4)
                    if i == n_pacotes:
                        tempo_throughput_final = time.time()
                        terminou = True
                        i += 1
                        break
                    else:
                        print(f"Mensagem tipo 4 averiguando pacote {numero_pacote} recebida, aumentando contador para {numero_pacote + 1}")
                        log(f"Mensagem tipo 4 averiguando pacote {numero_pacote} recebida, aumentando contador para {numero_pacote + 1}", "client")
                        i = numero_pacote + 1
                        j = i
                        
                elif tipo_mensagem == 5:
                    print("mensagem tipo 5 recebida, encerrando conexão")
                    log("mensagem tipo 5 recebida, encerrando conexão", "client")
                    break
                elif tipo_mensagem == 6:
                    tamanho, numero_pacote = ler_head(head_response, 6)
                    print(f"Recebeu mensagem tipo 6 orientando para envio de pacote {numero_pacote}, reestabelecendo contagem")
                    log(f"Recebeu mensagem tipo 6 orientando para envio de pacote {numero_pacote}, reestabelecendo contagem", "client")
                    i = numero_pacote
                    j = i
                    tipo_mensagem = 3
                    tipo_mensagem_byte = tipo_mensagem.to_bytes(1, "little")
                    payload = pacotes[i-1]
                    n_pacote = i.to_bytes(3, "little")
                    tamanho_pacote = len(payload)
                    tamanho_pacote_bytes = tamanho_pacote.to_bytes(3, "little")
                    head = tamanho_pacote_bytes + tipo_mensagem_byte + n_pacote + n_pacotes_bytes    
                    envio = head + payload + eop

                    com.sendData(envio)
                    while(com.tx.getIsBussy()):
                        pass
                else:
                    if time.time() - timer1 > 5:
                        print("Timer 1 passou de 5 segundos, reenviando")
                        log("Timer 1 passou de 5 segundos, reenviando", "client")
                        com.sendData(envio)   
                        while(com.tx.getIsBussy()):
                            pass
                        timer1 = time.time()
                    if time.time() - timer2 > 20:
                        i = n_pacotes + 1
                        print("Timer 2 passou de 20 segundos (mensagem tipo 5) , encerrando conexão")
                        log("Timer 2 passou de 20 segundos (mensagem tipo 5) , encerrando conexão", "client")
                        tipo_mensagem = 5
                        tipo_mensagem_byte = tipo_mensagem.to_bytes(1, "little")
                        payload = bytes([0x00])
                        tamanho = len(payload)
                        tamanho_bytes = tamanho.to_bytes(3, "little")
                        head = tamanho_bytes + tipo_mensagem_byte + 6*vazio
                        envio = head + payload + eop 
                        com.sendData(envio)
                        while(com.tx.getIsBussy()):
                            pass
                        break
                    
    print(i)
    print(j)
    print(n_pacotes)
    if j == n_pacotes:
        print("Comunicação realizada com sucesso!")
        log("Comunicação realizada com sucesso!", "client")
        throughput = len(objeto_bytearray_unstuffed)/(tempo_throughput_final - tempo_throughput)
        print("Through put", throughput)  
        log("Through put: {0}".format(throughput), "client")     
        print("A avaliação do through put é:", analisa_transmissao(throughput)[0], "de 0 à 2,que corresponde a:", analisa_transmissao(throughput)[1])
        log("A avaliação do through put é: {0} de 0 à 2 que corresponde a: {1}".format(analisa_transmissao(throughput)[0],analisa_transmissao(throughput)[1]), "client")

    else:
        print("Comunicação interrompida :(")
        log("Comunicação interrompida :(", "client")
   
    # Encerra comunicação
    print("-------------------------")
    print("Comunicação encerrada")
    log("Comunicação encerrada", "client")
    print("-------------------------")
    com.disable()
    #so roda o main quando for executado do terminal ... se for chamado dentro de outro modulo nao roda
if __name__ == "__main__":
    main()