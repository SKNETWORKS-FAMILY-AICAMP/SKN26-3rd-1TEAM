USE job_pocket_rdb;

CREATE TABLE
    IF NOT EXISTS users (
        idx INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
        username VARCHAR(50),
        password VARCHAR(255) NOT NULL,
        email VARCHAR(100) NOT NULL UNIQUE,
        resume_data TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    ) ENGINE = InnoDB DEFAULT CHARSET = utf8mb4;

CREATE TABLE
    IF NOT EXISTS chat_history (
        id INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
        user_email VARCHAR(100) NOT NULL,
        role VARCHAR(20) NOT NULL,
        content TEXT NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        CONSTRAINT fk_user_email FOREIGN KEY (user_email) REFERENCES users (email) ON DELETE CASCADE ON UPDATE CASCADE
    ) ENGINE = InnoDB DEFAULT CHARSET = utf8mb4;