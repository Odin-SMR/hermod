function poff(filename)

format long g;
a=load(filename,'Xs','L','SMR');
fprintf('\n');
%find pointing offset cell

for i=[1:size(a.Xs,2)], 
    if not (isempty(a.Xs{i})),
        point =1;
        for j=[1:size(a.Xs{i},1)],
            if strcmp(a.Xs{i}{j}.name,'Pointing: off-set'),
                point = j;
            end
        end
        poff=a.Xs{i}{point}.x;
        fprintf('!!,%d,%0.20d\n',i,poff)
        %sprintf('update low_priority ignore level2,scans set poffset=%f where calibration=%d and scan=%d and hex(orbit)=''%X'' and freqmode=%d and level2.id=scans.id;\n',a.Xs{i}{point}.x,bitand(a.L.LEVEL,255),i,a.L.ORBIT,strnr(a.SMR.FREQMODE));
    end;
end;
return

function x=strnr(str)
switch str 
case 'SM_AC2a'
    nr = 1;
case 'SM_AC2b' 
    nr= 1;
case 'SM_AC2ab' 
    nr= 1;
case 'SM_AC1e'
    nr= 2;
case 'HM_AC1f' 
    nr= 24;
case 'IM_AC2a' 
    nr= 8;
case 'IM_AC2b' 
    nr= 8;
case 'IM_AC2ab' 
    nr= 8;
case 'IM_AC2c' 
    nr= 17;
case 'IM_AC1c' 
    nr= 19;
case 'IM_AC1de' 
    nr= 21;
case 'HM_AC1c' 
    nr= 13;
case 'HM_AC2c' 
    nr= 14;
case 'HM_AC2ab' 
    nr= 22;
case 'HM_AC1d' 
    nr= 23;
case 'HM_AC1e' 
    nr= 23;
case 'TM_ACs1' 
    nr= 25;
case 'TM_AOS1' 
    nr= 26;
case 'TM_ACs2' 
    nr= 27;
case 'TM_AOS2' 
    nr= 28;
case 'SM_FB' 
    nr= 20;
case 'HM_AC1a' 
    nr= 3;
case 'HM_AC1b' 
    nr= 3;
case 'HM_AC2a' 
    nr= 4;
case 'HM_AC2b' 
    nr= 4;
case 'HM_AOS2' 
    nr= 5;
case 'NM_AC1a' 
    nr= 6;
case 'NM_AC1b' 
    nr= 6;
case 'NM_AC2a' 
    nr= 7;
case 'NM_AC2b' 
    nr= 7;
case 'IM_AC1a' 
    nr= 9;
case 'IM_AC1b' 
    nr= 9;
case 'SM_AC2c' 
    nr= 10;
case 'SM_AC2d' 
    nr= 10;
case 'HM_AOS1' 
    nr= 11;
case 'IM_AOS1' 
    nr= 12;
case 'HM_AC2d' 
    nr= 15;
case 'HM_AC2e' 
    nr= 15;
case 'HM_AC2d' 
    nr= 16;
case 'HM_AC2f' 
    nr= 16;
otherwise 
    nr=0;
end
x=nr;
