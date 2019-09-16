#!/usr/bin/env python3
# -- coding: utf-8 --
#####################################################
# Camada Física da Computação
#Carareto
#17/02/2018
#  Aplicação 
####################################################

#bytes([0xff])*5 + bytes([0xf1]) + bytes([0xf2]) + bytes([0xf3]) + bytes([0xff])*10

print("comecou")

from enlace import *
import time
from math import ceil

com = 0

def forma_envio(com, tipo_mensagem, head4):

    servidor = 84

    #com imagem
    #tipo_mensagem = int(input("Qual o tipo de mensagem desejada? "))
    if tipo_mensagem == 1 or tipo_mensagem == 4 or tipo_mensagem == 6:
        objeto_bytearray = bytes([0x00])    
      
    head_vazio = bytes([0x00]) 

    eop = bytes([0xF1]) + bytes([0xF2]) + bytes([0xF3])

    stuffing = bytes([0x00]) + bytes([0xF1]) + bytes([0x00]) + bytes([0xF2]) + bytes([0x00]) + bytes([0xF3])

    objeto_bytearray = head_vazio


    tamanho = len(objeto_bytearray)

    tipo_mensagem_byte = tipo_mensagem.to_bytes(1, "little")

    print("tipo", tipo_mensagem)
    print("tipobyte", tipo_mensagem_byte)

    servidor_byte = servidor.to_bytes(1, "little")

    if tipo_mensagem == 1:
        tamanho_bytes = tamanho.to_bytes(3, "little")
        head = tamanho_bytes + tipo_mensagem_byte + servidor_byte + tipo_mensagem_byte + head_vazio
        print("head enviado", head)
        payload = objeto_bytearray
        envio = head + payload + eop 

        com.sendData(envio)
        while(com.tx.getIsBussy()):
            pass

        time.sleep(0.1)

    if tipo_mensagem == 4:
        tamanhoaler, numero_pacote, total_pacotes = ler_head(head4, 3)
        tamanho_bytes = tamanho.to_bytes(3, "little")
        numero_pacote = numero_pacote.to_bytes(3, "little")
        head = tamanho_bytes + tipo_mensagem_byte + numero_pacote + 3*head_vazio
        payload = head_vazio + head_vazio
        envio = head + payload + eop 

        com.sendData(envio)
        while(com.tx.getIsBussy()):
            pass

        time.sleep(0.1)

    if tipo_mensagem == 6:
        print("AAAAAAAAAAAAAAAA MENSAGEM TIPO 6 ERRO")
        tamanhoaler, numero_pacote, total_pacotes = ler_head(head4, 3)
        tamanho_bytes = tamanho.to_bytes(3, "little")
        numero_pacote = numero_pacote.to_bytes(3, "little")
        head = tamanho_bytes + tipo_mensagem_byte + numero_pacote + 3*head_vazio
        payload = head_vazio + head_vazio
        envio = head + payload + eop 

        com.sendData(envio)
        while(com.tx.getIsBussy()):
            pass

        time.sleep(0.1)

    if tipo_mensagem == 5:
        tipo_mensagem_byte = tipo_mensagem.to_bytes(1, "little")
        payload = bytes([0x00])
        tamanho = len(payload)
        tamanho_bytes = tamanho.to_bytes(3, "little")
        head = tamanho_bytes + tipo_mensagem_byte + 6*payload 
        envio = head + payload + eop 

        com.sendData(envio)
        while(com.tx.getIsBussy()):
            pass

        time.sleep(0.1)


    

           
    #overhead = len(envio)/len(objeto_bytearray)
    #tamanho_total = len(envio)
    #print(envio)
    #print(tamanho)

    #print("conteudo enviado:", envio)



def descobrir_tipo(dado):

    tipo_mensagem = dado[3:4]
    tipo_mensagem = int.from_bytes(tipo_mensagem, "little")

    return tipo_mensagem

def ler_head(dado, tipo_mensagem):
    print("head recebido:", dado)
    tamanhoByte = dado[:3]
    tamanho = int.from_bytes(tamanhoByte, "little")
    print("Tamanho para ler", tamanho)
    print("Tamanho byte", tamanhoByte)

    if tipo_mensagem == 1:
        numero_servidor = dado[4:5]
        numero_servidor = int.from_bytes(numero_servidor, "little")
        total_pacotes = dado[5:8]
        return tamanho, numero_servidor, total_pacotes

    if tipo_mensagem == 3:
    
        numero_pacote = dado[4:7]
        numero_pacote = int.from_bytes(numero_pacote, "little")
        total_pacotes = dado[7:]
        total_pacotes = int.from_bytes(total_pacotes, "little")
        return tamanho, numero_pacote, total_pacotes
  
    
    #return numero_pacote, total_pacotes, tamanho


def tirar_stuffing(dado):
    stuffing = bytes([0x00]) + bytes([0xF1]) + bytes([0x00]) + bytes([0xF2]) + bytes([0x00]) + bytes([0xF3])
    eop = bytes([0xF1]) + bytes([0xF2]) + bytes([0xF3])
    dado = dado.replace(stuffing, eop)

    return dado

