CREATE DATABASE IF NOT EXISTS studylink;
USE studylink;
CREATE TABLE IF NOT EXISTS users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    username VARCHAR(100) NOT NULL UNIQUE,
    email VARCHAR(100) NOT NULL UNIQUE,
    password VARCHAR(255) NOT NULL
);
CREATE TABLE IF NOT EXISTS user_settings (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL UNIQUE,  
    profile_pic VARCHAR(255) DEFAULT '/static/uploads/ProfilePics/default.jpg',
    bio TEXT,
    class_year INT DEFAULT NULL,
    course VARCHAR(255) DEFAULT '',
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);
CREATE TABLE IF NOT EXISTS courses (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(255) NOT NULL UNIQUE
);
CREATE TABLE IF NOT EXISTS curricular_units (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(255) NOT NULL UNIQUE
);
CREATE TABLE IF NOT EXISTS user_subjects (
    user_id INT NOT NULL,
    subject_id INT NOT NULL,
    PRIMARY KEY (user_id, subject_id),
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (subject_id) REFERENCES curricular_units(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS course_curricular_units (
    course_id INT NOT NULL,
    curricular_unit_id INT NOT NULL,
    PRIMARY KEY (course_id, curricular_unit_id),
    FOREIGN KEY (course_id) REFERENCES courses(id) ON DELETE CASCADE,
    FOREIGN KEY (curricular_unit_id) REFERENCES curricular_units(id) ON DELETE CASCADE
);
CREATE TABLE IF NOT EXISTS contacto (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nome VARCHAR(255) NOT NULL,
    email VARCHAR(255) NOT NULL,
    mensagem TEXT NOT NULL,
    data TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);



-- Create a temporary table for CSV import
DROP TABLE IF EXISTS course_curricular_units_temp;
CREATE TABLE course_curricular_units_temp (
    Course VARCHAR(255),
    CurricularUnit VARCHAR(255)
);

-- Load data from CSV into the correct temp table
LOAD DATA INFILE '/docker-entrypoint-initdb.d/db/iscte_courses_units.csv'
INTO TABLE course_curricular_units_temp
FIELDS TERMINATED BY ','
LINES TERMINATED BY '\n'
IGNORE 1 ROWS;

-- Insert courses (ignore duplicates)
INSERT IGNORE INTO courses (name)
SELECT DISTINCT Course FROM course_curricular_units_temp;

-- Insert curricular units (ignore duplicates)
INSERT IGNORE INTO curricular_units (name)
SELECT DISTINCT CurricularUnit FROM course_curricular_units_temp;

-- Insert course-unit relationships (ignore duplicates)
INSERT IGNORE INTO course_curricular_units (course_id, curricular_unit_id)
SELECT c.id, u.id
FROM course_curricular_units_temp t
JOIN courses c ON t.Course = c.name
JOIN curricular_units u ON t.CurricularUnit = u.name;

-- Drop the temporary table
DROP TABLE course_curricular_units_temp;

