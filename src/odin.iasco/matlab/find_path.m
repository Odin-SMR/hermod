function path = find_path(DIR)

fid=fopen('~/.hermod.cfg');
text=textscan(fid, '%s','delimiter',':');
path=text{1,1}(find(ismember(text{1,1},DIR)==1)+1);