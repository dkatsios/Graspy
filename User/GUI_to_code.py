import zipfile

import CodeGeneratorBackend
import io
import os
import jinja2
import Pyro4
from remote_upload import remote_upload

cwd = os.path.dirname(os.path.abspath(__file__))
sep = os.sep
templates_path = os.path.join(cwd, r'templates')
#gui_output_path = os.path.join(cwd, r'GUI_output.txt')
ports_path = os.path.join(cwd, r'ports.conf')
main_code_template_path = r'main_code_template.txt'
main_code_path = os.path.join(cwd, r'main_code.py')
objects_uris_path = os.path.join(cwd, r'objects_uris.conf')
components_path = os.path.join(cwd, r'components', 'comp_files')
zip_file_path = os.path.join(cwd, r'tmp_files_to_upload.zip')
master_object_main_code_port_label = 'master_object_main_code_port'
ios_separator = '$'
master_object_ip = None
Master_name = 'Master'
line_components_separator = '\t'
code_tab = "    "
for_range_index = 0
threads_indices_list = []

c = CodeGeneratorBackend.CodeGeneratorBackend()

component_label = 'component'
variable_label = 'variable'
output_label = 'output'
IF_label = 'IF'
ELSE_IF_label = 'ELSE_IF'
ELSE_label = 'ELSE'
FOR_RANGE_label = 'FOR_RANGE'
WHILE_label = 'WHILE'
END_label = 'END'
start_threads_label = 'START_THREADS'
close_threads_label = 'CLOSE_THREADS'
new_thread_label = 'new_thread'
end_thread_label = 'end_thread'

file_path_text = 'File path: '
files_paths_to_upload = []
objects_uris_dict = dict()
paralleled_inputs_indices = []
first_parallel = None
last_parallel = None


def return_noninputs_comp_code(comp_id, parallel_state):
    global first_parallel
    global last_parallel
    comp_name = comp_id[0]
    if parallel_state == 0:
        code_string = 'inputs_dict[' + comp_id[1] + '] = ' + comp_name + '()'
        last_parallel = None
    elif parallel_state == 1:
        code_string = 'inputs_dict[' + comp_id[1] + '] = ' + '__a_' + comp_name + '()'
        paralleled_inputs_indices.append(comp_id[1])
        first_parallel = comp_id[1]
        last_parallel = comp_id[1]
    elif parallel_state == 2 and first_parallel is not None:
        code_string = 'inputs_dict[' + str(first_parallel) +\
                      '].then(__d_function, ' + first_parallel + ', ' + last_parallel + ', ' + '__a_' + comp_name + ', ' + comp_id[1] + ')'
        last_parallel = comp_id[1]
    return code_string


def is_number(s):
    try:
        float(s)
        return True
    except ValueError:
        return False


def process_io(ios):
    ios_list = []
    for inout in ios:
        if len(str(inout).split(ios_separator)) == 1:
            if is_number(inout):
                io_string = str(inout)
            elif inout.startswith(file_path_text):
                file_path = inout.replace(file_path_text, '').strip()
                files_paths_to_upload.append(file_path)
                io_string = "'__file_path__" + os.path.basename(file_path) + "'"
            else:
                io_string = "'" + str(inout) + "'"
        else:
            io_components = str(inout).split(ios_separator)
            if io_components[0] == '__variable__':
                io_string = "variables['" + io_components[1] + "']"
            else:
                if io_components[1] in paralleled_inputs_indices:
                    io_string = 'inputs_dict[' + str(io_components[1]) + '].value[' + str(
                        io_components[2]) + ']'
                else:
                    io_string = 'inputs_dict[' + str(io_components[1]) + '].value[' + str(
                        io_components[2]) + ']'
        ios_list.append(io_string)
    ios_string = ', '.join(ios_list)
    return ios_string


def return_inputs_comp_code(comp_id, inputs, parallel_state):
    global first_parallel
    global last_parallel
    comp_name = comp_id[0]
    inputs_string = process_io(inputs)
    if parallel_state == 0:
        code_string = 'inputs_dict[' + comp_id[1] + '] = ' + comp_name + '(' + inputs_string + ')'
        last_parallel = None
    elif parallel_state == 1:
        code_string = 'inputs_dict[' + comp_id[1] + '] = ' + '__a_' + comp_name + '(' + inputs_string + ')'
        paralleled_inputs_indices.append(comp_id[1])
        first_parallel = comp_id[1]
        last_parallel = comp_id[1]
    elif parallel_state == 2 and first_parallel is not None:
        print(type(inputs_string))
        code_string = 'inputs_dict[' + str(first_parallel) +\
                      '].then(__d_function, ' + first_parallel + ', ' + last_parallel + ', ' + \
                      '__a_' + comp_name + ', ' + str(comp_id[1]) + ', ' + inputs_string + ')'
        last_parallel = comp_id[1]
    return code_string


