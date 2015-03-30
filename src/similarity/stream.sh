#!/bin/bash
hadoop dfs -rmr /test-similarity
hadoop jar /home/hadoop/hadoop-install/libexec/../contrib/streaming/hadoop-streaming-1.2.1.jar \
-D mapred.job.name="Test-Similarity" \
-files similarity-mapper.py,similar_images.txt \
-input /logs/similarity.log \
-output /test-similarity \
-mapper "/opt/miniconda/bin/python similarity-mapper.py" \
-reducer NONE \
