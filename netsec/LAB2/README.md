This assignment implements confidentiality and authentication property as well as generates RSA keys for 1024 or 2048 key sizes. 
The problem statement is available in problem_statement.txt

The main script is written in Python language which uses cryptography package. The script is named as "lab2.py". 
Since the script is written in Python language, we do not need Make file for generating executable. 
Before executing the main script, the cryptography package should be installed. This can be done using the following command:
"pip install cryptography"

The script should be executed using the following commands which include all the cases that needs to be tested:

----- Key generation start -----
python3 lab2.py CreateKeys usernames.txt 2048
python3 lab2.py CreateKeys usernames.txt 1024
----- Key generation end -----

----- CONF case start -----
python3 lab2.py CreateMail CONF ashish zoro mail-sample.txt mail-out-aes-1024.txt sha512 aes-256-cbc 1024
python3 lab2.py ReadMail CONF ashish zoro mail-out-aes-1024.txt mail-decrypt-aes-1024.txt sha512 aes-256-cbc 1024
diff mail-sample.txt mail-decrypt-aes-1024.txt

python3 lab2.py CreateMail CONF walter jesse mail-sample.txt mail-out-des-2048.txt sha512 des-ede3-cbc 2048
python3 lab2.py ReadMail CONF walter jesse mail-out-des-2048.txt mail-decrypt-des-2048.txt sha512 des-ede3-cbc 2048
diff mail-sample.txt mail-decrypt-des-2048.txt
----- CONF case end -----

----- AUIN case start -----
python3 lab2.py CreateMail AUIN ashish zoro mail-sample.txt mail-out-sha-digest.txt sha512 aes-256-cbc 1024
python3 lab2.py ReadMail AUIN ashish zoro mail-out-sha-digest.txt mail-decrypt-sha-digest.txt sha512 aes-256-cbc 1024

python3 lab2.py CreateMail AUIN walter jesse mail-sample.txt mail-out-sha3-digest.txt sha3-512 des-ede3-cbc 2048
python3 lab2.py ReadMail AUIN walter jesse mail-out-sha3-digest.txt mail-decrypt-sha3-digest.txt sha3-512 des-ede3-cbc 2048
----- AUIN case end -----

----- COAI case end -----
python3 lab2.py CreateMail COAI ashish zoro mail-sample.txt mail-out-aes-sha-1024.txt sha512 aes-256-cbc 1024
python3 lab2.py ReadMail COAI ashish zoro mail-out-aes-sha-1024.txt mail-decrypt-aes-sha-1024.txt sha512 aes-256-cbc 1024
diff mail-sample.txt mail-decrypt-aes-sha-1024.txt

python3 lab2.py CreateMail COAI walter jesse mail-sample.txt mail-out-des-sha3-2048.txt sha3-512 des-ede3-cbc 2048
python3 lab2.py ReadMail COAI walter jesse mail-out-des-sha3-2048.txt mail-decrypt-des-sha3-2048.txt sha3-512 des-ede3-cbc 2048
diff mail-sample.txt mail-decrypt-des-sha3-2048.txt
----- COAI case end -----