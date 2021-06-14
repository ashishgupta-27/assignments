import argparse
import os
import sys
import socket
import base64
import select
import secrets
import string
import shutil
import time
from os import path
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives.ciphers.aead import AESCCM
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives import padding as sym_padding
from thread import *

print("SSH server started...")
print("Generating public and private keys for myself...")

serverKeysDirectory = "serverKeys";
if not os.path.exists(serverKeysDirectory):
    os.makedirs(serverKeysDirectory)

private_key = rsa.generate_private_key(
    public_exponent=65537,
    key_size=2048,
    backend=default_backend()
)

public_key = private_key.public_key()

pem = private_key.private_bytes(
    encoding=serialization.Encoding.PEM,
    format=serialization.PrivateFormat.PKCS8,
    encryption_algorithm=serialization.NoEncryption()
)

serverPrivateKeyFile = serverKeysDirectory+"/"+"serverpriv.txt"
with open(serverPrivateKeyFile, 'wb') as f:
    f.write(pem)

pem = public_key.public_bytes(
    encoding=serialization.Encoding.PEM,
    format=serialization.PublicFormat.SubjectPublicKeyInfo
)

serverPublicKeyFile = serverKeysDirectory+"/"+"serverpub.txt"
with open(serverPublicKeyFile, 'wb') as f:
    f.write(pem)

print("Public and private keys generated successfully")

def encryptMessage(message,sessionKey, nonce) :
    
    aesccm = AESCCM(sessionKey)
    
    encryptedMessage = aesccm.encrypt(nonce, message, None)
    
    return encryptedMessage
    
def decryptMessage(encryptedMessage, sessionKey, nonce) :

    aesccm = AESCCM(sessionKey)
    
    message = aesccm.decrypt(nonce, encryptedMessage, None)
    
    return message
    
def executeCommands(command):

    command_arr = command.split(" ")
    message = ""
    if command_arr[0] == "LS":
        files = [f for f in os.listdir('.') if os.path.isfile(f)]
        for f in files:
            message = message+f+"\n"

    elif command_arr[0] == "PWD":
        message = os.getcwd()

    elif command_arr[0] == "CD":
        destDir = command_arr[1].strip()
        #print("Changing directory to "+destDir)
        os.chdir(str(destDir))
        ddir = os.getcwd()
        message = "Directory changed to "+ddir

    elif command_arr[0] == "CP":
        file = command_arr[1].strip()
        sourceDir = command_arr[2].strip()
        destDir = command_arr[3].strip()

        fileToCopy = sourceDir+"/"+file
        print("Source file path:"+fileToCopy)
        print("Destination file path:"+destDir)
        try:
            shutil.copy(fileToCopy, destDir)
            message = "File copied successfully."
        except IOError as e:
            message = "Unable to copy file. " + e
            print("Unable to copy file. %s" % e)
        except:
            message = "Unexpected error."
            print("Unexpected error:", sys.exc_info())

    elif command_arr[0] == "MV":
        file = command_arr[1].strip()
        sourceDir = command_arr[2].strip()
        destDir = command_arr[3].strip()

        fileToMove = sourceDir+"/"+file
        print("Source file path:"+fileToMove)
        print("Destination file path:"+destDir)
        try:
            shutil.move(fileToMove, destDir)
            message = "File moved/renamed successfully."
        except IOError as e:
            message = "Unable to move file. " + e
            print("Unable to move file. %s" % e)
        except:
            message = "Unexpected error."
            print("Unexpected error:", sys.exc_info()) #os.rename(fileToMove, destDir)

    return message

def verifyUser(username, passphrase):
    userFile = 'UserCredentials/'+username+'.txt'
    with open(userFile, 'r') as file:
        lines = file.readlines()
        user = lines[0]
        user_salt = lines[1]
        user_key = lines[2]
    
    #print(user_key.strip())
    decodedUserSalt = base64.urlsafe_b64decode(user_salt)
    decodedKey = base64.urlsafe_b64decode(user_key)
    
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=decodedUserSalt,
        iterations=1000,
    )
    
    
    
    #newKey = base64.urlsafe_b64encode(kdf.derive(passphrase.encode()))
    #print("N:"+newKey.strip())
    #if newKey == user_key:
        #print("Same")
     
    try:
        kdf.verify(passphrase.encode(), decodedKey)
    except:
        return "NOK"
    
    return "OK"
           
port = int(sys.argv[1])

SOCKET_LIST = []
sock_list = []
stored = []
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
server_socket.bind(('', port))
server_socket.listen(10)
SOCKET_LIST.append(server_socket)
list_of_clients = []
global sessionKey
global nonce

