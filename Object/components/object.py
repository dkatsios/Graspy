import Pyro4
import do_print, faces_detected_from_file, get_photo, print_times, send_mail, wait_for_seconds
import socket
import os
import glob
import sys
from time import sleep
from socket import socket, AF_INET, SOCK_DGRAM, SOL_SOCKET, SO_BROADCAST, gethostbyname, gethostname
from threading import Thread

components_path = os.path.dirname(os.path.abspath(__file__))
project_path = os.path.dirname(components_path)
sep = os.sep

object_name_label = r'Object Name'
files_separator = "\n====\n"

boolean_broadcast = True
MAGIC = 'Broadcast'
time_to_sleep = 0.5

@Pyro4.expose
class ras1:
    @staticmethod
    def do_print(*args, **kwargs):
        return do_print.do_print(*args, **kwargs)

    @staticmethod
    def faces_detected_from_file(*args, **kwargs):
        return faces_detected_from_file.faces_detected_from_file(*args, **kwargs)

    @staticmethod
    def get_photo(*args, **kwargs):
        return get_photo.get_photo(*args, **kwargs)

    @staticmethod
    def print_times(*args, **kwargs):
        return print_times.print_times(*args, **kwargs)

    @staticmethod
    def send_mail(*args, **kwargs):
        return send_mail.send_mail(*args, **kwargs)

    @staticmethod
    def wait_for_seconds(*args, **kwargs):
        return wait_for_seconds.wait_for_seconds(*args, **kwargs)

    @staticmethod
    def stop_broadcast():
        global boolean_broadcast
        boolean_broadcast = False
    
    @staticmethod
    def get_component_files():
        files_str = ""
        print (components_path + sep + "*.comp")
        for file in glob.glob(components_path + sep + "*.comp"):
            print(file)
            fin = open (file, "r")
            filename = os.path.basename(file)
            files_str += "component_filename:" + filename + "\n"
            files_str += object_name_label + " = " + 'ras1' + "\n"
            files_str += fin.read() + files_separator
            fin.close()
        print (files_str)
        return (files_str)


    @classmethod
    def return_methods(cls):
        return [x for x, y in cls.__dict__.items() if type(y) == staticmethod]

def do_broadcast(broadcast_message):
    s = socket(AF_INET, SOCK_DGRAM) #create UDP socket
    s.bind(('', 0))
    s.setsockopt(SOL_SOCKET, SO_BROADCAST, 1) #this is a broadcast socket
    while boolean_broadcast:
        s.sendto(bytes(broadcast_message,'utf8'), ('<broadcast>', int('7774')))
        print (broadcast_message)
        sleep(time_to_sleep)

if __name__ == '__main__':
    broadcast_port = 7774
    daemon = Pyro4.Daemon(host='192.168.226.78', port=7771)
    uri = daemon.register(ras1, objectId='ras1')
    print(uri)
    #oxi broadcast_message = MAGIC + 'ras1' + '$' + 'Slave' + '$$' + str(uri)
    
    #uncomment for broadcast
    ###broadcast_message = MAGIC + 'Slave' + '$$' + str(uri)
    ###t1 = Thread(target=do_broadcast, args=(broadcast_message,))
    ###t1.start()
    daemon.requestLoop()