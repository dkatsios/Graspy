import io
import copy
import kivy
from kivy.app import App
from kivy.uix.button import Button
from kivy.uix.filechooser import FileChooserIconView
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.label import Label
from kivy.uix.togglebutton import ToggleButton
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.stacklayout import StackLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.tabbedpanel import TabbedPanelItem
from kivy.properties import ObjectProperty
from kivy.properties import NumericProperty, BooleanProperty
from kivy.uix.behaviors import ButtonBehavior
from kivy.graphics import Rectangle, Color
from Component import process_component
import GUI_to_code
import glob, os
import pickle
import tkinter as tk
from tkinter import messagebox
from tkinter import filedialog
#import wx
import shutil
import Pyro4
import time
from socket import socket, AF_INET, SOCK_DGRAM, SOCK_STREAM, SOL_SOCKET, SO_REUSEADDR

kivy.require('1.9.2')  # replace with your current kivy version !

cwd = os.path.dirname(os.path.abspath(__file__))
sep = os.sep

comp_files_path = os.path.join(cwd, r'components', r'comp_files')
flow_control_components_path = os.path.join(cwd, r'components', r'flow control')
GUI_output_path = os.path.join(cwd, r'GUI_output.txt')
GUI_to_code_path = os.path.join(cwd, r'GUI_to_code.py')

objects_uris_path = os.path.join(cwd, r'objects_uris.conf')

python_command = 'python'
program_name = 'Graspy'
file_path_text = 'File path: '
line_components_separator = '\t'

MAGIC = 'Broadcast'
seconds_to_listen = 10
broadcast_port_label = 'broadcast_port'

special_comps_list = ['FOR_RANGE', 'IF', 'ELSE_IF', 'ELSE', 'WHILE', 'END', 'START_THREADS', 'new_thread',
                      'end_thread', 'CLOSE_THREADS', 'variable']

indents_comps_list = ['FOR_RANGE', 'IF', 'ELSE_IF', 'ELSE', 'WHILE']

unindents_comps_list = ['ELSE_IF', 'ELSE', 'END']

attributes_to_copy = ['outputs_list', 'inputs_dict', 'name', 'text', 'index_number', 'num_of_indents',
                      'inputs', 'inputs_number', 'outputs', 'real_name', 'outputs_number', 'id', 'parallel_state']

categories_components_dict = dict()

g_zoom_level = 1
zoom_factor = 4/3


class LeftComponent(Button):
    pass


class ComponentsArea(StackLayout):
    pass


class InputButton(ToggleButton):
    pass


class OutputButton(Button):
    pass


class CenterComponent(ButtonBehavior, GridLayout):
    parallel_state = NumericProperty(1)
    inputs_number = NumericProperty(0)
    outputs_number = NumericProperty(0)
    index_number = NumericProperty(0)
    num_of_indents = NumericProperty(0)
    size_of_first = NumericProperty(0)
    unzoom_level = NumericProperty(g_zoom_level)
    font_size = NumericProperty(16)
    start_selected = BooleanProperty(False)
    symbols_list = ['o', '=', '||']

    def change_font_size(self, mylabel):
        mylabel.font_size = 16 / g_zoom_level

    def change_parallel_state(self, button):
        self.parallel_state = (self.parallel_state + 1) % 3
        button.text = self.symbols_list[self.parallel_state]

    def parallel_state_text(self):
        return self.symbols_list[self.parallel_state]


class SaveDialog(FloatLayout):
    save = ObjectProperty(None)
    text_input = ObjectProperty(None)
    cancel = ObjectProperty(None)


class LoadDialog(FloatLayout):
    load = ObjectProperty(None)
    cancel = ObjectProperty(None)


