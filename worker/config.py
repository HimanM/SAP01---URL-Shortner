import os

class Config:
    KAFKA_BROKER = os.getenv("KAFKA_BROKER", "kafka:9092")
    DB_HOST = os.getenv("DB_HOST", "analytics-db")
    DB_NAME = os.getenv("DB_NAME", "analytics")
    DB_USER = os.getenv("DB_USER", "postgres")
    DB_PASS = os.getenv("DB_PASSWORD", "password")
