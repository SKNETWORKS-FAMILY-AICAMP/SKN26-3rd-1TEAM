import os

RDB_CONFIG = {
    'host': os.getenv('RDB_URL'),
    'port': 3306,
    'user': os.getenv('MYSQL_RDB_USER'),
    'password': os.getenv('MYSQL_RDB_PASSWORD'),
    'db': 'job_pocket_rdb',
    'charset': 'utf8mb4'  
}

VECTOR_DB_CONFIG = {
    'host': os.getenv('VECTOR_DB_URL'),
    'port': 3306,
    'user': os.getenv('MYSQL_VECTOR_USER'),
    'password': os.getenv('MYSQL_VECTOR_PASSWORD'),
    'db': 'job_pocket_vector',
    'charset': 'utf8mb4'    
}

OLLAMA_CONFIG = {
    'model': "exaone3.5:7.8b",
    'base_url': "http://localhost:11434",
    'temperature': 0.9,
}

OPENAI_API_CONFIG = {
    'model':"gpt-4o-mini",
    'temperature':0.55,
}

GROQ_API_CONFIG = {
    'model': "openai/gpt-oss-120b",
    'temperature': 0.65,
    'top_p': 1,
    'stop': None,
}

EMBEDDING_CONFIG = {
    'model_name': "Qwen/Qwen3-Embedding-0.6B",
    'model_kwargs': {'device': 'cpu'},
    'encode_kwargs': {'normalize_embeddings': True}
}
