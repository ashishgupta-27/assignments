import sqlite3 as sl
import os
import sys
from itertools import islice
import time
from netaddr import IPNetwork, IPAddress

class Rule:
  def __init__(self, num, source_ip, dest_ip, src_port_start, src_port_end, dest_port_start, dest_port_end, protocol, data):
    self.num = num
    self.source_ip = source_ip
    self.dest_ip = dest_ip
    self.src_port_start = src_port_start
    self.src_port_end = src_port_end
    self.dest_port_start = dest_port_start
    self.dest_port_end = dest_port_end
    self.protocol = protocol
    self.data = data
    
class Packet:
  def __init__(self, num, source_ip, dest_ip, src_port, dest_port, protocol, data):
    self.num = num
    self.source_ip = source_ip
    self.dest_ip = dest_ip
    self.src_port = src_port
    self.dest_port = dest_port
    self.protocol = protocol
    self.data = data
    
rulefile = sys.argv[1]
pktfile = sys.argv[2]

n = 10
rules_list = []
valid_rules_list = []
packets_list = []
packet_process_times = []

def isValidPort(port):
    
    if port >=0 and port <=65535:
        return True
    
    return False

def isValidPortRange(start_port, end_port):
    
    if start_port <= end_port:
        return True
    
    return False
    
def isValidIpAddress(ip):
    
    ip_arr = ip.split('/')
    ip_addr = ip_arr[0]
    ip_prefix = int(ip_arr[1])
    ip_addr_arr = ip_addr.split('.')
    
    if (ip_prefix !=0) and (ip_prefix < 8 or ip_prefix > 32) :
        return False
    
    if len(ip_addr_arr) > 4 or len(ip_addr_arr) < 4:
        return False
        
    for octet in ip_addr_arr:
    
        if int(octet) < 0 or int(octet) > 255:
            return False
    
    return True
  
def validRules(rules_list):
    
    count = len(rules_list)

    for rule in rules_list:
        #print(rule.num)
        #print(rule.src_port_start)
        if isValidIpAddress(rule.source_ip) and isValidIpAddress(rule.dest_ip) and isValidPort(rule.src_port_start) and isValidPort(rule.src_port_end) and isValidPort(rule.dest_port_start) and isValidPort(rule.dest_port_end) and isValidPortRange(rule.src_port_start,rule.src_port_end) and isValidPortRange(rule.dest_port_start,rule.dest_port_end) :
            valid_rules_list.append(rule)
    
    valid_count = len(valid_rules_list)
    
    return count, valid_count
    
def processRule(lines):
    num = None
    source_ip = ''
    dest_ip = ''
    src_port = ''
    dest_port = ''
    protocol = ''
    data = ''
    src_port_start = None
    src_port_end = None
    dest_port_start = None
    dest_port_end = None
    
    for line in lines:
        #print(line)
        if line == 'BEGIN' or line =='END':
            continue
        elif 'NUM' in line:
            line_arr = line.split(':')
            num = int(line_arr[1].strip())
        elif 'SRC IP ADDR' in line:
            line_arr = line.split(':')
            source_ip = line_arr[1].strip()
        elif 'DEST IP ADDR' in line:
            line_arr = line.split(':')
            dest_ip = line_arr[1].strip()
        elif 'SRC PORT' in line:
            line_arr = line.split(':')
            src_port = line_arr[1].strip().split('-')
            src_port_start = int(src_port[0].strip())
            src_port_end = int(src_port[1].strip())
        elif 'DEST PORT' in line:
            line_arr = line.split(':')
            dest_port = line_arr[1].strip().split('-')
            dest_port_start = int(dest_port[0].strip())
            dest_port_end = int(dest_port[1].strip())
        elif 'PROTOCOL' in line:
            line_arr = line.split(':')
            protocol = line_arr[1].strip()
        elif 'DATA' in line:
            line_arr = line.split(':')
            data = line_arr[1].strip()
        else:
            continue
            
    r = Rule(num, source_ip, dest_ip, src_port_start, src_port_end, dest_port_start, dest_port_end, protocol, data)
    rules_list.append(r)

