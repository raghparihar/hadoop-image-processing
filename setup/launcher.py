#!/usr/bin/env python
#This script sets up a hadoop-spark cluster on Google Compute Engine
#usage: launcher.py <project> <no-slaves> <slave-type> <master-type> <identity-file> <zone> <cluster-name>

from __future__ import with_statement
import logging
import os
import pipes
import random
import shutil
import subprocess
import sys 
import tempfile
import time
import commands
import urllib2
from optparse import OptionParser
from sys import stderr
import shlex
import getpass
import threading
import json

identity_file=""
slave_no=""
slave_type=""
master_type=""
zone=""
cluster_name=""
username=""
project=""

def read_args():
  global identity_file
  global slave_type
  global slave_no
  global master_type
  global zone
  global cluster_name
  global username
  global project
  if len(sys.argv)==8:
    project = sys.argv[1]
    slave_no = int(sys.argv[2])
    slave_type=sys.argv[3]
    master_type=sys.argv[4]
    identity_file=sys.argv[5]
    zone=sys.argv[6]
    cluster_name=sys.argv[7]
    username=getpass.getuser()
  else:
    print "\nERROR : wrong usage of the launcher !"
    sys.exit(0)
  
def check_gcloud():
  myexec = "gcloud"
  print "checking gcloud ..."
  try:
    subprocess.call([myexec,"info"])
  except OSError:
    print "Error: gcloud executable not found"
    sys.exit(1)

def setup_network():
  print "setting up Network & Firewall Entries"
  try:
    command='gcloud compute --project='+project+' networks create "'+cluster_name+'-network" --range "10.240.0.0/16"'
    command = shlex.split(command)
    subprocess.call(command)
    command = 'gcloud compute firewall-rules create internal --network ' + cluster_name + '-network --allow tcp udp icmp --project '+ project
    command = shlex.split(command)
    subprocess.call(command)
  except OSError:
    print "Error : Failed to setup Network & firewall-rules"
    sys.exit(1)

def launch_master_slaves():
  print "launching master and slave nodes ..."
  command = 'gcloud compute --project "' + project + '" instances create "' + cluster_name + '-master" --zone "' + zone + '" --machine-type "' + master_type + '" --network "' + cluster_name + '-network" --maintenance-policy "MIGRATE" --scopes "https://www.googleapis.com/auth/devstorage.read_only" --image "https://www.googleapis.com/compute/v1/projects/centos-cloud/global/images/centos-6-v20141218" --boot-disk-type "pd-standard" --boot-disk-device-name "' + cluster_name + '-md"'
  command = shlex.split(command)
  subprocess.call(command)
  for s_id in range(1,slave_no+1):
    command='gcloud compute --project "' + project + '" instances create "' + cluster_name + '-slave' + str(s_id) + '" --zone "' + zone + '" --machine-type "' + slave_type + '" --network "' + cluster_name + '-network" --maintenance-policy "MIGRATE" --scopes "https://www.googleapis.com/auth/devstorage.read_only" --image "https://www.googleapis.com/compute/v1/projects/centos-cloud/global/images/centos-6-v20141218" --boot-disk-type "pd-standard" --boot-disk-device-name "' + cluster_name + '-s' + str(s_id) + 'd"'
    command = shlex.split(command)
    subprocess.call(command)

def launch_cluster():
  print "Creating cluster ..."
  setup_network()
  launch_master_slaves()

def get_cluster_ips():
  command = 'gcloud compute --project ' + project + ' instances list --format json'
  output = subprocess.check_output(command,shell=True)
  data = json.loads(output)
  master_nodes=[]
  slave_nodes=[]
  for instance in data:
    try:
      host_name = instance['name']
      host_ip = instance['networkInterfaces'][0]['accessConfigs'][0]['natIP']
      if host_name == cluster_name+'-master':
        master_nodes.append(host_ip)
      elif cluster_name+'-slave' in host_name:
        slave_nodes.append(host_ip)
    except:
      pass
  return (master_nodes,slave_nodes)


def enable_sudo(master,command):
  os.system("ssh -i " + identity_file + " -t -o 'UserKnownHostsFile=/dev/null' -o 'CheckHostIP=no' -o 'StrictHostKeyChecking no' "+ username + "@" + master + " '" + command + "'")

def ssh_thread(host,command):
  enable_sudo(host,command)

