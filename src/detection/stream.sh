#!/bin/bash
hadoop dfs -rmr /test-facedetection
hadoop jar /home/hadoop/hadoop-install/libexec/../contrib/streaming/hadoop-streaming-1.2.1.jar \
-D mapred.job.name="Test-faces" \
-files faces.py,frontalface.xml \
-input /logs/ped.log \
-output /test-facedetection \
-mapper "/opt/miniconda/bin/python faces.py" \
-reducer NONE \
