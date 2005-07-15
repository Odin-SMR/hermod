#!/usr/bin/gawk -f
#
    #set up the fqmode table;
function fmod(str) {    
    if (str in fm) {
        return fm[str];
    } else {
        return 0
    }
}

BEGIN{
    fm["SM_AC2a"]=1;
    fm["SM_AC2b"]=1;
    fm["SM_AC2ab"]=1;
    fm["SM_AC1e"]=2;
    fm["HM_AC1f"]=24;
    fm["IM_AC2a"]=8;
    fm["IM_AC2b"]=8;
    fm["IM_AC2ab"]=8;
    fm["IM_AC2c"]=17;
    fm["IM_AC1c"]=19;
    fm["IM_AC1de"]=21;
    fm["HM_AC1c"]=13;
    fm["HM_AC2c"]=14;
    fm["HM_AC2ab"]=22;
    fm["HM_AC1d"]=23;
    fm["HM_AC1e"]=23;
    fm["TM_ACs1"]=25;
    fm["TM_AOS1"]=26;
    fm["TM_ACs2"]=27;
    fm["TM_AOS2"]=28;
    fm["SM_FB"]=20;
    #supplementary modes
    fm["HM_AC1a"]=3;
    fm["HM_AC1b"]=3;
    fm["HM_AC2a"]=4;
    fm["HM_AC2b"]=4;
    fm["HM_AOS2"]=5;
    fm["NM_AC1a"]=6;
    fm["NM_AC1b"]=6;
    fm["NM_AC2a"]=7;
    fm["NM_AC2b"]=7;
    fm["IM_AC1a"]=9;
    fm["IM_AC1b"]=9;
    fm["SM_AC2c"]=10;
    fm["SM_AC2d"]=10;
    fm["HM_AOS1"]=11;
    fm["IM_AOS1"]=12;
    fm["HM_AC2d"]=15;
    fm["HM_AC2e"]=15;
    fm["HM_AC2d"]=16;
    fm["HM_AC2f"]=16;

    n=0;
    file=ARGV[1];

    #  /odin/smr/Data/SMRl2spool/SMRhdf/Qsmr-1-2/SM_AC2ab/SCH_5018_B5632_012.L2P
    #1-|-2--|-3-|-4--|----5-----|--6---|---7----|---8----|-----------9----------
    split(file,param,"/");
    #split the filname to get orbit number
    split(param[9],par,"_");
    
    command1 = "hdp dumpvd -n Geolocation -d -f SunZD,ScanNo,Day,Month,Year,Hour,Min,Secs,Latitude,Longitude,MJD " file;
    while (command1 | getline) {
        n++;
        sun[n]=$1;
        scan[n]=$2
        date[n]=$5"-"$4"-"$3" "$6":"$7":"$8;
        lat[n]=$9;
        lon[n]=$10;
        mjd[n]=$11;
    }
    close(command1);
} 

END{
    for (i=1; i<n-1; i++) { 
        printf "INSERT delayed ignore INTO level2\n(version,processed,id,latitude,longitude,mjd,date,sunZD)\nselect '%s',now(),scans.id,%f,%f,%f,'%s',%f\nfrom scans\nwhere scans.freqmode=%d and hex(scans.orbit)='%s' and scans.calibration=%d and scans.scan=%d;\n",substr(param[7],6),lat[i],lon[i],mjd[i],date[i],sun[i],fmod(param[8]),substr(par[3],2,4),4,scan[i];
    }
}
