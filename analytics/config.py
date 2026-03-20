import os

class Config:
    DB_HOST = os.getenv("DB_HOST", "analytics-db")
    DB_USER = os.getenv("POSTGRES_USER", "postgres")
    DB_PASS = os.getenv("POSTGRES_PASSWORD", "password")
    DB_NAME = os.getenv("POSTGRES_DB", "analytics")
