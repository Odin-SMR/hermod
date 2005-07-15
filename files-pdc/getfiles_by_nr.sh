#!/bin/bash -l

gawk 'BEGIN{"echo $1" | getline pat} /AC.\/pat/{print $0}' /home/odinop/files-missing/missing_AC2_at_pdc /home/odinop/files-missing/missing_AC1_at_pdc |gawk -F"/" -f /home/odinop/files-pdc/getfiles.awk | expect >& get$1.log
