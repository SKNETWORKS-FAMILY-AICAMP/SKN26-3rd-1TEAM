USE job_pocket_vector;

CREATE TABLE
    IF NOT EXISTS companies (
        id INT AUTO_INCREMENT PRIMARY KEY,
        name VARCHAR(100) UNIQUE NOT NULL,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
    );

CREATE TABLE
    IF NOT EXISTS job_posts (
        id INT AUTO_INCREMENT PRIMARY KEY,
        company_id INT NOT NULL,
        description TEXT,
        position_type ENUM (
            'frontend engineer',
            'backend engineer',
            'ai engineer'
        ) NOT NULL,
        career_type ENUM ('junior', 'senior') NOT NULL,
        responsibilities TEXT NOT NULL,
        qualifications TEXT NOT NULL,
        preferred TEXT,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        CONSTRAINT fk_company_id FOREIGN KEY (company_id) REFERENCES companies (id) ON DELETE CASCADE
    );

CREATE TABLE
    IF NOT EXISTS applicant_records (
        id BIGINT AUTO_INCREMENT PRIMARY KEY,
        jobpost_id INT NOT NULL,
        resume_cleaned TEXT NOT NULL,
        selfintro TEXT NOT NULL,
        selfintro_evaluation TEXT NOT NULL,
        selfintro_score INT NOT NULL,
        grade ENUM ('high', 'mid', 'low') NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        INDEX idx_grade (grade),
        CONSTRAINT fk_record_id FOREIGN KEY (jobpost_id) REFERENCES job_posts (id) ON DELETE CASCADE
    );

CREATE TABLE
    IF NOT EXISTS resume_vectors (
        record_id BIGINT PRIMARY KEY,
        embedding VECTOR (1024) NOT NULL,
        CONSTRAINT fk_resume_id FOREIGN KEY (record_id) REFERENCES applicant_records (id) ON DELETE CASCADE
    );