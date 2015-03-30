#!/bin/bash
hadoop dfs -rmr /test-filter
hadoop jar /home/hadoop/hadoop-install/libexec/../contrib/streaming/hadoop-streaming-1.2.1.jar \
-D mapred.job.name="Test-filter" \
-files noise-filter.py \
-input /logs/noise.log \
-output /test-filter \
-mapper "/opt/miniconda/bin/python noise-filter.py" \
-reducer NONE \
