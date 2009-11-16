delimiter |
create trigger gem_download_update after update on smr.level1
for each row 
    if new.uploaded>old.uploaded then
        insert not_downloaded_gem set id = new.id;
    end if;
|
