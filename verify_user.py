from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from backend.app.models import User

db_path = "/home/udumularahul/RAG-APP-DOCUMENT/test.db"
engine = create_engine(f"sqlite:///{db_path}", connect_args={"check_same_thread": False})

with Session(bind=engine) as session:
    users = session.query(User).all()
    for user in users:
        print(f"User: {user.username}")
