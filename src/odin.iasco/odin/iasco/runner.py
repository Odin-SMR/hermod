"""
Example how to use addlevel3.py
"""

from subprocess import Popen,PIPE
from sys import stderr,stdout
from time import sleep
run = Popen(['/usr/local/Plone/zinstance/bin/zopepy','addlevel3.py'],stdin=PIPE,stdout=stdout,stderr=stderr)
for i in ['aoe','nth','aoeu']:
    print "adding",i
    run.stdin.write("%s\n"%i)
    sleep(10)
run.stdin.close()
run.wait()

