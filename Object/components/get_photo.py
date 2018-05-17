import os
def get_photo(filename):
    outputs = []
    sep = os.sep
    cwd = os.path.dirname(os.path.abspath(__file__))
    os.system ('raspistill -w 640 -h 480 -vf -hf -n -t 100 -q 10 -o ' + cwd + sep + 'files' + sep + filename)    
    return outputs
