create trigger gem_download_insert after insert on smr.status
for each row 
begin
    if new.status then
        insert not_downloaded_gem set id = new.id;
    else 
        delete from not_downloaded_gem where id = new.id;
    end if;
end;


