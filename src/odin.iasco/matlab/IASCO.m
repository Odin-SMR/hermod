function IASCO(vDays, vLevels, sSpecies)

% Fast Isentropic Assimilation model for StratospheriC Ozone
% Function file written by Marcus & Erik 2008-09-11
%
%
%   function IASCO_func(vDays, vLevels, sSpecies, sWind_path, sSpecies_path, sSave_path)
% Inputs: vDays, vLevels, sSpecies, sWind_path, sSpecies_path, sSave_path.
% 1. vDays = The days over which the model is run, in Modified Julian
% Dates. Defined as a vector
% 2. vLevels = The potential temperature levels used in the model. Defined
% between 400 K and 1000 K with a step of 25 K. E.g. vLevels = [1 2 3]
% means 400 K, 425 K, 450 K. Defined as a vector.
% 3. sSpecies = The species of the simulation. Can be set to H2O, HNO3,
% N2O or O3_501 and O3_544 (501 and 544 defines the frequency bands). Defined as a string.
%
%
% Example: IASCO_func([52183:54465],[4 6 9],'O3_501') 
% will simulate between the days 2001-10-01 and 2007-12-31 at the potential 
% temperature levels 475 K, 525 K and 600 K for O3 (510Hz band). 

%NN is normally set to 1. Doubles the number of latitudes and longitudes and
%halves the timestep if set to 2.
NN=1;

%Set the days over which the model is run. In Modified Julian Dates.
sim_days=vDays;

%Set the vertical levels
sim_levels=vLevels; 
%Do not touch!!
ept=400:25:1000; 
ept=ept(sim_levels);
ept2=ept;

%Set the path to the satellite data
data_path=find_path('DATA_DIR')
save_path=find_path('LEVEL3_DIR')
switch sSpecies 
    case 'H2O'
        path_species=[data_path 'H2O_2_0/OdinSMR_H2O_544_'];
        path_savefields=[save_path 'DATA/H2O/']; 
        mkdir(path_savefields);
        SPECIES=sSpecies;
    case 'O3_544'
        path_species=[data_path 'Ozone_544_2_0/OdinSMR_O3_544_'];
        path_savefields=[save_path 'DATA/O3_544/'];
        mkdir(path_savefields);
        SPECIES=sSpecies(1:2);
    case 'HNO3'
        path_species=[data_path 'HNO3_2_0/OdinSMR_HNO3_544_'];
        path_savefields=[save_path 'DATA/HNO3/'];
        mkdir(path_savefields);
        SPECIES=sSpecies;
    case 'O3_501'
        path_species=[data_path 'Ozone_501_2_1/OdinSMR_O3_501_']; 
        path_savefields=[save_path 'DATA/O3_501/'];
        mkdir(path_savefields);
        SPECIES=sSpecies(1:2);
    case 'N2O'
        path_species=[data_path 'N2O_2_1/OdinSMR_N2O_501_'];
        path_savefields=[save_path 'DATA/N2O/'];
        mkdir(path_savefields);
        SPECIES=sSpecies;
    otherwise
        error('Undefined species')
end
%Set the variable name in the .mat satellite data files. I use H2O, O3, HNO3, N2O

%Set to 1 if tracer fields are to be saved or set to 0 if not.
save_tracerfields=1;


%Defines the path to the wind fields
path_winds = find_path('WIND2_DIR'); 
name_winds = '/winds2_';


%Do not touch!! Number of latitudes and longitudes in the model grid. 
N_Lat=80*NN;
N_Long=160*NN;

%Do not touch!! Grid spacing in degrees
D_ft=2.25/NN;

%Do not touch!!
if NN==1
   Latitudes=[88.875:-2.25:-89]';
   Longitudes=[-178.875:2.25:178.875]';
elseif NN==2
   Latitudes=[89.4375:-1.125:-89.4375]';
   Longitudes=[-179.4375:1.125:179.4375]';
end


%Do not touch!!Time step in minutes
dt=10/NN;



%Limits the first and second order moments in the Prather advection scheme.
if  sum(SPECIES)==sum('H2O')
   lim_x=5e-7;       
   lim_xx=2.5e-7;
elseif  sum(SPECIES)==sum('O3')
   lim_x=10e-7;       
   lim_xx=5e-7;
