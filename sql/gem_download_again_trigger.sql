create trigger gem_download_again after update on smr.level1
for each row insert not_downloaded_gem set id = new.id;
