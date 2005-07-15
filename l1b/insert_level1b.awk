#!/usr/bin/gawk -f
#
#Vdata: 1
#tag = 1962; reference = 3;
#number of records = 1809; interlace = FULL_INTERLACE (0);
#fields = [Version, Level, Quality, STW, MJD, Orbit, LST, Source, Discipline,
#Topic, Spectrum, ObsMode, Type, Frontend, Backend, SkyBeamHit,
#RA2000, Dec2000, VSource, Longitude, Latitude, Altitude,
#Qtarget, Qachieved, Qerror, GPSpos, GPSvel, SunPos, MoonPos,
#SunZD, Vgeo, Vlsr, Tcal, Tsys, SBpath, LOFreq, SkyFreq, RestFreq,
#MaxSuppression, FreqThrow, FreqRes, FreqCal, IntMode,
#IntTime, EffTime, Channels, pointer];
#record size (in bytes) = 424;
#name = SMR; class =        10000;
#               

function mjd2utc(mjdnr) {

    /* Julian date */
    jd = int(mjdnr) + 2400000.5;

    /* get the fraction of UTC day. */
    dayfrac = mjdnr - int(mjdnr);

    /* add a half */
    jd0 = jd + .5;

    /* determin the calender */
    if (jd0 < 2299161.0) {
        /* Julian */
        c = jd0 + 1524.0;
    } 
    else {
        /* Gregorian */
        b = int(((jd0 -1868216.25)/36524.25));
        c = jd0 + (b- int(b/4) + 1525.0);
    }

    d     = int( ((c - 122.1) / 365.25) );
    e     = 365.0 * d + int(d/4);
    f     = int( ((c - e) / 30.6001) );
    day   = int( (c - e + 0.5) - int(30.6001 * f) );
    month = int( (f - 1 - 12*int(f/14)) );
    year  = int( ( d - 4715 - int((7+month)/10)) );
    hour     = int(dayfrac*24.0);
    minute      = int((dayfrac*1440.0)-int(dayfrac*1440.0/60)*60.0);
    dayfrac  = dayfrac * 86400.0;
    ticks    = (dayfrac-int(dayfrac/60)*60.0);
    secs     = int(ticks);
    ticks    = ticks- secs;
    ret = year"-"month"-"day" "hour":"minute":"secs+ticks;
    return ret;
}

function fixstr(stringer) {
    better=gensub(" ","","g",stringer);
    split(better,z,"=");
    split(z[2],x,"\\");
    return x[1];
}

BEGIN{
    scan=0;
    n=1;
    file=ARGV[1];
    command1 = "hdp dumpvd -n SMR -d -f Version,Level,MJD,Orbit,Type,Latitude,Longitude,SunZD "file;
    while (command1 | getline) {
        vers[n]=$1;
        lev[n]=$2;
        mjd[n]=$3;
        orb[n]=$4;
        type[n]=$5;
        lat[n]=$6;
        lon[n]=$7;
        sun[n]=$8;
        n++;
    }
    close(command1);
    
    command2 = "hdp dumpvd -n SMR -d -f Source "file;
    nr=1;
    while (command2 | getline) {
        sour[nr]=fixstr($0);
        nr++;
    }
    close(command2);
} 

END{
    for (i=1; i<n; i++) { 
        if(type[i]==3){
            if (type[i-1]!=3){
                scan++;
                change=1;
            }
        } else if ( (type[i]==8) && (change==1)) {
            change=0;
            printf "insert delayed ignore into scans\n(orbit,freqmode,calibration,scan)\nvalues (%d,%d,%d,%d);\n",orb[i],sour[i],and(lev[i]+0,0xff),scan;
            print ""
            printf "insert delayed ignore into level1b\n(id,formatMajor,formatMinor,attitudeVersion,mjd,date,latitude,longitude)\nselect id,%d,%d,%d,%f,'%s',%f,%f\nfrom scans\nwhere scans.orbit=%d and scans.freqmode=%d and scans.calibration=%d and scans.scan=%d;\n",rshift(vers[i]+0,8),and(vers[i]+0,0xff),rshift(lev[i]+0,8),mjd[i],mjd2utc(mjd[i]),lat[i],lon[i],orb[i], sour[i],and(lev[i]+0,0xff),scan;
            print ""
        }
    }
}

	