elseif  sum(SPECIES)==sum('HNO3')    
   lim_x=3e-9;       
   lim_xx=1.5e-9; 
elseif  sum(SPECIES)==sum('N2O')    
   lim_x=100e-9;       
   lim_xx=50e-9; 
end    
  


%Used to filter out data with to high mixing ratio. Set to very large value
%othervise.
max_mixingratio=10e-6;


%Used to filter out data with lower measurement response. 
MeasResp_Limit=0.7;


%Assimilation radius of influence. Defines the model correlation length. The unit is number of grid points.
L_ass=3*NN;


%Defines the area for assimilation around one data point
Rad_ass=ceil(3*L_ass);

II_dx=[];
II_dy=[];
for i=-Rad_ass:Rad_ass
   for j=-Rad_ass:Rad_ass
      if (i^2+j^2)<Rad_ass^2
         II_dx=[II_dx; j];
         II_dy=[II_dy; i];
      end
   end
end

%Search for the the last day earlier than the first assimilation day with
%assimilated values to load
mjd=vDays(1);
mjd=mjd-1;
[year month day] = mjd2utc(mjd);
last_file = [path_savefields num2str(year) '/' num2str(month) '/' sSpecies '_' num2str(mjd) '_00.mat'];
last_file_exist=1;
while ~exist(last_file,'file')
    mjd=mjd-1;
    [year month day] = mjd2utc(mjd);
    if year<2001
        last_file_exist=0;
        mjd=vDays(1)-1;
        break;
    end
    last_file = [path_savefields num2str(year) '/' num2str(month) '/' sSpecies '_' num2str(mjd) '_00.mat'];
end

sim_days=[mjd:sim_days(end)];


%Obtains a flat initial field by averaging the tracer data for 10 days
OOO=[];
for i=[52183:52192]%%% These dates are chosen instead of sim_days(1:10) to avoid the 10 days minimum of the assimilation days. A change of these days to e.g. [54183:54192] didn't result in any visible differences in the pictures. 
    [utcyear,utcmonth,utcday]=mjd2utc(i); utcyear=utcyear-2000;
    if exist([path_species num2str(utcyear,'%02d') num2str(utcmonth,'%02d') num2str(utcday,'%02d') '.mat']); 
        
        eval(['load ' path_species num2str(utcyear,'%02d') num2str(utcmonth,'%02d') num2str(utcday,'%02d') '.mat']);
        %data_levels=interp1(PotT,1:length(PotT),ept2,'nearest');
        [dummy, data_levels]=intersect(PotT,[400:25:1000]);
          
        eval(['OOO=[OOO;' SPECIES '];' ]);
    end
end 

OOO(find(OOO(:)>max_mixingratio))=nan;
O3QQ=nanmean(OOO);

ERQQ=nanstd(OOO);




%Defines initial fields
S0=zeros(N_Lat,N_Long,length(sim_levels));
Err=S0;
for i=1:length(sim_levels)
    S0(:,:,i)=O3QQ(sim_levels(i));
    Err(:,:,i)=0.33*ERQQ(sim_levels(i));
end


if last_file_exist
    %It is possible to load a saved field and use it as initial field
    %disp(['Using initial field from file: ' last_file])
    load(last_file) 
    S0=double(TracerField_u16)*K_TracerField;
    Err=double(Err_u16)*K_Err;
end

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%





%Initializes first and second order moments used in the Prather advection
%scheme
Sx=zeros(size(S0)); Sy=Sx;  Sxy=Sx; Sxx=Sx; Syy=Sx;
S0R=Sx; SxR=Sx; SyR=Sx;  SxyR=Sx; SxxR=Sx; SyyR=Sx;
S0L=Sx; SxL=Sx; SyL=Sx;  SxyL=Sx; SxxL=Sx; SyyL=Sx;



%Loads wind fields. A is zonal winds and B is meridional winds.
A=zeros(N_Lat,N_Long,length(ept)); B=zeros(N_Lat,N_Long,length(ept));

