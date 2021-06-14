import random
import socket
import struct
import sys 

def generatePacketValidIpWithPrefix():
    ip = ".".join(str(random.randint(0, 255)) for _ in range(4))
    prefix = str(random.randint(0,35))
    ip = ip+'/'+prefix
    return ip
    
def generatePacketValidIp():
	ip_addr = socket.inet_ntoa(struct.pack('>I', random.randint(1, 0xffffffff)))
	
	return ip_addr
	
def generatePort():
	port = random.randint(0, 67000)
	
	return port
	
def generatePortRange():
	range_str=''
	while True:
		port1 = random.randint(0, 67000)
		port2 = random.randint(0, 67000)
		if port1 <= port2 :
			range_str = str(port1)+'-'+str(port2)
			return range_str
	
	return '0-0'
	
def generateProtocol():
	
	protocol_str = ['tcp', 'udp', 'icmp']
	
	i = random.randint(0, 2)
	
	return protocol_str[i]

def generateRuleData():
    
    data_list = ['*', 'FTPServer', 'SMTPServer' , 'HTTPServer' , 'DNSServer', 'SNMPServer', 'LDAPServer', 'Telnet', 'VTP', 'TFTPServer' ,'POP', 'IMAP', 'SSHServer' ]
    
    size = len(data_list)
    
    i = random.randint(0,size-1)
    
    return data_list[i]
    
def generatePacketData():
    
    data_list = [ 'Hello to FTPServer', 'Hello to SMTPServer' , 'Hello to HTTPServer' , 'Hello to DNSServer', 'Hello to SNMPServer', 'Hello to LDAPServer', 'Hello to Telnet', 'Hello to VTP', 'Hello to TFTPServer' ,'Hello to POP', 'Hello to IMAP', 'Hello to SSHServer', 'Bye.. FTPServer', 'Bye.. SSH server', 'Bye.. SMTPServer' ]
    
    size = len(data_list)
    
    i = random.randint(0,size-1)
    
    return data_list[i]
	
rsize = sys.argv[1]
psize = sys.argv[2]

rulefile = 'rules_'+str(rsize)+'.txt'
pktfile = 'packets_'+str(psize)+'.txt'
# = 300
# = 500

with open(rulefile, 'w') as rf:
	for i in range(rsize):
		rf.write('BEGIN\n')
		rf.write('NUM: '+str(i+1)+'\n')
		rf.write('SRC IP ADDR: '+generatePacketValidIpWithPrefix()+'\n')
		rf.write('DEST IP ADDR: '+generatePacketValidIpWithPrefix()+'\n')
		rf.write('SRC PORT: '+generatePortRange() + '\n')
		rf.write('DEST PORT: '+generatePortRange() + '\n')
		rf.write('PROTOCOL: '+generateProtocol() + '\n')
		rf.write('DATA: '+generateRuleData() + '\n')
		rf.write('END')
		rf.write('\n\n')
		
        
with open(pktfile, 'w') as rf:
	for i in range(psize):
		rf.write('BEGIN\n')
		rf.write('NUM: '+str(i+1)+'\n')
		rf.write('SRC IP ADDR: '+generatePacketValidIp()+'\n')
		rf.write('DEST IP ADDR: '+generatePacketValidIp()+'\n')
		rf.write('SRC PORT: '+str(generatePort()) + '\n')
		rf.write('DEST PORT: '+str(generatePort()) + '\n')
		rf.write('PROTOCOL: '+generateProtocol() + '\n')
		rf.write('DATA: '+generatePacketData() + '\n')
		rf.write('END')
		rf.write('\n\n')