class MainScreen(BoxLayout):
    but = CenterComponent()
    current_indentation = NumericProperty(0)
    current_component = None
    current_output_component = None
    current_input = None
    user_selected = BooleanProperty(True)
    selected_index = 0
    current_comp_id_number = 0
    components_list = []
    new_categories_set = set()
    input_list = BooleanProperty(False)
    max_canvas_width = NumericProperty(0)
    start_selected = BooleanProperty(True)

    def __init__(self):
        super().__init__()

    def start_component_pressed(self, my_widget):
        self.start_selected = True
        self.current_indentation = 0
        for index, widget in enumerate(self.ids.main_canvas.children):
            if widget == my_widget:
                self.selected_index = index
            if isinstance(widget, CenterComponent):
                widget.start_selected = False

    def remove_component(self, id):
        this_widget_list = filter(lambda x: x.id == id, self.ids.main_canvas.children)
        self.ids.main_canvas.remove_widget(next(this_widget_list))
        # for widget in self.ids.main_canvas.children:
        #     if widget.id == id:
        #         self.ids.main_canvas.remove_widget(widget)

    def left_component_pressed(self, widget):
        self.start_selected = False
        for other_widget in self.ids.main_canvas.children:
            if isinstance(other_widget, CenterComponent):
                other_widget.start_selected = False
        m_canvas = self.ids.main_canvas
        but = CenterComponent()
        but.bind(on_release=self.center_component_pressed)
        but.name = widget.name
        but.text = widget.text
        but.index_number = self.current_comp_id_number
        but.unzoom_level = g_zoom_level
        but.start_selected = True
        inputs_dict = dict()
        outputs_list = list()
        try:
            this_comp = [component for component in self.components_list
                         if component.component_name == widget.name].__getitem__(0)
            if (this_comp.component_name in unindents_comps_list) and self.current_indentation == 0:
                return
            for input in this_comp.inputs:
                inputs_dict[input.label] = input.value
            but.inputs_number = len(this_comp.inputs)
            but.inputs = copy.deepcopy(this_comp.inputs)
        except (IndexError, TypeError):
            but.inputs_number = 0
            but.inputs = []

        try:
            this_comp = [component for component in self.components_list
                         if component.component_name == widget.name].__getitem__(0)
            for output in this_comp.outputs:
                outputs_list.append(output.label)
            but.outputs_list = outputs_list
            but.outputs_number = len(outputs_list)
            but.outputs = copy.deepcopy(this_comp.outputs)
            but.real_name = this_comp.component_name
        except (IndexError, TypeError):
            but.outputs_number = 0
            but.outputs_list = []
            but.real_name = widget.name
            print(but.real_name)

        but.inputs_dict = inputs_dict
        but.id = widget.name + '_' + str(self.current_comp_id_number)
        if this_comp.component_name in unindents_comps_list:
            self.current_indentation -= 1
        but.num_of_indents = self.current_indentation
        if this_comp.component_name in indents_comps_list:
            self.current_indentation += 1
        self.max_canvas_width = max(self.max_canvas_width, but.width + self.current_indentation * 40)
        but.remove_component = self.remove_component
        print(but.num_of_indents)
        m_canvas.add_widget(but, self.selected_index)
        self.current_comp_id_number += 1

    def center_component_pressed(self, my_widget):
        if self.user_selected:
            print(my_widget.num_of_indents)
            self.start_selected = False
            self.current_component = my_widget
            self.current_indentation = my_widget.num_of_indents + (1 if my_widget.real_name in indents_comps_list else 0)
            # self.ids.inputs_list.clear_widgets()
            for index, widget in enumerate(self.ids.main_canvas.children):
                if isinstance(widget, CenterComponent):
                    widget.start_selected = False
                if widget == my_widget:
                    widget.start_selected = True
                    self.selected_index = index
            self.populate_inputs_list(my_widget)
            self.set_values_to_default()
            self.ids.component_inputs_label.text = my_widget.text + '  ' + str(my_widget.index_number)
        else:
            self.current_output_component = my_widget
            for index, widget in enumerate(self.ids.main_canvas.children):
                if widget == my_widget:
                    if index > self.selected_index:
                        self.populate_outputs_list(my_widget)
                    else:
                        self.ids.outputs_list.clear_widgets()
                        self.ids.selected_output.text = 'select component'

    def make_components_box(self, category_name):
        components_area = ComponentsArea()
        components_area.id = category_name + '_box'
        if category_name in categories_components_dict.keys():
            for component in categories_components_dict[category_name]:
                comp = LeftComponent()
                comp.bind(on_release=self.left_component_pressed)
                comp.name = component[1]
                comp.text = component[0]
                components_area.add_widget(comp)
        return components_area

    def make_new_category(self, category_name, index=0):
        components_categories = self.ids.components_categories
        new_tab = TabbedPanelItem()
        new_tab.id = category_name
        new_tab.text = category_name
        components_box = self.make_components_box(category_name)
        new_scroll = ScrollView()
        new_scroll.add_widget(components_box)
        new_tab.add_widget(new_scroll)
        components_categories.add_widget(new_tab, index + 1)

    def input_pressed(self, input):
        self.current_input = input
        self.ids.input_description.text = 'Description:\n' + input.description
        self.ids.input_value.text = 'Value:\n' + str(input.value)
        self.input_list = input.type == 'list'
        if self.user_selected:
            if input.type == 'list':
                self.ids.open_outputs_button.text = self.ids.open_outputs_button.input_text
                self.populate_input_values_list()
            else:
                self.ids.open_outputs_button.text = ''
        else:
            self.ids.open_outputs_button.text = self.ids.open_outputs_button.output_text

    def populate_input_values_list(self):
        values_list = [value for value in [input.type_values for input in self.current_component.inputs
                                           if input.label == self.current_input.label].__getitem__(0)]

        try:
            self.ids.outputs_list.clear_widgets()
            for value in values_list:
                btn = Button(text=str(value), size_hint_y=None, height=44)
                btn.bind(on_release=self.input_value_pressed)
                self.ids.outputs_list.add_widget(btn)
        except ReferenceError:
            pass

    @staticmethod
    def delete_files_from_folder(folder):
        for the_file in os.listdir(folder):
            file_path = os.path.join(folder, the_file)
            try:
                if os.path.isfile(file_path):
                    os.unlink(file_path)
                elif os.path.isdir(file_path):
                    shutil.rmtree(file_path)
            except Exception as e:
                print(e)

    def process_components_path(self, components_path):
        components_str = ''
        for file in glob.glob(components_path + sep + "*.comp"):
            component = process_component(file)
            components_str += component.component_name + ' = ' +\
                              component.object_name + '.' + component.component_name + '\n'
            # print(component)
            self.components_list.append(component)
            if component.component_category not in categories_components_dict.keys():
                categories_components_dict[component.component_category] = []
            categories_components_dict[component.component_category].append(
                (component.component_label, component.component_name))
            with open(components_path + sep + 'components_str', 'w') as f:
                f.write(components_str)

    def build_categories(self):
        for components_path in [comp_files_path, flow_control_components_path]:
            self.process_components_path(components_path)
        for index, category_name in enumerate(sorted(categories_components_dict.keys())):
            self.make_new_category(category_name, index)

    def populate_inputs_list(self, widget):
        self.ids.inputs_list.clear_widgets()
        print(widget.id)
        try:
            for input in widget.inputs:
                but = InputButton(text=input.label)
                but.name = input.name
                but.label = input.label
                but.description = input.description
                but.value = input.value
                but.type = input.type
                print(input.value)
                but.bind(on_release=self.input_pressed)
                self.ids.inputs_list.add_widget(but)
        except AttributeError:
            pass

    def populate_outputs_list(self, my_widget):
        self.ids.outputs_list.clear_widgets()
        self.ids.selected_output.text = 'select output'

        for output in my_widget.outputs_list:
            btn = OutputButton(text=output)
            btn.bind(on_release=self.output_value_pressed)
            self.ids.outputs_list.add_widget(btn)

    def output_value_pressed(self, output_button):
        self.ids.outputs_list.select(output_button.text)
        print('object: ', output_button.text)
        self.ids.selected_output.text = str(output_button.text)
        text = 'component: ' + self.current_output_component.name + '   ' + \
               str(self.current_output_component.index_number) + '\noutput: ' + str(output_button.text)
        self.change_input_value(text)
        self.ids.input_value.text = 'Value:\n' + text
        self.from_user_pressed(True)

    def input_value_pressed(self, input_value_button):
        self.ids.outputs_list.select(input_value_button.text)
        self.change_input_value(input_value_button.text)
        print(input_value_button.text)
        self.ids.input_value.text = 'Value:\n' + input_value_button.text

    def output_selected(self, instance):
        self.ids.selected_output.text = instance

    def from_user_pressed(self, state):
        self.user_selected = state
        self.ids.outputs_list.clear_widgets()
        if state:
            self.ids.from_user.state = 'down'
            self.ids.from_component.state = 'normal'
            self.ids.selected_output.text = ''
            if self.current_input.type == 'list':
                self.populate_input_values_list()
                self.ids.open_outputs_button.text = self.ids.open_outputs_button.input_text
            else:
                self.ids.open_outputs_button.text = ''
        else:
            self.ids.open_outputs_button.text = self.ids.open_outputs_button.output_text
            self.ids.from_component.state = 'down'
            self.ids.from_user.state = 'normal'

    def from_component_pressed(self):
        self.from_user_pressed(False)
        self.ids.outputs_list.clear_widgets()
        self.ids.selected_output.text = 'select component'

    def from_file_pressed(self):
        self.user_selected = False
        self.ids.from_component.state = 'normal'
        self.ids.from_user.state = 'normal'
        self.ids.from_file.state = 'down'
        self.ids.outputs_list.clear_widgets()
        self.ids.selected_output.text = 'select file'
        root = tk.Tk()
        root.withdraw()
        file_path = filedialog.askopenfilename()
        self.user_selected = True
        self.ids.from_component.state = 'normal'
        self.ids.from_user.state = 'down'
        self.ids.from_file.state = 'normal'
        if len(file_path) == 0:
            print('empty path')
            return
        print(file_path)
        self.ids.input_value.text = file_path_text + file_path
        self.change_input_value(file_path_text + file_path)


    def set_values_to_default(self):
        self.ids.input_value.text = self.ids.input_value.default_text
        self.ids.input_description.text = self.ids.input_description.default_text

    def change_input_value(self, text):
        # for comp_widget in self.ids.main_canvas.children:
        #     if not (comp_widget.id == 'start_button' or comp_widget.id is None):
        #         if comp_widget.index_number == self.current_comp_id_number:
        #             current_widget = comp_widget
        #             break
        # component_inputs = [comp.inputs for comp in self.components_list if
        #                     comp.component_name == current_widget.name].__getitem__(0)
        try:
            for input in self.current_component.inputs:
                if input.label == self.current_input.label:
                    input.value = text
                    break
            self.populate_inputs_list(self.current_component)
        except:
            self.ids.input_value.text = 'Error!'

    def on_enter(self, text):
        print('User pressed enter in', text)
        self.ids.input_value.text = 'Value:\n' + text
        self.change_input_value(text)
        self.ids.user_text_input.text = ''

    def return_component_line(self, value):
        # self.current_component.name + '   ' + str(self.current_component.index_number)
        #
        # str(output_button.text)

        value_parts = value.split('\noutput: ')
        comp_label, index = value_parts[0].replace('component: ', '').strip().split('   ')
        output_name = value_parts[1].strip()
        output_index = -1
        Break = False
        for widget in self.ids.main_canvas.children[::-1]:
            if isinstance(widget, CenterComponent):
                if widget.name == comp_label and widget.index_number == int(index):
                    comp_name = widget.real_name
                    for tmp_index, output in enumerate(widget.outputs_list):
                        if output_name == output:
                            output_index = tmp_index
                            Break = True
                            break
            if Break:
                break
        index = int(index)
        if comp_name == 'variable':
            return '__variable__', str(widget.inputs[0].value)
        return comp_name, str(index), str(output_index)

    def do_unzoom(self):
        global  g_zoom_level
        g_zoom_level *= zoom_factor
        for widget in self.ids.main_canvas.children[::-1]:
            if isinstance(widget, CenterComponent):
                widget.unzoom_level = g_zoom_level
                widget.do_layout()
        self.ids.main_canvas.canvas.ask_update()

    def do_zoom(self):
        global  g_zoom_level
        g_zoom_level /= zoom_factor
        for widget in self.ids.main_canvas.children[::-1]:
            if isinstance(widget, CenterComponent):
                widget.unzoom_level = g_zoom_level
                widget.do_layout()
        self.ids.main_canvas.canvas.ask_update()

    def run_pressed(self):
        with io.open(GUI_output_path, "w", encoding="utf-8") as GUI_output:
            print('==================')
            for widget in self.ids.main_canvas.children[::-1]:
                if isinstance(widget, CenterComponent):
                    prefix = 'component' + line_components_separator
                    index_number = line_components_separator + str(widget.index_number)
                    if widget.real_name in special_comps_list:
                        prefix = ''
                        index_number = ''
                    line = prefix + widget.real_name + index_number
                    for input in widget.inputs:
                        tmp_value = input.value
                        try:
                            if input.value.startswith('component: '):
                                tmp_value = '$'.join(self.return_component_line(input.value))
                        except AttributeError:
                            pass
                        line = line + line_components_separator + str(tmp_value)
                    line += line_components_separator + 'parallel_state ' + str(widget.parallel_state)
                    print(line)
                    line += '\n'
                    GUI_output.write(line)
                # GUI_output.write(line)
        # GUI_output.close()
        print('GUI_to_code main call')
        GUI_to_code.main(GUI_output_path)
        # os.system(python_command + ' "' + GUI_to_code_path + '"')
        print('==================')

    def save_file(self, save_comps_path):
        list_to_dump = [self.current_comp_id_number]

        for widget in self.ids.main_canvas.children[::-1]:
            if isinstance(widget, CenterComponent):
                tmp_dict = dict()
                for attribute in attributes_to_copy:
                    try:
                        tmp_dict[attribute] = widget.__getattribute__(attribute)
                    except AttributeError:
                        print('Error found!')
                        pass
                list_to_dump.append(tmp_dict)
        try:
            pickle.dump(list_to_dump, open(save_comps_path, 'wb'))
        except FileNotFoundError:
            pass

    def change_index_of_outputs(self, component, add_index):
        new_inputs_list = []
        for input in component.inputs:
            try:
                if input.value.startswith('component: '):
                    value_parts = input.value.split('\noutput: ')
                    comp_label, index = value_parts[0].split('   ')
                    index = int(index)
                    index += add_index
                    value_parts[0] = '   '.join([comp_label, str(index)])
                    input.value = '\noutput: '.join(value_parts)
            except AttributeError:
                pass
            new_inputs_list.append(input)
        component.inputs = new_inputs_list
        return component

    def load_file(self, load_comps_path):
        try:
            list_from_dump = pickle.load(open(load_comps_path, "rb"))
            self.current_comp_id_number = max(self.current_comp_id_number, list_from_dump.pop(0))
            max_index = 0
            for widget_dict in list_from_dump:
                m_canvas = self.ids.main_canvas
                but = CenterComponent()
                but.bind(on_release=self.center_component_pressed)
                for name, value in widget_dict.items():
                    but.__setattr__(name, value)
                    print(name, value)
                but = self.change_index_of_outputs(but, self.current_comp_id_number)
                but.index_number += self.current_comp_id_number
                max_index = max(max_index, but.index_number)
                m_canvas.add_widget(but, self.selected_index)
                but.remove_component = self.remove_component
                but.ids.do_parallel.text = but.parallel_state_text()
            self.current_comp_id_number = max_index + 1
        except FileNotFoundError:
            pass

    def show_save(self):
        root = tk.Tk()
        root.withdraw()
        myFormats = [('Graspy files', '*.grp'), ('Any file', '*')]
        file_path = filedialog.asksaveasfilename(filetypes=myFormats)
        #file_path = wx_save_as_dialog()
        if file_path == None:
            return
        file_path += '.grp' if not file_path.endswith('.grp') else ''
        print(file_path)
        self.save_file(file_path)

    def show_load(self):
        root = tk.Tk()
        root.withdraw()
        myFormats = [('Graspy files', '*.grp'), ('Any file', '*')]
        file_path = filedialog.askopenfilename(filetypes=myFormats)
        #file_path = wx_open_dialog('*.grp')
        if file_path == None:
            return
        print(file_path)
        self.load_file(file_path)


