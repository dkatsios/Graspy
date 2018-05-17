import os
# We'll render HTML templates and access data sent by POST
# using the request object from flask. Redirect and url_for
# will be used to redirect the user once the upload is done
# and send_from_directory will help us to send/show on the
# browser the file that the user just uploaded
from flask import Flask, render_template, request, redirect, url_for, send_from_directory
from werkzeug import secure_filename
import zipfile
import shutil

sep = os.sep
cwd = os.path.dirname(os.path.abspath(__file__))
ports_path = os.path.join(cwd, r'ports.conf')
port_label = 'master_object_main_code_port'
# Initialize the Flask application
app = Flask(__name__)

# This is the path to the upload directory
app.config['UPLOAD_FOLDER'] = './'
# These are the extension that we are accepting to be uploaded
app.config['ALLOWED_EXTENSIONS'] = set(['py', 'zip'])
temp_downloads_folder = os.path.join(cwd, "temp_downloads_folder")

Object_configuration_path = cwd + sep + r'Object_configuration.txt'

object_python_command = 'python command'

# For a given file, return whether it's an allowed type or not
def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1] in app.config['ALLOWED_EXTENSIONS']

# This route will show a form to perform an AJAX request
# jQuery is loaded to execute the request and update the
# value of the operation
@app.route('/')
def index():
    return render_template('index.html')


def return_object_python_command():
    command = "python3 "
    try:
        with open(os.path.join(cwd, Object_configuration_path)) as f:
            for line in f:
                if object_python_command in line:
                    command = line.split('=')[1].strip() + ' '
    except:
        pass
    return command


# Route that will process the file upload
@app.route('/upload', methods=['POST', 'GET'])
def upload():
    # Get the name of the uploaded file
    file = request.files['file']
    # Check if the file is one of the allowed types/extensions
    if file and allowed_file(file.filename):
        # Make the filename safe, remove unsupported chars
        filename = secure_filename(file.filename)
        # Move the file form the temporal folder to
        # the upload folder we setup
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(file_path)
        # Redirect the user to the uploaded_file route, which
        # will basicaly show on the browser the uploaded file
        ######
        # os command για να τρέξει το script στο Raspberry
        ######
        if filename.endswith(".py"):
            os.system(return_object_python_command() + file_path)
        elif filename.endswith(".zip"):
            print("elif")
            try:
                shutil.rmtree(temp_downloads_folder) 
            except:
                pass
            zip_ref = zipfile.ZipFile(file_path, 'r')
            zip_ref.extractall(temp_downloads_folder)
            zip_ref.close()
            #print(os.path.join(cwd,"Future.py"))
            #print(os.path.join(temp_downloads_folder, "Future.py"))
            shutil.copyfile(os.path.join(cwd,"Future.py"), os.path.join(temp_downloads_folder, "Future.py"))
            os.system(return_object_python_command() + os.path.join(temp_downloads_folder, "main_code.py"))

        return redirect(url_for('uploaded_file',
                                filename=filename))

    return ""

# This route is expecting a parameter containing the name
# of a file. Then it will locate that file on the upload
# directory and show it on the browser, so if the user uploads
# an image, that image is going to be show after the upload
@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'],
                               filename)


def find_port(port_label):
    with open(ports_path) as f:
        for line in f:
            if port_label in line:
                port = int(line.strip().split('$')[1].strip())
                return port

if __name__ == '__main__':
    port = int(find_port(port_label))
    app.run(
        host="0.0.0.0",
        port=int(find_port(port_label)),
        debug=True
    )
