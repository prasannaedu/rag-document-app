import os
import pytest
from datetime import datetime
from sqlalchemy import create_engine, inspect
from sqlalchemy.orm import Session

from backend.app.models import User, Document
from backend.app.database import Base as DatabaseBase


TEST_DB_PATH = "/home/udumularahul/RAG-APP-DOCUMENT/test.db"


@pytest.fixture(scope="module")
def test_db_engine():
    
    if os.path.exists(TEST_DB_PATH):
        os.remove(TEST_DB_PATH)
        print("Removed existing DB.")
    open(TEST_DB_PATH, 'a').close()
    print("Created new DB.")

    
    SQLALCHEMY_DATABASE_URL = f"sqlite:///{TEST_DB_PATH}"
    engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
    
   
    DatabaseBase.metadata.create_all(bind=engine)
    print("Tables created.")

    yield engine

    
    engine.dispose()
    if os.path.exists(TEST_DB_PATH):
        os.remove(TEST_DB_PATH)
        print("Deleted test DB.")


@pytest.fixture
def db_session(test_db_engine):
    with Session(bind=test_db_engine) as session:
        yield session


def test_insert_and_verify_user_and_document(db_session):
    
    db_session.query(Document).delete()
    db_session.query(User).delete()
    db_session.commit()

    
    new_user = User(username="testuser", hashed_password="testpass")
    db_session.add(new_user)
    db_session.flush()

    
    new_doc = Document(
        user_id=new_user.id,
        filename="testfile",
        filepath="/test/path",
        uploaded_at=datetime.now()
    )
    db_session.add(new_doc)
    db_session.commit()
    print("Data committed.")

    
    user = db_session.query(User).filter_by(username="testuser").first()
    doc = db_session.query(Document).filter_by(filename="testfile").first()

    assert user is not None
    assert user.username == "testuser"
    assert doc is not None
    assert doc.filename == "testfile"
    print("Verified User and Document.")


def test_tables_exist(test_db_engine):
    inspector = inspect(test_db_engine)
    tables = inspector.get_table_names()
    print("Tables:", tables)

    assert "users" in tables
    assert "documents" in tables
