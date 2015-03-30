import sys
import numpy as np
import cv2
import base64

def encode(image):
    ret,jpeg=cv2.imencode('.jpg',image)
    if ret:
        base64i=base64.b64encode(jpeg)
        return base64i

def decode(image):
    jpeg = image.decode('base64')
    jpeg = np.frombuffer(jpeg,np.uint8)
    image = cv2.imdecode(jpeg,1)
    return image 

for line in sys.stdin:
    data = line.split("\t")
    image = data[1]
    img=decode(image)
    img_filtered = cv2.medianBlur(img,5)
    print data[0]+"\t"+encode(img_filtered)

