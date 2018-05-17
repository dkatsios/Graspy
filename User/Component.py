import os


class Component:
    def __repr__(self):
        return self.component_label


class Input:
        pass


class Output:
        pass


def process_inputs_types(comp, attr_value):
    values_list = attr_value.split('$')
    for index, value in enumerate(values_list):
        value = value.strip()
        val_list = value.split(':')
        input = comp.inputs[index]
        input.type = val_list[0]
        type_values = []
        if len(val_list) > 1:
            for val in val_list[1].split(','):
                val = val.strip()
                if val == 'None':
                    type_values.append(None)
                else:
                    try:
                        type_values.append(float(val))
                    except ValueError:
                        type_values.append(val)
            input.type_values = type_values
        comp.inputs[index] = input
    return comp


def process_default_values(comp, attr_value):
    values_list = attr_value.split('$')
    inputs_default_values = []
    for value in values_list:
        value = value.strip()
        if value == 'None':
            inputs_default_values.append(None)
        else:
            try:
                inputs_default_values.append(float(value))
            except ValueError:
                inputs_default_values.append(value)
    for index, default_value in enumerate(inputs_default_values):
        comp.inputs[index].value = default_value
    return comp


def process_component(comp_path):
    comp_file = open(comp_path)
    comp = Component()
    comp.object_name = 'default_name'
    for line in comp_file:
        attr_name = line.strip().split('=')[0]
        attr_value = ''.join(line.strip().split('=')[1:])
        attr_name = attr_name.strip()
        attr_value = attr_value.strip()
        if attr_name == 'Object Name':
            comp.object_name = attr_value
        elif attr_name == 'component_name':
            comp.component_name = attr_value
        elif attr_name == 'component_category':
            comp.component_category = attr_value
        elif attr_name == 'component_label':
            comp.component_label = attr_value
        elif attr_name == 'inputs_names':
            if attr_value == 'None':
                comp.inputs = None
            else:
                inputs_names = attr_value.split('$')
                inputs = []
                for name in inputs_names:
                    name = name.strip()
                    input = Input()
                    input.name = name
                    inputs.append(input)
                comp.inputs = inputs
        elif attr_name == 'inputs_labels' and comp.inputs is not None:
            inputs_labels = attr_value.split('$')
            for index, label in enumerate(inputs_labels):
                if label == 'None':
                    label = None
                comp.inputs[index].label = label.strip()
        elif attr_name == 'inputs_description' and comp.inputs is not None:
            inputs_description = attr_value.split('$')
            for index, description in enumerate(inputs_description):
                if description == 'None':
                    description = None
                comp.inputs[index].description = description.strip()
        elif attr_name == 'inputs_default_values' and comp.inputs is not None:
            comp = process_default_values(comp, attr_value)
        elif attr_name == 'inputs_types' and comp.inputs is not None:
            comp = process_inputs_types(comp, attr_value)
        elif attr_name == 'outputs_names':
            if attr_value == 'None':
                comp.outputs = None
            else:
                outputs_names_list = attr_value.split('$')
                outputs = []
                for output_name in outputs_names_list:
                    output = Output()
                    if output_name == 'None':
                        output_name = None
                    output.name = output_name.strip()
                    output.value = None
                    outputs.append(output)
                comp.outputs = outputs
        elif attr_name == 'outputs_labels' and comp.outputs is not None:
            outputs_label = attr_value.split('$')
            for index, label in enumerate(outputs_label):
                if label == 'None':
                    label = None
                comp.outputs[index].label = label.strip()
        elif attr_name == 'outputs_description' and comp.outputs is not None:
            outputs_description = attr_value.split('$')
            for index, description in enumerate(outputs_description):
                if description == 'None':
                    description = None
                comp.outputs[index].description = description.strip()
    comp_file.close()
    return comp
