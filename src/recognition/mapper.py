import cv2, base64
import numpy as np
import os, sys
from PIL import Image
import zipfile

cascadepath = "frontalface.xml"
facecascade = cv2.CascadeClassifier(cascadepath)
recognizer  = cv2.createLBPHFaceRecognizer()
path        = 'faces16'

def unzip(source_filename, dest_dir):
    with zipfile.ZipFile(source_filename) as zf:
        for member in zf.infolist():
            # Path traversal defense copied from
            # http://hg.python.org/cpython/file/tip/Lib/http/server.py#l789
            words = member.filename.split('/')
            path = dest_dir
            for word in words[:-1]:
                drive, word = os.path.splitdrive(word)
                head, word = os.path.split(word)
                if word in (os.curdir, os.pardir, ''): continue
                path = os.path.join(path, word)
            zf.extract(member, path)


def get_images_and_labels(path):
    image_paths=[os.path.join(path,f) for f in os.listdir(path) if not f.endswith('.sad')]
    images = []
    labels = []
    for image_path in image_paths:
        image_pil = Image.open(image_path).convert('L')
        image = np.array(image_pil,'uint8')
        nbr = int(os.path.split(image_path)[1].split(".")[0].replace("subject",""))
        faces = facecascade.detectMultiScale(image)
        for (x,y,w,h) in faces:
            images.append(image[y:y+h,x:x+w])
            labels.append(nbr)
    return images, labels

#training the models
unzip('faces.zip','faces16')
images,labels = get_images_and_labels(path)
recognizer.train(images,np.array(labels))

def decode_base64_image(b64image):
    jpeg_image = b64image.decode('base64')
    jpeg_image_array = np.frombuffer(jpeg_image,np.uint8)
    image = cv2.imdecode(jpeg_image_array,1)
    return image

def encode_base64_image(image):
    ret,jpeg_image = cv2.imencode('.jpg',image)
    if ret:
        base64_image=base64.b64encode(jpeg_image)
        return base64_image
    return 

for line in sys.stdin:
    line = line.strip()
    timestamp = line.split("\t")[0]
    b64img = line.split("\t")[1]
    predict_image = decode_base64_image(b64img)
    predict_image = cv2.cvtColor(predict_image, cv2.COLOR_RGB2GRAY)
    faces = facecascade.detectMultiScale(predict_image)
    for (x,y,w,h) in faces:
        nbr_predicted, conf = recognizer.predict(predict_image[y:y+h,x:x+w])
        if int(conf) : #need to fine-tune
            print timestamp+"\t"+str(nbr_predicted)+"\t"+str(conf)

    

