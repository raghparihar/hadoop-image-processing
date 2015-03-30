# use the docker image joemathai/caffe-cpu
# usage via pipes
from subprocess import Popen, PIPE
import os,sys

def kill_and_remove(ctr_name):
    for action in ('kill', 'rm'):
        p = Popen('sudo docker %s %s' % (action, ctr_name), shell=True,
                  stdout=PIPE, stderr=PIPE)
        if p.wait() != 0:
            raise RuntimeError(p.stderr.read())


def execute(code, arg=""):
    ctr_name = 'joemathai/caffe-cpu'
    p = Popen([
               'sudo','docker', 'run', ctr_name,
               'python',  code, arg],
              stdout=PIPE)
    out = p.stdout.read()

    if p.wait() == -9:  # Happens on timeout
        # We have to kill the container since it still runs
        # detached from Popen and we need to remove it after because
        # --rm is not working on killed containers
        kill_and_remove(ctr_name)

    return out

#print  execute("print 'test1'")
for line in sys.stdin:
  time = line.split('\t')[0]
  arg = line.split("\t")[1]
  print time+"\t"+str(execute("/home/classify.py",arg).split("\n")[-3:-2])
  
