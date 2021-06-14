This assignment help us to implement SSH functionality using Client Server socket programming and cryptographic algorithms.

There are two executables here viz. one for SSH server and one for SSH client and both of them are written in Python.

SSH Server:
1. SSH server script can be invoked using the following command:
	python sshserver.py 12345
	
	
SSH Client:
1. SSH client script can be invoked in one of the following ways:
	python sshclient.py 127.0.0.1 12345 alice123
	python sshclient.py localhost 12345 alice123
	python sshclient.py 12345 alice123
	
2. Then the user will be prompted to type their passphrase on the command line.

3. Once the authentication is complete and sessionKey is exchanged, the following commands can be invoked.
	a. listfiles
	b. cwd
	c. chgdir <DIR_NAME>
	d. cp <FILENAME> <SOURCE_DIR> <DEST_DIR>
	e. mv <FILENAME> <SOURCE_DIR> <DEST_DIR>
	
There is an additional helper executable which helps us to store user credentials in encrypted form in <USERNAME>.txt file in UserCredentials directory. It can be invoked as follows:
	python credGen.py alice123 alice123