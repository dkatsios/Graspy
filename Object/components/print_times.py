import Pyro4
from time import sleep

def print_times(text = '', times = 1):
    outputs = []
    for i in range(times):
        print(text)
        sleep(0.5)
    outputs.append(text)
    return outputs


print_times_f = Pyro4.Future(print_times)
