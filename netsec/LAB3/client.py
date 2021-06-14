import argparse
import os
import sys
import socket 
import base64
import select
import secrets
import string
import time
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

my_parser = argparse.ArgumentParser(description='To establish KDC connection with client')

my_parser.add_argument('-n', type=str, help='Client\'s name')
my_parser.add_argument('-o', type=str, help='Receiver\'s name if it is a sender and decrypted output file received by the receiver')
my_parser.add_argument('-m', type=str, help='Type : S for sender and R for receiver')
my_parser.add_argument('-i', type=str, help='File where contents have to be encrypted and send to the receiver')
my_parser.add_argument('-a', type=str, help='KDC\'s IP address')
my_parser.add_argument('-p', type=int, help='KDC\'s port number')
my_parser.add_argument('-s', type=str, help='File with encrypted contents received by receiver.')

args = my_parser.parse_args()

sender=args.n
client_type=args.m
if client_type == "S":
	receiver = args.o
elif client_type == "R":
	outfile = args.o
	
inputfile = args.i
outenc=args.s
kdc_ip=args.a
kdc_port=args.p


# Create a socket object 
# s = socket.socket()                       
  
# # connect to the server on local computer 
# s.connect((kdc_ip, kdc_port)) 
# s.send(b'Hello, I am alice')
# # receive data from the server 
# print (s.recv(1024) )
# # close the connection 
# s.close()   

# with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    # s.connect((kdc_ip, kdc_port))
    # client_port=s.getsockname()[1]
    # client_ip=s.getsockname()[0]
    # #reg_message='| 301 | '+client_ip+' | '+str(client_port)+' | password | alice |'
    # while True:
        # message = input()
        # s.sendall(message.encode())
    
        # data = s.recv(1024).decode()
        # #print(data)

        # print('Received', repr(data))

# s.close()
# s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
# #s.settimeout(2)
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM) 
server.connect((kdc_ip, kdc_port))
client_port=server.getsockname()[1]
client_ip=server.getsockname()[0]


def key_request():
    # sender_keyfile=os.getcwd()+'/'+sender+"_key.txt"
    # with open(sender_keyfile,'r') as sf:
        # encodedKey=sf.readline()
    
    #nonce1=os.urandom(16)
    nonce = secrets.randbelow(1000)
    temp_message=sender+' || '+receiver+' || '+ str(nonce)
    #print
    #print("Nonce:")
    #print(base64.urlsafe_b64encode(nonce1))
    #key = base64.urlsafe_b64decode(encodedKey)
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=sender.encode(),
        iterations=1000,
    )
    
    key = base64.urlsafe_b64encode(kdf.derive(client_pwd.encode()))
    
    #key=encodedKey
    f = Fernet(key)
    token = f.encrypt(temp_message.encode())
    request_message= '| 305 | '+ base64.urlsafe_b64encode(token)+ ' | '+ sender +' |'
    return request_message
    
def retrieve_session_key(rec_req_msg):
    message_arr=rec_req_msg.split('|')
    skey_enc_message=message_arr[2].strip()
    
    # sender_keyfile=os.getcwd()+'/'+sender+"_key.txt"
    # with open(sender_keyfile,'r') as sf:
        # encodedKey=sf.readline()
    
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=sender.encode(),
        iterations=1000,
    )
    
    key = base64.urlsafe_b64encode(kdf.derive(client_pwd.encode()))
    
    #key = base64.urlsafe_b64decode(encodedKey)
    #key = encodedKey
    f = Fernet(key)
    decoded_skey_message = base64.urlsafe_b64decode(skey_enc_message)
    skey_message = f.decrypt(decoded_skey_message)
    skey_msg_arr=skey_message.decode().split("||")
    session_key=skey_msg_arr[0].strip()
    receiverToken=skey_msg_arr[6].strip()
    nonce1 = skey_msg_arr[3].strip()
    #print("Nonce:")
    #print(nonce1)
    receiver_ip=skey_msg_arr[4].strip()
    receiver_port=skey_msg_arr[5].strip()
    #print("Session key:"+session_key)
    return session_key,receiverToken,receiver_ip,receiver_port,nonce1

def encrypt_file(session_key, inputfile,nonce1):
    
    salt=os.urandom(16)
    saltfile=os.getcwd()+'/file_salt.txt'
    
    with open(saltfile, 'wb') as file:
        file.write(base64.urlsafe_b64encode(salt))
        file.close()
        
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=1000,
    )
    
    encodedSessionKey = base64.urlsafe_b64encode(kdf.derive(session_key.encode()))
    f = Fernet(encodedSessionKey)
    #print("Encoded session key:")
    #print(encodedSessionKey)
    
    encfile = os.getcwd()+'/outenc.txt'
    with open(inputfile) as infile, open(encfile, 'w') as enfile:
            for line in infile:
                enc_line=f.encrypt(line.encode())
                enfile.write(base64.urlsafe_b64encode(enc_line))
            
            #newfile.write("\n")
            #newfile.write(user_details)    
            enfile.close()
            infile.close()

