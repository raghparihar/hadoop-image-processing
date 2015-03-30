import sys
import os

for line in sys.stdin:
    data=line.split("\t")
    data[0]=int(data[0].split(".")[0].replace('subject',''))
    if data[0] == int(data[1]):
        print 'SUCCESS\t'+line
