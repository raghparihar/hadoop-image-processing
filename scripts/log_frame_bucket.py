#A script to convert logs in google bucket to corresponding frames
# Usage : gsutil cat location | ./script
import numpy as np
import base64
import sys
import os
import tempfile

project_bucket="demohdfs"

for line in sys.stdin:
    imgb64 = line.split("\t")[1]
    filename = line.split("\t")[0]+".jpg"
    jpeg = imgb64.decode('base64')
    with open("tempfile.jpeg","w") as outfile:
      outfile.write(jpeg)
    os.system('gsutil mv '+"tempfile.jpeg"+' gs://'+project_bucket+'/frames/'+filename)
    print "Success "+filename
