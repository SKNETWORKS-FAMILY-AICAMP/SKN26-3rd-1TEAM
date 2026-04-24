"""
JobPocket 데이터 인제션에서 사용되는 SQL 쿼리 상수 정의 모듈입니다.
SQLAlchemy text() 기능을 위해 이름 기반 파라미터(:name) 형식을 사용합니다.
"""

# 회사 정보 적재
INSERT_COMPANY_SQL = (
    "INSERT IGNORE INTO companies (id, name) VALUES (:company_id, :company)"
)

# 채용공고 정보 적재
INSERT_JOBPOST_SQL = """
    INSERT IGNORE INTO job_posts
    (id, company_id, career_type, position_type, responsibilities, qualifications, preferred, description)
    VALUES (:jobpost_id, :company_id, :career_type, :position_type, :responsibilities, :qualifications, :preferred, :description)
"""

# 지원자 기록 적재
INSERT_APPLICANT_SQL = """
    INSERT IGNORE INTO applicant_records
    (id, jobpost_id, resume_cleaned, selfintro, selfintro_evaluation, selfintro_score, grade)
    VALUES (:applicant_id, :jobpost_id, :resume_cleaned, :selfintro, :selfintro_evaluation, :selfintro_score, :selfintro_grade)
"""

# 벡터 데이터 적재
INSERT_VECTOR_SQL = """
    INSERT IGNORE INTO resume_vectors (record_id, embedding) 
    VALUES (:record_id, STRING_TO_VECTOR(:embedding))
"""