def install_tools(master_nodes,slave_nodes):
  print "installing java and other tools..."
  master = master_nodes[0]
  master_thread = threading.Thread(target=ssh_thread, args=(master,"sudo yum install -y java-1.7.0-openjdk;sudo yum install -y java-1.7.0-openjdk-devel;sudo yum groupinstall \'Development Tools\' -y"))
  master_thread.start()
  for slave in slave_nodes:
    slave_thread = threading.Thread(target=ssh_thread, args=(slave,"sudo yum install -y java-1.7.0-openjdk;sudo yum install -y java-1.7.0-openjdk-devel;sudo yum groupinstall \'Development Tools\' -y"))
    slave_thread.start()
  slave_thread.join()
  master_thread.join()

def deploy_keys(master_nodes,slave_nodes):
  print "generating SSH keys on Master"
  key_file = os.path.basename(identity_file)
  master=master_nodes[0]
  ssh_command(master,"ssh-keygen -q -t rsa -N \"\" -f ~/.ssh/id_rsa")
  ssh_command(master,"cat ~/.ssh/id_rsa.pub >> ~/.ssh/authorized_keys")
  os.system("scp -i " + identity_file + " -oUserKnownHostsFile=/dev/null -oCheckHostIP=no -oStrictHostKeyChecking=no -o 'StrictHostKeyChecking no' "+ identity_file + " " + username + "@" + master + ":")
  ssh_command(master,"chmod 600 "+key_file)
  ssh_command(master,"tar czf .ssh.tgz .ssh")
  ssh_command(master,"ssh-keyscan -H $(/sbin/ifconfig eth0 | grep \"inet addr:\" | cut -d: -f2 | cut -d\" \" -f1) >> ~/.ssh/known_hosts")
  ssh_command(master,"ssh-keyscan -H $(cat /etc/hosts | grep $(/sbin/ifconfig eth0 | grep \"inet addr:\" | cut -d: -f2 | cut -d\" \" -f1) | cut -d\" \" -f2) >> ~/.ssh/known_hosts")
  print "transferring SSH keys to slaves"
  for slave in slave_nodes:
    print commands.getstatusoutput("ssh -i " + identity_file + " -oUserKnownHostsFile=/dev/null -oCheckHostIP=no -oStrictHostKeyChecking=no " + username + "@" + master + " 'scp -i " + key_file + " -oStrictHostKeyChecking=no .ssh.tgz " + username +"@" + slave + ":'")
    ssh_command(slave,"tar xzf .ssh.tgz")
    ssh_command(master,"ssh-keyscan -H " + slave + " >> ~/.ssh/known_hosts")
    ssh_command(slave,"ssh-keyscan -H $(cat /etc/hosts | grep $(/sbin/ifconfig eth0 | grep \"inet addr:\" | cut -d: -f2 | cut -d\" \" -f1) | cut -d\" \" -f2) >> ~/.ssh/known_hosts")
    ssh_command(slave,"ssh-keyscan -H $(/sbin/ifconfig eth0 | grep \"inet addr:\" | cut -d: -f2 | cut -d\" \" -f1) >> ~/.ssh/known_hosts")

def attach_drives(master_nodes,slave_nodes):
  print "adding storage to nodes ..."
  master=master_nodes[0]
  command='gcloud compute --project="' + project + '" disks create "' + cluster_name + '-m-disk" --size 500GB --type "pd-standard" --zone ' + zone
  command=shlex.split(command)
  subprocess.call(command)
  command = 'gcloud compute --project="' + project + '" instances attach-disk ' + cluster_name + '-master --device-name "' + cluster_name + '-m-disk" --disk ' + cluster_name + '-m-disk --zone ' + zone
  command=shlex.split(command)
  master_thread = threading.Thread(target=ssh_thread,args=(master,"sudo mkfs.ext3 /dev/disk/by-id/google-"+ cluster_name + "-m-disk " + " -F < /dev/null"))
  master_thread.start()
  i=1
  for slave in slave_nodes:
    master=slave
    command='gcloud compute --project="' + project + '" disks create "' + cluster_name + '-s' + str(i) + '-disk" --size 500GB --type "pd-standard" --zone ' + zone
    command=shlex.split(command)
    subprocess.call(command)
    command = 'gcloud compute --project="' + project + '" instances attach-disk ' + cluster_name + '-slave' + str(i) + ' --disk ' + cluster_name + '-s' + str(i) + '-disk --device-name "' + cluster_name + '-s' + str(i) + '-disk" --zone ' + zone
    command=shlex.split(command)
    subprocess.call(command)
    slave_thread = threading.Thread(target=ssh_thread, args=(slave,"sudo mkfs.ext3 /dev/disk/by-id/google-" + cluster_name + "-s" + str(i) + "-disk -F < /dev/null"))
    slave_thread.start()
    i+=1
  slave_thread.join()
  master_thread.join()
  enable_sudo(master_nodes[0],"sudo mount /dev/disk/by-id/google-"+ cluster_name + "-m-disk /mnt")
  enable_sudo(master_nodes[0],"sudo chown " + username + ":" + username + " /mnt")
  i=1
  for slave in slave_nodes:
    enable_sudo(slave,"sudo mount /dev/disk/by-id/google-"+ cluster_name + "-s" + str(i) +"-disk /mnt")
    enable_sudo(slave,"sudo chown " + username + ":" + username + " /mnt")
    i+=1
  print 'all volumes mounted and available at /mnt'


