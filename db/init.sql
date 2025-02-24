CREATE TABLE  if not exists users (
    ->     id INT AUTO_INCREMENT PRIMARY KEY,
    ->     name VARCHAR(100) NOT NULL,
    ->     username VARCHAR(100) NOT NULL UNIQUE,
    ->     email VARCHAR(100) NOT NULL UNIQUE,
    ->     password VARCHAR(100) NOT NULL
    -> );
