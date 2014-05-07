%------------------------------------------------------------------------
% NAME:       read_l2_smr;
%
% DESCRIPTION          
%             Read the results of an orbit inversion from a l2p  
%             or l2d hdf file. The extension l2d correspond to
%             level-2 product file, l2d to level-2 diagnostic
%             file. The input is the file name of the  
%             level-2 file. More information can be found in the
%             document level2_product.ps
%
% FORMAT:     l2 = read_l2_smr(filename,scanno)
%           
% IN:         filename  full file name
%
% OPTIONAL:   scanno    number of scan to read from inversion, if
%                       not given all scans read           
%
% OUT:        l2       Level 2 structure or structure array containing fields
%                         'Version1b',
%                         'Version2',
%                         'Quality',
%                         'Source',
%                         'ZPTSource',
%                         'OrbitFilename',
%                         'SunZD',
%                         'LST',
%                         'ScanNo',
%                         'Nspecies',
%                         'NzptParam'
%                         'Day',
%                         'Month',
%                         'Year',
%                         'Hour',
%                         'Min',
%                         'Secs',
%                         'Ticks',
%                         'Latitude',
%                         'Longitude',
%                         'StartLat',
%                         'EndLat',
%                         'StartLong',
%                         'EndLong',
%                         'StartTan',
%                         'EndTan',
%                         'Species',
%                         'Naltitudes',
%                         'ZPTNames',
%                         'Nzpt',
%                         'Altitudes',
%                         'Pressures',
%                         'Profiles',
%                         'ZPT',
%                         'SmoothingError',
%                         'MeasError',
%                         'MeasResp',
%                         'TotalError'
%                       if diagnostics also
%                         'Quality1',
%                         'Quality2',
%                         'TotalScanNo'
%                         'AskScans'
%                         'PointOffset',
%                         'Chi2Meas',
%                         'Chi2Apriori',
%                         'MaxOpacity',
%                         'ArtNoise',
%                         'Marquardt',
%                         'MarqConverged',
%                         'FreqShift',
%                         'Iter',
%                         'Ntangents',
%                         'Chi2',
%                         'BaseLine',
%                         'BaseLineRet1',
%                         'BaseLineRet2',
%                         'BinMode',
%                         'ClimCon',
%                         'Channels',
%                         'TangentHeights',
%                         'SpectraNo',
%                         'AprioriUncert',
%                         'AprioriProf',
%                         'AverKernels',
%                         'Measurement',
%                         'Fit'
%                        but no 'total error'.                       
%
% Also adds potential temperature (theta) profile, corresponding 
% to the ZPT profiles. 
%
%------------------------------------------------------------------------
%
% HISTORY: 2002.09.17  Created by Carlos Jimenez
%
% Last changes: J. Urban 2005-10-18 - version 2.5
% Last changes: S. Lossow June-2006 - version 2.6
% Last changes: J. Urban August-2006 - version 2.7
% Last changes: J. Urban November-09-2006 - version 2.8


function l2 = read_l2_smr(filename,scanno);

%=== Checking input
%
if ~exist('scanno')
  do_all = 1;
else
  if isempty(scanno)
    do_all = 1;
  else
    do_all = 0;
  end    
end


%=== Checking if file exist
%
if exist(filename,'file') == 0
  disp(['... read_l2_smr: ',filename,' does not exist, nothing done ... ']) 
  l2 = [];
  return
end

%=== Finding type of file
%
%ind   = find('.'==filename);
ind=findstr(filename,'.');
if ~isempty(ind) 
  types = filename(ind(end)+1:ind(end)+3);
else
  types='';
end
if ~(strcmpi(types,'L2P') | strcmpi(types,'L2D') )  
  disp('... read_l2_smr: file does not have the right extension, nothing done ... ');
  l2 = [];
  return
end


%=== Getting hdf file
%
file_id = hdfpt('open',filename,'read');
if file_id <= 0 
  message=['Error opening file ',filename,' for read ...'];
  disp(['... read_l2_smr: ',message]);
  clear message
  l2 = [];
  return
end

%=== Read level 0,1,2 info into memory for L2P pr L2D
%
point_name = hdfpointname(filename);
point_name = char(point_name(1,:)); 
%
message=['Error reading file ',filename,' (',point_name,') ... '];
if     strcmpi(types,'L2P')
  status = 0;
  [smr_l0,status] = read_l2prod(file_id,point_name,0); 
  if (status ~= 0) l2=[]; disp(['... read_l2_smr: ',message]); return; end
  [smr_l1,status] = read_l2prod(file_id,point_name,1); 
  if (status ~= 0) l2=[]; disp(['... read_l2_smr: ',message]); return; end
  [smr_l2,status] = read_l2prod(file_id,point_name,2); 
  if (status ~= 0) l2=[]; disp(['... read_l2_smr: ',message]); return; end
elseif strcmpi(types,'L2D')
  status = 0;
  [smr_l0,status] = read_l2diag(file_id,point_name,0); 
  if (status ~= 0) l2=[]; disp(['... read_l2_smr: ',message]); return; end
  [smr_l1,status] = read_l2diag(file_id,point_name,1); 
  if (status ~= 0) l2=[]; disp(['... read_l2_smr: ',message]); return; end
  [smr_l2,status] = read_l2diag(file_id,point_name,2); 
  if (status ~= 0) l2=[]; disp(['... read_l2_smr: ',message]); return; end
  [smr_l3,status] = read_l2diag(file_id,point_name,3); 
  if (status ~= 0) l2=[]; disp(['... read_l2_smr: ',message]); return; end
