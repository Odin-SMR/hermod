#!/usr/bin/gawk -f
#
# Move Sort and launch a file to the cluster.
#
# Annotations about the hdf-file format.
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

###
# fmod
# returns the freqmodestring from the number
#
function fmod(number,   fm) {
    fm[1]="SM_AC2ab"
    fm[2]="SM_AC1e"
    fm[24]="HM_AC1f"
    fm[8]="IM_AC2ab"
    fm[17]="IM_AC2c"
    fm[19]="IM_AC1c"
    fm[21]="IM_AC1de"
    fm[13]="HM_AC1c"
    fm[14]="HM_AC2c"
    fm[22]="HM_AC2ab"
    fm[23]="HM_AC1e"
    fm[25]="TM_ACs1"
    fm[26]="TM_AOS1"
    fm[27]="TM_ACs2"
    fm[28]="TM_AOS2"
    fm[20]="SM_FB"
    fm[3]="HM_AC1b"
    fm[4]="HM_AC2b"
    fm[5]="HM_AOS2"
    fm[6]="NM_AC1b"
    fm[7]="NM_AC2b"
    fm[9]="IM_AC1b"
    fm[10]="SM_AC2d"
    fm[11]="HM_AOS1"
    fm[12]="IM_AOS1"
    fm[15]="HM_AC2e"
    fm[16]="HM_AC2f"
    if (number exist in fm)
        return fm[number]
    else
        return "unknown"
}

###
# backend
# returns the backend string
function backend(number,   b) {
    b[1]="AC1"
    b[2]="AC2"
    b[3]="AOS"
    b[4]="FBA"
    if (number exist in b)
        return b[number]
    else
        return "unknown"
}

###
# fixstr
# returns the freqmode number
function fixstr(stringer) {
    better=gensub(" ","","g",stringer);
    split(better,z,"=");
    split(z[2],x,"\\");
    return x[1];
}

BEGIN{
    ## read the hdf-input file
    file=ARGV[1];
    printf "\necho Reading file: %s\n\n",file
    command2 = "hdp dumpvd -n SMR -d -f Source "file;
    while (command2 | getline) {
        fqmod = fixstr($0)
        sour[fqmod]=fqmod;
    }
    close(command2);
    level=0;
    command1 = "hdp dumpvd -n SMR -d -f Level,Orbit,Backend "file" | grep -E \".+\"";
    while (command1 | getline) {
        if (level<$1) level=$1;
        orb=$2;
        back=$3;
    }
    close(command1);
} 
END{
    split(file,filename,".");
    split(file,parts,"/");
    orig = sprintf("%s",filename[1]);
    targetdir=sprintf("/odin/smr/Data/level1b/V-%d/%s/%02X/",and(level+0,0xFF),backend(back),rshift(orb+0,8));
    ## part[6] is path-depth dependent 
    ##  /odin/smr/Data/spool/file.hdf
    ## 1|-2--|-4-|-4--|--5--|---6----|
    dest = sprintf("/odin/smr/Data/level1b/V-%d/%s/%02X/%s",and(level+0,0xFF),backend(back),rshift(orb+0,8),substr(parts[6],1,8));
    printf "echo Move file to right directory, this is a calibration %d file\n\n",and(level+0,0xFF)
    printf "if [ ! -e %s ]; then mkdir -p %s; fi;\n",targetdir,targetdir;
    printf "mv %s.HDF %s\n",orig,targetdir;
    printf "mv %s.LOG %s\n",orig,targetdir;;
    for (i in sour) {
        if (i!="") {
            linkdir=sprintf("/odin/smr/Data/SMRl1b/V-%d/%s/",and(level+0,0xFF),fmod(i));
            printf "\necho Link file to SMR-directory structure %s:\n",fmod(i);
            printf "if [ ! -e %s ]; then mkdir -p %s; fi;\n",linkdir,linkdir;
            printf "ln -sf %s.HDF %s \n",dest,linkdir;;
            printf "ln -sf %s.LOG %s \n",dest,linkdir;
        }
    }
    
    ## insert parameters to database
    printf "\necho Add parameters to the level1b database\n"
    printf "~/hermod/l1b/insert_level1b.awk %s.HDF |mysql -uodinuser -pIK\\)Bag4F odin\n",dest;

    ## Create the ZPT-file.
    #printf "if [ ! -e /odin/smr/Data/SMRl1b/ECMWF/%X.ZPT ]; then",orb 
    printf "\necho Create ZPT-file with matlab\n"
    printf "matlab -nodisplay << end_tag\n"
    printf "addpath('/odin/extdata/ecmwf/tz');\n"
    printf "create_tp_ecmwf_rss2('%s.LOG');\n",dest;
    printf "quit;\n"
    printf "end_tag\n"
    #printf "fi"
    cal = and(level+0,0xFF)

    ## Link ZPT-file to a QSMR friendly directory structure
    zpttargetdir = sprintf("/odin/smr/Data/SMRl1b/V-%d/ECMWF/%s",and(level+0,0xFF),backend(back))
    printf "if [ ! -e %s ]; then mkdir -p %s; fi;\n",zpttargetdir,zpttargetdir;
    printf "ln -sf %s.ZPT %s \n",dest,zpttargetdir
        
    printf "\necho Launch processes to cluster\n"
    ## Send the job into the cluster	
#    if (cal==4) {
#        for (i in sour) {
#            if (i!="") {
#                printf "cd /home/odinop/logs && echo \"~/bin/odinrun_Qsmr-1-2 %X %d %s\" | qsub -qstratos -l walltime=24:0:0 -N %s.%X.1-2\n",orb,cal,fmod(i),fmod(i),orb
#            }
#        }
#    } 
#    else {
        if (cal==6) {
            for (i in sour) {
                if (i!="") {
                    printf "cd /home/odinop/logs && echo \"~/bin/odinrun_Qsmr-2-0 %X %d %s\" | qsub -qstratos -l walltime=6:0:0 -N %s.%X.2-0\n",orb,cal,fmod(i),fmod(i),orb
                }
            }
        }
#    }
}
