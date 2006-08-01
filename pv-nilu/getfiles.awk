BEGIN {printf "connect zardoz.nilu.no\n"}
{printf "get %s -o /odin/extdata/ecmwf/pv/%s/%s\n",$0,substr($6,6,4),$6}
END {printf "bye\n"}
