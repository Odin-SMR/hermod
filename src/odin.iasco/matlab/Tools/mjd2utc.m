%----------------------------------------------------------------
%
% function [year,month,day,hour,minute,secs,ticks] = mjd2utc(mjd)
%
% In:
%    mjd :          the modified julian date
%
% Out:
%    day, month, year, hour, minute, secs, ticks : all obvious
%    if no argout then return string with date time  (DPM 20010725)
%
% Originally taken from Nick Lloyds Onyx software.
%
% Finds the civil calendar date for a given value
% of the Modified Julian Date (MJD).
% Julian calendar is used up to 1582 October 4,
% Gregorian calendar is used from 1582
% October 15 onwards.
% Follows Algorithm given in "Astronomy on the
% Personal Computer"  O. Montenbruck and T. Pfleger.
%
% Translated from C++ to Matlab by Frank Merino.
%
% Improved vectorisation by Donal Murtagh 20010731
% NOTA BENE the gregorian julian fix is not yet vectorised
%
%----------------------------------------------------------------

function [year,month,day,hour,minute,secs,ticks] = mjd2utc(mjd)
 
   dayfrac = mjd - floor(mjd);                    % Get the fraction of UTC day.
   jd      = floor(mjd) + 2400000.5;              % Get the Julian Date
   jd0     = jd+0.5;                              % and add a half.

   if jd0 < 2299161.0                             % Determine the calendar
      c = jd0 + 1524.0;                           % Its Julian
   else                                           % Its Gregorian.
      b = fix( ((jd0 - 1867216.25) / 36524.25) );
      c = jd0 + (b - fix(b/4)) + 1525.0;
   end

   d     = fix( ((c - 122.1) / 365.25) );
   e     = 365.0 * d + fix(d/4);
   f     = fix( ((c - e) / 30.6001) );
   day   = fix( (c - e + 0.5) - fix(30.6001 * f) );
   month = fix( (f - 1 - 12*fix(f/14)) );
   year  = fix( ( d - 4715 - fix((7+month)/10)) );

   hour     = fix(dayfrac*24.0);
   minute      = fix(mod(dayfrac*1440.0,  60.0));
   dayfrac  = dayfrac * 86400.0;
   ticks    = (mod(dayfrac, 60.0));
   secs     = fix(ticks);
   ticks    = ticks- secs;

   if nargout<=1
     year=[num2str(year) '-' num2str(month,'%02d') '-' num2str(day,'%02d') ' '...
           num2str(hour) ':' num2str(minute,'%02d') ':' num2str(secs+ticks,'%05.3f')];
   end
   
return
