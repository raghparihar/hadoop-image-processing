# Mapper for face-detecion using cascades
# Usage : 
import numpy as np
import sys
import base64
import cv2

cascade_path="frontalface.xml"

def encode_base64_image(image,timestamp):
    ret,jpeg_encoded_image = cv2.imencode('.jpg',image)
    if ret:
        base64_image=base64.b64encode(jpeg_encoded_image)
        print timestamp+"\t"+base64_image


def face_detect(image,timestamp):
    global cascade_path
    facecascade=cv2.CascadeClassifier(cascade_path)
    gray=cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    faces = facecascade.detectMultiScale(gray,1.3,5)
    count=0
    for (x,y,w,h) in faces:
        count+=1
        crop_img = image[y:y+h,x:x+w]
        #testing 
        #cv2.imshow("detected",crop_img)
        encode_base64_image(crop_img,timestamp+"-"+str(count))


def decode_base64_image(b64image):
    jpeg_image = b64image.decode('base64')
    jpeg_image_array = np.frombuffer(jpeg_image,np.uint8)
    image = cv2.imdecode(jpeg_image_array,1)
    #testing 
    #cv2.imshow("decoded",image)
    return image


# hadoop streaming input from STDIN
for line in sys.stdin:
    #remove any trailing spaces
    line=line.strip()
    data=line.split("\t")
    image=decode_base64_image(data[1])
    face_detect(image,data[0])

