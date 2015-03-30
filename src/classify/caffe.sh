#!/bin/bash
hadoop dfs -rmr /test-classify
hadoop dfs -cat /logs/classify.log | /opt/miniconda/bin/python docker_caffe.py > out
hadoop dfs -mkdir /test-classify
hadoop dfs -put out /test-classify/part-00000.txt 
rm out
