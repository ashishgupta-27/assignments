import os
import sys
import base64
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

user = sys.argv[1]
password = sys.argv[2]

cwd = os.getcwd()
saltfile = cwd+'/'+user+'_salt.txt'
keyfile = cwd+'/'+user+'_key.txt'
print("Generating salt and key for "+user)
salt = os.urandom(16)
       
kdf = PBKDF2HMAC(
    algorithm=hashes.SHA256(),
    length=32,
    salt=salt,
    iterations=1000,
)

key = base64.urlsafe_b64encode(kdf.derive(password.encode()))  
# newsaltfile = cwd + '/salt1.txt'

# #user_salt=":"+user+":"+base64.urlsafe_b64decode(salt)
# if os.path.isfile(saltfile) :

    # with open(saltfile) as oldfile, open(newsaltfile, 'wb') as newfile:
        # for line in oldfile:
            # if not (user in line):
                # newfile.write(line+"\n")
                
        # newfile.write(base64.urlsafe_b64encode(salt))    
        # newfile.close()
        # oldfile.close()
        # os.remove(saltfile)
        # os.rename(newsaltfile,saltfile)
        
# else :
with open(saltfile, 'wb') as file:
    file.write(base64.urlsafe_b64encode(salt))
    
with open(keyfile, 'wb') as kf:
    kf.write(key)
    
        
print("Salt and key successfully generated for "+user)