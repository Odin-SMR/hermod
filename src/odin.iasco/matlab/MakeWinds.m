function MakeWinds(vMjd)
%This file converts wind data from ECMWF to .mat-files

%Data files must first be downloaded from ECMWF and placed
%in the directories described by the path below.

%/DIRECTORY/YYMM/ecmwfYYMMDD.U.-1.HH.gz

%The files should be placed according to the year and month of the
%data (YYMM) and have a name starting with ecmwf followed by year
%month and day (YYMMDD), then .U or .V depending on if the winds are
%zonal or meridional, then .-1, then the time of day .HH and last
%.gz since the files are large and therefore gzipped


times=[0 6 12 18]; %defines what times of the dday should be converted
% [0 6 12 18] are possible


ept=[400:25:1000]; %defines the potential temperature levels for which
%.mat-files are produced.

string=getenv('PBS_JOBID');
if string==''
    st=round(rand*10000);
else
    str=regexp(string,'\.','split');
    st=str(1);
end
folder=strcat('/tmp/tmp', st, '/');
folder=folder{1};
mkdir(folder);

for i=1:length(vMjd)

    [year, month, day]=mjd2utc(vMjd(i)); year=year-floor(year/100)*100; % Makes year format YY

    %Defines the path to the ECMWF data
    s.path_winds=[find_path('WIND_DIR') num2str(year,'%02d')  num2str(month,'%02d') '/'];
    %Gives a path where .mat-files are saved
    wind2_path=find_path('WIND2_DIR');
    s.path_output=[wind2_path num2str(year,'%02d') '/' num2str(month,'%02d') '/'];
    
    if ~exist([wind2_path num2str(year,'%02d') '/'])
        mkdir([wind2_path num2str(year,'%02d') '/']);
    end
    if ~exist([wind2_path num2str(year,'%02d') '/' num2str(month,'%02d') '/'])
        mkdir([wind2_path num2str(year,'%02d') '/' num2str(month,'%02d') '/']);
    end

    for time=times
        if exist([s.path_winds 'ecmwf' num2str(year,'%02d') num2str(month,'%02d') num2str(day,'%02d') '.U.-1.' num2str(time,'%02d') '.gz'])
            tmp_file=floor(rand(1)*1000);

            eval(['unix ([''gunzip -c ' s.path_winds 'ecmwf' num2str(year,'%02d') num2str(month,'%02d') num2str(day,'%02d') '.U.-1.' num2str(time,'%02d') '.gz > ' folder num2str(tmp_file) '_U''])']);
            eval(['unix ([''gunzip -c ' s.path_winds 'ecmwf' num2str(year,'%02d') num2str(month,'%02d') num2str(day,'%02d') '.V.-1.' num2str(time,'%02d') '.gz > ' folder num2str(tmp_file) '_V''])']);

            filename = [folder num2str(tmp_file) '_U'];
            [level_ecmwf,U_ecmwf,lat_ecmwf,long_ecmwf] = readecmwfmult(filename);

            filename = [folder num2str(tmp_file) '_V'];
            [level_ecmwf,V_ecmwf,lat_ecmwf,long_ecmwf] = readecmwfmult(filename);

            eval(['unix ([''rm ' folder num2str(tmp_file) '_U''])']);
            eval(['unix ([''rm ' folder num2str(tmp_file) '_V''])']);

            for i=1:length(ept)
                %fprintf(1,'\rInterpolating level: %i   \n',ept(i))

                Iept=find(level_ecmwf==ept(i));

                zon_wind = 1e-3*U_ecmwf(:,:,Iept);
                mer_wind = 1e-3*V_ecmwf(:,:,Iept);

                eval(['save ' s.path_output 'winds2_' num2str(year,'%02d') num2str(month,'%02d') num2str(day,'%02d') '.' num2str(time) '.' num2str(ept(i)) '.mat zon_wind mer_wind']);

            end
            display(['Date:' num2str(year+2000) '-' num2str(month) '-' num2str(day) ' Time: ' num2str(time)])

        else
            continue
        end


    end
end