def retrieve_session_key_receiver(rec_msg_arr):
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=sender.encode(),
        iterations=1000,
    )
    
    key = base64.urlsafe_b64encode(kdf.derive(client_pwd.encode()))
    
    encodedReceiverToken = rec_msg_arr[2]
    encrpytedReceiverToken = base64.urlsafe_b64decode(encodedReceiverToken)
    
    f = Fernet(key)
    token = f.decrypt(encrpytedReceiverToken)
    token_arr = token.split('||')
    session_key = token_arr[0].strip()
    nonce = token_arr[3].strip()
    
    return session_key, nonce
    
def decrypt_file(session_key,outenc,outfile):
    
    # receiver_keyfile=os.getcwd()+'/'+sender+"_key.txt"
    # with open(receiver_keyfile,'r') as sf:
        # key=sf.readline()
        
    # kdf = PBKDF2HMAC(
        # algorithm=hashes.SHA256(),
        # length=32,
        # salt=sender.encode(),
        # iterations=1000,
    # )
    
    # key = base64.urlsafe_b64encode(kdf.derive(client_pwd.encode()))
    
    saltfile=os.getcwd()+'/file_salt.txt'
    with open(saltfile,'r') as sa:
        svalue=sa.readline()
    
    salt=base64.urlsafe_b64decode(svalue)
    
    # encodedReceiverToken = rec_msg_arr[2]
    # encrpytedReceiverToken = base64.urlsafe_b64decode(encodedReceiverToken)
    
    # f = Fernet(key)
    # token = f.decrypt(encrpytedReceiverToken)
    # token_arr = token.split('||')
    # session_key = token_arr[0].strip()
    #print(session_key)
    #print(token_arr)
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=1000,
    )
    
    encodedSessionKey = base64.urlsafe_b64encode(kdf.derive(session_key.encode()))
    rf = Fernet(encodedSessionKey)
    #rf = Fernet(base64.urlsafe_b64encode(session_key))
    #print("Encoded session key:")
    #print(encodedSessionKey)
    with open(outenc) as infile, open(outfile, 'w') as decfile:
        for line in infile:
            dec_line=rf.decrypt(base64.urlsafe_b64decode(line))
            decfile.write(dec_line)
            
            #newfile.write("\n")
            #newfile.write(user_details)    
        infile.close()
        decfile.close()
    
#def initiate_connection_with_receiver(receiver_ip,receiver_port,receiverToken,sender):
    
# while True: 
  
    # # maintains a list of possible input streams 
    # sockets_list = [sys.stdin, server] 
  
    # """ There are two possible input situations. Either the 
    # user wants to give manual input to send to other people, 
    # or the server is sending a message to be printed on the 
    # screen. Select returns from sockets_list, the stream that 
    # is reader for input. So for example, if the server wants 
    # to send a message, then the if condition will hold true 
    # below.If the user wants to send a message, the else 
    # condition will evaluate as true"""
    # read_sockets,write_socket, error_socket = select.select(sockets_list,[],[]) 
  
    # for socks in read_sockets: 
        # if socks == server: 
            # message = socks.recv(2048) 
            # print (message) 
        # else:
            
            # message = sys.stdin.readline() 
            # server.send(message)
                
            # sys.stdout.write("<You>") 
            # sys.stdout.write(message) 
            # sys.stdout.flush()
            
# server.close() 

print(server.recv(2048)) 
print("Enter your registration message:")
message=sys.stdin.readline()
reg_msg_arr = message.split('|')
client_pwd = reg_msg_arr[4].strip()
server.send(message)
rec_message=server.recv(2048)
print("Received: "+rec_message)
time.sleep(15)

if client_type=='S':
    print("Initiating key request to KDC")
    req_msg=key_request()
    server.send(req_msg)
    rec_req_msg=server.recv(2048)
    print("Received: " + rec_req_msg)
    session_key,receiverToken,receiver_ip,receiver_port,nonce1=retrieve_session_key(rec_req_msg)
    print("Received session_key from KDC")
    #print(session_key)
    
    #print("Receiver token")
    #print(receiverToken)
    print("Initiating connection with receiver "+receiver)
    encrypt_file(session_key,inputfile,nonce1)
    messageToReceiver = '| 309 | '+receiverToken+' | '+sender+ ' |'
    receiverSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM) 
    #print(receiver_ip.strip())
    #print(receiver_port.strip())
    receiverSocket.connect((receiver_ip.strip(), int(receiver_port.strip())))
    receiverSocket.send(messageToReceiver)
    rec_ack_message=receiverSocket.recv(2048)
    print("Received: "+ rec_ack_message)
    
    
elif client_type == 'R':
    print("Waiting for messages from sender")
    #server_socket.bind(('',port))
    clientSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    clientSocket.bind(('',45561))
    clientSocket.listen(5)
    conn, addr = clientSocket.accept() 
    while True: 
            try: 
                rec_msg = conn.recv(2048) 
                if rec_msg:    
                    #rec_msg=clientSocket.recv(2048)
                    print("Received: "+ rec_msg)
                    
                    break
                
            except: 
                continue
                
    rec_msg_arr=rec_msg.split('|')
    session_key, nonce = retrieve_session_key_receiver(rec_msg_arr)
    conn.send("| 310 | "+ nonce+ " |")
    decrypt_file(session_key,outenc,outfile)
    conn.close()
    clientSocket.close()
    
server.close()

