#!/bin/bash
hadoop dfs -rmr /test-recognition
hadoop jar /home/hadoop/hadoop-install/libexec/../contrib/streaming/hadoop-streaming-1.2.1.jar \
-files mapper.py,reducer.py,frontalface.xml,faces.zip \
-input /logs/yale.log \
-output /test-recognition \
-mapper "/opt/miniconda/bin/python mapper.py" \
-reducer "/opt/miniconda/bin/python reducer.py" \  # remove the reducer for other inputs 

