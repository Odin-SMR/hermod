#!/bin/bash

datapath=/odin/smr/Data/level1b

ssh malachite tar -cz \
    ${datapath}/6.0/AC2/137/OC1B13728.* \
    ${datapath}/7.0/AC2/139/OC1B139C4.* \
    ${datapath}/7.0/AC1/139/OB1B139C5.* \
    ${datapath}/6.1/AC1/103/OB1B103A6.* \
    ${datapath}/6.1/AC2/103/OC1B103BE.* \
    ${datapath}/6.0/AC1/139/OB1B139CA.* \
    > test_data/datafile.tar.gz