[a b c]=mjd2utc(sim_days(1)); a=a-2000;
zon_wind=[];
mer_wind=[];
for i=1:length(sim_levels)
   eval(['load ' path_winds num2str(a,'%02d') '/' num2str(b,'%02d') name_winds num2str(a,'%02d') num2str(b,'%02d') num2str(c,'%02d') '.0.' num2str(ept(i)) '.mat']);
   
   if NN==1
      A(:,:,i)=zon_wind(2:2:end,1:2:end)*60*dt/40e6*N_Long./cos(repmat(Latitudes/180*pi,1,N_Long));
      B(:,:,i)=mer_wind(2:2:end,2:2:end)*60*dt/20e6*N_Lat;
   elseif NN==2    
      A(:,:,i)=(zon_wind(1:end-1,:)+zon_wind(2:end,:))/2*60*dt/40e6*N_Long./cos(repmat(Latitudes/180*pi,1,N_Long));
      B(:,:,i)=(mer_wind(1:end-1,:)+mer_wind(2:end,:))/2*60*dt/20e6*N_Lat;
   end
   
   A(1,:,i)=0; A(end,:,i)=0;
   B(end,:,i)=(B(end,:,i)-abs(B(end,:,i)))/2;
end
 
  
   

%Finds coordinates for upwind and downwind gridboxes.
Iap=find(A>=0);
Ial=Iap-N_Lat; 
Ial(find(rem(floor((Iap-1)/N_Lat),N_Long)==0))= ...
    Iap(find(rem(floor((Iap-1)/N_Lat),N_Long)==0))+N_Lat*(N_Long-1);

           
Ian=find(A<0);
Iar=Ian+N_Lat; 
Iar(find(rem(floor((Ian-1)/N_Lat),N_Long)==(N_Long-1)))= ...
    Ian(find(rem(floor((Ian-1)/N_Lat),N_Long)==(N_Long-1)))-N_Lat*(N_Long-1);

A(Ian)=-A(Ian); A(find(A(:)>.6))=.6;          
           
           
Ibp=find(B>0);
Ibl=Ibp+1;
           
Ibn=find(B<=0);
Ibu=Ibn-1;
Ibu(find(rem(Ibn,N_Lat)==1))=Ibn(find(rem(Ibn,N_Lat)==1));
B(Ibn)=-B(Ibn);



