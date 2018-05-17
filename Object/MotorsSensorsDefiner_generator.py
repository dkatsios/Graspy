import os
import jinja2
import re


main_code_template_name = 'MotorsSensorsDefiner_template.txt'
path_to_components_list = 'Object_configuration.txt'
MotorsSensorsDefiner_name = r'components/MotorsSensorsDefiner.py'
templates_subpath = r'./templates'
tab = "    "


def return_code(type_name, dict_name):
    conf_file = open(path_to_components_list)
    return_text = ''
    flag = False
    this_tab = ''
    if dict_name is not None:
        this_tab = tab
    for line in conf_file:
        if line.startswith('#') or not line.strip():
            continue
        if line.startswith(type_name + '_START'):
            flag = True
            continue
        if line.startswith(type_name + '_END'):
            flag = False
            break
        if flag:
            return_text += this_tab + line
            if dict_name is not None:
                comp_name = line.split('=')[0].strip()
                return_text += this_tab + dict_name + '[\'' + comp_name + '\'] = ' + comp_name + '\n'
    return return_text


if __name__ == '__main__':
    rend_dict = {'imports': return_code('IMPORTS', None),
                 'pin_parameters': return_code('PINS', None),
                 'motors_code': return_code('MOTORS', 'motors'),
                 'sensors_code': return_code('SENSORS', 'sensors')}

    env = jinja2.Environment(
        loader=jinja2.FileSystemLoader(templates_subpath),
        autoescape=False
    )

    template = env.get_template(main_code_template_name)
    output_code = template.render(rend_dict)

    out_code = open(MotorsSensorsDefiner_name, 'w')
    out_code.write(output_code)
