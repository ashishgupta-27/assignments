import argparse
import os
import sys
import socket 
import base64
import select
import secrets
import string
import shutil
from os import path
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives import padding as sym_padding
#from thread import *


def generatePassword(username, password):

    print("Generating credentials for user:" +username)
    salt=os.urandom(8)
    
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=1000,
    )
    
    key = base64.urlsafe_b64encode(kdf.derive(password.encode()))
    encodedSalt=base64.urlsafe_b64encode(salt)
    
    userCredentialsDirectory="UserCredentials";
    if not os.path.exists(userCredentialsDirectory):
        os.makedirs(userCredentialsDirectory)
        
    userFile = userCredentialsDirectory + "/"+username+".txt"
    
    with open(userFile, 'wb') as f:
        f.write(username.encode())
        f.write("\n".encode())
        f.write(encodedSalt)
        f.write("\n".encode())
        f.write(key)
    
    f.close()
	
    print("Credentials generation is successful")
	
username = sys.argv[1]
password = sys.argv[2]

generatePassword(username, password.strip())