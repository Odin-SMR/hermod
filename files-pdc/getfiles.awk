BEGIN {printf "set timeout 1200\nspawn /usr/lib/heimdal/bin/ftp -p esrange.pdc.kth.se\nexpect \"Name*):\"\nsend \"donal\\r\"\n"}
{printf "expect \"ftp>\"\nsend \"get %s /odin/smr/Data/spool/%s\\r\"\n",$0,$11 }
END {printf "expect \"ftp> \"\nsend \"bye\\r\"\nexpect \"Goodbye.\"\nclose\nwait\n"}