end


%=== Read level 0,1,2 info into memory for T/P
%
point_name = hdfpointname(filename);
point_name = char(point_name(2,:));
%
message=['Error reading file ',filename,' (',point_name,') ... '];
[smr_l0tp,status] = read_l2tp(file_id,point_name,0); 
if (status ~= 0) l2=[]; disp(['... read_l2_smr: ',message]); return; end
[smr_l1tp,status] = read_l2tp(file_id,point_name,1); 
if (status ~= 0) l2=[]; disp(['... read_l2_smr: ',message]); return; end
[smr_l2tp,status] = read_l2tp(file_id,point_name,2); 
if (status ~= 0) l2=[]; disp(['... read_l2_smr: ',message]); return; end


%=== Read level 0,1,2 info into memory for Tb
%
if strcmpi(types,'L2D')
 
 point_name = hdfpointname(filename);
 point_name = char(point_name(3,:));
 %
 message=['Error reading file ',filename,' (',point_name,') ... '];
 [smr_l0tb,status] = read_l2tb(file_id,point_name,0);
 if (status ~= 0) l2=[]; disp(['... read_l2_smr: ',message]); return; end
 [smr_l1tb,status] = read_l2tb(file_id,point_name,1);
 if (status ~= 0) l2=[]; disp(['... read_l2_smr: ',message]); return; end
 [smr_l2tb,status] = read_l2tb(file_id,point_name,2);
 if (status ~= 0) l2=[]; disp(['... read_l2_smr: ',message]); return; end

end


%=== Display ScanNo
%
scanin = smr_l0.ScanNo;

