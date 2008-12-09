from MySQLdb import connect
from hermod.hermodBase import connection_str
from sys import argv
from numpy import histogram,array,arange,nan
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
    orbits = arange(0x900,0xB000)
    cur.execute("""
    select ro.orbit 
    from reference_orbit ro
    join level0 l0 on (ro.orbit>=floor(l0.start_orbit) and ro.orbit<=floor(l0.stop_orbit))
    where l0.setup='S1A'
    """)
    measurment = array(cur.fetchall())
    cur.execute("""
    select l1.orbit
    from reference_orbit ro
    join level0 l0 on (ro.orbit>=floor(l0.start_orbit) and ro.orbit<=floor(l0.stop_orbit))
    join level1 l1 on (ro.orbit=l1.orbit)
    join status s on (l1.id=s.id)
    where l0.setup='S1A' and s.status
    """)
    calibrated = array(cur.fetchall())
    cur.execute('''
    select l1.orbit
    from reference_orbit ro
    join level0 l0 on (ro.orbit>=floor(l0.start_orbit) and ro.orbit<=floor(l0.stop_orbit))
    join level1 l1 on (ro.orbit=l1.orbit)
    join status s on (l1.id=s.id)
    join Aero a on (l0.setup=a.mode and a.backend=l1.backend)
    join versions v on (a.id=v.id and l1.calversion=v.calversion)
    join level2files l2f on (l1.id=l2f.id and a.id=l2f.fqid and v.qsmr=l2f.version)
    where a.id=3 and v.qsmr='2-0'
    ''')    
    processed = array(cur.fetchall())
    cur.close()
    db.close()
    plt.figure(figsize=(20.,2.))
    plt.plot(orbits,orbits,'r+')
    plt.plot(measurment,measurment,'y+')
    plt.plot(calibrated,calibrated,'g+')
    plt.plot(processed,processed,'b+')
    plt.show()


if __name__=="__main__":
    plotmissing()

print "hek"