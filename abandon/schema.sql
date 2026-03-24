-- IoT System Database Schema
-- Table: sensor_data

CREATE TABLE IF NOT EXISTS `sensor_data` (
  `id` INT(11) NOT NULL AUTO_INCREMENT,
  `timestamp` TIMESTAMP NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  `temperature` FLOAT DEFAULT 0,
  `humidity` FLOAT DEFAULT 0,
  `data_source` VARCHAR(50) NOT NULL COMMENT 'e.g., esp32, simulator',
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_general_ci;
