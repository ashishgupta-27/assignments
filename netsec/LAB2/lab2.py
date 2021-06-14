import sys
import cryptography
import base64
import os
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives import padding as sym_padding

# total arguments
n = len(sys.argv)


def createKeys(userNameListFile, rsaKeySize):
    file = open(userNameListFile, "r")
    for user in file:
        user = user.rstrip("\n")
        print("Generating private and public keys for ", user)

        private_key = rsa.generate_private_key(
            public_exponent=65537,
            key_size=rsaKeySize,
            backend=default_backend()
        )
    # print('d1')

        public_key = private_key.public_key()

        pem = private_key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=serialization.NoEncryption()
        )

        userPrivateKeyFile = user+'_priv_'+str(rsaKeySize)+'.txt'

        with open(userPrivateKeyFile, 'wb') as f:
            f.write(pem)
# f.close()

        pem = public_key.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo
        )

        userPublicKeyFile = user+'_'+'pub_'+str(rsaKeySize)+'.txt'

        with open(userPublicKeyFile, 'wb') as f:
            f.write(pem)
            # f.close()

        print("Generation of private and public keys for ", user, " successful")

    file.close()


def createMail(secType, sender, receiver, emailInputFile, emailOutputFile, digestAlg, encryAlg, rsaKeySize):

    senderPrivateKeyFile = sender+'_priv_'+str(rsaKeySize)+'.txt'
    senderPublicKeyFile = sender+'_pub_'+str(rsaKeySize)+'.txt'
    receiverPrivateKeyFile = receiver + '_priv_'+str(rsaKeySize)+'.txt'
    receiverPublicKeyFile = receiver + '_pub_'+str(rsaKeySize)+'.txt'

    with open(senderPrivateKeyFile, "rb") as key_file:
        senderPrivateKey = serialization.load_pem_private_key(
            key_file.read(),
            password=None,
            backend=default_backend()
        )

    # print(senderPrivateKey)
    with open(senderPublicKeyFile, "rb") as key_file:
        senderPublicKey = serialization.load_pem_public_key(
            key_file.read(),
            backend=default_backend()
        )

    with open(receiverPrivateKeyFile, "rb") as key_file:
        receiverPrivateKey = serialization.load_pem_private_key(
            key_file.read(),
            password=None,
            backend=default_backend()
        )

    with open(receiverPublicKeyFile, "rb") as key_file:
        receiverPublicKey = serialization.load_pem_public_key(
            key_file.read(),
            backend=default_backend()
        )

    with open(emailInputFile, 'r') as file:
        message = file.read()

    if secType == 'AUIN':

        print("Generating message digest")
        if digestAlg == 'sha512':
            signature = senderPrivateKey.sign(
                message.encode(),
                padding.PSS(
                    mgf=padding.MGF1(hashes.SHA512()),
                    salt_length=padding.PSS.MAX_LENGTH
                ),
                hashes.SHA512()
            )
            # digest = hashes.Hash(hashes.SHA512(), backend=default_backend())
            # digest.update(message.encode())
            # digest.finalize()

            # encrypted = senderPrivateKey.encrypt(
            # digest,
            # padding.OAEP(
            # mgf=padding.MGF1(algorithm=hashes.SHA256()),
            # algorithm=hashes.SHA256(),
            # label=None
            # )
            # )

        elif digestAlg == 'sha3-512':
            # digest = hashes.Hash(hashes.SHA3_512())
            # digest.update(message.encode())
            # digest.finalize()

            # encrypted = senderPrivateKey.encrypt(
            # digest,
            # padding.OAEP(
            # mgf=padding.MGF1(algorithm=hashes.SHA256()),
            # algorithm=hashes.SHA256(),
            # label=None
            # )
            # )

            signature = senderPrivateKey.sign(
                message.encode(),
                padding.PSS(
                    mgf=padding.MGF1(hashes.SHA3_512()),
                    salt_length=padding.PSS.MAX_LENGTH
                ),
                hashes.SHA3_512()
            )

        base64_enc_digest = base64.b64encode(signature)

        with open(emailOutputFile, 'wb') as f:
            f.write(base64_enc_digest)
            # f.newLine()
            f.write('\n'.encode())
            f.write(message.encode())

        print("Message digest generation is successful")

    elif secType == 'CONF':
        print("Encrypting sender's message")
        
        
        if encryAlg == 'aes-256-cbc':
            # sessionKey = AESGCM.generate_key(bit_length=256)
            # aesgcm = AESGCM(sessionKey)
            # nonce = os.urandom(12)
            # encryptedMessage = aesgcm.encrypt(nonce, message.encode(), None)

            sessionKey = os.urandom(32)
            iv = os.urandom(16)
            padder = sym_padding.PKCS7(128).padder()
            padded_message = padder.update(message.encode())
            padded_message += padder.finalize()
            cipher = Cipher(algorithms.AES(sessionKey), modes.CBC(iv))
            encryptor = cipher.encryptor()
            encryptedMessage = encryptor.update(padded_message) + encryptor.finalize()

        elif encryAlg == 'des-ede3-cbc':
            #print("DES")
            sessionKey = os.urandom(24)
            iv = os.urandom(8)
            padder = sym_padding.PKCS7(64).padder()
            padded_message = padder.update(message.encode())
            padded_message += padder.finalize()
            cipher = Cipher(algorithms.TripleDES(sessionKey), modes.CBC(iv))
            encryptor = cipher.encryptor()
            encryptedMessage = encryptor.update(padded_message) + encryptor.finalize()
            
        encryptedSessionKey = receiverPublicKey.encrypt(
            sessionKey,
            padding.OAEP(
                mgf=padding.MGF1(algorithm=hashes.SHA256()),
                algorithm=hashes.SHA256(),
                label=None
            )
        )

        with open(emailOutputFile, 'wb') as f:
            f.write(base64.b64encode(encryptedSessionKey))
                # f.newLine()
            f.write('\n'.encode())
            f.write(base64.b64encode(encryptedMessage))
            f.write('\n'.encode())
            f.write(base64.b64encode(iv))
            
        print("Encryption of sender's message successful")
        
    elif secType == 'COAI':
        print("Generating message digest")
        if digestAlg == 'sha512':
            signature = senderPrivateKey.sign(
                message.encode(),
                padding.PSS(
                    mgf=padding.MGF1(hashes.SHA512()),
                    salt_length=padding.PSS.MAX_LENGTH
                ),
                hashes.SHA512()
            )
            
        elif digestAlg == 'sha3-512':
            signature = senderPrivateKey.sign(
                message.encode(),
                padding.PSS(
                    mgf=padding.MGF1(hashes.SHA3_512()),
                    salt_length=padding.PSS.MAX_LENGTH
                ),
                hashes.SHA3_512()
            )
            
        print("Message digest generation is successful")
        print("Encrypting sender's message digest")
        
        if encryAlg == 'aes-256-cbc':

            sessionKey = os.urandom(32)
            iv = os.urandom(16)
            sig_padder = sym_padding.PKCS7(128).padder()
            msg_padder = sym_padding.PKCS7(128).padder()
            padded_signature = sig_padder.update(signature)
            padded_signature += sig_padder.finalize()
            padded_message = msg_padder.update(message.encode())
            padded_message += msg_padder.finalize()
            cipher = Cipher(algorithms.AES(sessionKey), modes.CBC(iv))
            sig_encryptor = cipher.encryptor()
            msg_encryptor = cipher.encryptor()
            encryptedSignature = sig_encryptor.update(padded_signature) + sig_encryptor.finalize()
            encryptedMessage = msg_encryptor.update(padded_message) + msg_encryptor.finalize()

        elif encryAlg == 'des-ede3-cbc':
            #print("DES")
            sessionKey = os.urandom(24)
            iv = os.urandom(8)
            sig_padder = sym_padding.PKCS7(64).padder()
            msg_padder = sym_padding.PKCS7(64).padder()
            padded_signature = sig_padder.update(signature)
            padded_signature += sig_padder.finalize()
            padded_message = msg_padder.update(message.encode())
            padded_message += msg_padder.finalize()
            cipher = Cipher(algorithms.TripleDES(sessionKey), modes.CBC(iv))
            sig_encryptor = cipher.encryptor()
            msg_encryptor = cipher.encryptor()
            encryptedSignature = sig_encryptor.update(padded_signature) + sig_encryptor.finalize()
            encryptedMessage = msg_encryptor.update(padded_message) + msg_encryptor.finalize()
            
        encryptedSessionKey = receiverPublicKey.encrypt(
            sessionKey,
            padding.OAEP(
                mgf=padding.MGF1(algorithm=hashes.SHA256()),
                algorithm=hashes.SHA256(),
                label=None
            )
        )

        with open(emailOutputFile, 'wb') as f:
            f.write(base64.b64encode(encryptedSessionKey))
                # f.newLine()
            f.write('\n'.encode())
            f.write(base64.b64encode(encryptedSignature))
            f.write('\n'.encode())
            f.write(base64.b64encode(encryptedMessage))
            f.write('\n'.encode())
            f.write(base64.b64encode(iv))
            
        print("Encryption of sender's message successful")
        

