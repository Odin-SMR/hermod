import numpy as n
from numpy.random import rand 
import os
from sys import argv
import gzip
from tempfile import TemporaryFile,NamedTemporaryFile


def readecmwf(filename):
    if filename[-2:]=='gz' :
        f = NamedTemporaryFile()
        command= 'gunzip -c '+filename+' > ' + f.name
        print command
        os.system(command)
        f=file(f.name)
    else:
        f=file(filename,'r')
        
    print f
    a=f.readline().split()
    print a
    for i in range(int(a[0])-1) :
      f.readline()

    lats=n.arange(90,-90.1,-1.125)
    longs=n.arange(-180,180,1.125)
    nlevels=150
    data=n.zeros((nlevels,161,320))
    level=n.zeros((nlevels,1))
    i=0
    while f.readline()!='':
        a = n.fromfile(f,dtype=int,sep='    ',count=320*161)
        data[i,:,:]=a.reshape(161,320)
        i=i+1
    level=level[0:i-1]
    data=data[0:i-1,:,:]
    f.close()
    return level,data

if __name__=="__main__":
    if len(argv)==2:
        readecmwf(argv[1])
        

