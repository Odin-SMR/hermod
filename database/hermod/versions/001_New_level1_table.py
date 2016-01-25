from sqlalchemy import Table, Column, Integer, String, Float, MetaData, ForeignKeyConstraint, Numeric, DateTime, func

meta = MetaData()

level1 = Table(
    'level1',
    meta,
    Column('orbit', Integer, primary_key=True),
    Column('backend', String(7), primary_key=True),
    Column('calversion', Numeric(2,1), primary_key=True),
    )

hdf = Table(
    'l1hdffiles',
    meta,
    Column('orbit', Integer, primary_key=True),
    Column('backend', String(7), primary_key=True),
    Column('calversion', Numeric(2,1), primary_key=True),
    Column('filedate', DateTime()),
    Column('update', DateTime(), onupdate=func.utc_timestamp()),
    ForeignKeyConstraint(['orbit', 'backend', 'calversion'], ['level1.orbit', 'level1.backend','level1.calversion'])
    )

log = Table(
    'l1logfiles',
    meta,
    Column('orbit', Integer, primary_key=True),
    Column('backend', String(7), primary_key=True),
    Column('calversion', Numeric(2,1), primary_key=True),
    Column('filedate', DateTime()),
    Column('update', DateTime(), onupdate=func.utc_timestamp()),
    ForeignKeyConstraint(['orbit', 'backend', 'calversion'], ['level1.orbit', 'level1.backend','level1.calversion'])
    )

scans = Table(
    'scans',
    meta,
    Column('orbit', Integer, primary_key=True),
    Column('backend', String(7), primary_key=True),
    Column('calversion', Numeric(2,1), primary_key=True),
    Column('mjd', Float),
    Column('stw', Integer),
    ForeignKeyConstraint(['orbit', 'backend', 'calversion'], ['level1.orbit', 'level1.backend','level1.calversion'])
    )

def upgrade(migrate_engine):
    meta.bind = migrate_engine
    level1.create()
    hdf.create()
    log.create()
    scans.create()

def downgrade(migrate_engine):
    scans.drop()
    log.drop()
    hdf.drop()
    level1.drop()
