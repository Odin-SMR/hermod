### The odin.iasco README-file ###

This README file contains information for installing and using the odin.iasco-egg. There are also explanations for each program and their purpose.
==========================

### Installing the egg and necessary preparations ###

Info about installation, changing paths, other stuff thats needed (e.g hermod, matlab-files) and other good things to know before start

==========================

### The programs ### 

blackbox_main.py
    This is the main program that controls and runs all the other parts in the right order. The process runs for each day from a given start date until three days before today. This three days limit is there because the wind files that are used are downloaded from NILU with a limit of two days before today and the assimilation program (IASCO.m) need winds from 00.00 the day after. 
¤ Example: Today is 2009-06-24, there are wind-files up until 2009-06-22 for the times 00.00, 06.00, 12.00 and 18.00. The assimilation for 2009-06-21 need the wind-file for 00.00 the 22nd. The 21st is therefor the last date that can be assimilated.
     
    There are three different ways to decide which processes that are needed for each day. This is if there are an update in a wind-file (wind) or in an orbit file (hdf) and if the assimilation (assim) of the day needs to be updated due to a change in a previous day (90 days range). 
¤ wind: A new extraction of the wind-files are needed for this day, because of the update. While the assimilation need wind-files for the day after (according to the example above) it's also needed to run the assimilation, make new pictures and update the database for the day before the update of wind-files.
¤ hdf: If there have been an update in satellite data the files that are used in the assimilation also need an update. When the assimilation is complete a datebase update is processed.
¤ assim: Assimilates, produce pictures and write to the database. There are also an control to make sure that all the wind-files exists for this day.

    If the day never been assimilated before (the date is in new_dates) an extraction of the wind-files is needed for the day after due to the assimilation process, see example above.

----------------
assimilate.py
    Info kommer här
    
----------------
color_axis.py
    Defines the color axis for the produced images. These are defined and not default because of an easier comparison between different days for the same level and species.
    
----------------
convert_date.py
    Convert days from utc to mjd or vice versa.
    
----------------
db_calls.py
    w2iasco - Check in the iasco database if there are some information for the specific day and species. If there are no information it inserts new data (frequence id, date of the procession, filename to assimilated data, date of the assimilation, species, version of used data)
    
----------------
mark_iasco_db.py
    markWinds - Find the days where the windfiles have been updated since the last time the assimilation were run and mark this day. The mark is a 1 instead of a 0 which is the default value in the database.
    
    markL2 - Find the the number of updated orbits since the last time the assimilation were run and compare with the number of old orbits. If the number of new orbits is half as many as the new ones, the day will be marked (#old/#new>=0.5 => mark). The mark is a 1 instead of a 0 which is the default value in the database. The limit of 0.5 makes sure that there will be a change that is big enough to make the reassimilation necessary
    
    markAss - Find the days that are wind- and/or L2-marked and mark 90 days from this day. The 90 days limit is there to certify that the effects of the changes has declined enough. The mark is a 1 instead of a 0 which is the default value in the database.
    
    markDaysWithNewOrbits - Find days where there were no orbit-data the last time the assimilation were run. The program find all the days that don't have any orbit-data and and control if there are any orbit-data for these days. If there are, this day and 90 days ahead will be marked. 
    
----------------
pics.py
    Info kommer här
    
----------------
plot.py
    Info kommer här
    
----------------
tracer_fields.py
    Info kommer här
    
----------------
winds.py
    Info kommer här
    
==========================
