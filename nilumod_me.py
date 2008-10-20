#!/usr/bin/python

import time as t
import os.path as p
import popen2 as s
import sys
import os
import gzip

class weatherdata:
    '''
    Identifies if its possible to download data from a specific day. Generates 
    files if possible. Print filnames to stdout
    '''

    def __init__(self,dates):
        self.dates =[]
        self.okdates = []
        self.files = []
        for i in dates:
            try:
                a =t.strptime(i,'%y%m%d%H')
            except ValueError:
                pass
            else:
                self.dates.append(a)
        self.exists() 
        self.create()

    def exists(self):
        '''
        Check if nilu has the t106 data needed to extract our data.
        '''
        top = '/nadir/t106/'
        for date in self.dates:
            file = top + t.strftime('%Y/%m/nilut106.%y%m%d%H',date)
            if p.isfile(file):
                self.okdates.append(date)

    def create(self,template="%%s",mode=''):
        '''
        run met-mars command to create files
        stub to implement in derriving classes. here met-mars command will be 
        launched. put all created files in self.files
         '''
        for date in self.okdates:
            command = t.strftime(template,date) % mode
            file = p.join(p.expanduser('~'),'tmp',t.strftime('ecmwf%y%m%d.0%%s.gz',date)%mode)
            if p.exists(file):
                os.remove(file)
            sess = s.Popen3(command,True)
            g = gzip.GzipFile(file,'w')
            for line in sess.fromchild:
                g.write(line)
            status = sess.wait()
            g.close()
            if sess.childerr.readlines()==[]:
                print file

class weatherdata_T(weatherdata):
    '''
    Special case for creating the T files
    '''
    def create(self):
        '''
        run met-mars command to create files
        '''
        command_template = '/nadir/bin/met-mars %y %m %d %H -180 180 90 -90 1.125 p -1 %%s -'
        weatherdata.create(self,template=command_template,mode='T')

class weatherdata_Z(weatherdata):
    '''
    Special case for creating the Z files
    '''
    def create(self):
        '''
        run met-mars command to create files
        '''
        command_template = '/nadir/bin/met-mars %y %m %d %H -180 180 90 -90 1.125 p -1 %%s -'
        weatherdata.create(self,template=command_template,mode='Z')

class weatherdata_PV(weatherdata):
    '''
    Special case for creating the PV files
    '''
    def create(self):
        command_template = '/nadir/bin/met-mars %y %m %d %H -180 180 90 -90 1.125 th -1 %%s -'
        weatherdata.create(self,template=command_template,mode='PV')
        
### M&E
class weatherdata_U(weatherdata):
    '''
    Special case for creating the U files
    '''
    def create(self):
        '''
        run met-mars command to create files
        '''
        command_template = '/nadir/bin/met-mars %y %m %d %H -180 180 90 -90 1.125 th -1 %%s -'
        weatherdata.create(self,template=command_template,mode='U')

class weatherdata_V(weatherdata):
    '''
    Special case for creating the V files
    '''
    def create(self):
        '''
        run met-mars command to create files
        '''
        command_template = '/nadir/bin/met-mars %y %m %d %H -180 180 90 -90 1.125 th -1 %%s -'
        weatherdata.create(self,template=command_template,mode='V')
### M&E


def main():
    '''
    This is an example of how to use it
    '''
    #read argument list, if no given read stdin
    dates = sys.argv[1:]
    if dates==[]:
        while True:
            try:
                dates.append(raw_input())
            except EOFError:
                break
    #start pv,t,z,u,v file creation
    #t = weatherdata_T(dates)
    #z = weatherdata_Z(dates)
    #pv = weatherdata_PV(dates)
    ### M&E
    u = weatherdata_U(dates)
    #v = weatherdata_V(dates)
    ### M&E
if __name__=='__main__':
    main()