def clientthread(conn, addr):

    # sends a message to the client whose user object is conn
    welcomeMessage = "Welcome to this SSH server on port "+str(port)
    conn.send(encryptMessage(welcomeMessage, sessionKey, nonce))

    while True:
        try:
            message = conn.recv(2048)
            if message:

                """prints the message and address of the
                 user who just sent the message on the server
                 terminal"""
                decryptedCommand = decryptMessage(message, sessionKey, nonce)
                #print(decryptedCommand)
                print ("<" + addr[0] +":"+str(addr[1])+ ">: " + decryptedCommand.strip())
                
                message_to_send = executeCommands(decryptedCommand.strip())
                print("Message to send:\n"+message_to_send)
                encryptedMessageToSend = encryptMessage(message_to_send, sessionKey, nonce)
                    # message_arr=message.split("|")
                    # #print(len(message_arr))
                    # logfile.write("<" + addr[0] +":"+str(addr[1])+ ">: " + message+"\n")
                    # if message_arr[1].strip() == '301':
                        # message_to_send=register_user(message_arr,pwdfile)
                    # elif message_arr[1].strip() == '305':
                        # message_to_send=generate_session_key(message_arr,pwdfile)
                    # print(message_arr)
                    # Calls broadcast function to send message to all 
                    # message_to_send = "<" + addr[0] +":"+str(addr[1])+ "> " + message 
                    # logfile.write(message_to_send+"\n")
                broadcast(encryptedMessageToSend, conn) 
  
            else: 
                """message may have no content if the connection 
                 is broken, in this case we remove the connection"""
                #print("Problem 1")
                remove(conn)
        except:
            #print("Problem 2")
            continue
				

"""Using the below function, we broadcast the message to all 
clients who's object is not the same as the one sending 
the message """
def broadcast(message, connection): 
    # for clients in list_of_clients: 
        # if clients!=connection: 
            # try: 
                # clients.send(message) 
            # except: 
                # clients.close() 
  
                # # if the link is broken, we remove the client 
                # remove(clients)
    try:
        connection.send( message)
    except:
        connection.close()
  
"""The following function simply removes the object 
from the list that was created at the beginning of 
the program"""
def remove(connection): 
    if connection in list_of_clients: 
        list_of_clients.remove(connection) 
  
while True: 
  
    """Accepts a connection request and stores two parameters, 
    conn which is a socket object for that user, and addr 
    which contains the IP address of the client that just 
    connected"""
    conn, addr = server_socket.accept() 
  
    """Maintains a list of clients for ease of broadcasting 
    a message to all available people in the chatroom"""
    list_of_clients.append(conn) 
  
    # prints the address of the user that just connected 
    print (addr[0] +" "+str(addr[1])+ " connected")
    print ("Sending server public key to client... ")
    f = open(serverPublicKeyFile,'rb')
    l = f.read(1024)
    conn.send(l)
    f.close()
    
    print("Sending of server public key complete")
    time.sleep(10)
    
    encryptedUser = conn.recv(2048)
    conn.send(b'User received')
    encryptedPassphrase = conn.recv(2048)
    conn.send(b'Passphrase received')
    encryptedNonce = conn.recv(2048)
    conn.send(b'Nonce received')
    encryptedSessionKey = conn.recv(2048)
    
    
    username = private_key.decrypt(
        encryptedUser,
        padding.OAEP(
            mgf=padding.MGF1(algorithm=hashes.SHA256()),
            algorithm=hashes.SHA256(),
            label=None
        )
    )
    
    passphrase = private_key.decrypt(
        encryptedPassphrase,
        padding.OAEP(
            mgf=padding.MGF1(algorithm=hashes.SHA256()),
            algorithm=hashes.SHA256(),
            label=None
        )
    )
    
    sessionKey = private_key.decrypt(
        encryptedSessionKey,
        padding.OAEP(
            mgf=padding.MGF1(algorithm=hashes.SHA256()),
            algorithm=hashes.SHA256(),
            label=None
        )
    )
    
    nonce = private_key.decrypt(
        encryptedNonce,
        padding.OAEP(
            mgf=padding.MGF1(algorithm=hashes.SHA256()),
            algorithm=hashes.SHA256(),
            label=None
        )
    )
    ackMessage = verifyUser(username, passphrase.strip())
    #ackMessage = "OK"
    conn.send(ackMessage.encode())
    #sessionKeyMessage_arr = sessionKeyMessage.split("|")
    print("Username: "+username)
    #print("Passphrase: " +passphrase.strip())
    sessionKeyEncoded = base64.urlsafe_b64encode(sessionKey)
    #print("SessionKey: " +sessionKeyEncoded)
    #logfile.write(addr[0] +" "+str(addr[1])+ " connected\n")
    # creates and individual thread for every user 
    # that connects 
    start_new_thread(clientthread,(conn,addr))     
  
conn.close() 
server_socket.close()
