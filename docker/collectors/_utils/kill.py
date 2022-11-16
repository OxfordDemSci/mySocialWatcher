import os
import signal
import sys

name = "main.py"
if len(sys.argv) > 1:
    name = sys.argv[1]

for line in os.popen("ps ax | grep " + name + " | grep -v grep | grep -v kill.py"):
    print(line)
    fields = line.split()
    pid = fields[0]
    os.kill(int(pid), signal.SIGKILL)
