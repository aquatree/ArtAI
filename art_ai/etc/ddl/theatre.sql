CREATE TABLE work.theatre(
    id INT NOT NULL AUTO_INCREMENT,
    title VARCHAR(100),
    `date` VARCHAR(100),
    place VARCHAR(100),
    price VARCHAR(100),
    `start_date` DATE,
    `end_date` DATE,
    `url` VARCHAR(100),
    `description` TEXT(200),
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX(id)
);