# main imports
import os
import Pyro4
import math
from random import uniform
from threading import Thread
from time import sleep
from Future import Future as _do_parallel
import _thread

# objects URIs
a_ras1 = Pyro4.Proxy('PYRO:ras1@192.168.1.16:7771')
a_ras1._pyroAsync()
ras1 = Pyro4.Proxy('PYRO:ras1@192.168.1.16:7771')

# components matching
##do_print = ras1.do_print
##faces_detected_from_file = ras1.faces_detected_from_file
##get_photo = ras1.get_photo
print_times = ras1.print_times
print_times_f = a_ras1.print_times
##send_mail = ras1.send_mail
##wait_for_seconds = ras1.wait_for_seconds
wait_for_seconds = sleep

# components dictionaries initialization
inputs_dict = dict()
variables = dict()

#code goes here
##def print_times(text, num):
##    for i in range(num):
##        print(text)
##        sleep(0.5)
##    return text

def run():
    outputs = []
    a = print_times_f('jj', 8)
    print_times('oo', 8)
    sleep(2)
    print(a.value)
##    _thread.start_new_thread(print_times, ('bla', 5))
##    _thread.start_new_thread(print_times, ('biu', 5))
##    inputs_dict[4] = _do_parallel(print_times, 'bla', 8)
##    inputs_dict[5] = print_times('jj', 8)
##    inputs_dict[7] = wait_for_seconds(3)
##    inputs_dict[6] = print_times(inputs_dict[4]()[0], 4)
    return outputs

run()
#code ends here
