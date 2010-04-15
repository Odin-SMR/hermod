function SMR_501hdf_read(orbits,backward,forward)

% Program modified and function file written 2008-11-06 by Marcus Jansson

% Program to read and select species from Odin SMR data directly from and HDF file
% 
% orbits contains all the orbits for this run of the m-file
% backward contains the overlapping orbits where the first part of the
%   orbit is not going to be saved
% forward contains the overlapping orbits where the last part of the
%   orbit is not going to be saved


%defines directories where .mat files are stored
outputpath_clo='/odin/extdata/SMR/ClO_2_1/';
outputpath_n2o='/odin/extdata/SMR/N2O_2_1/';
outputpath_o3='/odin/extdata/SMR/Ozone_501_2_1/';


if ~exist(outputpath_clo)
    mkdir([outputpath_clo]);
end
if ~exist(outputpath_n2o)
    mkdir([outputpath_n2o]);
end
if ~exist(outputpath_o3)    
    mkdir([outputpath_o3]);
end
%the path to SMR 501GHz v2.1 data
data_path='/odin/smr/Data/SMRl2/SMRhdf/Qsmr-2-1/SM_AC2ab/';

date=0;

%defines the potential temperature levels used for vertical coordinate in
%the .mat files
d_ept=25;
ept=[400:d_ept:1000];
PotT=ept;

%initializes the matlab data fields
ClO=[];
ClO_QUALITY=[];
ClO_QUALITY_meas=[];
ClO_measresp=[];

O3=[];
O3_QUALITY=[];
O3_QUALITY_meas=[];
O3_measresp=[];

N2O=[];
N2O_QUALITY=[];
N2O_QUALITY_meas=[];
N2O_measresp=[];

Nalt=[]; Nalt2=[];

tidmat=[];
longmat=[];
latmat=[];

ScL=0;

%orbit numbers for the SMR data files
hexorb=dec2hex(orbits,4);


for orbit=1:length(orbits)
    filename=['SCH_5018_C' hexorb(orbit,:) '_021.L2P'];

    file=[data_path filename];
    
    if exist(file)==2
    l2=read_l2_smr(file);
       
    scan=size(l2,2);
    for i=1:scan
       ScL=ScL+1;
       L=l2(i);


       %stores the data in .mat format if the current satellite scan comes
       %from the following day
       if floor(L.MJD)>date 
 
          if (not(isempty(O3)) && isempty(find(backward==orbits(orbit)))) % Overlapping orbit 
             mjd2utc(L.MJD);
             
             [year, month, day]=mjd2utc(date); year=year-2000;
             
             %saves data in .mat format
             
             eval(['save ' outputpath_clo 'OdinSMR_ClO_501_' num2str(year,'%02d') num2str(month,'%02d') ...
                    num2str(day,'%02d') '.mat ClO ClO_QUALITY ClO_QUALITY_meas ClO_measresp PotT tidmat longmat latmat Nalt']);
                
             Nalt=Nalt2;
             eval(['save ' outputpath_o3 'OdinSMR_O3_501_' num2str(year,'%02d') num2str(month,'%02d') ...
                    num2str(day,'%02d') '.mat O3 O3_QUALITY O3_QUALITY_meas O3_measresp PotT tidmat longmat latmat Nalt']);
             
             Nalt=Nalt3;
             
             eval(['save ' outputpath_n2o 'OdinSMR_N2O_501_' num2str(year,'%02d') num2str(month,'%02d') ...
                    num2str(day,'%02d') '.mat N2O N2O_QUALITY N2O_QUALITY_meas N2O_measresp PotT tidmat longmat latmat Nalt']);
            
          end

          %sets a new date
          date=floor(L.MJD);

          %initializes data fields
          ClO=[];
          ClO_QUALITY=[];
          ClO_QUALITY_meas=[];
          ClO_measresp=[];

          O3=[];
          O3_QUALITY=[];
          O3_QUALITY_meas=[];
          O3_measresp=[];

          N2O=[];
          N2O_QUALITY=[];
          N2O_QUALITY_meas=[];
          N2O_measresp=[];


          Nalt=[]; Nalt2=[]; Nalt3=[];

          tidmat=[];
          longmat=[];
          latmat=[];
       end

       
       % satellite profiles are not stored if they have bad Quality or
       % fewer than 16 vertical levels
       if L.Quality==0 && L.Naltitudes(1)>15 
           clo=L.Profiles{1}; %vmr
           clo_measresp=L.MeasResp{1};
           
           n2o=L.Profiles{3}; %vmr
           n2o_measresp=L.MeasResp{3};

           o3=L.Profiles{2}; %vmr
           o3_toterr=L.TotalError{2};
           o3_measerr=L.MeasError{2};
           
           o3_measresp=L.MeasResp{2};
           altitude=L.ZPT(:,1);%km
           pressure=L.ZPT(:,2);%Hpa
           temp=L.ZPT(:,3);%K
           
           temp1=interp1(altitude',temp',L.Altitudes{1},'nearest');
           temp2=interp1(altitude',temp',L.Altitudes{2},'nearest');
           temp3=interp1(altitude',temp',L.Altitudes{3},'nearest');
           
           pressure1=interp1(altitude',pressure',L.Altitudes{1},'nearest');
           pressure2=interp1(altitude',pressure',L.Altitudes{2},'nearest');
           pressure3=interp1(altitude',pressure',L.Altitudes{3},'nearest');
           
           Theta1 =temp1.*(1000./pressure1).^(287/1024);
           Theta2 =temp2.*(1000./pressure2).^(287/1024);
           Theta3 =temp3.*(1000./pressure3).^(287/1024);

