import requests


def remote_upload(url, port, filename):
    url = url + ":" + str(port)
    
    try:
        files = {'file': open(filename, 'rb')}
        values = {}
        r = requests.post(url + "/upload", files=files, data=values)
        print(r)
    except:
        print("Could not send file")

    #r = requests.post(files=files, data=values)
