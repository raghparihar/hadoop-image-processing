#!/bin/bash
hadoop dfs -rmr /test-people
hadoop jar /home/hadoop/hadoop-install/libexec/../contrib/streaming/hadoop-streaming-1.2.1.jar \
-D mapred.job.name="Test-people" \
-files people.py \
-input /logs/ped.log \
-output /test-people \
-mapper "/opt/miniconda/bin/python people.py" \
-reducer NONE \
