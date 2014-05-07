function [mjd] = utc2mjd(year,month,day,hour,minute,secs,ticks)
%----------------------------------------------------------------
%
% [mjd] = utc2mjd(year,month,day,hour,minute,secs,ticks)
%
% In:
%    day, month, year, hour, minute, secs, ticks : all obvious
%
% Out:
%    mjd :          the modified julian date
%
% Originally taken from Nick Lloyds Onyx software.
%
% Finds the Modified Julian Date given the civil calendar date.
% Julian calendar is used up to 1582 October 4,
% Gregorian calendar is used from 1582
% October 15 onwards.
% Follows Algorithm given in "Astronomy on the
% Personal Computer"  O. Montenbruck and T. Pfleger.
%
% Translated from C++ to Matlab by Frank Merino.
%
%----------------------------------------------------------------

% set optional variables
if (nargin < 4)  
  hour  = 0;  
end
if (nargin < 5)  
  minute = 0; 
end
if (nargin < 6)  
  secs   = 0; 
end
if (nargin < 7)  
  ticks  = 0; 
end

I=find(year<100);
if ~isempty(I)
  subset=year(I);
  J=find(subset>40);
  subset=subset+2000;
  subset(J)=subset(J)-2000+1900;
  year(I)=subset;
end

%   if (year < 100)
%      if (year > 40)
%        year = year + 1900; 
%      else 
%        year = year + 2000;
%      end
%   end

   y = fix(year);
   
   I=find(month<=2);
   if ~isempty(I)
      y(I)=y(I)-1;
      month(I)=month(I)+12;
   end
   
%   if (month <= 2)
%      y = y - 1;
%      month = month + 12;
%   end

   if ((year < 1582) | ((year == 1582) & ((month < 10) | ((month == 10) & (day < 15)))) )
     B = fix(-2 + fix((y+4716)/4) - 1179);
   else
     B = fix(y/400) - fix(y/100)+ fix(y/4);
   end

   A = 365.0*y - 679004.0;

   mjd =  A+B+(fix(30.6001*(month+1)))+day+...
            (hour/24.0)+minute/1440.0+(secs+ticks)/86400.0;


return
