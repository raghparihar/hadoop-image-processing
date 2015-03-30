import numpy as np
import cv2
import os, sys
import glob,base64

if len(sys.argv)<2:
    print "Usage : ./script dir"
    sys.exit(0)

os.chdir(sys.argv[1])
for file in glob.glob('*.jpg'):
    image = cv2.imread(file)
    cv2.imshow('sdf',image)
    print 'processing '+file
    _,encoded_image = cv2.imencode('.jpg',image)
    base64_image = base64.b64encode(encoded_image)
    with open(os.path.join('..','b64.log'),'a') as outfile:
        filename = file.split('.')[0]
        line = filename+"\t"+base64_image+"\n"
        outfile.write(line)

