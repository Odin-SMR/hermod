delimiter |
create trigger gem_download_insert after insert on smr.level1
for each row
    if new.uploaded>0 then
        insert not_downloaded_gem set id=new.id;
    end if;
|
