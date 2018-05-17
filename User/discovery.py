import Pyro4
from socket import socket, AF_INET, SOCK_DGRAM, SOCK_STREAM, SOL_SOCKET, SO_REUSEADDR
from time import sleep, time

MAGIC = 'Broadcast'
seconds_to_listen = 10

def update_objects_uris_path(objects_uris_path, port):
    s = socket(AF_INET, SOCK_DGRAM)  # create UDP socket
    s.bind(('', port))
    s.settimeout(4.0)
    uris_set = set()
    start_time = time()
    while (time() - start_time) < seconds_to_listen:
        try:
            data, addr = s.recvfrom(1024) #wait for a packet
        except:
            continue
        if data.startswith(bytes(MAGIC,'utf8')):
            tmp_uri = bytes.decode(data[len(MAGIC):]).strip()
            tmp_uri = tmp_uri.strip().split('$$')[1]
            tmp_object = Pyro4.Proxy(tmp_uri)
            tmp_object.stop_broadcast()
            uris_set.add(tmp_uri)
            print ("got service announcement from", data[len(MAGIC):])

    if len(uris_set) > 0:
        string_to_write = '\n'.join(uris_set)
        print (string_to_write)
        with open(objects_uris_path, 'w') as f:
            f.write(string_to_write)

update_objects_uris_path('objects_uris.conf', 7774)