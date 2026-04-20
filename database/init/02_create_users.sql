CREATE USER IF NOT EXISTS 'rdb_user'@'%' IDENTIFIED BY 'rdb_password';
CREATE USER IF NOT EXISTS 'vector_user'@'%' IDENTIFIED BY 'vector_password';

GRANT ALL PRIVILEGES ON job_pocket_rdb.* TO 'rdb_user'@'%';
GRANT ALL PRIVILEGES ON job_pocket_vector.* TO 'vector_user'@'%';

FLUSH PRIVILEGES;