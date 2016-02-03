"""
Database model for hermod
"""
from sqlalchemy import (
    Column,
    DateTime,
    String,
    Integer,
    Float,
    Numeric,
    ForeignKeyConstraint)
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class Level1(Base):
    __tablename__ = 'level1'
    orbit = Column(Integer, primary_key=True)
    backend = Column(String(7), primary_key=True)
    calversion = Column(Numeric(2, 1), primary_key=True)
    hdffile = relationship('HdfFile')
    logfile = relationship('LogFile')
    scans = relationship('Scan')

class HdfFile(Base):
    __tablename__ = 'l1hdffiles'
    __table_args__ = (
        ForeignKeyConstraint(
            ['orbit', 'backend', 'calversion'],
            ['level1.orbit', 'level1.backend', 'level1.calversion']
        ),
    )

    orbit = Column(Integer, primary_key=True)
    backend = Column(String(7), primary_key=True)
    calversion = Column(Numeric(2, 1), primary_key=True)
    filedate = Column(DateTime)
    update = Column(DateTime)

class LogFile(Base):
    __tablename__ = 'l1logfiles'
    __table_args__ = (
        ForeignKeyConstraint(
            ['orbit', 'backend', 'calversion'],
            ['level1.orbit', 'level1.backend', 'level1.calversion']
        ),
    )
    orbit = Column(Integer, primary_key=True)
    backend = Column(String(7), primary_key=True)
    calversion = Column(Numeric(2, 1), primary_key=True)
    filedate = Column(DateTime)
    update = Column(DateTime)

class Scan(Base):
    __tablename__ = 'scans'
    __table_args__ = (
        ForeignKeyConstraint(
            ['orbit', 'backend', 'calversion'],
            ['level1.orbit', 'level1.backend', 'level1.calversion']
        ),
    )
    orbit = Column(Integer, primary_key=True)
    backend = Column(String(7), primary_key=True)
    calversion = Column(Numeric(2, 1), primary_key=True)
    mjd = Column(Float)
    stw = Column(Integer)
    level1 = relationship("Level1", back_populates="scans")


