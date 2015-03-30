#!/bin/bash

hadoop dfs -rmr /frames
hadoop dfs -mkdir /frames
hadoop dfs -cat $1 | /opt/miniconda/bin/python log_frame_bucket.py 