if do_all

  i = 1:length(scanin);
  %disp('')
  %disp(['... read_l2_smr: reading inversion of all scans',...
  %      ' in orbit ',smr_l0.OrbitFilename(:,1)',' ... ']); %'

else

  i  = find(scanin == scanno);

  if isempty(i)
    disp(['... read_l2_smr: Inversion ',num2str(scanno),' is not a scan or was ',...
	  'not inverted succesfully ...']); 
    l2 = [];
    return
  end
  disp('')
  disp(['... read_l2_smr: reading inversion of scan number ',num2str(double(scanin(i))),...
        ' in orbit ',smr_l0.OrbitFilename(:,i)',' ... ']); %'
end


%=== Reading one or all scans
%
for l = i

  %=== Getting l2m structure
  %
  if     strcmpi(types,'L2P')
    [l2m] = read_l2product(smr_l0,smr_l1,smr_l2,l); 
  elseif strcmpi(types,'L2D')
    [l2m] = read_l2diagnostics(smr_l0,smr_l1,smr_l2,smr_l3,l); 
  end


  %=== Getting l2tp structure
  %
  [l2tp] = read_tp(smr_l0tp,smr_l1tp,smr_l2tp,l); 


  %=== Getting l2tb structure if L2D
  %
  if strcmpi(types,'L2D')
 
    [l2tb] = read_l2spectra(smr_l0tb,smr_l1tb,smr_l2tb,l); 

  end

  %=== Closing file 
  %
  status = hdfpt('close',file_id);

  %=== Combining into single structure
  %
  if strcmpi(types,'L2P')

    la =  struc_comb(l2m,l2tp);
    clear l2m l2tp;

  else

    la = struc_comb(l2m,l2tp,l2tb);
    clear l2m l2tp l2tb;

  end

  %=== Saving
  %
  if do_all
    l2(l) = la;
  else
    l2    = la;
  end

end

% Force longitudes to be -180<long<180 ...
if ~isempty(l2)
  %
  tmp =    ([l2.Longitude]<=180).*([l2.Longitude]    ) ... 
         + ([l2.Longitude]> 180).*([l2.Longitude]-360);
  %
  for i=1:length(tmp) 
    % 
    % Copy corrected longitudes ...
    l2(i).Longitude = tmp(i);
    % 
  end;
  %  
end

% ... also add theta (potential temperature) ...
%
if ~isempty(l2) 
  %
  for i=1:length(l2) 
    %
    % Check availibility of zpt data ...
    if (l2(i).Nzpt(1)==0) | (l2(i).Nzpt(2)==0) | (l2(i).Nzpt(3)==0) 
      disp(['... WARNING (read_l2_smr): no zpt data for scan ',num2str(double(l2(i).ScanNo)),'!']);
    else
      l2(i).theta=l2(i).ZPT(:,3).*(1013./l2(i).ZPT(:,2)).^0.2859;
    end
  end
  %
end



return


%-------------------------------------------------------------------
%
%                            SUBFUNCTIONS
%
%-------------------------------------------------------------------

%=======================================================
%
% function l2 = struc_comb(l2m,l2tp,l2tb);
%
%=======================================================

function l2 = struc_comb(l2m,l2tp,l2tb);


if ~exist('l2tb')
  do_l2tb = 0;
else
  do_l2tb = 1;
end


%=== Basic fields in l2m
%
l2  = l2m;

%=== Adding fields from l2tp
%
l2.NzptParam = l2tp.NzptParam;
l2.ZPTNames  = l2tp.ZPTNames;
l2.Nzpt      = l2tp.Nzpt;
l2.ZPT       = l2tp.ZPT;


%=== Adding fields from l2tb if diagnostics struc
%
if do_l2tb
  l2.Channels       = l2tb.Channels;
  l2.Frequencies    = l2tb.Frequencies;
  l2.TangentHeights = l2tb.TangentHeights;
  l2.BaseLineRet1   = l2tb.BaseLineRet1;
  l2.BaseLineRet2   = l2tb.BaseLineRet2;
  l2.SpectraNo      = l2tb.SpectraNo;
  l2.Measurement    = l2tb.Measurement;
  l2.Fit            = l2tb.Fit;

end

return



%========================================================
%
% function [point_names] = hdfpointname(filename)
%
% In:   filename
%
% Out:  point_names
%
% Frank Merino 2001
%
%=========================================================

function [point_names] = hdfpointname(filename)

[numpoints,pointnames] = hdfpt('inqpoint',filename);

for i = 1:numpoints
  [t,pointnames] = strtok(pointnames,',');
  point_names(i,:) = cellstr(t);
end

return


%========================================================
%
% function [smrl2,status] = read_l2prod(file_id,point_name,level)
%
% In:   file_id            HDF-EOS file id
%       pointname          the point name within the HDF-EOS file to access
%       level              point grid level
%
% Out:  smrl2              structure containing all the 'level' fields
%       status             status is -1 if the operation fails
%
% Frank Merino 2001
%
%=========================================================

function [smrl2,status] = read_l2prod(file_id,point_name,level)

if ( file_id<0 )
    error(['Error in the file id passed to read_l2prod.']);
end

[data,status] = smr_eos(file_id,point_name,level); 
if (status < 0)
  smrl2=[];
  return
end

if level == 0
   smrl2 = struct('Version1b',char(data{1}),...
                'Version2',char(data{2}),...
                'Quality',double(data{3}),...
                'Source',char(data{4}),...
                'ZPTSource',char(data{5}),...
                'OrbitFilename',char(data{6}),...
                'SunZD',double(data{7}),...
                'LST',double(data{8}),...
                'ScanNo',double(data{9}),...
                'Nspecies',double(data{10}),...
                'Day',double(data{11}),...
                'Month',double(data{12}),...
                'Year',double(data{13}),...
                'Hour',double(data{14}),...
                'Min',double(data{15}),...
                'Secs',double(data{16}),...
                'Ticks',double(data{17}),...
                'Latitude',double(data{18}),...
                'Longitude',double(data{19}),...
                'StartLat',double(data{20}),...
                'EndLat',double(data{21}),...
                'StartLong',double(data{22}),...
                'EndLong',double(data{23}),...
                'StartTan',double(data{24}),...
                'EndTan',double(data{25}),...
                'MJD',double(data{26}),....
                'Time',double(data{27}),....
                'ID1',double(data{28}));
  if (data{26} == 0) status=-1; end
elseif level == 1
   smrl2 = struct('ID1',double(data{1}),...
                'SpeciesNames',char(data{2}),...
                'Naltitudes',double(data{3}),...
                'ID2',double(data{4}));
elseif level == 2 & length(data) == 8
   smrl2 = struct('ID2',double(data{1}),...
                'Altitudes',double(data{2}),...
                'Pressures',double(data{3}),...
                'Profiles',double(data{4}),...
                'MeasError',double(data{5}),...
                'MeasResp',double(data{6}),...
                'TotalError',double(data{7}),...
                'SmoothingError',double(data{8}));

elseif level == 2 & length(data) == 7
   smrl2 = struct('ID2',double(data{1}),...
                'Altitudes',double(data{2}),...
                'Profiles',double(data{3}),...
                'MeasError',double(data{4}),...
                'MeasResp',double(data{5}),...
                'TotalError',double(data{6}),...
                'SmoothingError',double(data{7}));

end

return

%========================================================
%
% function [l2prod] = read_l2product(smr_l0,smr_l1,smr_l2,record)
%
% In:   smr_l0 :           smr level 0 data structure fields
%       smr_l1 :           smr level 1 data structure fields
%       smr_l2 :           smr level 2 data structure fields
%       scanno :           the scan number to read.
%
% Out:  l2prod             structure containing all the level 2 
%                          fields except for T/P apriori
%
% Frank Merino 2001
%
%=========================================================

function [l2prod] = read_l2product(smr_l0,smr_l1,smr_l2,record)

% information from level 0
nspecies = double(smr_l0.Nspecies(record));              % How many species were retrieved from this scan
id01 = smr_l0.ID1(record);

% information from level 1
id11 = smr_l1.ID1;
indexes1 = find(id01 == id11);
nalt = double(smr_l1.Naltitudes(:,indexes1)');       %' No. of retrieval altitudes for
                                                       % each of the retrieved species
% forming altitude index
for k=1:nspecies
  kb = sum(nalt(1:k));
  ka = kb + 1 - nalt(k);
  indalt{k} = ka:kb;
end
  
naltitudes = sum(nalt);
id12 = smr_l1.ID2(indexes1);

% information from level 2
id22 = smr_l2.ID2;


% treat error in version fields (undefined character at end) ...
Version1b = smr_l0.Version1b(:,record)';  %' 
Version2   = smr_l0.Version2(:,record)';  %'
if (length(Version1b) >= 5) Version1b = deblank(Version1b(1:5)); end;
if (length(Version2)  >= 3) Version2  = deblank(Version2(1:3));  end;

if isfield(smr_l2,'Pressures')

  l2prod = struct('Version1b',Version1b,...                         
                'Version2',Version2,...                             
                'Quality',smr_l0.Quality(record),...
                'Source',smr_l0.Source(:,record)',...              %'
                'ZPTSource',smr_l0.ZPTSource(:,record)',...         %' 
                'OrbitFilename',smr_l0.OrbitFilename(:,record)',... %'
                'SunZD',smr_l0.SunZD(record),...
                'LST',smr_l0.LST(record),...
                'MJD',smr_l0.MJD(record),...
                'Time',smr_l0.Time(record),...
                'ScanNo',smr_l0.ScanNo(record),...
                'Nspecies',smr_l0.Nspecies(record),...
                'Day',smr_l0.Day(record),...
                'Month',smr_l0.Month(record),...
                'Year',smr_l0.Year(record),...
                'Hour',smr_l0.Hour(record),...
                'Min',smr_l0.Min(record),...
                'Secs',smr_l0.Secs(record),...
                'Ticks',smr_l0.Ticks(record),...
                'Latitude',smr_l0.Latitude(record),...
                'Longitude',smr_l0.Longitude(record),...
                'StartLat',smr_l0.StartLat(record),...
                'EndLat',smr_l0.EndLat(record),...
                'StartLong',smr_l0.StartLong(record),...
                'EndLong',smr_l0.EndLong(record),...
                'StartTan',smr_l0.StartTan(record),...
                'EndTan',smr_l0.EndTan(record),...
                'SpeciesNames',smr_l1.SpeciesNames(:,indexes1)',... %'
                'Naltitudes',smr_l1.Naltitudes(:,indexes1),...
                'Altitudes',zeros(1,naltitudes),...
                'Pressures',zeros(1,naltitudes),...
                'Profiles',zeros(1,naltitudes),...
                'MeasError',zeros(1,naltitudes),...
                'MeasResp',zeros(1,naltitudes),...
                'TotalError',zeros(1,naltitudes),...
                'SmoothingError',zeros(1,naltitudes));

  for i = 1:nspecies
    indexes2 = find(id12(i) == id22);
    if length(indalt{i}) == length(indexes2) 
      l2prod.Profiles(indalt{i}) = smr_l2.Profiles(indexes2);
      l2prod.Altitudes(indalt{i}) = smr_l2.Altitudes(indexes2);
      l2prod.Pressures(indalt{i}) = smr_l2.Pressures(indexes2);
      l2prod.MeasError(indalt{i}) = smr_l2.MeasError(indexes2);
      l2prod.MeasResp(indalt{i}) = smr_l2.MeasResp(indexes2);
      l2prod.TotalError(indalt{i}) = smr_l2.TotalError(indexes2);
      l2prod.SmoothingError(indalt{i}) = smr_l2.SmoothingError(indexes2);
    end
  end

else

  l2prod = struct('Version1b',Version1b,...  
                'Version2',Version2,...     
                'Quality',smr_l0.Quality(record),...
                'Source',smr_l0.Source(:,record)',...        %'
                'ZPTSource',smr_l0.ZPTSource(:,record)',...   %' 
                'OrbitFilename',smr_l0.OrbitFilename(:,record)',... %'
                'SunZD',smr_l0.SunZD(record),...                        
                'LST',smr_l0.LST(record),...
                'MJD',smr_l0.MJD(record),...
                'Time',smr_l0.Time(record),...
                'ScanNo',smr_l0.ScanNo(record),...
                'Nspecies',smr_l0.Nspecies(record),...
                'Day',smr_l0.Day(record),...
                'Month',smr_l0.Month(record),...
                'Year',smr_l0.Year(record),...
                'Hour',smr_l0.Hour(record),...
                'Min',smr_l0.Min(record),...
                'Secs',smr_l0.Secs(record),...
                'Ticks',smr_l0.Ticks(record),...
                'Latitude',smr_l0.Latitude(record),...
                'Longitude',smr_l0.Longitude(record),...
                'StartLat',smr_l0.StartLat(record),...
                'EndLat',smr_l0.EndLat(record),...
                'StartLong',smr_l0.StartLong(record),...
                'EndLong',smr_l0.EndLong(record),...
                'StartTan',smr_l0.StartTan(record),...
                'EndTan',smr_l0.EndTan(record),...
                'SpeciesNames',smr_l1.SpeciesNames(:,indexes1)',... %'
                'Naltitudes',smr_l1.Naltitudes(:,indexes1),...
                'Altitudes',zeros(1,naltitudes),...
                'Profiles',zeros(1,naltitudes),...
                'MeasError',zeros(1,naltitudes),...
                'MeasResp',zeros(1,naltitudes),...
                'TotalError',zeros(1,naltitudes),...
                'SmoothingError',zeros(1,naltitudes));

  for i = 1:nspecies
    indexes2 = find(id12(i) == id22);
    if length(indalt{i}) == length(indexes2) 
      l2prod.Profiles(indalt{i}) = smr_l2.Profiles(indexes2);
      l2prod.Altitudes(indalt{i}) = smr_l2.Altitudes(indexes2);
      l2prod.MeasError(indalt{i}) = smr_l2.MeasError(indexes2);
      l2prod.MeasResp(indalt{i}) = smr_l2.MeasResp(indexes2);
      l2prod.TotalError(indalt{i}) = smr_l2.TotalError(indexes2);
      l2prod.SmoothingError(indalt{i}) = smr_l2.SmoothingError(indexes2);
    end
  end

end


%== Building arrays for some variables
%
auxa = l2prod.SpeciesNames;
for j=1:l2prod.Nspecies
  auxb{j} = auxa(j,:);  
end
l2prod.SpeciesNames = auxb;

auxa = l2prod.Altitudes;
for j=1:l2prod.Nspecies
  auxb{j} = auxa(indalt{j});  
end
l2prod.Altitudes = auxb;

auxa = l2prod.Profiles;
for j=1:l2prod.Nspecies
  auxb{j} = auxa(indalt{j});  
end
l2prod.Profiles = auxb;

auxa = l2prod.SmoothingError;
for j=1:l2prod.Nspecies
  auxb{j} = auxa(indalt{j});  
end
l2prod.SmoothingError = auxb;

auxa = l2prod.MeasError;
for j=1:l2prod.Nspecies
  auxb{j} = auxa(indalt{j});  
end
l2prod.MeasError = auxb;

auxa = l2prod.TotalError;
for j=1:l2prod.Nspecies
  auxb{j} = auxa(indalt{j});  
end
l2prod.TotalError = auxb;

auxa = l2prod.MeasResp;
for j=1:l2prod.Nspecies
  auxb{j} = auxa(indalt{j});  
end
l2prod.MeasResp = auxb;


return




%========================================================
%
% function [smrl2,status] = read_l2diag(file_id,point_name,level)
%
% In:   file_id            file id
%       pointname          point name
%       level              point grid level
%
% Out:  smrl2              structure containing all the 'level' fields
%       status             status is -1 if the operation fails
%
% Frank Merino 2001
%
%=========================================================

function [smrl2,status] = read_l2diag(file_id,point_name,level)

if ( file_id<0 )
    error(['Error in the file id passed to read_l2diag.']);
end

[data,status] = smr_eos(file_id,point_name,level);
if (status < 0)
  smrl2=[];
  return
end


if level == 0
   smrl2 = struct('Version1b',char(data{1}),...
                'Version2',char(data{2}),...
                'Quality1',double(data{3}),...
                'Quality2',double(data{4}),...
                'Source',char(data{5}),...
                'ZPTSource',char(data{6}),...
                'OrbitFilename',char(data{7}),...
                'SunZD',double(data{8}),...
                'LST',double(data{9}),...
                'ScanNo',double(data{10}),...
                'TotalScanNo',double(data{11}),...
                'AskScans',double(data{12}),...
                'Nspecies',double(data{13}),...
                'Day',double(data{14}),...
                'Month',double(data{15}),...
                'Year',double(data{16}),...
                'Hour',double(data{17}),...
                'Min',double(data{18}),...
                'Secs',double(data{19}),...
                'Ticks',double(data{20}),...
                'PointOffset',double(data{21}),...
                'Chi2Meas',double(data{22}),...
                'Chi2Apriori',double(data{23}),...
                'Latitude',double(data{24}),...
                'Longitude',double(data{25}),...
                'StartLat',double(data{26}),...
                'EndLat',double(data{27}),...
                'StartLong',double(data{28}),...
                'EndLong',double(data{29}),...
                'StartTan',double(data{30}),...
                'EndTan',double(data{31}),...
                'MaxOpacity',double(data{32}),...
                'ArtNoise',double(data{33}),...
                'Marquardt',double(data{34}),...
                'MarqConverged',double(data{35}),...
                'FreqShift',double(data{36}),...
                'Iter',double(data{37}),...
                'Ntangents',double(data{38}),...
                'Chi2',double(data{39}),...
                'BaseLine',char(data{40}),...
                'BinMode',char(data{41}),...
                'ClimCon',char(data{42}),...
                'MJD',double(data{43}),...
                'Time',double(data{44}),...
                'ID1',double(data{45}));
elseif level == 1
   smrl2 = struct('ID1',double(data{1}),...
                'SpeciesNames',char(data{2}),...
                'Naltitudes',double(data{3}),...
                'ID2',double(data{4}));
elseif level == 2
    
  if length(data) == 7          % see qsmr_write_l2 
  smrl2 = struct('ID2',double(data{1}),...
                 'Altitudes',double(data{2}),...
                 'Profiles',double(data{3}),...
                 'AprioriProf',double(data{4}),...
                 'AprioriUncert',double(data{5}),...
                 'MeasResp',double(data{6}),...
                 'ID3',double(data{7}));
  elseif length(data) == 8  
  smrl2 = struct('ID2',double(data{1}),...
                 'Altitudes',double(data{2}),...
                 'Pressures',double(data{3}),...
                 'Profiles',double(data{4}),...
                 'AprioriProf',double(data{5}),...
                 'AprioriUncert',double(data{6}),...
                 'MeasResp',double(data{7}),...
                 'ID3',double(data{8}));
  end    

elseif level == 3
   smrl2 = struct('ID3',double(data{1}),...
                'MeasError',double(data{2}),...
                'SmoothingError',double(data{3}),...
                'AverKernels',double(data{4}));

end

return

%========================================================
%
% function [l2diag] = read_l2diagnostics(smr_l0,smr_l1,smr_l2,smr_l3,record)
%
% In:   smr_l0 :           smr level 0 data structure fields
%       smr_l1 :           smr level 1 data structure fields
%       smr_l2 :           smr level 2 data structure fields
%       smr_l3 :           smr level 3 data structure fields
%       scanno :           the scan number to read.
%
% Out:  l2diag             structure containing all the level 2 diagnostics
%                          fields except for the T/P apriori
%
% Frank Merino 2001
%
%=========================================================
function [l2diag] = read_l2diagnostics(smr_l0,smr_l1,smr_l2,smr_l3,record)


% information from level 0
nspecies = smr_l0.Nspecies(record);      % How many species were retrieved from this scan
id01 = smr_l0.ID1(record);

% information from level 1
id11 = smr_l1.ID1;
indexes1 = find(id01 == id11);
nalt = double(smr_l1.Naltitudes(:,indexes1)');       %' No. of retrieval altitudes for
                                                       % each of the retrieved species
% forming altitude index
for k=1:nspecies
  kb = sum(nalt(1:k));
  ka = kb + 1 - nalt(k);
  indalt{k} = ka:kb;
end  
naltitudes = sum(nalt);

% information from level 2
id12 = smr_l1.ID2(indexes1);
id22 = smr_l2.ID2;


% information from level 3
id33 = smr_l3.ID3;


% treat error in version fields (undefined character at end) ...
Version1b = smr_l0.Version1b(:,record)';%'
Version2   = smr_l0.Version2(:,record)';%'
if (length(Version1b) >= 5) Version1b = deblank(Version1b(1:5)); end;
if (length(Version2)  >= 3) Version2  = deblank(Version2(1:3));  end;

l2diag = struct('Version1b',Version1b,...  
                'Version2',Version2,...    
                'Quality1',smr_l0.Quality1(record),...
                'Quality2',smr_l0.Quality2(record),...
                'Source',smr_l0.Source(:,record)',...        %'
                'ZPTSource',smr_l0.ZPTSource(:,record)',...  %' 
                'OrbitFilename',smr_l0.OrbitFilename(:,record)',... %'
                'SunZD',smr_l0.SunZD(record),...
                'LST',smr_l0.LST(record),...
                'MJD',smr_l0.MJD(record),...
                'Time',smr_l0.Time(record),...
                'ScanNo',smr_l0.ScanNo(record),...
                'TotalScanNo',smr_l0.TotalScanNo(record),...
                'AskScans',smr_l0.AskScans(:,record)',...    %'
                'Nspecies',smr_l0.Nspecies(record)',...      %'
                'Day',smr_l0.Day(record),...
                'Month',smr_l0.Month(record),...
                'Year',smr_l0.Year(record),...
                'Hour',smr_l0.Hour(record),...
                'Min',smr_l0.Min(record),...
                'Secs',smr_l0.Secs(record),...
                'Ticks',smr_l0.Ticks(record),...
                'PointOffset',smr_l0.PointOffset(record),...
                'Chi2Meas',smr_l0.Chi2Meas(record),...
                'Chi2Apriori',smr_l0.Chi2Apriori(record),...
                'Latitude',smr_l0.Latitude(record),...
                'Longitude',smr_l0.Longitude(record),...
                'StartLat',smr_l0.StartLat(record),...
                'EndLat',smr_l0.EndLat(record),...
                'StartLong',smr_l0.StartLong(record),...
                'EndLong',smr_l0.EndLong(record),...
                'StartTan',smr_l0.StartTan(record),...
                'EndTan',smr_l0.EndTan(record),...
                'MaxOpacity',smr_l0.MaxOpacity(record),...
                'ArtNoise',smr_l0.ArtNoise(record),...
                'Marquardt',smr_l0.Marquardt(record),...
                'MarqConverged',smr_l0.MarqConverged(record),...
                'FreqShift',smr_l0.FreqShift(record),...
                'Iter',smr_l0.Iter(record),...
                'Ntangents',smr_l0.Ntangents(record),...
                'Chi2',smr_l0.Chi2(record),...
                'BaseLine',smr_l0.BaseLine(:,record)',...         %'
                'BinMode',smr_l0.BinMode(:,record)',...            %'
                'ClimCon',smr_l0.ClimCon(:,record)',...             %'
                'SpeciesNames',smr_l1.SpeciesNames(:,indexes1)',... %'
                'Naltitudes',smr_l1.Naltitudes(:,indexes1),...
                'Altitudes',zeros(1,naltitudes),...
                'Pressures',zeros(1,naltitudes),...
                'AprioriUncert',zeros(1,naltitudes),...
                'AprioriProf',zeros(1,naltitudes),...
                'Profiles',zeros(1,naltitudes),...
                'MeasError',zeros(naltitudes,naltitudes),...
                'MeasResp',zeros(1,naltitudes),...
                'SmoothingError',zeros(naltitudes,naltitudes),...
                'AverKernels',zeros(naltitudes,naltitudes));

for i = 1:length(id12) % number of retrieved species
   indexes2 = find(id12(i) == id22);
   l2diag.Profiles(indalt{i}) = smr_l2.Profiles(indexes2);
   l2diag.Altitudes(indalt{i}) = smr_l2.Altitudes(indexes2);
   l2diag.AprioriUncert(indalt{i}) = smr_l2.AprioriUncert(indexes2);
   l2diag.AprioriProf(indalt{i}) = smr_l2.AprioriProf(indexes2);
   l2diag.MeasResp(indalt{i}) = smr_l2.MeasResp(indexes2);

     if isfield(smr_l2,'Pressures') % check if the field exists 
     l2diag.Pressures(indalt{i}) = smr_l2.Pressures(indexes2);
     end
   
   id23 = smr_l2.ID3(indexes2);

   for j=  1:length(id23)  % number of altitudes
      indexes3 = find(id23(j) == id33);

      %ind = (i-1) * length(id23) + j   % this stupid error implemented by someone cost me several hours :-( 
      ind=indalt{i}(j);
      l2diag.MeasError(:,ind) = smr_l3.MeasError(indexes3);
      l2diag.SmoothingError(:,ind) = smr_l3.SmoothingError(indexes3);
      l2diag.AverKernels(:,ind) = smr_l3.AverKernels(indexes3);
      
   end 

end

% rearrange arrays above 
auxa = l2diag.AverKernels;
for j=1:l2diag.Nspecies
  auxb{j} = auxa(indalt{j},indalt{j});  
end
l2diag.AverKernels = auxb;

auxa = l2diag.MeasError;
for j=1:l2diag.Nspecies
  auxb{j} = auxa(indalt{j},indalt{j});  
end
l2diag.MeastError = auxb;

auxa = l2diag.SmoothingError;
for j=1:l2diag.Nspecies
  auxb{j} = auxa(indalt{j},indalt{j});  
end
l2diag.SmoothingError = auxb;


%== Buliding arrays for some variables
%
auxa = l2diag.SpeciesNames;
for j=1:l2diag.Nspecies
  auxb{j} = auxa(j,:);  
end
l2diag.SpeciesNames = auxb;

auxa = l2diag.Altitudes;
for j=1:l2diag.Nspecies
  auxb{j} = auxa(indalt{j});  
end
l2diag.Altitudes = auxb;

auxa = l2diag.Pressures;
for j=1:l2diag.Nspecies
  auxb{j} = auxa(indalt{j});  
end
l2diag.Pressures = auxb;

auxa = l2diag.Profiles;
for j=1:l2diag.Nspecies
  auxb{j} = auxa(indalt{j});  
end
l2diag.Profiles = auxb;

auxa = l2diag.MeasResp;
for j=1:l2diag.Nspecies
  auxb{j} = auxa(indalt{j});  
end
l2diag.MeasResp = auxb;

auxa = l2diag.AprioriUncert;
for j=1:l2diag.Nspecies
  auxb{j} = auxa(indalt{j});  
end
l2diag.AprioriUncert = auxb;

auxa = l2diag.AprioriProf;
for j=1:l2diag.Nspecies
  auxb{j} = auxa(indalt{j});  
end
l2diag.AprioriProf = auxb;

%%

return


%========================================================
%
% function [data_eos,status] = read_l2tp(file_id,point_name,level)
%
% In:   file_id            file id
%       pointname          point name
%       level              point grid level
%
% Out:  data_eos           structure containing all the level 0 fields
%       status             status is -1 if the operation fails
%
% Frank Merino 2001
%
%=========================================================

function [data_eos,status] = read_l2tp(file_id,point_name,level)

if ( file_id<0 )
    error(['Error in the file id passed to read_l2tp.']);
end

[data,status] = smr_eos(file_id,point_name,level);
if (status < 0)
  data_eos=[];
  return
end

if level == 0
   data_eos = struct('ScanNo',double(data{1}),...
                'NzptParam',double(data{2}),...
                'Latitude',double(data{3}),...
                'Longitude',double(data{4}),...
                'ID1',double(data{5}));
elseif level == 1
   data_eos = struct('ID1',double(data{1}),...
                'ZPTNames',char(data{2}),...
                'Nzpt',double(data{3}),...
                'ID2',double(data{4}));
elseif level == 2
   data_eos = struct('ID2',double(data{1}),...
                    'ZPT',double(data{2}));
end

return


%========================================================
%
% function [l2tp] = read_tp(smr_l0,smr_l1,smr_l2,record)
%
% In:   smr_l0 :           smr level 0 data structure fields
%       smr_l1 :           smr level 1 data structure fields
%       smr_l2 :           smr level 2 data structure fields
%       scanno :           the scan number to read.
%
% Out:  l2tp          T/P apriori fields
%
% Frank Merino 2001
%
%=========================================================

function [l2tp] = read_tp(smr_l0,smr_l1,smr_l2,record)

% information from level 0
%
nspecies = double(smr_l0.NzptParam(record)); % How many species were retrieved from this scan
id01 = smr_l0.ID1(record);

% information from level 1
%
indexes = find(id01 == smr_l1.ID1);
id12    = smr_l1.ID2(indexes);

% information from level 2
%
indexes_altitude    = find(id12(1) == smr_l2.ID2);    % altitude
indexes_pressure    = find(id12(2) == smr_l2.ID2);    % pressure
indexes_temperature = find(id12(3) == smr_l2.ID2);    % temperature

% smr_l0.ScanNo(record); 
% Check and correct number of altitudes for ZPT profiles ... (...to be verified...) 
smr_l1.Nzpt(:,indexes) = [length(indexes_altitude),length(indexes_pressure),length(indexes_temperature)];
naltitudes = double(smr_l1.Nzpt(:,indexes)');  %' Get the number of retrieval altitudes for ZPT

l2tp = struct('ScanNo',smr_l0.ScanNo(record),...
             'NzptParam',smr_l0.NzptParam(record),...
             'Latitude',smr_l0.Latitude(record),...
             'Longitude',smr_l0.Longitude(record),...
             'ZPTNames',smr_l1.ZPTNames(:,indexes)',...     %' should always be, altitude, pressure and temperature
             'Nzpt',smr_l1.Nzpt(:,indexes),...
             'ZPT',zeros(nspecies,naltitudes(1)));

if (length(indexes_altitude) > 0) & (length(indexes_pressure) > 0) & (length(indexes_temperature) > 0)
  l2tp.ZPT(1,:) = smr_l2.ZPT(indexes_altitude(1:naltitudes(1)));
  l2tp.ZPT(2,:) = smr_l2.ZPT(indexes_pressure(1:naltitudes(2)));
  l2tp.ZPT(3,:) = smr_l2.ZPT(indexes_temperature(1:naltitudes(3)));
end

l2tp.ZPT= l2tp.ZPT'; %'

auxa = l2tp.ZPTNames;
for j=1:3
  auxb{j} = auxa(j,:);  
end
l2tp.ZPTNames = auxb;


return


%========================================================
%
% function [data_eos,status] = read_l2tb(file_id,point_name,level)
%
% In:   file_id            file id
%       pointname          point name
%       level              point grid level
%
% Out:  data_eos           structure containing all the level 0 fields
%       status             status is -1 if the operation fails
%
% Frank Merino 2001
%
%=========================================================

function [data_eos,status] = read_l2tb(file_id,point_name,level)

if ( file_id<0 )
    error(['Error in the file id passed to read_l2tb.']);
end

[data,status] = smr_eos(file_id,point_name,level);
if (status < 0)
  data_eos=[];
  return
end

if level == 0
   data_eos = struct('ScanNo',double(data{1}),...
                'Ntangents',double(data{2}),...
                'Latitude',double(data{3}),...
                'Longitude',double(data{4}),...
                'Frequencies',double(data{5}),...
                'Channels',double(data{6}),...
                'ID1',double(data{7}));
elseif level == 1
   data_eos = struct('ID1',double(data{1}),...
                'TangentHeights',double(data{2}),...
                'SpectraNo',double(data{3}),...
                'BaseLineRet1',double(data{4}),...
                'BaseLineRet2',double(data{5}),...
                'ID2',double(data{6}));
elseif level == 2
   data_eos = struct('ID2',double(data{1}),...
                'Measurement',double(data{2}),...
                'Fit',double(data{3}));
end

return

%========================================================
%
% function [l2tb] = read_l2spectra(smr_l0,smr_l1,smr_l2,record)
%
% In:   smr_l0 :           smr level 0 data structure fields
%       smr_l1 :           smr level 1 data structure fields
%       smr_l2 :           smr level 2 data structure fields
%       record :           the scan number to read.
%
% Out:  l2tb               Temperature brightness fields
%
% Frank Merino 2001
%
%=========================================================

function [l2tb] = read_l2spectra(smr_l0,smr_l1,smr_l2,record)

% information from level 0
ntangents = smr_l0.Ntangents(record);   % How many tangent altitudes in this scan
id01 = smr_l0.ID1(record);

% information from level 1
indexestan = find(id01 == smr_l1.ID1);
id12 = smr_l1.ID2(indexestan);

% information from level 2
nid12 = length(id12);

for i = 1:nid12  % each tangent height
   indexes  = find(id12(i) == smr_l2.ID2);  % all channels
   Measurement(:,i)  = smr_l2.Measurement(indexes)';
   Fit(:,i) = smr_l2.Fit(indexes)';
end

% information from level 2

l2tb = struct('ScanNo',smr_l0.ScanNo(record),...
                'Ntangents',smr_l0.Ntangents(record),...
                'Latitude',smr_l0.Latitude(record),...
                'Longitude',smr_l0.Longitude(record),...
                'Frequencies',smr_l0.Frequencies(:,record)',... %'
                'Channels',smr_l0.Channels(record),...           
                'TangentHeights',smr_l1.TangentHeights(:,indexestan),...  
                'BaseLineRet1',smr_l1.BaseLineRet1(:,indexestan),...         
                'BaseLineRet2',smr_l1.BaseLineRet2(:,indexestan),...         
                'SpectraNo',smr_l1.SpectraNo(:,indexestan),...         
                'Measurement',Measurement,...
                'Fit',Fit);


return


%========================================================
%
% function [data,status] = smr_eos(file_id,point_name)
%
% In:   file_id            file id
%       pointname          point name
%       level              point grid level
%
% Out:  data               data
%       status             status is -1 if the operation fails
%
% Frank Merino 1999
%
%=========================================================

function [data,status] = smr_eos(file_id,point_name,level)

point_id = hdfpt('attach',file_id,point_name);
nrecs = hdfpt('nrecs',point_id,level);
records   = 0:nrecs-1;
[numfields,fieldlist,fieldtype,fieldorder] = hdfpt('levelinfo',point_id,level);
if ~isempty(fieldlist)
  [data,status] = hdfpt('readlevel',point_id,level,fieldlist,records);
else
  data=[];
  status=-1;
  return
end
status = hdfpt('detach',point_id);

return