class GUI_mainApp(App):
    def build(self):
        self.title = program_name
        return MainScreen()


def components_from_object(object):
    print(type(object))
    files_str = object.get_component_files()
    print(files_str)
    files_separator = "===="
    files_lines = files_str.split("\n")
    fout = None
    for line in files_lines:
        if "component_filename" in line.strip():
            file_str = ""
            filename = line.strip().split(":")
            filename = filename[1]
            filepath = os.path.join(comp_files_path, filename)
        elif line.strip() == files_separator.strip():
            fout = open(filepath, "w")
            file_str = file_str.split("\n")[:-1]
            file_str = "\n".join(file_str)
            fout.write(file_str)
            fout.close()
            file_str = ""
        elif line.strip() == "":
            continue
        else:
            file_str += line + "\n"


def update_objects_uris(objects_uris_path, port):
    s = socket(AF_INET, SOCK_DGRAM)  # create UDP socket
    s.bind(('', port))
    s.settimeout(4.0)
    uris_set = set()
    start_time = time.time()
    while (time.time() - start_time) < seconds_to_listen:
        try:
            data, addr = s.recvfrom(1024)  # wait for a packet
        except:
            continue
        if data.startswith(bytes(MAGIC, 'utf8')):
            tmp_uri = bytes.decode(data[len(MAGIC):]).strip()
            short_uri = tmp_uri.strip().split('$$')[1]
            tmp_object = Pyro4.Proxy(short_uri)
            tmp_object.stop_broadcast()
            uris_set.add(tmp_uri)
            print("got service announcement from", data[len(MAGIC):])

    if len(uris_set) > 0:
        string_to_write = '\n'.join(uris_set)
        print(string_to_write)
        with open(objects_uris_path, 'w') as f:
            f.write(string_to_write)


def retrieve_comp_files():
    broadcast_port = GUI_to_code.find_port(broadcast_port_label)
    print(broadcast_port)
    print(broadcast_port_label)

    MainScreen.delete_files_from_folder(comp_files_path)
    update_objects_uris(objects_uris_path, broadcast_port)
    objects_uris_file = open(objects_uris_path, encoding='utf8')
    for line in objects_uris_file:
        uri = line.strip().split('$$')[1]
        object = Pyro4.Proxy(uri)
        components_from_object(object)

if __name__ == '__main__':
    root = tk.Tk()
    root.withdraw()
    response = messagebox.askyesno("Update components", "Would you like to update component files?")
    # #response = wx_yes_no_dialog("Would you like to update component files?", "Update components")
    if response:
        retrieve_comp_files()
    GUI_mainApp().run()
