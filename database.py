from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

DATABASE_URL = "sqlite:///./users.db"  # Database file path
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db():
    print('in get_db')
    db = SessionLocal()
    print('after db session')
    try:
        yield db
    finally:
        db.close()