I_Theta2=find(not(isnan(Theta2)));
o3=o3(I_Theta2); Theta2=Theta2(I_Theta2);
o3_measresp=o3_measresp(I_Theta2);

o3toterr=L.TotalError{2};
o3measerr=L.MeasError{2};
o3toterr=o3toterr(I_Theta2);
o3measerr=o3measerr(I_Theta2);
          
           
           
           if isempty(find(diff(Theta2)==0)) && isempty(find(diff(Theta3)==0))
               ClO=[ClO; interp1(Theta1,clo,ept)]; % ppv
               ClO_QUALITY=[ClO_QUALITY; interp1(Theta1,L.TotalError{1},ept)];
               
               ClO_QUALITY_meas=[ClO_QUALITY_meas; interp1(Theta1,L.MeasError{1},ept)];
               ClO_measresp=[ClO_measresp; interp1(Theta1,clo_measresp,ept)];
               
               N2O=[N2O; interp1(Theta3,n2o,ept)]; % ppv
               N2O_QUALITY=[N2O_QUALITY; interp1(Theta3,L.TotalError{3},ept)];
               
               N2O_QUALITY_meas=[N2O_QUALITY_meas; interp1(Theta3,L.MeasError{3},ept)];
               N2O_measresp=[N2O_measresp; interp1(Theta3,n2o_measresp,ept)];
               
               O3=[O3; interp1(Theta2,o3,ept)]; % ppv
               O3_QUALITY=[O3_QUALITY; interp1(Theta2,o3toterr,ept)];
               
               O3_QUALITY_meas=[O3_QUALITY_meas; interp1(Theta2,o3measerr,ept)];
               O3_measresp=[O3_measresp; interp1(Theta2,o3_measresp,ept)];
               
               Nalt=[Nalt; L.Naltitudes(1)];
               Nalt2=[Nalt2; L.Naltitudes(2)];
               Nalt3=[Nalt3; L.Naltitudes(3)];
               
               longmat=[longmat; L.Longitude];
               latmat=[latmat; L.Latitude];
               tidmat=[tidmat; L.MJD];
           end
       end
    end
    end
end

if isempty(find(forward==orbits(orbit))) % Overlapping orbit
    [year, month, day]=mjd2utc(date); year=year-2000;

    eval(['save ' outputpath_clo 'OdinSMR_ClO_501_' num2str(year,'%02d') num2str(month,'%02d') ...
       num2str(day,'%02d') '.mat ClO ClO_QUALITY ClO_QUALITY_meas ClO_measresp tidmat longmat latmat Nalt2']); 

    eval(['save ' outputpath_o3 'OdinSMR_O3_501_' num2str(year,'%02d') num2str(month,'%02d') ...
       num2str(day,'%02d') '.mat O3 O3_QUALITY O3_QUALITY_meas O3_measresp tidmat longmat latmat Nalt']);

    eval(['save ' outputpath_n2o 'OdinSMR_N2O_501_' num2str(year,'%02d') num2str(month,'%02d') ...
       num2str(day,'%02d') '.mat N2O N2O_QUALITY N2O_QUALITY_meas N2O_measresp tidmat longmat latmat Nalt']);
end
