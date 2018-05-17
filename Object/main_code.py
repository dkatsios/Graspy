# main imports
import os
import Pyro4
import math
from random import uniform
from threading import Thread
from time import sleep
from Future import Future as _do_parallel

# objects URIs
__a_ras1 = Pyro4.Proxy('PYRO:ras1@192.168.226.78:7771')
__a_ras1._pyroAsync()
ras1 = Pyro4.Proxy('PYRO:ras1@192.168.226.78:7771')


# components matching
get_photo = ras1.get_photo
__a_get_photo = __a_ras1.get_photo
stop_broadcast = ras1.stop_broadcast
__a_stop_broadcast = __a_ras1.stop_broadcast
send_mail = ras1.send_mail
__a_send_mail = __a_ras1.send_mail
get_component_files = ras1.get_component_files
__a_get_component_files = __a_ras1.get_component_files
do_print = ras1.do_print
__a_do_print = __a_ras1.do_print
print_times = ras1.print_times
__a_print_times = __a_ras1.print_times
wait_for_seconds = ras1.wait_for_seconds
__a_wait_for_seconds = __a_ras1.wait_for_seconds
faces_detected_from_file = ras1.faces_detected_from_file
__a_faces_detected_from_file = __a_ras1.faces_detected_from_file


# components dictionaries initialization
inputs_dict = dict()
variables = dict()


# __d_function definition
def __d_function(answer, first_parallel, number, function, comp_id, *args):
    global inputs_dict
    if number != first_parallel:
        inputs_dict[number].wait()
    inputs_dict[comp_id] =  eval('function(*args)')


#code goes here

def run():
    outputs = []
    inputs_dict[0] = print_times('kati', 2)
    return outputs

run()
#code ends here