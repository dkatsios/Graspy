# Import OpenCV
import cv2

def get_faces(filename):  
    face_cascade = cv2.CascadeClassifier('/usr/share/opencv/haarcascades/haarcascade_frontalface_default.xml')
    eye_cascade = cv2.CascadeClassifier('/usr/share/opencv/haarcascades/haarcascade_eye.xml')
    img = cv2.imread(filename)
    gray = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)


    faces = face_cascade.detectMultiScale(gray, 1.2, 5)
    print (len(faces))

get_faces('files/test.png')
