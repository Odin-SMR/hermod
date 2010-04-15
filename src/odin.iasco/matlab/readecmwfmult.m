function  [levels, data, lat, long] = readecmwfmult(filnamn)
% function  [level, data, lat, long] = readecmwf1(filnamn)

%Reads ECMWF files from NILU.


lat=90:-1.125:-90;
long =-180:1.125:179.9;

fid=fopen(filnamn,'rt');

[Ndummies, count]=fscanf(fid,'%d',1);
line =fgetl(fid);
for i=1:Ndummies-1;
  line =fgetl(fid);
end

i= 0;
feof(fid);
while ~feof(fid)
  i = i+1;
  [level, count]=fscanf(fid,'%d',1);
  
  levels(i) = (level);
  %fprintf(1,'\rLevel: %i   ',levels(i))
  line =fgetl(fid); % Skip the rest of the line
  data(:,:,i)=fscanf(fid,'%f',[320 161])';
  
  junk1=fscanf(fid,'%c',1);  % Read away two spaces, to get the eof warning
  junk2=fscanf(fid,'%c',1);
end

%fprintf(1,'\n')

fclose(fid);
