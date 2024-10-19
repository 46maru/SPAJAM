from sqlalchemy.engine import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import Session, scoped_session, sessionmaker

from env import DB_HOST, DB_NAME, DB_PASSWORD, DB_USER


DATABASE = "mysql://%s:%s@%s/%s?charset=utf8mb4" % (
    DB_USER,
    DB_PASSWORD,
    DB_HOST,
    DB_NAME,
)


engine = create_engine(
    DATABASE,
    echo=True,
    pool_size=20,
    max_overflow=100
)
Base = declarative_base()

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

ScopedSessionLocal = scoped_session(SessionLocal)

def get_db():
    db = SessionLocal()
    try:
        yield db
        db.commit()
    except Exception as e:
        print(e)
        db.rollback()
    finally:
        db.close()
