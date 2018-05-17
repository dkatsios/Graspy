from time import sleep
from socket import socket, AF_INET, SOCK_DGRAM, SOL_SOCKET, SO_BROADCAST, gethostbyname, gethostname
from ip import get_ip
import os

PORT = 50000
MAGIC = 'Graspy'
cwd = os.path.dirname(os.path.abspath(__file__))
sep = os.sep

object_name_label = r'Object Name'
default_name = 'default_name'
Object_configuration_path = cwd + sep + r'Object_configuration.txt'
def return_object_name():
    name = None
    try:
        print (Object_configuration_path)
        with open(Object_configuration_path) as f:
            for line in f:
                if object_name_label in line:
                    tmp_name = line.split('=')[1].strip()
                    if tmp_name == default_name:
                        raise Exception('No name has been defined!')
                    else:
                        name = tmp_name
                    if name is None:
                        raise Exception('No name has been defined!')
    except:
        print('No name has been defined!')
        sys.exit()
    return name




s = socket(AF_INET, SOCK_DGRAM) #create UDP socket
s.bind(('', 0))
s.setsockopt(SOL_SOCKET, SO_BROADCAST, 1) #this is a broadcast socket
ip = get_ip()
print (cwd + sep + "object_uri.txt")
f = open (cwd + sep + "object_uri.txt")
pyro_uri = f.read().strip()
print (pyro_uri)

while 1:
        data = MAGIC + return_object_name() + " " + pyro_uri 
        s.sendto(bytes(data,'utf8'), ('<broadcast>', PORT))
        print ("sent service announcement")
        sleep(2)
