#!/usr/bin/env python
#Usage : ./mp4_base64_converter.py filename.mp4
import os
import sys
import cv2
import datetime
import base64

vidcap = cv2.VideoCapture(sys.argv[1])
success, image = vidcap.read()
fps=int(vidcap.get(cv2.cv.CV_CAP_PROP_FPS))
count = 0
os.mkdir("Frames-"+sys.argv[1].split(".")[0])
while success:
    count+=1
    success, image = vidcap.read()
    if count%(fps-1)==0 and image is not None:
      ftime=str(datetime.datetime.now().isoformat())
      cv2.imwrite(os.path.join("Frames-"+sys.argv[1].split(".")[0],ftime+".jpg"), image)
      ret,jpeg_encoded_image=cv2.imencode('.jpg',image)
      if ret:
        base64_encoded_image=base64.b64encode(jpeg_encoded_image)
        with open(os.path.join("Frames-"+sys.argv[1].split(".")[0],sys.argv[1].split(".")[0]+"-logs.txt"),"a") as outfile:
          line=ftime+"\t"+base64_encoded_image+"\n"
          outfile.write(line)
      print "writing ",ftime
