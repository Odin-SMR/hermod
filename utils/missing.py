from MySQLdb import connect
from hermod.hermodBase import connection_str
from sys import argv
from numpy import histogram,array,arange,nan,zeros
import matplotlib.pyplot as plt

def plotmissing():
    db = connect(**connection_str)
    cur = db.cursor()
#    cur.execute('''
#    select ro.orbit,l0.id,l0.mode,l0.setup,l1.id,s.status,l1.backend,l1.calversion,a.mode,a.id,v.qsmr,l2f.id,l2f.hdfname
#from reference_orbit ro
#left join level0 l0 on (ro.orbit>=floor(l0.start_orbit) and ro.orbit<=floor(l0.stop_orbit))
#left join level1 l1 on (ro.orbit=l1.orbit)
#left join status s on (l1.id=s.id)
#left join Aero a on (l0.setup=a.mode and a.backend=l1.backend)
#left join versions v on (a.id=v.id and l1.calversion=v.calversion)
#left join level2files l2f on (l1.id=l2f.id and a.id=l2f.fqid and v.qsmr=l2f.version)
#where ro.orbit>0x900 and ro.orbit<0xB000
#    ''')
    orbits = arange(0x8000,0xA000)
    cur.execute("""
    select ro.orbit 
    from reference_orbit ro
    join level0 l0 on (ro.orbit>=floor(l0.start_orbit) and ro.orbit<=floor(l0.stop_orbit))
    where l0.setup='S1A' and ro.orbit>=%s and ro.orbit<%s
    """,(orbits.min(),orbits.max()))
    measurment = array(cur.fetchall())
    print 2
    cur.execute("""
    select l1.orbit
    from reference_orbit ro
    join level0 l0 on (ro.orbit>=floor(l0.start_orbit) and ro.orbit<=floor(l0.stop_orbit))
    join level1 l1 on (ro.orbit=l1.orbit)
    join status s on (l1.id=s.id)
    where l0.setup='S1A' and s.status and ro.orbit>=%s and ro.orbit<%s
    """,(orbits.min(),orbits.max()))
    calibrated = array(cur.fetchall())
    print 1
    cur.execute('''
    select l1.orbit
    from reference_orbit ro
    join level0 l0 on (ro.orbit>=floor(l0.start_orbit) and ro.orbit<=floor(l0.stop_orbit))
    join level1 l1 on (ro.orbit=l1.orbit)
    join status s on (l1.id=s.id)
    join Aero a on (l0.setup=a.mode and a.backend=l1.backend)
    join versions v on (a.id=v.id and l1.calversion=v.calversion)
    join level2files l2f on (l1.id=l2f.id and a.id=l2f.fqid and v.qsmr=l2f.version)
    where a.id=3 and v.qsmr='2-0' and ro.orbit>=%s and ro.orbit<%s
    ''',(orbits.min(),orbits.max()))    
    processed = array(cur.fetchall())
    cur.close()
    db.close()
    m = zeros((orbits.size,3))
    m[measurment-orbits.min(),0]=1
    m[calibrated-orbits.min(),1]=1
    m[processed-orbits.min(),2]=1

    plt.figure(figsize=(orbits.size/32,2.),dpi=72)

    
#    p0 = plt.plot(orbits,m[:,0],'o',color='r')
#    p1 = plt.plot(orbits,m[:,1],'+',color='y')
#    p2 = plt.plot(orbits,m[:,2],'.',color='g')
    p0 = plt.bar(orbits,m[:,0],color='r',linewidth=0,width=1,align='center')
    p1 = plt.bar(orbits,m[:,1],color='y',bottom=m[:,0],linewidth=0,width=1,align='center')
    p2 = plt.bar(orbits,m[:,2],color='g',bottom=m[:,[0,1]].sum(axis=1),linewidth=0,width=1,align='center')
    plt.yticks(arange(4),['','measured','calibrated','l2product'],rotation=45,fontsize='x-small')
    xmarks = orbits[orbits%32==0]
    plt.xticks(xmarks,map(str,map(hex,xmarks)),fontsize='xx-small')
#    p2 = plt.plot(orbits,m[:,2]+2,color='g')
#    p1 = plt.plot(orbits,m[:,2]+1,color='y')
#    p0 = plt.plot(orbits,m[:,0],color='r')
    plt.ylim(0,3.2)
    plt.xlim((orbits.min()-10,orbits.max()))
    plt.title('Process chain %s to calversion %.1f to %i',size='small')
    #plt.show()
    
    plt.savefig('image.png')


if __name__=="__main__":
    plotmissing()

print "hek"