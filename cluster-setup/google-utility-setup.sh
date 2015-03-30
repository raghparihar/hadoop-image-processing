#!/bin/bash
wget https://storage.googleapis.com/pub/gsutil.tar.gz
tar xfz gsutil.tar.gz -C $HOME
echo "export PATH=${PATH}:$HOME/gsutil" >> ~/.bashrc
#restart the terminal and configure the gsutil
source ~/.bashrc
gsutil update
curl https://sdk.cloud.google.com | bash
