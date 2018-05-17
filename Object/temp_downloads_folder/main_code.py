# main imports
import os
import Pyro4
import math
from random import uniform
from threading import Thread
from time import sleep
from Future1 import Future1 as _do_parallel

# objects URIs
ras1 = Pyro4.Proxy('PYRO:ras1@192.168.1.16:7771')


# components matching
do_print = ras1.do_print
faces_detected_from_file = ras1.faces_detected_from_file
get_photo = ras1.get_photo
print_times = ras1.print_times
send_mail = ras1.send_mail
wait_for_seconds = ras1.wait_for_seconds


# components dictionaries initialization
inputs_dict = dict()
variables = dict()

#code goes here

def run():
    outputs = []
    _do_parallel(print_times, 'test1', 10)
    _do_parallel(print_times, 'test2', 10)
    inputs_dict[4] = print_times('test2', 10)
    inputs_dict[6] = wait_for_seconds(3)
    variables['var'] = '__file_path__Single.java'
    return outputs

run()
#code ends here