def ocioso():
    servidor = 84
    ocioso = True
    while ocioso:
        print("procurando conexao")
        recebeu_pacote = True
        time1 = time.time()
        while com.rx.getIsEmpty():
            if time.time() - time1 > 1:
                recebeu_pacote = False
                break
        print(f"recebeu pacote: {recebeu_pacote}")
        if recebeu_pacote:
            head, nRx = com.getData(10, time.time(), time.time())

            tipo_mensagem = descobrir_tipo(head)
            if tipo_mensagem == 1:
                numero_servidor = ler_head(head, tipo_mensagem)[1]
                if numero_servidor == servidor:
                    servidor_pronto = True
                    total_pacotes = ler_head(head, 1)[2]
            else:
                servidor_pronto = False
            print("Esperando")
            if servidor_pronto:
                ocioso = False
    return total_pacotes


def read_package(timer2):
    timer1 = time.time()
    head, nRx = com.getData(10, timer1, timer2)
    if head == -1:
        print("timeout")
        return
    elif head == -2:
        forma_envio(com, 4, head)
        return 

    tamanhoaler, numero_pacote, total_pacotes = ler_head(head, tipo_mensagem)
    print("Numero do pacote", numero_pacote)
    print("Total de pacotes", total_pacotes)
    print("head recebido", head)

    payload, nRx = com.getData(tamanhoaler, timer1, timer2)
    if head == -1:
        print("timeout")
        return b""
    elif head == -2:
        forma_envio(com, 4, head)
        return b""

    eop, nRxEnd = com.getData(3)
    
    tudo = head + payload + eop
    posicao_encontrada = []
    eop = bytes([0xF1]) + bytes([0xF2]) + bytes([0xF3])
    for i in range(0, len(tudo)-2):
        end = bytes([tudo[i]]) + bytes([tudo[i + 1]]) + bytes([tudo[i + 2]])
        if end == eop:
            posicao_encontrada.append(i)
            posicao_encontrada.append(i+1)
            posicao_encontrada.append(i+2)
            print("EOP encontrado na posição {0}, {1} e {2}.".format(i, i+1, i+2))
    posicao_esperada = [len(tudo)-2, len(tudo)-1, len(tudo)]
    
    if posicao_encontrada == posicao_esperada:
        if payload is not None:
            payload_total_stuffed = payload
        else:
            payload_total_stuffed = b""
        forma_envio(com, 4, head)
        print("EOP encontrado na posição esperada")
        return payload_total_stuffed

    if eop in (head + payload):
        print("EOP encontrado no lugar errado")
        forma_envio(com, 6, head)
    elif eop not in(tudo):
        print("Erro, EOP não encontrado")
        forma_envio(com, 6, head)

    if (len(tudo) - len(eop) - len(head)) == len(payload):
        print("Tamanho esperado encontrado")
    else:
        print("Tamanho esperado não encontrado")
        forma_envio(com, 6, head)
    return b""
    
    


def ler_payload(head, tipo_mensagem, com):

    if tipo_mensagem == 1:
        
        print("tipo mensagem", tipo_mensagem)
        tamanhoaler, numero_servidor, total_pacotes = ler_head(head, tipo_mensagem)
        if numero_servidor == servidor:
            print("Servidor correto")
        else:
            print("Servidor incorreto")

        payload,nRx2 = com.getData(tamanhoaler)
        #print("numero:",int.from_bytes(numero_pacote, "little"),"total:",int.from_bytes(total_pacotes, "little"))
        print(head)

        payload_total = payload

        eop, nRxEnd = com.getData(3)
            
        tudo = head + payload + eop
        posicao_encontrada = []
        eop = bytes([0xF1]) + bytes([0xF2]) + bytes([0xF3])
        for i in range(0, len(tudo)-2):
            end = bytes([tudo[i]]) + bytes([tudo[i + 1]]) + bytes([tudo[i + 2]])
            if end == eop:
                posicao_encontrada.append(i)
                posicao_encontrada.append(i+1)
                posicao_encontrada.append(i+2)
                print("EOP encontrado na posição {0}, {1} e {2}.".format(i, i+1, i+2))
        posicao_esperada = [len(tudo)-2, len(tudo)-1, len(tudo)]
        
        if posicao_encontrada == posicao_esperada:
            print("EOP encontrado na posição esperada")
        if eop in (head + payload):
            print("EOP encontrado no lugar errado")
            forma_envio(com, 6, head)
        elif eop not in(tudo):
            print("Erro, EOP não encontrado")
            forma_envio(com, 6, head)

        if (len(tudo) - len(eop) - len(head)) == len(payload):
            print("Tamanho esperado encontrado")

        else:
            print("Tamanho esperado não encontrado") 
            forma_envio(com, 6, head)

        tipo_mensagem = 2
        tipo_mensagem_byte = tipo_mensagem.to_bytes(1, "little")

        head = head[:3] + tipo_mensagem_byte + head[4:] 
        print("head", head)
        payload = 2*bytes([0x00])
        envio = head + payload + eop 
        print(envio)

        com.sendData(envio)
        return

    elif tipo_mensagem == 3:
        tempo1 = time.time()
        tempo2 = time.time()
        t = time.time()
        tamanhoaler, numero_pacote, total_pacotes = ler_head(head, tipo_mensagem)

        print("Numero do pacote", numero_pacote)
        print("Total de pacotes", total_pacotes)
        print("head recebido", head)

        payload,nRx2 = com.getData(tamanhoaler, tempo1, tempo2)
        
        payload_total = payload

        eop, nRxEnd = com.getData(3, t, t)
            
        tudo = head + payload + eop
        posicao_encontrada = []
        eop = bytes([0xF1]) + bytes([0xF2]) + bytes([0xF3])
        for i in range(0, len(tudo)-2):
            end = bytes([tudo[i]]) + bytes([tudo[i + 1]]) + bytes([tudo[i + 2]])
            if end == eop:
                posicao_encontrada.append(i)
                posicao_encontrada.append(i+1)
                posicao_encontrada.append(i+2)
                print("EOP encontrado na posição {0}, {1} e {2}.".format(i, i+1, i+2))
        posicao_esperada = [len(tudo)-2, len(tudo)-1, len(tudo)]
        
        if posicao_encontrada == posicao_esperada:
            print("EOP encontrado na posição esperada")
        if eop in (head + payload):
            print("EOP encontrado no lugar errado")
            forma_envio(com, 6, head)
        elif eop not in(tudo):
            print("Erro, EOP não encontrado")
            forma_envio(com, 6, head)

        if (len(tudo) - len(eop) - len(head)) == len(payload):
            print("Tamanho esperado encontrado")
        else:
            print("Tamanho esperado não encontrado")  
            forma_envio(com, 6, head)  
        
        

        forma_envio(com, 4, head)
        

        dadoSemStuffing = tirar_stuffing(payload_total)

        return dadoSemStuffing
       
        
         
    
    
        