def setup_spark(master_nodes,slave_nodes):
  print "installing spark"
  master=master_nodes[0]
  ssh_command(master,"rm -fr december")
  ssh_command(master,"mkdir december")
  ssh_command(master,"cd december;wget https://s3.amazonaws.com/sigmoidanalytics-builds/spark/1.2.0/spark-1.2.0-bin-cdh4.tgz")
  ssh_command(master,"cd december;wget https://s3.amazonaws.com/sigmoidanalytics-builds/spark/0.9.1/gce/scala.tgz")
  ssh_command(master,"cd december;tar zxf spark-1.2.0-bin-cdh4.tgz;rm spark-1.2.0-bin-cdh4.tgz")
  ssh_command(master,"cd december;tar zxf scala.tgz;rm scala.tgz")
  ssh_command(master,"cd december;cd spark-1.2.0-bin-cdh4/conf;cp spark-env.sh.template spark-env.sh")
  ssh_command(master,"cd december;cd spark-1.2.0-bin-cdh4/conf;echo 'export SCALA_HOME=\"/home/`whoami`/december/scala\"' >> spark-env.sh")
  ssh_command(master,"cd december;cd spark-1.2.0-bin-cdh4/conf;echo 'export SPARK_MEM=2454m' >> spark-env.sh")
  ssh_command(master,"cd december;cd spark-1.2.0-bin-cdh4/conf;echo \"SPARK_JAVA_OPTS+=\\\" -Dspark.local.dir=/mnt/spark \\\"\" >> spark-env.sh")
  ssh_command(master,"cd december;cd spark-1.2.0-bin-cdh4/conf;echo 'export SPARK_JAVA_OPTS' >> spark-env.sh")
  ssh_command(master,"cd december;cd spark-1.2.0-bin-cdh4/conf;echo 'export SPARK_MASTER_IP=PUT_MASTER_IP_HERE' >> spark-env.sh")
  ssh_command(master,"cd december;cd spark-1.2.0-bin-cdh4/conf;echo 'export MASTER=spark://PUT_MASTER_IP_HERE:7077' >> spark-env.sh")
  ssh_command(master,"cd december;cd spark-1.2.0-bin-cdh4/conf;echo 'export JAVA_HOME=/usr/lib/jvm/java-1.7.0-openjdk-1.7.0.71.x86_64' >> spark-env.sh")
  for slave in slave_nodes:
    ssh_command(master,"echo "+slave+" >> december/spark-1.2.0-bin-cdh4/conf/slaves")
  ssh_command(master,"sed -i \"s/PUT_MASTER_IP_HERE/$(/sbin/ifconfig eth0 | grep \"inet addr:\" | cut -d: -f2 | cut -d\" \" -f1)/g\" december/spark-1.2.0-bin-cdh4/conf/spark-env.sh")
  ssh_command(master,"chmod +x december/spark-1.2.0-bin-cdh4/conf/spark-env.sh")
  enable_sudo(master,"sudo chown " + username + ":" + username + " /mnt")
  i=1
  for slave in slave_nodes:
    enable_sudo(slave,"sudo chown " + username + ":" + username + " /mnt")
  for slave in slave_nodes:
    ssh_command(master,"rsync -za /home/" + username + "/december " + slave + ":")
    ssh_command(slave,"mkdir /mnt/spark")
  ssh_command(master,"mkdir /mnt/spark")
  ssh_command(master,"december/spark-1.2.0-bin-cdh4/sbin/start-all.sh")

