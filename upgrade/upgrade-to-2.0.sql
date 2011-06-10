
/*
Create table to hold filesystem tracks (fs) playlist
*/
CREATE TABLE `fs_playlist` (
`id` INT NOT NULL AUTO_INCREMENT PRIMARY KEY ,
`tr_name` TINYTEXT NOT NULL ,
`tr_location` TINYTEXT NOT NULL ,
`pl_id` INT NOT NULL
) ENGINE = MYISAM CHARACTER SET utf8 COLLATE utf8_general_ci;


/*
Create table to hold configuration parameters
*/
CREATE TABLE `config` (
`param` VARCHAR( 255 ) NOT NULL ,
`value` VARCHAR( 255 ) NOT NULL
) ENGINE = MYISAM CHARACTER SET utf8 COLLATE utf8_general_ci;
