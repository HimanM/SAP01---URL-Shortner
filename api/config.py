import os

class Config:
    BASE_URL = os.getenv("BASE_URL", "http://localhost:8080")
    DB_HOST = os.getenv("DB_HOST", "postgres-primary")
    DB_USER = os.getenv("POSTGRES_USER", "postgres")
    DB_PASS = os.getenv("POSTGRES_PASSWORD", "password")
    DB_NAME = os.getenv("POSTGRES_DB", "urls")
    REDIS_HOST = os.getenv("REDIS_HOST", "redis")
    REDIS_PORT = int(os.getenv("REDIS_PORT", 6379))
    KAFKA_BROKER = os.getenv("KAFKA_BROKER", "kafka:9092")
