#!/usr/bin/python

import sys
from nilumod import *

def main():
    '''
    This is an example of how to use it
    '''
    # Read arguments, if no given read stdin
    # The arguments must be defined as DATE, HOUR and can not be a list of dates
    dates = sys.argv[1]
    hour = sys.argv[2]
    if dates==[] or hour==[]:
        while True:
            try:
                if dates==[]:   
                    dates.append(raw_input())
                if hour==[]:
                    hour.append(raw_input())
            except EOFError:
                break
    u = weatherdata_U(dates,hour)

if __name__=='__main__':
    main()
