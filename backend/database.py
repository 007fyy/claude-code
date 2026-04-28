from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

# 默认 SQLite（开箱即用）；换 MySQL 只需改这一行：
# mysql+pymysql://root:password@localhost/jewelry_vtryon
SQLALCHEMY_DATABASE_URL = "sqlite:///./jewelry.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
