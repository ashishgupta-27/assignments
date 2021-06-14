import argparse
import os
import sys
import socket 
import base64
import select
import secrets
import string
import time
import getpass
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives.ciphers.aead import AESCCM
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives.asymmetric import padding

arg_len = len(sys.argv)

host = ""
port = ""
user = ""
if arg_len == 4:
    host = sys.argv[1]
    port = int(sys.argv[2])
    user = sys.argv[3]
    
elif arg_len == 3:
    port = int(sys.argv[1])
    user = sys.argv[2]
    host = "127.0.0.1"

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM) 
server.connect((host, port))
client_port=server.getsockname()[1]
client_ip=server.getsockname()[0]
init_complete = False

serverKeysDirectory = "serverKeys";
serverPublicKeyFile = 'server_pub.txt'
serverPublicKeyFile1 = serverKeysDirectory+"/"+"serverpub.txt"


def encryptMessage(message,sessionKey, nonce) :
    
    aesccm = AESCCM(sessionKey)
    
    encMessage = aesccm.encrypt(nonce, message, None)
    
    return encMessage
    
def decryptMessage(encMessage, sessionKey, nonce) :

    aesccm = AESCCM(sessionKey)
    
    message = aesccm.decrypt(nonce, encMessage, None)
    
    return message
    

def executeCommand(message) :
    
    message_arr = message.split(' ')
    actualCommand = 'Error in command. Please try again...'
    if message_arr[0] == 'listfiles':
        actualCommand = 'LS'
    elif message_arr[0] == 'cwd':
        actualCommand = 'PWD'
    elif message_arr[0] == 'chgdir':
        actualCommand = 'CD ' + message_arr[1].strip()
    elif message_arr[0] == 'cp':
        actualCommand = 'CP '+message_arr[1].strip()+' '+message_arr[2].strip()+' '+message_arr[3].strip()
    elif message_arr[0] == 'mv':
        actualCommand = 'MV '+message_arr[1].strip()+' '+message_arr[2].strip()+' '+message_arr[3].strip()
    
    return actualCommand
    
    

sessionKey = AESCCM.generate_key(bit_length=256)
nonce = os.urandom(13)
  
while True: 
  
    # maintains a list of possible input streams 
    sockets_list = [sys.stdin, server] 
  
    """ There are two possible input situations. Either the 
    user wants to give manual input to send to other people, 
    or the server is sending a message to be printed on the 
    screen. Select returns from sockets_list, the stream that 
    is reader for input. So for example, if the server wants 
    to send a message, then the if condition will hold true 
    below.If the user wants to send a message, the else 
    condition will evaluate as true"""
    read_sockets,write_socket, error_socket = select.select(sockets_list,[],[]) 
    
    for socks in read_sockets: 
        if socks == server:
            if init_complete == False :
                print ("Receiving public key from SSH server")
                f = open(serverPublicKeyFile,'wb')
                l = socks.recv(2048)
                f.write(l)
                f.close()
                print ("Done Receiving the public key")
                
                #print("Enter passphrase for the user "+user)
                
                #passphrase=sys.stdin.readline()
                passphrase = getpass.getpass("Enter passphrase for the user "+user+": ")
                #sessionKey = os.urandom(32)
                print("Sending encrypted session key to the server")
                sessionKeyEncoded = base64.urlsafe_b64encode(sessionKey)
                sessionKeyMessage = "| "+user+" | "+passphrase.strip()+" | "+sessionKeyEncoded + " |"
                
                #print(sessionKeyMessage)
                with open(serverPublicKeyFile, "rb") as key_file:
                    serverPublicKey = serialization.load_pem_public_key(
                        key_file.read(),
                        backend=default_backend()
                    )
                
                message =b"Hello"
                #print(serverPublicKey)
                encryptedUser = serverPublicKey.encrypt(
                    user.encode(),
                    padding.OAEP(
                        mgf=padding.MGF1(algorithm=hashes.SHA256()),
                        algorithm=hashes.SHA256(),
                        label=None
                    )
                )
                
                encryptedPassphrase = serverPublicKey.encrypt(
                    passphrase.encode(),
                    padding.OAEP(
                        mgf=padding.MGF1(algorithm=hashes.SHA256()),
                        algorithm=hashes.SHA256(),
                        label=None
                    )
                )
                
                encryptedSessionKey = serverPublicKey.encrypt(
                    sessionKey,
                    padding.OAEP(
                        mgf=padding.MGF1(algorithm=hashes.SHA256()),
                        algorithm=hashes.SHA256(),
                        label=None
                    )
                )
                
                
                
                encryptedNonce = serverPublicKey.encrypt(
                    nonce,
                    padding.OAEP(
                        mgf=padding.MGF1(algorithm=hashes.SHA256()),
                        algorithm=hashes.SHA256(),
                        label=None
                    )
                )
                
                server.send(encryptedUser)
                message = server.recv(2048)
                print(message)
                server.send(encryptedPassphrase)
                message = server.recv(2048)
                print(message)
                server.send(encryptedNonce)
                message = server.recv(2048)
                print(message)
                server.send(encryptedSessionKey)
                
                print("Sending of encrypted session key complete")
                
                ackMessage = server.recv(2048)
                print(ackMessage)
                if ackMessage == 'OK' :
                    init_complete = True
                
                
            else :
                message = socks.recv(2048)
                print("Server output:")
                print (decryptMessage(message, sessionKey, nonce)) 
        else:
            #print("Client-Prompt>")
            message = sys.stdin.readline() 
            commandToSend = executeCommand(message.strip())
            #print("Command to send:" + commandToSend.strip())
            server.send(encryptMessage(commandToSend.strip(),sessionKey, nonce))
                
            #sys.stdout.write("<You>") 
            #sys.stdout.write(message.strip()) 
            sys.stdout.flush()
            
server.close() 