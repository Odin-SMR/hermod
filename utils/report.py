#!/usr/bin/python2.5


"""
This module creates database reports.
"""

from MySQLdb import connect
from hermod.hermodBase import connection_str
from sys import argv
from numpy import histogram,array,arange
import matplotlib.pyplot as plt
#import bar,xticks,show,title,legend,ylabel,xlabel,Figure
TABLES = { 
        'ref':'reference_orbit',
        'l0':'level0_raw',
        'l1':'level1',
        'l2':'level2files',
        'mod':'Aero',
        'ver':'versions',
        'sta':'status',
        }


def missing_l0(start,stop):
    """
    List all possible orbits agains Level0.
    """
    
    db = connect(**connection_str)
    cur = db.cursor()
    cur.execute('''
        select orbit,setup
        from %(ref)s as r
        left join %(l0)s as l0
            on ( floor(start_orbit)<=orbit and floor(stop_orbit)>=orbit )
        where orbit>%%s and orbit<%%s
        ''' %TABLES,(start,stop))
    for i in cur:
        print i

def l0_orbits(setup='S.*1A'):
    db = connect(**connection_str)
    cur = db.cursor()
    status = cur.execute('''
        select r.orbit
        from %(ref)s as r
        join %(l0)s as l0
            on ( floor(l0.start_orbit)<=r.orbit 
                and floor(l0.stop_orbit)>=r.orbit )
        where l0.setup regexp  %%s
        ''' %TABLES,(setup,))
    a = cur.fetchall()
    arr = array(a,dtype=int)
    cur.close
    db.close()
    return arr.squeeze()



def missing_l1(start,stop):
    db = connect(**connection_str)
    cur = db.cursor()
    cur.execute('''
        select r.orbit,setup,backend,freqmode,calversion
        from %(ref)s as r
        left join %(l0)s as l0
            on ( floor(start_orbit)<=r.orbit and floor(stop_orbit)>=r.orbit )
        left join %(l1)s as l1
            on ( r.orbit=l1.orbit )
        where r.orbit>%%s and r.orbit<%%s
        ''' %TABLES,(start,stop))
    for i in cur:
        print i

def l1_orbits(setup='S.*1A',backend='AC2',calversion=6):
    db = connect(**connection_str)
    cur = db.cursor()
    cur.execute('''
        select r.orbit
        from %(ref)s as r
        join %(l0)s as l0
            on ( floor(l0.start_orbit)<=r.orbit 
                and floor(l0.stop_orbit)>=r.orbit )
        join %(l1)s as l1 using (orbit)
        join %(sta)s as s on (l1.id=s.id)
        where l0.setup regexp  %%s and l1.calversion=%%s 
            and l1.backend=%%s and s.status
        ''' %TABLES,(setup,calversion,backend))
    a = cur.fetchall()
    arr = array(a,dtype=int)
    arr.squeeze()
    cur.close
    db.close()
    return arr.squeeze()

def missing_l2(start,stop):
    db = connect(**connection_str)
    cur = db.cursor()
    cur.execute('''
        select r.orbit,setup,backend,freqmode,calversion,fqid,version
        from %(ref)s as r
        left join %(l0)s as l0
            on ( floor(start_orbit)<=r.orbit and floor(stop_orbit)>=r.orbit )
        left join %(l1)s as l1
            on ( r.orbit=l1.orbit )
        left join %(l2)s as l2
            on ( l1.id=l2.id )
        where r.orbit>%%s and r.orbit<%%s
        ''' %TABLES,(start,stop))
    for i in cur:
        print i

def l2_orbits(setup='S.*1A',backend='AC2',calversion=6,fqid=29,version='2-1'):
    db = connect(**connection_str)
    cur = db.cursor()
    cur.execute('''
        select r.orbit
        from %(ref)s as r
        join %(l0)s as l0
            on ( floor(l0.start_orbit)<=r.orbit 
                and floor(l0.stop_orbit)>=r.orbit )
        join %(l1)s as l1 using (orbit)
        join %(sta)s as s on (l1.id=s.id)
        join %(l2)s as l2 on (l1.id=l2.id)
        where l0.setup regexp  %%s and l1.calversion=%%s 
            and l1.backend=%%s and s.status and l2.fqid=%%s and l2.version=%%s
        ''' %TABLES,(setup,calversion,backend,fqid,version))
    a = cur.fetchall()
    arr = array(a,dtype=int)
    arr.squeeze()
    cur.close
    db.close()
    return arr.squeeze()

def products(start,stop):
    db = connect(**connection_str)
    cur = db.cursor()
    cur.execute('''
        select distinct r.orbit,l0.setup,l1.calversion,l1.backend,m.id,v.qsmr,l2.verstr,l2.processed
        from %(ref)s as r
        left join %(l0)s as l0
            on ( floor(start_orbit)<=r.orbit and floor(stop_orbit)>=r.orbit )
        left join %(l1)s as l1
            on ( r.orbit=l1.orbit )
        left join %(mod)s as m
            on ( l0.setup=m.mode and l1.backend=m.backend)
        join %(ver)s as v
            on ( l1.calversion=v.calversion and m.id=v.id and m.fm=v.fm )
        left join %(l2)s as l2
            on ( l1.id=l2.id and m.id=l2.fqid and v.qsmr=l2.version )
        where r.orbit>%%s and r.orbit<%%s
        order by r.orbit,l1.calversion,l1.backend
        ''' %TABLES,(start,stop))
    for i in cur:
        print i

def plot(a,b,c):
    #barplot
    x = arange(0,0xB000,0X1000)
    ah,y = histogram(a,bins=x)
    bh,y = histogram(b,bins=x)
    ch,y = histogram(c,bins=x)

    plt.figure(figsize=(12.,5.))

    l0 = plt.bar(x,ah,width=1000,color='#803300')
    l1 = plt.bar(x+1000,bh,width=1000,color='#ff7f2a')
    l2 = plt.bar(x+2000,ch,width=1000,color='#ffb480')


    plt.xticks(x,map(hex,map(int,x)))
    plt.ylabel('number of orbit files')
    plt.xlabel('orbitnumber hex')
    plt.legend((l0[0],l1[0],l2[0]),('Level0','Level1b','Level2'),loc=2)
    return plt

def plotmissing():
    db = connect(**connection_str)
    cur = db.cursor()
    cur.execute('''
    select ro.orbit,l0o.orbit
    from reference_orbit ro
    left join l0orbits l0o on (l0o.orbit=ro.orbit)
    left join level1 l1 on (l1.orbit=ro.orbit)
    left join level2files l2f on (l1.id=l2f.id)
    where ro.orbit>0x900 and ro.orbit<0xB000
    ''')
    cur.close()
    db.close()

if __name__=="__main__":
    if len(argv)==3:
        products(argv[1],argv[2])


