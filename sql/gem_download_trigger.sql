create trigger gem_download after insert on smr.level1
for each row insert not_downloaded_gem set id = new.id;