def process_component(line_parts, parallel_state):
    line_parts.pop(0)
    if len(line_parts) < 2:
        print('wrong syntax')
    comp_name = line_parts.pop(0)
    comp_num = line_parts.pop(0)
    comp_id = [comp_name, comp_num]
    if len(line_parts) == 0:
        code_line = return_noninputs_comp_code(comp_id, parallel_state)
    else:
        inputs = line_parts
        code_line = return_inputs_comp_code(comp_id, inputs, parallel_state)
    c.write(code_line + '\n')


def process_output(line_parts):
    line_parts.pop(0)
    outputs_string = process_io(line_parts)
    code_string = 'outputs = [' + outputs_string + ']'
    c.write(code_string + '\n')


def process_variable(line_parts):
    line_parts.pop(0)
    if len(line_parts) != 2:
        print('wrong syntax')
        return
    code_line = "variables['" + line_parts[0] + "'] = " + process_io(line_parts[1:])
    c.write(code_line + '\n')


def process_if_type(line_parts):
    line_parts.pop(0)
    outputs_string = process_io(line_parts)
    code_string = 'if ' + outputs_string + ':'
    c.write(code_string + '\n')
    c.indent()


def process_else_if_type(line_parts):
    line_parts.pop(0)
    outputs_string = process_io(line_parts)
    code_string = 'elif ' + outputs_string + ':'
    c.write(code_string + '\n')
    c.indent()


def process_else_type():
    code_string = 'elif ' + ':'
    c.write(code_string + '\n')
    c.indent()


def process_for_range_type(line_parts):
    line_parts.pop(0)
    input_string = process_io(line_parts)
    global for_range_index
    code_string = 'for __i__' + str(for_range_index) + ' in range(' + input_string + '):'
    for_range_index += 1
    c.write(code_string + '\n')
    c.indent()


def process_while_type(line_parts):
    line_parts.pop(0)
    input_string = process_io(line_parts)
    code_string = 'while ' + input_string + ':'
    c.write(code_string + '\n')
    c.indent()


def process_start_threads_type():
    global threads_indices_list
    threads_indices_list.append(0)
    code_string = '__threads_list__ = []'
    c.write(code_string + '\n')


def process_new_thread_type():
    global threads_indices_list
    threads_indices_list[-1] += 1
    thread_index = ''.join(map(str, threads_indices_list))
    code_string = 'def __thread__' + thread_index + '():'
    c.write(code_string + '\n')
    c.indent()


def process_end_thread_type():
    global threads_indices_list
    c.dedent()
    thread_index = ''.join(map(str, threads_indices_list))
    code_string = '__threads_list__.append(__thread__' + thread_index + ')'
    c.write(code_string + '\n')


def process_close_threads_type():
    global threads_indices_list
    threads_indices_list.pop()
    code_string = 'thr = []'
    c.write(code_string + '\n')
    code_string = 'for thread in __threads_list__:'
    c.write(code_string + '\n')
    c.indent()
    code_string = 'thr.append(Thread(target=thread))'
    c.write(code_string + '\n')
    code_string = 'thr[-1].start()'
    c.write(code_string + '\n')
    c.dedent()

    code_string = 'for thread in thr:'
    c.write(code_string + '\n')
    c.indent()
    code_string = 'thread.join()'
    c.write(code_string + '\n')
    c.dedent()


