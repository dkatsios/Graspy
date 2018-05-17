inputs_dict = dict()

def __d_function(answer, number, function, *wargs):
	global inputs_dict
	inputs_dict[str(number)] = answer
	return eval(function + '(*wargs)')

def print_2(t1, t2):
    print(t1)
    print(t2)

answer = 1 + 3

__d_function(answer, 6, 'print', 'kati', 'allo')
print(inputs_dict['6'])