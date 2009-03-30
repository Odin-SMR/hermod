from MySQLdb import connect
from _mysql_exceptions import Warning
from MySQLdb.cursors import SSCursor
from gemlogger import timer
from hermod.hermodBase import connection_str

@timer
def dbcons():
    con1 =  connect(**connection_str)
    cursor1 = con1.cursor(SSCursor)
    cursor1.execute('''create temporary table ttemp
        (id INT,
         backend varchar(3),
         calversion decimal(5,2),
         freqmode int,
         primary key (id,backend,calversion,freqmode)
         )
        engine = memory 
        ''')
    query = '''
    select * from (
select id,substr(backend,1,3) back,freqmode,freqmode mode,calversion from level1
join status using (id)
join level1b_gem l1g using (id)
where status and l1g.filename regexp ".*HDF" and not locate(',',freqmode)
union
(
select id,substr(backend,1,3) back,freqmode,substr(freqmode,1, locate(',',freqmode)-1) mode,calversion from level1
join status using (id)
join level1b_gem l1g using (id)
where status and l1g.filename regexp ".*HDF" and locate(',',freqmode)
)
union
(
select id,substr(backend,1,3) back,freqmode,substr(freqmode from locate(',',freqmode)+1) mode,calversion from level1
join status using (id)
join level1b_gem l1g using (id)
where status and l1g.filename regexp ".*HDF" and locate(',',freqmode)
)) as TZ
    '''
    con2 = connect(**connection_str)
    cursor2 = con2.cursor()
    cursor2.execute('''
        select id,backend,freqmode,calversion from level1
        join status using (id)
        join level1b_gem l1g using (id)
        where status and l1g.filename regexp ".*HDF"
    #    order by orbit desc,backend
        ''')
    set_size = 1000
    set = cursor2.fetchmany(set_size)

    while not set==():
        for i in set:
            for j in i[2].split(','):
                expanded = i[:2]+i[3:]+(int(j),)
                try:
                    cursor1.execute("""
                        insert ttemp values (%s,%s,%s,%s)
                        """,expanded)
                except Warning,w:
                    print w
        set = cursor2.fetchmany(set_size)    
            
            
    cursor1.execute("""select count(*) from ttemp""")
    a = cursor1.fetchall()
    print a
    cursor1.close()
    cursor2.close()
    
    con1.close()
    con2.close()
    
if __name__=="__main__":
    dbcons()
