import argparse
import os
import sys
import socket 
import base64
import select
import secrets
import string
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from thread import *

my_parser = argparse.ArgumentParser(description='To establish KDC connection with client')

my_parser.add_argument('-p', type=int, help='Port number to establish connection using TCP sockets')
my_parser.add_argument('-o', type=str, help='File where KDC activities will be logged')
my_parser.add_argument('-f', type=str, help='Clients details will be stored in this file')

args = my_parser.parse_args()

port=args.p
outfile=args.o
pwdfile=args.f

logfile = open(outfile, 'w')
#print(str(port)+" "+outfile+" "+pwdfile)

#Create a socket and bind it to a port
# s = socket.socket()         

# s.bind(('', port))         
# #print ("socket binded to %s" %(port)) 

# # put the socket into listening mode 
# s.listen(5)     
# print ("socket is listening")    

# # a forever loop until we interrupt it or 
# # an error occurs 
# while True: 
  
    # # Establish connection with client. 
    # c, addr = s.accept()     
    # print ('Got connection from', addr )
      
    # # send a thank you message to the client. 
    # c.send(b'Thank you for connecting') 
    # print (c.recv(1024) )  
    # # Close the connection with the client 
    # c.close() 

SOCKET_LIST = []
sock_list = []
stored = []
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
server_socket.bind(('',port))
server_socket.listen(5)
SOCKET_LIST.append(server_socket)

list_of_clients = [] 

print("KDC server started and waiting for clients")
def clientthread(conn, addr): 
  
    # sends a message to the client whose user object is conn 
    conn.send("Welcome to this KDC server on port "+str(port)) 
    logfile.write("Welcome to this KDC server on port "+str(port))
    logfile.write("\n")
    while True: 
            try: 
                message = conn.recv(2048) 
                if message: 
  
                    """prints the message and address of the 
                    user who just sent the message on the server 
                    terminal"""
                    print ("<" + addr[0] +":"+str(addr[1])+ ">: " + message) 
                    message_arr=message.split("|")
                    #print(len(message_arr))
                    logfile.write("<" + addr[0] +":"+str(addr[1])+ ">: " + message+"\n")
                    if message_arr[1].strip() == '301':
                        message_to_send=register_user(message_arr,pwdfile)
                    elif message_arr[1].strip() == '305':
                        message_to_send=generate_session_key(message_arr,pwdfile)
                    #print(message_arr)
                    # Calls broadcast function to send message to all 
                    #message_to_send = "<" + addr[0] +":"+str(addr[1])+ "> " + message 
                    logfile.write(message_to_send+"\n")
                    broadcast(message_to_send, conn) 
  
                else: 
                    """message may have no content if the connection 
                    is broken, in this case we remove the connection"""
                    remove(conn) 
  
            except: 
                continue

def register_user(message_arr, pwdfile):
    code = int(message_arr[1].strip())
    client_ip = message_arr[2].strip()
    client_port = message_arr[3].strip()
    client_pwd = message_arr[4].strip()
    client_name = message_arr[5].strip()
    
    #key = Fernet.generate_key()
    print("Received registration request from "+client_name)
    logfile.write("Received registration request from "+client_name+"\n")
    print("Generating encrypted master key for "+client_name)
    logfile.write("Generating encrypted master key for "+client_name)
    print(code)
    print(client_ip)
    print(client_port)
    print(client_name)
    #salt = os.urandom(16)
    #saltfile=os.getcwd()+'/'+client_name+'_salt.txt'
    
    #with open(saltfile,'r') as  sf:
        #svalue=sf.readline()
        #salt= base64.urlsafe_b64decode(svalue)
        
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=client_name.encode(),
        iterations=1000,
    )
    
    key = base64.urlsafe_b64encode(kdf.derive(client_pwd.encode()))
    f = Fernet(key)
    
    #file=open(pwdfile,'a+')
    user_details=":"+client_name+":"+client_ip+":"+client_port+":"+key+":"
    if os.path.isfile(pwdfile) :

        newpwdfile=os.getcwd()+'/pwd1.txt'
        with open(pwdfile) as oldfile, open(newpwdfile, 'w') as newfile:
            for line in oldfile:
                if not (client_name in line):
                    newfile.write(line)
            
            newfile.write("\n")
            newfile.write(user_details)    
            newfile.close()
            oldfile.close()
        os.remove(pwdfile)
        os.rename(newpwdfile,pwdfile)
    else :
        with open(pwdfile, 'w') as file:
            file.write(user_details)
            
    #print(user_details)
    print("Master key generated")
    logfile.write("Master key generated\n")
    ack_message="| 302 | "+client_name+" |"
    return ack_message

def generate_session_key(message_arr,pwdfile):

    client_name=message_arr[3].strip()
    print("Received session key generation request from "+client_name)
    
    logfile.write("Received session key generation request from "+client_name+"\n")
    #logfile.write("Generating session key for "+client_name+"\n")
    key_line=[]
    rkey_line=[]
    with open(pwdfile) as file:
        for line in file:
            if client_name in line:
                #print(line)
                key_line=line.split(':')
                #break
            
        file.close()
    #print(key_line)   
    #clientkey = base64.urlsafe_b64decode(key_line[4].strip())
    clientkey = key_line[4].strip()
    clientIP=key_line[2].strip()
    clientPort=key_line[3].strip()
    #print(clientkey)
    f = Fernet(clientkey)
    #f=Fernet(clientkey)
    encodedToken = base64.urlsafe_b64decode(message_arr[2].strip())
    token = f.decrypt(encodedToken).decode()
    
    #print("Token: "+ token)
    token_arr = token.split("||")
    receiver_name = token_arr[1].strip()
    nonce=token_arr[2].strip()
    print("Generating session key for "+client_name+" and "+receiver_name)
    logfile.write("Generating session key for "+client_name+" and "+receiver_name+"\n")
    #print("Nonce:")
    #print(nonce)
    with open(pwdfile) as file:
        for line in file:
            if receiver_name in line:
                rkey_line=line.split(':')
                #break
        
        file.close()
    
    #print(rkey_line)
    #receiverkey = base64.urlsafe_b64decode(rkey_line[4].strip())
    receiverkey = rkey_line[4].strip()
    receiverIP=rkey_line[2].strip()
    receiverPort=rkey_line[3].strip()
    
    rf = Fernet(receiverkey)
    
    
    session_key = ''.join(secrets.choice(string.ascii_uppercase + string.digits + string.ascii_lowercase)
                                                  for i in range(8))
    #print(session_key)
    receiverToken = session_key + " || "+ client_name + " || "+ receiver_name+ " || "+nonce+" || "+clientIP+" || "+clientPort
    encryptedReceiverToken = rf.encrypt(receiverToken.encode())
    encodedReceiverToken = base64.urlsafe_b64encode(encryptedReceiverToken)
    
    clientToken = session_key + " || " + client_name + " || "+ receiver_name+" || "+nonce+" || "+receiverIP+" || "+receiverPort+ " || "+encodedReceiverToken
    encryptedClientToken = f.encrypt(clientToken.encode())
    encodedClientToken = base64.urlsafe_b64encode(encryptedClientToken)
    
    ack_message = '| 306 | '+encodedClientToken+' |'
    print("Session key generated for "+client_name+" and "+receiver_name)
    logfile.write("Session key generated for "+client_name+" and "+receiver_name+"\n")
    return ack_message
    
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
    logfile.write(addr[0] +" "+str(addr[1])+ " connected\n")
    # creates and individual thread for every user 
    # that connects 
    start_new_thread(clientthread,(conn,addr))     
  
conn.close() 
server_socket.close()
logfile.close()