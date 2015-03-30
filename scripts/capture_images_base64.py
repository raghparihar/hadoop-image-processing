#!/usr/bin/env python
# A Script to capture sequential frames and convert them into base64 log file.
# Usage : ./capture_images_base64.py log-filename

import numpy as np
import base64
import time
import cv2
import sys

if len(sys.argv)<2:
    print "Usage : ./capture_images_base64.py log-filename"
    sys.exit(0)
log_file = sys.argv[1]
cap = cv2.VideoCapture(1)
while True:
    #check if cap is open
    if not cap.isOpened():
        cap.open()

    ret, frame = cap.read()
    if ret:
        #testing purpose only
        cv2.imshow('frame',frame)
        _,encoded_image = cv2.imencode('.jpg',frame)
        base64_image = base64.b64encode(encoded_image)
        with open(log_file,"a") as outfile:
            #save as tsv
            line = str(int(time.time()*24))+"\t"+base64_image+"\n"
            outfile.write(line)
        # to quit enter q
        if cv2.waitKey(1) & 0xff == ord('q'):
            print 'Exit Normal (q)'
            break

cap.release()
cv2.destroyAllWindows()


            

