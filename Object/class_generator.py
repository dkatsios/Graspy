import CodeGeneratorBackend

import os
import sys
import jinja2
import re
import socket
import glob
from ip import get_ip
from random import randint

cwd = os.path.dirname(os.path.abspath(__file__))
sep = os.sep

ports_path = os.path.join(cwd, r'ports.conf')
##main_code_template_name = os.path.join(cwd, 'class_template.txt')
main_code_template_name = 'class_template.txt'
path_to_components_list = cwd + sep + 'components_list.txt'
main_code_name = 'components' + sep + 'object.py'
templates_subpath = os.path.join(cwd, 'templates')
Object_configuration_path = cwd + sep + r'Object_configuration.txt'
components_path = os.path.join(cwd, 'components')
object_name_label = 'Object Name'
object_role_label = 'Object Role'
object_python_command = 'python command'
Master_name = 'Master'
default_role = 'Slave'
default_name = 'default_name'

objects_pyro_port_label = 'objects_pyro_port'
broadcast_port_label = 'broadcast_port'
tab = "    "

c = CodeGeneratorBackend.CodeGeneratorBackend()


##def process_components_list_file(path_to_components_list):
##    fin = open(path_to_components_list)
##    component_names_inputs = []
##    for line in fin:
##        if line.__contains__("name = "):
##            name = line.replace('name = ', '')
##        else:
##            component_names_inputs.append(line.replace('\n', '').split('\t'))
##    return name.replace('\n', ''), component_names_inputs
##
##
##def process_component(component):
##    inputs = ''
##    if len(component) > 1:
##        inputs = component[1]
##    inputs_2 = re.sub('=.*?(,|$)', ',', inputs)
##    inputs_2 = re.sub(',$', '', inputs_2)
##    string_code = '@staticmethod\n' + tab + 'def ' + component[0] + '(' + inputs + '):\n' + tab + tab + 'return ' + component[0] + '.' + component[0] + '(' + inputs_2 + ')\n\n'
##    return string_code


def return_object_name_role():
    name = 'Object_' + str(randint(0, 10000))
    role = default_role
    try:
        with open(os.path.join(cwd, Object_configuration_path)) as f:
            for line in f:
                if object_name_label in line:
                    tmp_name = line.split('=')[1].strip()
                    if tmp_name != default_name:
                        name = tmp_name.replace(' ', '_').replace(':', '').replace('$', '')
                elif object_role_label in line:
                    tmp_role = line.split('=')[1].strip()
                    if tmp_role == Master_name:
                        role = Master_name
    except:
        pass
    return name, role


def find_port(port_label):
    with open(ports_path) as f:
        for line in f:
            if port_label in line:
                port = int(line.strip().split('$')[1].strip())
                return port


def return_methods(components_path):
    string_code = ''
    imports_list = []
    for file in glob.glob(components_path + sep + "*.comp"):
        filename = os.path.basename(file)
        comp_name = filename.replace('.comp', '')
        imports_list.append(comp_name)
        string_code += tab + '@staticmethod\n' + tab + 'def ' + comp_name + '(*args, **kwargs):\n' + tab + tab + 'return ' + comp_name + '.' + comp_name + '(*args, **kwargs)\n\n'
    string_imports = ', '.join(imports_list)
    return string_code, string_imports
        

if __name__ == '__main__':
    # components imports
   # from os import listdir
   # from os.path import isfile, join
   #
   # name, component_names_inputs = process_components_list_file(path_to_components_list)
   # comp_imports_list = []
   # for name_inputs in component_names_inputs:
   #     comp_imports_list.append(name_inputs[0])
   # comp_imports_text = ', '.join(comp_imports_list)

    # gui output to code transformation
    c.begin(tab=tab)
##    for component in component_names_inputs:
##        c.write(process_component(component))
    string_code, string_imports = return_methods(components_path)
    c.write(string_code)
    name, role = return_object_name_role()
    rend_dict = {
                 'ip': get_ip(),
                 'class_name': name,
                 'object_role': role,
                 'components_imports': string_imports,
                 'func_defs': c.end(),
                 'objects_pyro_port': find_port(objects_pyro_port_label),
                 'broadcast_port': find_port(broadcast_port_label)
                 }
    
    env = jinja2.Environment(
        loader=jinja2.FileSystemLoader(cwd + r'/templates'),
        autoescape=False
    )
    template = env.get_template(main_code_template_name)
    output_code = template.render(rend_dict)

    out_code = open(main_code_name, 'w')
    out_code.write(output_code)
    out_code.close()