def process_line(line):
    parallel_state = 0
    line = line.replace('\n', '')
    line_parts = line.split(line_components_separator)
    if 'parallel_state' in line_parts[-1]:
        parallel_state = int(line_parts.pop(-1).replace('parallel_state', '').strip())
    if line_parts[0] == component_label:
        process_component(line_parts, parallel_state)
    elif line_parts[0] == variable_label:
        process_variable(line_parts)
    elif line_parts[0] == output_label:
        process_output(line_parts)
    elif line_parts[0] == IF_label:
        process_if_type(line_parts)
    elif line_parts[0] == ELSE_IF_label:
        process_else_if_type(line_parts)
    elif line_parts[0] == ELSE_label:
        process_else_type()
    elif line_parts[0] == FOR_RANGE_label:
        process_for_range_type(line_parts)
    elif line_parts[0] == WHILE_label:
        process_while_type(line_parts)
    elif line_parts[0] == start_threads_label:
        process_start_threads_type()
    elif line_parts[0] == close_threads_label:
        process_close_threads_type()
    elif line_parts[0] == new_thread_label:
        process_new_thread_type()
    elif line_parts[0] == end_thread_label:
        process_end_thread_type()
    elif line_parts[0] == END_label:
        c.dedent()


def process_comp_name_import(name):
    name = name.replace('\n', '')
    comp_string = 'from ' + '.components import ' + name
    return comp_string


def populate_object_uris_dict():
    global objects_uris_dict
    global master_object_ip
    with open(objects_uris_path, encoding='utf8') as objects_uris_file:
        for line in objects_uris_file:
            role, uri = line.strip().split('$$')
            name = uri.strip().split('@')[0].split(':')[1]
            objects_uris_dict[name] = uri
            if master_object_ip is None or role == Master_name:
                master_object_ip = uri.split(':')[1].split('@')[1]


def methods(cls):
    return [x for x, y in cls.__dict__.items() if type(y) == staticmethod]


def return_components_functions():
    components_functions = ''
    for class_name, uri in objects_uris_dict.items():
        print(uri)
        tmp_object = Pyro4.Proxy(uri)
        tmp_methods_list = tmp_object.return_methods()
        for method in tmp_methods_list:
            components_functions +=          method + ' = ' +          class_name + '.' + method + '\n'
            components_functions += '__a_' + method + ' = ' + '__a_' + class_name + '.' + method + '\n'
    return components_functions


def return__d_function_definition():
    __d_function_string = 'def __d_function(answer, first_parallel, number, function, comp_id, *args):\n' + \
    code_tab + 'global inputs_dict\n' + \
    code_tab + 'if number != first_parallel:\n' + \
    code_tab + code_tab + 'inputs_dict[number].wait()\n' + \
    code_tab + 'inputs_dict[comp_id] =  eval(\'function(*args)\')\n'
    code_tab + 'return answer\n'
    return __d_function_string


def return_components_functions_from_file():
    with open(components_path + sep + 'components_str') as f:
        return f.read()


def find_port(port_label):
    with open(ports_path) as f:
        for line in f:
            if port_label in line:
                port = int(line.strip().split('$')[1].strip())
                return port


def make_zip(files_paths_to_upload):
    with zipfile.ZipFile(zip_file_path, 'w') as myzip:
        for f in files_paths_to_upload:
            myzip.write(f, os.path.basename(f))
        print('files_zipped')


def main(gui_output_path):
    # components imports
    from os import listdir
    objects_uris = ''
    populate_object_uris_dict()
    for key, value in objects_uris_dict.items():
        objects_uris += '__a_' + key + ' = Pyro4.Proxy(\'' + value + '\')\n' +\
                        '__a_' + key + '._pyroAsync()\n' +\
                        key + ' = Pyro4.Proxy(\'' + value + '\')\n'

    components_functions = return_components_functions()

    # gui output to code transformation
    c.begin(tab=code_tab)
    c.indent()

    with io.open(gui_output_path, "r",
                 encoding="utf-8") as gui_output:
        for line in gui_output:
            process_line(line)

    rend_dict = {'objects_uris': objects_uris,
                 'components_functions': components_functions,
                 'code_to_run': c.end(),
                 '__d_function_definition': return__d_function_definition()}
    env = jinja2.Environment(
        loader=jinja2.FileSystemLoader(templates_path),
        autoescape=False
    )

    template = env.get_template(main_code_template_path)
    output_code = template.render(rend_dict)
    print(output_code)
    with io.open(main_code_path, "w", encoding="utf-8") as out_code:
        out_code.write(output_code)
    port = find_port(master_object_main_code_port_label)
    if len(files_paths_to_upload) != 0:
        files_paths_to_upload.append(main_code_path)
        try:
            make_zip(files_paths_to_upload)
            remote_upload("http://" + master_object_ip, port, zip_file_path)
        except:
            print("error")
            pass
    else:
        remote_upload("http://" + master_object_ip, port, main_code_path)