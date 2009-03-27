from MySQLdb import connect

from hermod.hermodBase import connection_str


db =  connect(**connection_str)
cursor = db.cursor()
cursor.execute('''
    select id,backend,freqmode,calversion from level1
    join status using (id)
    where status
    order by orbit desc,backend
    ''')
    
jobs = []
for i in cursor:
    for j in i[2].split(','):
        jobs.append(i[:2]+i[3:]+(int(j),))
        
cursor.execute('''create temporary table ttemp
    (id INT,
     backend varchar(3),
     calversion decimal(5,2),
     freqmode int,
     primary key (id,backend,calversion,freqmode)
     )
    ''')
print jobs
cursor.executemany("""
    insert ttemp values (%s,%s,%s,%s)
    """,jobs)

cursor.execute("""select count(*) from ttemp""")
a = cursor.fetchall()
print a
cursor.close()

db.close