def readMail(secType, sender, receiver, secureInputFile, plainOutputFile, digestAlg, encryAlg, rsaKeySize):
    
    senderPrivateKeyFile = sender+'_priv_'+str(rsaKeySize)+'.txt'
    senderPublicKeyFile = sender+'_pub_'+str(rsaKeySize)+'.txt'
    receiverPrivateKeyFile = receiver + '_priv_'+str(rsaKeySize)+'.txt'
    receiverPublicKeyFile = receiver + '_pub_'+str(rsaKeySize)+'.txt'
    
    with open(senderPrivateKeyFile, "rb") as key_file:
        senderPrivateKey = serialization.load_pem_private_key(
            key_file.read(),
            password=None,
            backend=default_backend()
        )

    # print(senderPrivateKey)
    with open(senderPublicKeyFile, "rb") as key_file:
        senderPublicKey = serialization.load_pem_public_key(
            key_file.read(),
            backend=default_backend()
        )

    with open(receiverPrivateKeyFile, "rb") as key_file:
        receiverPrivateKey = serialization.load_pem_private_key(
            key_file.read(),
            password=None,
            backend=default_backend()
        )

    with open(receiverPublicKeyFile, "rb") as key_file:
        receiverPublicKey = serialization.load_pem_public_key(
            key_file.read(),
            backend=default_backend()
        )

    
    if secType == 'CONF':
        print("Decrypting message")
        
        with open(secureInputFile, 'r') as file:
            lines = file.readlines()
            encryptedb64SessionKey = lines[0]
            encryptedb64Message =lines[1]
            b64iv=lines[2]
        
        #print(encryptedKey)
        #print(encryptedMessage)
        #Decode from base 64 to bytes
        encryptedSessionKey = base64.b64decode(encryptedb64SessionKey)
        encryptedMessage = base64.b64decode(encryptedb64Message)
        iv = base64.b64decode(b64iv)
        sessionKey = receiverPrivateKey.decrypt(
            encryptedSessionKey,
            padding.OAEP(
                mgf=padding.MGF1(algorithm=hashes.SHA256()),
                algorithm=hashes.SHA256(),
                label=None
            )
        )
        
        if encryAlg == 'aes-256-cbc':

            cipher = Cipher(algorithms.AES(sessionKey), modes.CBC(iv))
            decryptor = cipher.decryptor()
            decryptedMessage = decryptor.update(encryptedMessage) + decryptor.finalize()
            unpadder = sym_padding.PKCS7(128).unpadder()
            data = unpadder.update(decryptedMessage)
            data = data + unpadder.finalize()
            #print(decryptedMessage)
            #print(data)

        elif encryAlg == 'des-ede3-cbc':
            #print("DES")
            #sessionKey = os.urandom(24)
            #v = os.urandom(8)
            cipher = Cipher(algorithms.TripleDES(sessionKey), modes.CBC(iv))
            decryptor = cipher.decryptor()
            decryptedMessage = decryptor.update(encryptedMessage) + decryptor.finalize()
            unpadder = sym_padding.PKCS7(64).unpadder()
            data = unpadder.update(decryptedMessage)
            data = data + unpadder.finalize()
            #print(decryptedMessage)
            #print(data)
        
        with open(plainOutputFile, 'wb') as f:
            f.write(data)
                # f.newLine()
            #f.write('\n'.encode())
            #f.write(base64.b64encode(encryptedMessage))
        print("Decryption successful")
        
    elif secType == 'AUIN':
        
        print("Verifying digital signature of the message")
        with open(secureInputFile, 'r') as file:
            lines = file.readlines()
            b64Signature = lines[0]
            b64Message =lines[1]
            #b64iv=lines[2]
            
        signature = base64.b64decode(b64Signature)
        #message = base64.b64decode(b64Message)
        if digestAlg == 'sha512':
            senderPublicKey.verify(
                signature,
                b64Message.encode(),
                padding.PSS(
                    mgf=padding.MGF1(hashes.SHA512()),
                    salt_length=padding.PSS.MAX_LENGTH
                ),
                hashes.SHA512()
            )
            
        elif digestAlg == 'sha3-512':
            senderPublicKey.verify(
                signature,
                b64Message.encode(),
                padding.PSS(
                    mgf=padding.MGF1(hashes.SHA3_512()),
                    salt_length=padding.PSS.MAX_LENGTH
                ),
                hashes.SHA3_512()
            )
        
        with open(plainOutputFile, 'wb') as f:
            f.write(b"Digital signature verified")
            
        print("Digital signature verified")
        
    elif secType == 'COAI':
        print("Decrypting message and verifying digital signature")
        with open(secureInputFile, 'r') as file:
            lines = file.readlines()
            encryptedb64SessionKey = lines[0]
            encryptedb64Signature =lines[1]
            encryptedb64Message = lines[2]
            b64iv=lines[3]
        
        encryptedSessionKey = base64.b64decode(encryptedb64SessionKey)
        encryptedSignature = base64.b64decode(encryptedb64Signature)
        encryptedMessage = base64.b64decode(encryptedb64Message)
        iv = base64.b64decode(b64iv)
        
        sessionKey = receiverPrivateKey.decrypt(
            encryptedSessionKey,
            padding.OAEP(
                mgf=padding.MGF1(algorithm=hashes.SHA256()),
                algorithm=hashes.SHA256(),
                label=None
            )
        )
        print("Digital signature verified")
        
        if encryAlg == 'aes-256-cbc':

            cipher = Cipher(algorithms.AES(sessionKey), modes.CBC(iv))
            sig_decryptor = cipher.decryptor()
            msg_decryptor = cipher.decryptor()
            decryptedPaddedMessage = msg_decryptor.update(encryptedMessage) + msg_decryptor.finalize()
            msg_unpadder = sym_padding.PKCS7(128).unpadder()
            message = msg_unpadder.update(decryptedPaddedMessage)
            message = message + msg_unpadder.finalize()
            decryptedPaddedSignature = sig_decryptor.update(encryptedSignature) + sig_decryptor.finalize()
            sig_unpadder = sym_padding.PKCS7(128).unpadder()
            signature = sig_unpadder.update(decryptedPaddedSignature)
            signature = signature + sig_unpadder.finalize()

            #print(decryptedMessage)
            #print(data)

        elif encryAlg == 'des-ede3-cbc':
            #print("DES")
            #sessionKey = os.urandom(24)
            #v = os.urandom(8)
            cipher = Cipher(algorithms.TripleDES(sessionKey), modes.CBC(iv))
            sig_decryptor = cipher.decryptor()
            msg_decryptor = cipher.decryptor()
            decryptedPaddedMessage = msg_decryptor.update(encryptedMessage) + msg_decryptor.finalize()
            msg_unpadder = sym_padding.PKCS7(64).unpadder()
            message = msg_unpadder.update(decryptedPaddedMessage)
            message = message + msg_unpadder.finalize()
            decryptedPaddedSignature = sig_decryptor.update(encryptedSignature) + sig_decryptor.finalize()
            sig_unpadder = sym_padding.PKCS7(64).unpadder()
            signature = sig_unpadder.update(decryptedPaddedSignature)
            signature = signature + sig_unpadder.finalize()
            #print(decryptedMessage)
            #print(data)
        
        if digestAlg == 'sha512':
            senderPublicKey.verify(
                signature,
                message,
                padding.PSS(
                    mgf=padding.MGF1(hashes.SHA512()),
                    salt_length=padding.PSS.MAX_LENGTH
                ),
                hashes.SHA512()
            )
            
        elif digestAlg == 'sha3-512':
            senderPublicKey.verify(
                signature,
                message,
                padding.PSS(
                    mgf=padding.MGF1(hashes.SHA3_512()),
                    salt_length=padding.PSS.MAX_LENGTH
                ),
                hashes.SHA3_512()
            )

        with open(plainOutputFile, 'wb') as f:
            f.write(message)
            
        print("Decryption successful")

command = ""
userNameListFile = ""
rsaKeySize = 1024

command = sys.argv[1]
if command == 'CreateKeys':
    userNameListFile = sys.argv[2]
    rsaKeySize = int(sys.argv[3])
    createKeys(userNameListFile, rsaKeySize)

elif command == 'CreateMail':
    secType = sys.argv[2]
    sender = sys.argv[3]
    receiver = sys.argv[4]
    emailInputFile = sys.argv[5]
    emailOutputFile = sys.argv[6]
    digestAlg = sys.argv[7]
    encryAlg = sys.argv[8]
    rsaKeySize = int(sys.argv[9])
    createMail(secType, sender, receiver, emailInputFile,
               emailOutputFile, digestAlg, encryAlg, rsaKeySize)

elif command == 'ReadMail':
    secType = sys.argv[2]
    sender = sys.argv[3]
    receiver = sys.argv[4]
    emailInputFile = sys.argv[5]
    emailOutputFile = sys.argv[6]
    digestAlg = sys.argv[7]
    encryAlg = sys.argv[8]
    rsaKeySize = int(sys.argv[9])
    readMail(secType, sender, receiver, emailInputFile,
             emailOutputFile, digestAlg, encryAlg, rsaKeySize)