# Serial Com Port
#   para saber a sua porta, execute no terminal :
#   python -m serial.tools.list_ports


serialName = "COM17"                  # Windows(variacao de)
print(f"abriu com {serialName}")
servidor = 84

def run():
    total_pacotes = ocioso()
    forma_envio(com, 2, 0)
    pacote_atual = 1
    payload_total_stuffed = b""
    total_pacotes = int.from_bytes(total_pacotes, "little")
    while pacote_atual <= total_pacotes:
        timer2 = time.time()
        payload_total_stuffed += read_package(timer2)
        pacote_atual += 1
    payload_destuffed = tirar_stuffing(payload_total_stuffed)
    return payload_destuffed




def main():
    print("a")
    global com
    # Inicializa enlace ... variavel com possui todos os metodos e propriedades do enlace, que funciona em threading
    com = enlace(serialName) # repare que o metodo construtor recebe um string (nome)
    # Ativa comunicacao
    com.enable()
    print("b")
    com.rx.clearBuffer()
    print("c")
    payload_destuffed = run()

   

    # Log
    print("-------------------------")
    print("Comunicação inicializada")
    print("  porta : {}".format(com.fisica.name))
    print("-------------------------")

    # Carrega dados
    print ("gerando dados para transmissao :")
  


    # Faz a recepção dos dados
    print ("Recebendo dados .... ")
    
    #forma_envio(com, 2, head)


    # if servidor_pronto:
    #     print("recebendo")
        
    #     while tipo_mensagem != 3:
    #         head,nRx = com.getData(10, timer1, timer2)
    #         tipo_mensagem = descobrir_tipo(head)
    #         if tipo_mensagem == 3:
    #             dadoSemStuffing = ler_payload(head, tipo_mensagem, com)
    #         else: 
    #             time.sleep(1)
    #             if timer2>20:
    #                 forma_envio(com,5,0)
    #                 com.disable()
    #                 print("Encerrando")
    #                 exit()
    #             if timer1>2:
    #                 forma_envio(com,4,head)
    #                 timer1 = time.time()
    nome = input("Qual é o nome desejado?")

    with open(nome, "wb") as image:
        image.write(payload_destuffed) 

    
    #repare que o tamanho da mensagem a ser lida é conhecida!
    #while(com.rx.getIsEmpty()):
    #    pass

    
               
    #if numero_pacote == total_pacotes:
       # print("Todos os pacotes foram recebidos")

    # espera o fim da transmissão
    #while(com.tx.getIsBussy()):
    #    pass
    
    
    # Atualiza dados da transmissão
    # txSize = com.tx.getStatus()
    # print ("Transmitido       {} bytes ".format(txSize))
    # print("Enviado")
    #nome = input("Qual é o nome desejado?")
    
    #with open(nome, "wb") as image:
      #  image.write(dadoSemStuffing)

    

    # Encerra comunicação
    print("-------------------------")
    print("Comunicação encerrada")
    print("-------------------------")
    com.disable()

    #so roda o main quando for executado do terminal ... se for chamado dentro de outro modulo nao roda
if __name__ == "__main__":
    main()