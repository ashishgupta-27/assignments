This assignment implements KDC functionality using Client Server socket programming and the cryptographic algorithms.

There are two executables available and all of them are written in Python.

1. kdc.py
This program acts as KDC server which will register a user in his records and generate a session key if requested by any user.
python kdc.py -p 12345 -o kdclog.txt -f pwd.txt

2. client.py
This program can be either used as sender and receiver based on arguments passed. 
If it is a sender, it will register itself, initiate request for session key with other user/party, encrypt the file using session key and send to other user/party.
If it is a receiver, it will register itself, and wait for messages from the sender. Once the session key is received from the sender in an encrypted form, it will decrypt the file using the session key.

Sender side commands example:
python client.py -n alice -m S -o bob -i in.txt -a 127.0.0.1 -p 12345
Here, alice is the name of the sender, bob is the name of the receiver, in.txt is the input file having contents, 127.0.0.1 is the KDC IP and 12345 is the KDC port.
Once invoked, it will ask  for a registration message from the command line. We can something like below:
| 301 | 127.0.0.1 | 35768 | alice123 | alice |

Once, the registration is complete and acknowledgment message is received from the KDC, it will initiate session key request and all other activities mentioned above for the sender.

Receiver side commands example:
python client.py -n bob -m R -s outenc.txt -o out.txt -a 127.0.0.1 -p 12345
Here, bob is the receiver name, outenc.txt is the encrypted file, out.txt is the decrypted file, 127.0.0.1 is the KDC IP and 12345 is the KDC port.
Once invoked, it will ask  for a registration message from the command line. We can something like below:
| 301 | 127.0.0.1 | 45561 | bob123 | bob |

Once, the registration is complete and acknowledgment message is received from the KDC, it will wait for the messages from the sender and once it receives the session key from the sender, it will perform decryption on the encrypted file and retrieve the contents from it.