def setup_hadoop():
  master=master_nodes[0]
  ssh_command(master,"cd december;wget https://s3.amazonaws.com/sigmoidanalytics-builds/hadoop/hadoop-2.0.0-cdh4.2.0.tar.gz")
  ssh_command(master,"cd december;tar zxf hadoop-2.0.0-cdh4.2.0.tar.gz")
  ssh_command(master,"cd december;rm hadoop-2.0.0-cdh4.2.0.tar.gz")
  ssh_command(master,"echo '#HADOOP_CONFS' >> .bashrc")
  ssh_command(master,"echo 'export JAVA_HOME=/usr/lib/jvm/java-1.7.0-openjdk-1.7.0.71.x86_64' >> .bashrc")
  ssh_command(master,"echo 'export HADOOP_INSTALL=/home/`whoami`/december/hadoop-2.0.0-cdh4.2.0' >> .bashrc")
  ssh_command(master,"echo 'export PATH=$PATH:\$HADOOP_INSTALL/bin' >> .bashrc")
  ssh_command(master,"echo 'export PATH=$PATH:\$HADOOP_INSTALL/sbin' >> .bashrc")
  ssh_command(master,"echo 'export HADOOP_MAPRED_HOME=\$HADOOP_INSTALL' >> .bashrc")
  ssh_command(master,"echo 'export HADOOP_COMMON_HOME=\$HADOOP_INSTALL' >> .bashrc")
  ssh_command(master,"echo 'export HADOOP_HDFS_HOME=\$HADOOP_INSTALL' >> .bashrc")
  ssh_command(master,"echo 'export YARN_HOME=\$HADOOP_INSTALL' >> .bashrc")
  ssh_command(master,"cd december/hadoop-2.0.0-cdh4.2.0;rm etc/hadoop/core-site.xml")
  ssh_command(master,"cd december/hadoop-2.0.0-cdh4.2.0;rm etc/hadoop/yarn-site.xml")
  ssh_command(master,"cd december/hadoop-2.0.0-cdh4.2.0;rm etc/hadoop/hdfs-site.xml")
  ssh_command(master,"cd december/hadoop-2.0.0-cdh4.2.0/etc/hadoop/;wget https://s3.amazonaws.com/sigmoidanalytics-builds/spark/0.9.1/gce/configs/core-site.xml")
  ssh_command(master,"cd december/hadoop-2.0.0-cdh4.2.0/etc/hadoop/;wget https://s3.amazonaws.com/sigmoidanalytics-builds/spark/0.9.1/gce/configs/hdfs-site.xml")
  ssh_command(master,"cd december/hadoop-2.0.0-cdh4.2.0/etc/hadoop/;wget https://s3.amazonaws.com/sigmoidanalytics-builds/spark/0.9.1/gce/configs/mapred-site.xml")
  ssh_command(master,"cd december/hadoop-2.0.0-cdh4.2.0/etc/hadoop/;wget https://s3.amazonaws.com/sigmoidanalytics-builds/spark/0.9.1/gce/configs/yarn-site.xml")
  ssh_command(master,"sed -i \"s/PUT-MASTER-IP/$(/sbin/ifconfig eth0 | grep \"inet addr:\" | cut -d: -f2 | cut -d\" \" -f1)/g\" december/hadoop-2.0.0-cdh4.2.0/etc/hadoop/core-site.xml")
  ssh_command(master,"mkdir -p /mnt/hadoop/hdfs/namenode;mkdir -p /mnt/hadoop/hdfs/datanode")
  ssh_command(master,"cd december/hadoop-2.0.0-cdh4.2.0/etc/hadoop/;rm slaves")
  for slave in slave_nodes:
    ssh_command(master,"cd december/hadoop-2.0.0-cdh4.2.0/etc/hadoop/;echo " + slave + " >> slaves")
  for slave in slave_nodes:
    ssh_command(master,"rsync -za /home/" + username + "/december " + slave + ":")
    ssh_command(slave,"mkdir -p /mnt/hadoop/hdfs/namenode;mkdir -p /mnt/hadoop/hdfs/datanode")
    ssh_command(master,"rsync -za /home/" + username + "/.bashrc " + slave + ":")
  ssh_command(master,"december/hadoop-2.0.0-cdh4.2.0/bin/hdfs namenode -format")
  print "starting dfs..."
  ssh_command(master,"december/hadoop-2.0.0-cdh4.2.0/sbin/start-dfs.sh")

def real_main():
  print " script Launched ! "
  read_args()
  check_gcloud()
  launch_cluster()
  #wait for the cluster to boot
  print "Waiting for 2mins for cluster to boot..."
  time.sleep(120)
  (master_nodes,slave_nodes)=get_cluster_ips()
  install_tools(master_nodes,slave_nodes)
  deploy_keys(master_nodes,slave_nodes)
  attach_drives(master_nodes,slave_nodes)
  setup_spark(master_nodes,slave_nodes)
  setup_hadoop(master_nodes,slave_nodes)
  print "\n\nSpark Master Started, WebUI available at : http://" + master_nodes[0] + ":8080"

def main():
  try:
    real_main()
  except Exception as e:
    print >> stderr, "\nError !!!!\n",e
if __name__ == "__main__":
  main()
