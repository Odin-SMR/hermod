from MySQLdb import connect
from odin.hermod.hermodBase import connection_str
from sys import argv
from numpy import histogram,array,arange,nan,zeros
import matplotlib.pyplot as plt
import matplotlib as mpl
from matplotlib.figure import Figure, SubplotParams
from matplotlib.backends.backend_agg import FigureCanvasAgg 

def plotmissing(*args,**kwargs):
    ax = args[0]
    db = connect(**connection_str)
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
    orbits = arange(kwargs['start'],kwargs['stop'])
    
    cur = db.cursor()
    
    cur.execute("""
    select distinct mode
    from Aero
    where id=%(id)s""",kwargs)
    setups=['dummy']
    for i in cur:
        setups.append(i[0])
    kwargs['setup']= tuple(setups)
    cur.fetchall()
    cur.execute("""
    select ro.orbit 
    from reference_orbit ro
    join level0 l0 on (ro.orbit>=floor(l0.start_orbit) 
                        and ro.orbit<=floor(l0.stop_orbit))
    where l0.setup in %s and ro.orbit>=%%(start)s and ro.orbit<%%(stop)s
    """%str(kwargs['setup']),kwargs)

    measurment = array(cur.fetchall())

    cur.execute("""
    select l1.orbit
    from reference_orbit ro
    join level0 l0 on (ro.orbit>=floor(l0.start_orbit) 
                        and ro.orbit<=floor(l0.stop_orbit))
    join level1 l1 on (ro.orbit=l1.orbit)
    join status s on (l1.id=s.id)
    where l0.setup in %s and s.status and calversion=%%(cal)s
        and ro.orbit>=%%(start)s and ro.orbit<%%(stop)s
    """%str(kwargs['setup']),kwargs)
    calibrated = array(cur.fetchall())

    cur.execute('''
    select l1.orbit
    from reference_orbit ro
    join level0 l0 on (ro.orbit>=floor(l0.start_orbit) 
                        and ro.orbit<=floor(l0.stop_orbit))
    join level1 l1 on (ro.orbit=l1.orbit)
    join status s on (l1.id=s.id)
    join Aero a on (l0.setup=a.mode and a.backend=l1.backend)
    join versions v on (a.id=v.id and l1.calversion=v.calversion)
    join level2files l2f on (l1.id=l2f.id and a.id=l2f.fqid 
                            and v.qsmr=l2f.version)
    where s.status and a.id=%(id)s and v.qsmr=%(qsmr)s and ro.orbit>=%(start)s 
        and ro.orbit<%(stop)s and l1.calversion=%(cal)s
    ''',kwargs)    
    processed = array(cur.fetchall())
    cur.close()
    db.close()
    m = zeros((orbits.size,3))
    if measurment.size!=0:
        m[measurment-orbits.min(),0]=1
    if calibrated.size!=0:
        m[calibrated-orbits.min(),1]=1
    if processed.size!=0:
        m[processed-orbits.min(),2]=1
    
    p0 = ax.plot(orbits,m.sum(axis=1),color='r')
    p1 = ax.plot(orbits,m[:,[0,1]].sum(axis=1),color='b')
    p2 = ax.plot(orbits,m[:,0],color='g')
    
    ymarks = ['','measured','calibrated','l2product']
    ax.set_yticks(arange(4))
    ax.set_yticklabels(ymarks,rotation=45,fontsize='x-small')
    
    xmarks = orbits[orbits%32==0]
    ax.set_xticks(xmarks)
    ax.set_xticklabels(map(str,map(hex,xmarks)),fontsize='xx-small')

    ax.set_ylim(0,3.2)
    ax.set_xlim((orbits.min()-10,orbits.max()))

    ax.set_title('Processing chain %(setup)s to calversion %(cal).1f to id %(id)i Qsmr %(qsmr)s'%kwargs,
                 size='small')


def plotmany(*args,**kwargs):
    mpl.rc('lines',linestyle='steps') 
    datalength = kwargs['stop']-kwargs['start']
    subplt = SubplotParams(left=1*32./datalength, bottom=None, 
                           right=(datalength-1*32.)/datalength,hspace=0.3)   
    fig = Figure(figsize=(datalength/32.,2.*len(args[0])),subplotpars=subplt)
    if type(args[0])==list:
        for i,j in enumerate(args[0]):
            j.update(kwargs)
            ax = fig.add_subplot(len(args[0]),1,i+1)
            plotmissing(ax,**j)
    canvas = FigureCanvasAgg(fig)
    canvas.print_figure(kwargs['filename'],dpi=100)
    

if __name__=="__main__":
    f = plotmany([{'id':35,'qsmr':'2-1','cal':6},
                  {'id':20,'qsmr':'2-1','cal':6},
                  {'id':32,'qsmr':'2-1','cal':6},
                  {'id':37,'qsmr':'2-1','cal':6},
                  {'id':39,'qsmr':'2-1','cal':6}],
                  start=0x900,stop=0x3000,
                  filename='/home/joakim/workspace/hermod/utils/image.0-3.png')
    f = plotmany([{'id':35,'qsmr':'2-1','cal':6},
                  {'id':20,'qsmr':'2-1','cal':6},
                  {'id':32,'qsmr':'2-1','cal':6},
                  {'id':37,'qsmr':'2-1','cal':6},
                  {'id':39,'qsmr':'2-1','cal':6}],
                  start=0x3000,stop=0x5000,
                  filename='/home/joakim/workspace/hermod/utils/image.3-5.png')
    f = plotmany([{'id':35,'qsmr':'2-1','cal':6},
                  {'id':20,'qsmr':'2-1','cal':6},
                  {'id':32,'qsmr':'2-1','cal':6},
                  {'id':37,'qsmr':'2-1','cal':6},
                  {'id':39,'qsmr':'2-1','cal':6}],
                  start=0x5000,stop=0x7000,
                  filename='/home/joakim/workspace/hermod/utils/image.5-7.png')
    f = plotmany([{'id':35,'qsmr':'2-1','cal':6},
                  {'id':20,'qsmr':'2-1','cal':6},
                  {'id':32,'qsmr':'2-1','cal':6},
                  {'id':37,'qsmr':'2-1','cal':6},
                  {'id':39,'qsmr':'2-1','cal':6}],
                  start=0x7000,stop=0x9000,
                  filename='/home/joakim/workspace/hermod/utils/image.7-9.png')
    f = plotmany([{'id':35,'qsmr':'2-1','cal':6},
                  {'id':20,'qsmr':'2-1','cal':6},
                  {'id':32,'qsmr':'2-1','cal':6},
                  {'id':37,'qsmr':'2-1','cal':6},
                  {'id':39,'qsmr':'2-1','cal':6}],
                  start=0x9000,stop=0xA000,
                  filename='/home/joakim/workspace/hermod/utils/image.9-A.png')
    f = plotmany([{'id':35,'qsmr':'2-1','cal':6},
                  {'id':20,'qsmr':'2-1','cal':6},
                  {'id':32,'qsmr':'2-1','cal':6},
                  {'id':37,'qsmr':'2-1','cal':6},
                  {'id':39,'qsmr':'2-1','cal':6}],
                  start=0xA000,stop=0xA600,
                  filename='/home/joakim/workspace/hermod/utils/image.A-B.png')

