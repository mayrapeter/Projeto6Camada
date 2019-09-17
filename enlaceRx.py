#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#####################################################
# Camada Física da Computação
#Carareto
#08/008/2019
#  Camada de Enlace 
####################################################

# Importa pacote de tempo
import time

# Threads
import threading

# Class
class RX(object):
    """ This class implements methods to handle the reception
        data over the p2p fox protocol
    """
    
    def __init__(self, fisica):
        """ Initializes the TX class
        """
        self.fisica      = fisica
        self.buffer      = bytes(bytearray())
        self.threadStop  = False
        self.threadMutex = True
        self.READLEN     = 1024

    def thread(self): 
        """ RX thread, to send data in parallel with the code
        essa é a funcao executada quando o thread é chamado. 
        """
        while not self.threadStop:
            if(self.threadMutex == True):
                rxTemp, nRx = self.fisica.read(self.READLEN)
                if (nRx > 0):
                    self.buffer += rxTemp
                time.sleep(0.001)

    def threadStart(self):
        """ Starts RX thread (generate and run)
        """
        self.thread = threading.Thread(target=self.thread, args=())
        self.thread.start()

    def threadKill(self):
        """ Kill RX thread
        """
        self.threadStop = True

    def threadPause(self):
        """ Stops the RX thread to run

        This must be used when manipulating the Rx buffer
        """
        self.threadMutex = False

    def threadResume(self):
        """ Resume the RX thread (after suspended)
        """
        self.threadMutex = True

    def getIsEmpty(self):
        """ Return if the reception buffer is empty
        """
        if(self.getBufferLen() == 0):
            return(True)
        else:
            return(False)

    def getBufferLen(self):
        """ Return the total number of bytes in the reception buffer
        """
        return(len(self.buffer))

    def getAllBuffer(self, len):
        """ Read ALL reception buffer and clears it
        """
        self.threadPause()
        b = self.buffer[:]
        self.clearBuffer()
        self.threadResume()
        return(b)

    def getBuffer(self, nData):
        """ retorna e remove n data from buffer
        """
        self.threadPause()
        b           = self.buffer[0:nData]
        self.buffer = self.buffer[nData:]
        self.threadResume()
        return(b)

    def getNData(self, size, timer1,timer2):
        """ Read N bytes of data from the reception buffer
        This function blocks until the number of bytes is received
        """
        reenvio = False 
        time_out = False
        x = 0
        while(self.getBufferLen() < size):
            x = 0
            print('Aguardando dados...')
            if time.time() - timer2 > 20:
                reenvio = False
                time_out = True
                x = 1
                break
            elif time.time() - timer1 > 5:
                reenvio = True
                time_out = False
                x = 1
                break
            time.sleep(0.1)

        eop = bytes([0xF1]) + bytes([0xF2]) + bytes([0xF3])
        vazio = 0
        vazio = vazio.to_bytes(9, "little")
                
        if x == 0:          
            return(self.getBuffer(size), reenvio, time_out)
        elif x == 1:
            if not time_out:
                deu_x = 0
                return(deu_x.to_bytes(1, "little") + vazio + eop, reenvio, time_out)
            else:
                deu_x = 5
                return(deu_x.to_bytes(1, "little") + vazio + eop, reenvio, time_out)

 
    def clearBuffer(self):
        """ Clear the reception buffer
        """
        self.buffer = b""


