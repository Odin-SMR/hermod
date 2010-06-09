
from odin.config.database import connect
from os.path import dirname,basename,join
import os, stat, errno
import fuse
from fuse import Fuse





fuse.fuse_python_api = (0, 2)

hello_path = '/hello'
hello_path2 = '/hello2'
cal = ['/V-1','/V-6','/V-7']
keys = ['calversion','fmode']
hello_str = 'Hello World!\n'

def filelist(cal,fm):
    db = connect()
    cur = db.cursor()
    cur.execute('''
        SELECT l1g.filename FROM level1b_gem l1g join level1 l1 using (id) where freqmode=%s and calversion=%s limit 100;
        ''',(fm,cal))
    result = cur.fetchall()
    cur.close()
    db.close()
    return [basename(r[0]) for r in result]

class MyStat(fuse.Stat):
    def __init__(self):
        self.st_mode = 0
        self.st_ino = 0
        self.st_dev = 0
        self.st_nlink = 0
        self.st_uid = 507
        self.st_gid = 500
        self.st_size = 0
        self.st_atime = 0
        self.st_mtime = 0
        self.st_ctime = 0

def pathdepth(path):
    p = path
    if p.endswith('/'):
	p=p[:-1]
    out = len(p.split('/'))
    return out

def smrlist(path):
    cal = {'V-1':1,'V-6':6,'V-7':7}
    fm = {
	"SM_AC2a":1,
	"SM_AC2b":1,
	"SM_AC2ab":1,
	"SM_AC1e":2,
	"HM_AC1f":24,
	"IM_AC2a":8,
	"IM_AC2b":8,
	"IM_AC2ab":8,
	"IM_AC2c":17,
	"IM_AC1c":19,
	"IM_AC1de":21,
	"HM_AC1c":13,
	"HM_AC2c":14,
	"HM_AC2ab":22,
	"HM_AC1d":23,
	"HM_AC1e":23,
	"HM_AC1g":29,
	"HM_AC1e":29,
	"TM_ACs1":25,
	"TM_AOS1":26,
	"TM_ACs2":27,
	"TM_AOS2":28,
	"SM_FB":20,
        }
    if pathdepth(path)==1:
        return cal.keys()
    elif pathdepth(path)==2:
        return fm.keys()
    else:
	f = path.split('/')
        return filelist(cal[f[1]],fm[f[2]])


class HelloFS(Fuse):

    def getattr(self, path):
        st = MyStat()
        if pathdepth(path)<4 :
            st.st_mode = stat.S_IFDIR | 0755
            st.st_nlink = 2
	elif pathdepth(path)==4:
            st.st_mode = stat.S_IFREG | 0444
            st.st_nlink = 1
            st.st_size = len(hello_str)
        else:
            return -errno.ENOENT
        return st

    def readdir(self, path, offset):
        for r in ['.','..']+smrlist(path):
			yield fuse.Direntry(r)
		

    def open(self, path, flags):
        if pathdepth(path)!=4:
            return -errno.ENOENT
        accmode = os.O_RDONLY | os.O_WRONLY | os.O_RDWR
        if (flags & accmode) != os.O_RDONLY:
            return -errno.EACCES

    def read(self, path, size, offset):
	if pathdepth(path)!=4:
            return -errno.ENOENT
        slen = len(hello_str)
        if offset < slen:
            if offset + size > slen:
                size = slen - offset
            buf = hello_str[offset:offset+size]
        else:
            buf = ''
        return buf

def main():
    usage="""
Userspace hello example

""" + Fuse.fusage
    server = HelloFS(version="%prog " + fuse.__version__,
                     usage=usage,
                     dash_s_do='setsingle')

    server.parse(errex=1)
    server.main()

if __name__ == '__main__':
    main()
