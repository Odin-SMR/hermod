CREATE TABLE `smr`.`level1b_gem` (
  `id` BIGINT UNSIGNED NOT NULL COMMENT 'Id is linked to smr.level1.',
  `filename` VARCHAR(30) NOT NULL COMMENT 'The filename on disk, note not full path',
  `date` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT 'Time the file was downloaded',
  PRIMARY KEY (`id`, `filename`)
)
ENGINE = MyISAM
CHARACTER SET utf8
COMMENT = 'All files downloaded from pdc';