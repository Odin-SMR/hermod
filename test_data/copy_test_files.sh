#!/bin/bash

l1_datapath=/odin/smr/Data/level1b
nc_datapath=/odin/external/ecmwfNCD

(ssh malachite tar -cz \
    ${l1_datapath}/6.0/AC2/137/OC1B13728.PTZ \
    ${l1_datapath}/6.0/AC2/137/OC1B13728.HDF \
    ${l1_datapath}/6.0/AC2/137/OC1B13728.LOG \
    ${l1_datapath}/7.0/AC2/139/OC1B139C4.PTZ \
    ${l1_datapath}/7.0/AC2/139/OC1B139C4.HDF \
    ${l1_datapath}/7.0/AC2/139/OC1B139C4.LOG \
    ${l1_datapath}/7.0/AC1/139/OB1B139C5.PTZ \
    ${l1_datapath}/7.0/AC1/139/OB1B139C5.HDF \
    ${l1_datapath}/7.0/AC1/139/OB1B139C5.LOG \
    ${l1_datapath}/6.1/AC1/103/OB1B103A6.PTZ \
    ${l1_datapath}/6.1/AC1/103/OB1B103A6.HDF \
    ${l1_datapath}/6.1/AC1/103/OB1B103A6.LOG \
    ${l1_datapath}/6.1/AC2/103/OC1B103BE.PTZ \
    ${l1_datapath}/6.1/AC2/103/OC1B103BE.HDF \
    ${l1_datapath}/6.1/AC2/103/OC1B103BE.LOG \
    ${l1_datapath}/6.0/AC1/139/OB1B139CA.PTZ \
    ${l1_datapath}/6.0/AC1/139/OB1B139CA.HDF \
    ${l1_datapath}/6.0/AC1/139/OB1B139CA.LOG \
    ${nc_datapath}/2013/04/ODIN_NWP_2013_04_27_12.NC \
    ${nc_datapath}/2013/04/ODIN_NWP_2013_04_27_12.lait.mat \
    )  > datafile.tar.gz
