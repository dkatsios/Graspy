from Future import Future as parallel
from time import sleep

def print_times(text, num):
    for i in range(num):
        print(text)
        sleep(0.5)
    return text

##out = parallel(print_times, 'bla', 5)
##print_times('nia', 3)
##sleep(2)
##print(out()*3)

inputs_dict = dict()

def run():
    outputs = []
    inputs_dict[4] = parallel(print_times, 'bla', 8)
    inputs_dict[5] = print_times('jj', 8)
    inputs_dict[7] = sleep(3)
    inputs_dict[6] = print_times(inputs_dict[4]()[0], 4)
    return outputs

run()
