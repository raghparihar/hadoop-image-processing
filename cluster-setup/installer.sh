#!/bin/bash
#this script installs the needed dependencies and the docker image for running caffe
sudo apt-get update && sudo apt-get upgrade -y
sudo ln /dev/null /dev/raw1394
sudo apt-get install build-essential python-dev python-setuptools git vim htop g++ bzip2 -y
wget http://repo.continuum.io/miniconda/Miniconda-3.8.3-Linux-x86_64.sh
sudo bash Miniconda-3*.sh
sudo /opt/miniconda/bin/conda update conda -y
sudo /opt/miniconda/bin/conda install binstar -y
sudo /opt/miniconda/bin/conda install -c https://conda.binstar.org/menpo opencv -y
sudo /opt/miniconda/bin/conda install scikit-learn -y
sudo /opt/miniconda/bin/conda install PIL -y
#echo "deb http://http.debian.net/debian wheezy-backports main" >> /etc/apt/sources.list
sudo apt-get update
sudo apt-get install -t wheezy-backports linux-image-amd64 -y
curl -sSL https://get.docker.com/ | sh
sudo docker pull joemathai/caffe-cpu
rm Mini*
