#!/bin/bash
hadoop dfs -rmr /test-classify
hadoop jar /home/hadoop/hadoop-install/libexec/../contrib/streaming/hadoop-streaming-1.2.1.jar \
-D mapred.job.name="Test-classify" \
-files docker-classify.py \
-input /logs/classify.log \
-output /test-classify \
-mapper "/opt/miniconda/bin/python docker-classify.py" \
-reducer NONE \
