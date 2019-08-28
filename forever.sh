#!/usr/bin/python
from subprocess import Popen
import sys

filename = sys.argv[1]
while True:
    print("\nStarting " + filename)
    p = Popen("python3 bot.py -l -d 10 30", shell=True)
    p.wait()
