#!/bin/bash
hadoop dfs -rmr /test-anomaly
hadoop jar /home/hadoop/hadoop-install/libexec/../contrib/streaming/hadoop-streaming-1.2.1.jar \
-D mapred.job.name="Test-Anomaly" \
-files anomaly.py,train.tsv \
-input /logs/anomaly.log \
-output /test-anomaly \
-mapper "/opt/miniconda/bin/python anomaly.py" \
-reducer NONE \
