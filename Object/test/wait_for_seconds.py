import time


def wait_for_seconds(word, seconds=1):
    outputs = []
    #for key in kwargs:
    #    print (key, kwargs[key])
        #exec('%s = %s' % (key, repr(kwargs[key])))
    #    exec ('global %s' % (key))
    #    exec('%s = %s' % (key, kwargs[key]))
    #    print('%s = %s' % (key, kwargs[key]))
    #    print (seconds) 
    #for k, v in kwargs.items():
    #    locals()[k] = v
    print('start')
    time.sleep(float(seconds))
    print(word)
    return outputs
