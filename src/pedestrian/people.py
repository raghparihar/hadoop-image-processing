import numpy as np
import cv2
import os,sys
import base64

hog = cv2.HOGDescriptor()
hog.setSVMDetector(cv2.HOGDescriptor_getDefaultPeopleDetector())

def encode_base64_image(image):
    ret,jpeg_encoded_image = cv2.imencode('.jpg',image)
    if ret:
        base64_image=base64.b64encode(jpeg_encoded_image)
        return base64_image

def decode_base64_image(b64image):
    jpeg_image = b64image.decode('base64')
    jpeg_image_array = np.frombuffer(jpeg_image,np.uint8)
    image = cv2.imdecode(jpeg_image_array,1)
    return image

def inside(r, q):
    rx,ry,rw,rh = r
    qx,qy,qw,qh = q
    return rx > qx and ry > qy and rx+rw < qx+qw and ry+rh < qy+qh

def draw_detection(img,rects,thickness = 1):
    for x,y,w,h in rects:
        pad_w,pad_h = int(0.15*w),int(0.05*h)
        cv2.rectangle(img, (x+pad_w, y+pad_h), (x+w-pad_w, y+h-pad_h), (0, 255, 0), thickness)


for line in sys.stdin:
    line = line.strip()
    timestamp = line.split("\t")[0]
    image = decode_base64_image(line.split("\t")[1])
    found, w = hog.detectMultiScale(image, winStride=(8,8), padding=(32,32), scale=1.05 )
    found_filtered = []
    for ri,r in enumerate(found):
        for qi,q in enumerate(found):
            if ri != qi and inside(r,q):
                break
            else:
                found_filtered.append(r)
    draw_detection(image,found_filtered,3)
    #cv2.imshow('',image)
    #cv2.waitKey(0)
    print timestamp+"-"+str(len(found_filtered))+"\t"+encode_base64_image(image)


