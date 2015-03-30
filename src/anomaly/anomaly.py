from sklearn import svm
import os,sys

def train_data_load():
    train_data=[]
    with open("train.tsv","r") as infile:
        for line in infile:
            data=line.split("\t")[0]
	    hrs=int(data.split("T")[1].split(":")[0])
 	    min=int(data.split("T")[1].split(":")[1])
	    sec=int(data.split("T")[1].split(":")[2].split(".")[0])
	    time=hrs+min/60
	    ped=int(data.split("-")[1])
	    train_data.append([time,ped])
    return train_data

for i in range(1000): #train for 1000 epoch
    train_data_load()
clf=svm.OneClassSVM()
clf.fit(train_data_load())

for line in sys.stdin:
    data=line.split("\t")[0]
    hrs=int(data.split("T")[1].split(":")[0])
    min=int(data.split("T")[1].split(":")[1])
    sec=int(data.split("T")[1].split(":")[2].split(".")[0])
    time=hrs+min/60
    ped=int(data.split("-")[1])
    if clf.predict([hrs,time]) > 0:
        print "NORMAL"+"\t0"+"\t"+data
    else:
        print "ANOMALY"+"\t"+str(clf.predict([hrs,time]))+"\t"+data



	    
	    