%Iterates over days
for dag=sim_days
    disp(' ')
    disp(['Simulating ' SPECIES ' for date: ' num2str(dag) ', ' mjd2utc(dag)])
    disp(' ')

    
    %LOADS OZONE DATA FOR CURRENT DAY        
    [utcyear,utcmonth,utcday]=mjd2utc(dag); utcyear=utcyear-2000;
    Modell_O3=[]; sun=[]; Modell_QUALITY=[]; Chi2=[]; N_chi=[]; T_chi=[]; OZON=[]; OZON_QUALITY=[]; OZON_measresp=[]; ORIGINAL_QUALITY=[];
    if exist([path_species num2str(utcyear,'%02d') num2str(utcmonth,'%02d') num2str(utcday,'%02d') '.mat']); 
        
        eval(['load ' path_species num2str(utcyear,'%02d') num2str(utcmonth,'%02d') num2str(utcday,'%02d') '.mat']);
        
        [dummy, data_levels]=intersect(PotT,ept2);
      
        ept=ept2;
        
        eval(['OZON=' SPECIES ';']);
        
        if not(isempty(OZON))        
            
           eval(['OZON=' SPECIES '(:,data_levels);']);
           
           eval(['OZON_measresp=' SPECIES '_measresp(:,data_levels);']);
           
           
           eval(['ORIGINAL_QUALITY=' SPECIES '_QUALITY_meas(:,data_levels);']);
                   
           
           OZON_QUALITY=repmat(1.25*ERQQ(sim_levels),size(OZON,1),1);
     
          obs_minut=(tidmat-dag)*60*24;
        else
           TR=[];
           TR_QUALITY=[];
           OZON_measresp=[];
           ORIGINAL_QUALITY=[];
        
           latmat=[];
           longmat=[];
           tidmat=[];
           Nalt=[];
           obs_minut=[];
        end
     
     
    else
        OZON=[];
        TR=[];
        TR_QUALITY=[];
        
        
        latmat=[];
        longmat=[];
        tidmat=[];
        Nalt=[];
        obs_minut=[];
    end
    
            
    %Iterates the transport and assimilation model
    for minut=[0:dt:(24*60-dt)]
        
      
        
        % Saves the tracer fields at 00:00 hours
        if minut==0 && save_tracerfields==1
            
            K_TracerField=max(S0(:))/65535; 
            TracerField_u16=uint16(S0/K_TracerField);
     
            K_Err=max(Err(:))/65535; 
            Err_u16=uint16(Err/K_Err);
            
            [year month] = mjd2utc(dag);
            savepath=([path_savefields num2str(year) '/' num2str(month) '/']);
            mkdir(savepath);
            
        end
        
        
        
        
        %Loads new wind fields every 6 hours. Loads at 03:00, 09:00, 15:00 and
        %21:00 hours the fields that represent the winds at 06:00, 12:00,
        %18:00 and 24:00 hours.
        
        if rem(minut+60*3,60*6)==0
           if minut==60*21;
              [a b c]=mjd2utc(dag+1); a=a-2000;
              windhour='0';
           else 
              [a b c]=mjd2utc(dag); a=a-2000;
              windhour=num2str(minut/60+3);
           end
           
           
           for i=1:length(sim_levels)
              winds_exist=0; 
              for j=1:4
                 if exist([path_winds num2str(a,'%02d') '/' num2str(b,'%02d') '/' name_winds num2str(a,'%02d') num2str(b,'%02d') num2str(c,'%02d') '.' windhour '.' num2str(ept(i)) '.mat']) 
                    eval(['load ' path_winds num2str(a,'%02d') '/' num2str(b,'%02d') '/' name_winds num2str(a,'%02d') num2str(b,'%02d') num2str(c,'%02d') '.' windhour '.' num2str(ept(i)) '.mat']);
                    winds_exist=1;
                    break;
                 else
                    tic;
                    while toc<30
                    end
                 end
              end
              
              if winds_exist==0
                 error(['ERROR: There is no wind data for ' num2str(a+2000) '-' num2str(b,'%02d') '-' num2str(c,'%02d') '  ' windhour '  ' num2str(ept(i)) 'K']);
              end    
              
              
              
               %A is the zonal wind field and B is the meridional wind field  
               if NN==1
                  A(:,:,i)=zon_wind(2:2:end,1:2:end)*60*dt/40e6*N_Long./cos(repmat(Latitudes/180*pi,1,N_Long));
                  B(:,:,i)=mer_wind(2:2:end,2:2:end)*60*dt/20e6*N_Lat;
               elseif NN==2    
                  A(:,:,i)=(zon_wind(1:end-1,:)+zon_wind(2:end,:))/2*60*dt/40e6*N_Long./cos(repmat(Latitudes/180*pi,1,N_Long));
                  B(:,:,i)=(mer_wind(1:end-1,:)+mer_wind(2:end,:))/2*60*dt/20e6*N_Lat;
               end
   
               A(1,:,i)=0; A(end,:,i)=0;
               B(end,:,i)=(B(end,:,i)-abs(B(end,:,i)))/2;
              
           end
           
           %Finds coordinates for upwind and downwind gridboxes.
           Iap=find(A>=0);
           Ial=Iap-N_Lat; 
           Ial(find(rem(floor((Iap-1)/N_Lat),N_Long)==0))= ...
               Iap(find(rem(floor((Iap-1)/N_Lat),N_Long)==0))+N_Lat*(N_Long-1);
           
           Ian=find(A<0);
           Iar=Ian+N_Lat; 
           Iar(find(rem(floor((Ian-1)/N_Lat),N_Long)==(N_Long-1)))= ...
               Ian(find(rem(floor((Ian-1)/N_Lat),N_Long)==(N_Long-1)))-N_Lat*(N_Long-1);

           A(Ian)=-A(Ian); A(find(A(:)>.6))=.6;
           
           Ibp=find(B>0);
           Ibl=Ibp+1;
           
           Ibn=find(B<=0);
           Ibu=Ibn-1;
           Ibu(find(rem(Ibn,N_Lat)==1))=Ibn(find(rem(Ibn,N_Lat)==1));
           B(Ibn)=-B(Ibn);
        end
        
        
        % The Prather advection scheme
        S0R(Iap)=(1-A(Iap)).*(S0(Iap)-A(Iap).*Sx(Iap)-A(Iap).*(1-2*A(Iap)).*Sxx(Iap));
        S0L(Iap)=A(Iap).*(S0(Ial)+(1-A(Iap)).*Sx(Ial)+(1-A(Iap)).*(1-2*A(Iap)).*Sxx(Ial));
        
        SxR(Iap)=(1-A(Iap)).^2.*(Sx(Iap)-3*A(Iap).*Sxx(Iap));
        SxL(Iap)=A(Iap).^2.*(Sx(Ial)+3*(1-A(Iap)).*Sxx(Ial));
        
        SyR(Iap)=(1-A(Iap)).*(Sy(Iap)-A(Iap).*Sxy(Iap));
        SyL(Iap)=A(Iap).*(Sy(Ial)+(1-A(Iap)).*Sxy(Ial));
        
        SxxR(Iap)=(1-A(Iap)).^3.*Sxx(Iap);
        SxxL(Iap)=A(Iap).^3.*Sxx(Ial);
        
        SxyR(Iap)=(1-A(Iap)).^2.*Sxy(Iap);
        SxyL(Iap)=A(Iap).^2.*Sxy(Ial);
        
        SyyR(Iap)=(1-A(Iap)).*Syy(Iap);
        SyyL(Iap)=A(Iap).*Syy(Ial);
        
        
        S0R(Ian)=A(Iar).*(S0(Iar)-(1-A(Ian)).*Sx(Iar)+(1-A(Iar)).*(1-2*A(Iar)).*Sxx(Iar));
        S0L(Ian)=(1-A(Iar)).*(S0(Ian)+A(Iar).*Sx(Ian)-A(Iar).*(1-2*A(Iar)).*Sxx(Ian));
     %+-Sxx   
        SxR(Ian)=A(Iar).^2.*(Sx(Iar)-3*(1-A(Iar)).*Sxx(Iar));
        SxL(Ian)=(1-A(Iar)).^2.*(Sx(Ian)+3*A(Iar).*Sxx(Ian));
        
        SyR(Ian)=A(Iar).*(Sy(Iar)-(1-A(Iar)).*Sxy(Iar));
        SyL(Ian)=(1-A(Iar)).*(Sy(Ian)+A(Iar).*Sxy(Ian));
        
        SxxR(Ian)=A(Iar).^3.*Sxx(Iar);
        SxxL(Ian)=(1-A(Iar)).^3.*Sxx(Ian);
        
        SxyR(Ian)=A(Iar).^2.*Sxy(Iar);
        SxyL(Ian)=(1-A(Iar)).^2.*Sxy(Ian);
        
        SyyR(Ian)=A(Iar).*Syy(Iar);
        SyyL(Ian)=(1-A(Iar)).*Syy(Ian);
        
        
        
        S0=S0L+S0R;
        Sx(Iap)=(1-A(Iap)).*SxR(Iap)+A(Iap).*SxL(Iap)+3*(A(Iap).*S0R(Iap)-(1-A(Iap)).*S0L(Iap));
        Sx(Ian)=A(Iar).*SxR(Ian)+(1-A(Iar)).*SxL(Ian)+3*((1-A(Iar)).*S0R(Ian)-A(Iar).*S0L(Ian));
        Sy=SyR+SyL;
        Sxx(Iap)=(1-A(Iap)).^2.*SxxR(Iap)+A(Iap).^2.*SxxL(Iap)+5*(A(Iap).* ...
            (1-A(Iap)).*(SxR(Iap)-SxL(Iap))-(1-2*A(Iap)).*(A(Iap).*S0R(Iap) ...
            -(1-A(Iap)).*S0L(Iap)));
        Sxx(Ian)=A(Iar).^2.*SxxR(Ian)+(1-A(Iar)).^2.*SxxL(Ian)+5*(A(Iar).* ...
            (1-A(Iar)).*(SxR(Ian)-SxL(Ian))+(1-2*A(Iar)).*((1-A(Iar)).*S0R(Ian) ...
            -A(Iar).*S0L(Ian)));
        Sxy(Iap)=(1-A(Iap)).*SxyR(Iap)+A(Iap).*SxyL(Iap)+3*(A(Iap).*SyR(Iap) ...
            -(1-A(Iap)).*SyL(Iap));
        Sxy(Ian)=A(Iar).*SxyR(Ian)+(1-A(Iar)).*SxyL(Ian)+3*((1-A(Iar)).*SyR(Ian) ...
            -A(Iar).*SyL(Ian));
        Syy=SyyL+SyyR;
        

        
        
        S0R(Ibp)=(1-B(Ibp)).*(S0(Ibp)-B(Ibp).*Sy(Ibp)-B(Ibp).*(1-2*B(Ibp)).*Syy(Ibp));
        S0L(Ibp)=B(Ibp).*(S0(Ibl)+(1-B(Ibp)).*Sy(Ibl)+(1-B(Ibp)).*(1-2*B(Ibp)).*Syy(Ibl));
        
        SxR(Ibp)=(1-B(Ibp)).*(Sx(Ibp)-B(Ibp).*Sxy(Ibp));
        SxL(Ibp)=B(Ibp).*(Sx(Ibl)+(1-B(Ibp)).*Sxy(Ibl));
        
        SyR(Ibp)=(1-B(Ibp)).^2.*(Sy(Ibp)-3*B(Ibp).*Syy(Ibp));
        SyL(Ibp)=B(Ibp).^2.*(Sy(Ibl)+3*(1-B(Ibp)).*Syy(Ibl));
        
        SxxR(Ibp)=(1-B(Ibp)).*Sxx(Ibp);
        SxxL(Ibp)=B(Ibp).*Sxx(Ibl);
        
        SxyR(Ibp)=(1-B(Ibp)).^2.*Sxy(Ibp);
        SxyL(Ibp)=B(Ibp).^2.*Sxy(Ibl);
        
        SyyR(Ibp)=(1-B(Ibp)).^3.*Syy(Ibp);
        SyyL(Ibp)=B(Ibp).^3.*Syy(Ibl);
        
        
        
        S0R(Ibn)=B(Ibn).*(S0(Ibu)-(1-B(Ibn)).*Sy(Ibu)+(1-B(Ibn)).*(1-2*B(Ibn)).*Syy(Ibu));
        S0L(Ibn)=(1-B(Ibn)).*(S0(Ibn)+B(Ibn).*Sy(Ibn)-B(Ibn).*(1-2*B(Ibn)).*Syy(Ibn));
       
        SxR(Ibn)=B(Ibn).*(Sx(Ibu)-(1-B(Ibn)).*Sxy(Ibu));
        SxL(Ibn)=(1-B(Ibn)).*(Sx(Ibn)+B(Ibn).*Sxy(Ibn));
        
        SyR(Ibn)=B(Ibn).^2.*(Sy(Ibu)-3*(1-B(Ibn)).*Syy(Ibu));
        SyL(Ibn)=(1-B(Ibn)).^2.*(Sy(Ibn)+3*B(Ibn).*Syy(Ibn));
        
        SxxR(Ibn)=B(Ibn).*Sxx(Ibu);
        SxxL(Ibn)=(1-B(Ibn)).*Sxx(Ibn);
        
        SxyR(Ibn)=B(Ibn).^2.*Sxy(Ibu);
        SxyL(Ibn)=(1-B(Ibn)).^2.*Sxy(Ibn);
        
        SyyR(Ibn)=B(Ibn).^3.*Syy(Ibu);
        SyyL(Ibn)=(1-B(Ibn)).^3.*Syy(Ibn);
        
        
        
        S0=S0L+S0R;
        Sx=SxL+SxR;
        Sy(Ibp)=B(Ibp).*SyL(Ibp)+(1-B(Ibp)).*SyR(Ibp)+3*(B(Ibp).*S0R(Ibp)- ...
            (1-B(Ibp)).*S0L(Ibp));
        Sy(Ibn)=(1-B(Ibn)).*SyL(Ibn)+B(Ibn).*SyR(Ibn)+3*((1-B(Ibn)).*S0R(Ibn)- ...
            B(Ibn).*S0L(Ibn));
        Sxx=SxxL+SxxR;
        Sxy(Ibp)=(1-B(Ibp)).*SxyR(Ibp)+B(Ibp).*SxyL(Ibp)+3*(B(Ibp).*SxR(Ibp) ...
            -(1-B(Ibp)).*SxL(Ibp));
        Sxy(Ibn)=B(Ibn).*SxyR(Ibn)+(1-B(Ibn)).*SxyL(Ibn)+3*((1-B(Ibn)).*SxR(Ibn) ...
            -B(Ibn).*SxL(Ibn));
        Syy(Ibp)=B(Ibp).^2.*SyyL(Ibp)+(1-B(Ibp)).^2.*SyyR(Ibp)+5*(B(Ibp).* ...
            (1-B(Ibp)).*(SyR(Ibp)-SyL(Ibp))-(1-2*B(Ibp)).*(B(Ibp).*S0R(Ibp)- ...
            (1-B(Ibp)).*S0L(Ibp)));
        Syy(Ibn)=(1-B(Ibn)).^2.*SyyL(Ibn)+B(Ibn).^2.*SyyR(Ibn)+5*(B(Ibn).* ...
            (1-B(Ibn)).*(SyR(Ibn)-SyL(Ibn))+(1-2*B(Ibn)).*((1-B(Ibn)).*S0R(Ibn)- ...
            B(Ibn).*S0L(Ibn)));
        
        
        %Turns off the higher order moments of the Prather scheme near the poles
        Sx(1,:)=0; Sy(1,:)=0;
        Sxx(1,:)=0; Syy(1,:)=0; Sxy(1,:)=0;
       
        Sx(2,:)=0; Sy(2,:)=0;
        Sxx(2,:)=0; Syy(2,:)=0; Sxy(2,:)=0;
        
        
        Sx(end,:)=0; Sy(end,:)=0;
        Sxx(end,:)=0; Syy(end,:)=0; Sxy(end,:)=0;
        
        Sx(end-1,:)=0; Sy(end-1,:)=0;
        Sxx(end-1,:)=0; Syy(end-1,:)=0; Sxy(end-1,:)=0;
        
        
        if NN>1
            
           Sx(3,:)=0; Sy(3,:)=0;
           Sxx(3,:)=0; Syy(3,:)=0; Sxy(3,:)=0;
        
           Sx(end-2,:)=0; Sy(end-2,:)=0;
           Sxx(end-2,:)=0; Syy(end-2,:)=0; Sxy(end-2,:)=0;
        end
        
        
        %Merges all grid boxes that border the poles
        for j=1:length(sim_levels)
           S0(1,:,j)=mean(S0(1,:,j)); 
           S0(end,:,j)=mean(S0(end,:,j));
        end



        %Limits the first and second order moments
        Sx(find(Sx>lim_x))=lim_x;
        Sx(find(Sx<-lim_x))=-lim_x;
        Sy(find(Sy>lim_x))=lim_x;
        Sy(find(Sy<-lim_x))=-lim_x;
        Sxx(find(Sxx>lim_xx))=lim_xx;
        Sxx(find(Sxx<-lim_xx))=-lim_xx;
        Sxy(find(Sxy>lim_xx))=lim_xx;
        Sxy(find(Sxy<-lim_xx))=-lim_xx;
        Syy(find(Syy>lim_xx))=lim_xx;
        Syy(find(Syy<-lim_xx))=-lim_xx;
     
        
        
        
        
        %First-order upstream advection for the error field
        S0R(Iap)=(1-A(Iap)).*Err(Iap);
        S0L(Iap)=A(Iap).*Err(Ial);
        S0R(Ian)=A(Ian).*Err(Iar);
        S0L(Ian)=(1-A(Ian)).*Err(Ian);
                         
        Err=S0L+S0R;
        
        S0R(Ibp)=(1-B(Ibp)).*Err(Ibp);
        S0L(Ibp)=B(Ibp).*Err(Ibl);
        S0R(Ibn)=B(Ibn).*Err(Ibu);
        S0L(Ibn)=(1-B(Ibn)).*Err(Ibn);
       
        Err=S0L+S0R;
        
        for j=1:length(sim_levels)
           Err(1,:,j)=mean(Err(1,:,j)); 
           Err(end,:,j)=mean(Err(end,:,j));
        end    
         
    
        
        
      %Assimilation every XX minutes
      XX=10;
      if rem(minut,XX)==0
         %Finds an index to data within XX/2 minutes of the current minut 
         I_obs=intersect(find(obs_minut>=(minut-XX/2)),find(obs_minut<(minut+XX/2)));
        
         if ~isempty(I_obs)
            
            %xobs and yobs are given the zonal and meridional coordinates
            %(indexes) of the observations
            xobs=interp1(Longitudes,[1:N_Long]',longmat(I_obs),'nearest','extrap');
            yobs=interp1(Latitudes,[1:N_Lat]',latmat(I_obs),'nearest','extrap');
            II_obs=yobs+(xobs-1)*N_Lat;
            [II_ass2d,Roo_x,Roo_y,Rob_x,Rob_y]=define_assgridG(xobs,yobs,II_dx,II_dy,N_Lat,N_Long);
            
            
            %I_ass is given the indexes of observation in the 2D latitude
            %Longitude grid
            %II_ass is given the indexes of observations in the 3D model
            %grid
            I_ass=[]; II_ass=[];
            for i=1:length(sim_levels)
               I_ass=[I_ass yobs+(xobs-1)*N_Lat+(i-1)*N_Lat*N_Long];
               II_ass=[II_ass II_ass2d+(i-1)*N_Lat*N_Long];
            end
            
            
            %Stores the data, data error and measurement response that are
            %to be assimilated in the current time step
            TR=OZON(I_obs,:);
            OQ=OZON_QUALITY(I_obs,:);
            OM=OZON_measresp(I_obs,:);
        
            
            %Finds indexes to bad data
            I_nan=find(isnan(TR));
            I_nan=union(I_nan,find(isnan(OQ)));
            I_nan=union(I_nan,find(OQ<=0));
        
            %Adds indexes of data with measurement response below 0.7
            I_nan=union(I_nan,find(OM(:)<MeasResp_Limit));
           
            %filters out water with too high mixing ratio
            I_nan=union(I_nan,find(TR(:)>max_mixingratio));
            
            
            %I_nan=union(I_nan,find((O3-S0(I_ass)).^2>10*(Err(I_ass).^2+OQ.^2)));
       
       
            %Sets bad data to model data and gives them a large error.
            TR(I_nan)=S0(I_ass(I_nan));
            OQ(I_nan)=5*Err(I_ass(I_nan));
        
        
            %Stores model predictions at the observation points before assimilation so
            %it can be analysed off line
            Modell_O3=[Modell_O3; S0(I_ass)];
            Modell_QUALITY=[Modell_QUALITY; Err(I_ass)];
        
       
            %Assimilates data
            [dS0,Err_new,Chi2_temp,N_temp]=assimilateG(S0(I_ass),Err(I_ass),Err(II_ass), ...
                  TR,OQ,Roo_x,Roo_y,Rob_x,Rob_y,L_ass^2);
        
            S0(II_ass)=S0(II_ass)+dS0;
            Err(II_ass)=Err_new;
            
            %Stores Chi2 values for off line analysis
            Chi2=[Chi2; Chi2_temp];
            N_chi=[N_chi; N_temp];
            T_chi=[T_chi; dag+minut/60/24];
         end
      end
      
      if minut == 0 && save_tracerfields==1
          
            eval(['save ' savepath sSpecies '_' num2str(dag) '_' num2str(minut/60,'%02d') ...
                    '.mat TracerField_u16 Err_u16 K_TracerField  K_Err Chi2 N_chi T_chi']);
      end
      
         
     %Adds growth to the error field  
     for i=1:size(Err,3)
        Err(:,:,i)=Err(:,:,i)+ERQQ(sim_levels(i))*dt/60/24/150;
        
        %Limits the error field
        ErrT=squeeze(Err(:,:,i));
        I_ErrT=find(ErrT>ERQQ(sim_levels(i))/3);
        ErrT(I_ErrT)=ERQQ(sim_levels(i))/3;
           
        Err(:,:,i)=ErrT;
     end
         
        
    end
    if  not(isempty(OZON))
       eval([SPECIES '=OZON;']);
       eval([SPECIES '_NOISE=OZON_QUALITY;']);
    
       eval([SPECIES '_measresp=' SPECIES '_measresp(:,data_levels);']);
    
       eval(['Modell_' SPECIES '=Modell_O3;']);
       Modell_NOISE=Modell_QUALITY;
       ORIGINAL_NOISE=ORIGINAL_QUALITY;
    
  
    end
end

