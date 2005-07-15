#!/bin/bash -l 
matlab -nodisplay << end_tag
addpath('~/hermod/mat/');
poff('$1');
quit;
end_tag
    
    
