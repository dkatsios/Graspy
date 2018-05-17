import sys

import dlib
from skimage import io
import os

sep = os.sep
cwd = os.path.dirname(os.path.abspath(__file__))

def faces_detected_from_file(filename="test.png"):
    outputs = []

    filename = cwd + sep + "files" + sep + filename 
    detector = dlib.get_frontal_face_detector()
    print("Processing file: {}".format(filename))
    img = io.imread(filename)
    # The 1 in the second argument indicates that we should upsample the image
    # 1 time.  This will make everything bigger and allow us to detect more
    # faces.
    dets = detector(img, 1)   
    print("Number of faces detected: {}".format(len(dets)))
    num_of_faces = len(dets)
    are_detected_faces = False
    if  num_of_faces > 0:
        are_detected_faces = True
    outputs.append(num_of_faces)
    outputs.append(are_detected_faces)
    return outputs
