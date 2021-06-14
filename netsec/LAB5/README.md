This assignment helps us to implement packet filtering firewall.

There are two python executables available in the folder. One is for generating rules and packets which serve as an actual input to the other.

Please ensure the following module is installed : netaddr (Command: pip install netaddr)

1. rulePacketGen.py
This script is used for generating random rules and packets data so that they can be matched against by firewall script. The command to invoke the same is below:
python rulePacketGen.py <RULESIZE> <PKTSIZE> where <RULESIZE> is number of rules to be generated and <PKTSIZE> is the number of packets to be generated. 
eg. python rulePacketGen.py 300	500

2. lab5-fw.py
This script contains the actual matching logic where it reads the rules and filters the valid ones and then reads the packets and matches against the valid rules and returns the output. It can be invoked as below:
python lab5-fw.py <RULEFILENAME> <PKTFILENAME>
eg. python lab5-fw.py rules_300.txt packets_500.txt