def processPackets(lines):
    num = None
    source_ip = ''
    dest_ip = ''
    src_port = None
    dest_port = None
    protocol = ''
    data = ''
    
    for line in lines:
        #print(line)
        if line == 'BEGIN' or line =='END':
            continue
        elif 'NUM' in line:
            line_arr = line.split(':')
            num = int(line_arr[1].strip())
        elif 'SRC IP ADDR' in line:
            line_arr = line.split(':')
            source_ip = line_arr[1].strip()
        elif 'DEST IP ADDR' in line:
            line_arr = line.split(':')
            dest_ip = line_arr[1].strip()
        elif 'SRC PORT' in line:
            line_arr = line.split(':')
            src_port = int(line_arr[1].strip())
        elif 'DEST PORT' in line:
            line_arr = line.split(':')
            dest_port = int(line_arr[1].strip())
        elif 'PROTOCOL' in line:
            line_arr = line.split(':')
            protocol = line_arr[1].strip()
        elif 'DATA' in line:
            line_arr = line.split(':')
            data = line_arr[1].strip()
        else:
            continue
            
    p = Packet(num, source_ip, dest_ip, src_port, dest_port, protocol, data)
    packets_list.append(p)

def isPacketIpValid(pkt_ip, rule_ip):
    if IPAddress(pkt_ip) in IPNetwork(rule_ip) or rule_ip == '0.0.0.0/0':
        return True
    
    return False

def isPacketPortValid(pkt_port, rule_port_start, rule_port_end):
    
    if (rule_port_start == 0 and rule_port_end ==0 ) or (isValidPort(pkt_port) and pkt_port >=rule_port_start and pkt_port <= rule_port_end ):
        return True
        
    return False

def isPacketDataValid(pkt_data, rule_data):
    
    if rule_data == '*' or rule_data in pkt_data:
        return True
    
    return False

def getMatchingRules(packet) :
    
    start = time.time()
    matching_rules=[]
    #print("pn:"+str(packet.num))
    #print("sp:"+str(packet.src_port))
    #print("dp:"+str(packet.dest_port))
    if not isValidPort(packet.src_port) or not isValidPort(packet.dest_port):
        print("Packet number %s is invalid." % packet.num)
    else:
        for rule in valid_rules_list:
            if isPacketDataValid(packet.data, rule.data) and isPacketIpValid(packet.source_ip, rule.source_ip) and isPacketIpValid(packet.dest_ip, rule.dest_ip) and isPacketPortValid(packet.src_port, rule.src_port_start, rule.src_port_end) and isPacketPortValid(packet.dest_port, rule.dest_port_start, rule.dest_port_end) and packet.protocol == rule.protocol :
                matching_rules.append(str(rule.num))
        
        matching_rules_str = ','.join(matching_rules)
        matching_rules_size = len(matching_rules)
        if matching_rules_size == 0:
            print('Packet number %s matches 0 rule(s).' % (packet.num)) 
        else:
            print('Packet number %s matches %s rules(s): %s' % (packet.num, matching_rules_size, matching_rules_str))
            
    end = time.time()
    #print("Start time:"+str(start))
    #print("End time:" + str(end))
    packet_process_times.append((end-start))
        
with open(rulefile, 'r') as f:
    for n_lines in iter(lambda: tuple(islice(f, n)), ()):
        processRule(n_lines)
    
total, valid_count = validRules(rules_list)
print('A total of %s rules were read; %s valid rules are stored.' % (total, valid_count))
#print('Valid rules numbers: ')
#for rule in valid_rules_list:
    #print("Num:"+str(rule.num))
    #print("SIP:"+rule.source_ip)
    #print("Data:"+str(rule.src_port_start))
    
with open(pktfile, 'r') as f:
    for n_lines in iter(lambda: tuple(islice(f, n)), ()):
        processPackets(n_lines)

for packet in packets_list:
    getMatchingRules(packet)

average_time = sum(packet_process_times)/len(packet_process_times)
print('A total of %s packet(s) were read from the file and processed. Bye.' % (len(packets_list)))
print('Average time taken per packet: %s microseconds.' % (average_time*1000000))