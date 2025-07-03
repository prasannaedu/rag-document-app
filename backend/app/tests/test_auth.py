import pytest
from httpx import AsyncClient
from sqlalchemy.orm import Session

from app.main import app
from app.database import get_db
from app.models import User
from app.config import settings


@pytest.fixture
def test_user(db: Session):
    
    user = User(username="testuser", email="test@example.com", password="testpass")
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@pytest.mark.asyncio
async def test_login_success(test_user):
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.post(
            "/auth/login",
            data={"username": "testuser", "password": "testpass"}
        )
        assert response.status_code == 200
        json_data = response.json()
        assert "access_token" in json_data
        assert json_data["token_type"] == "bearer"


@pytest.mark.asyncio
async def test_login_failure():
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.post(
            "/auth/login",
            data={"username": "wronguser", "password": "wrongpass"}
        )
        assert response.status_code == 401


@pytest.mark.asyncio
async def test_me_authenticated(test_user):
    
    async with AsyncClient(app=app, base_url="http://test") as client:
        login_response = await client.post(
            "/auth/login",
            data={"username": "testuser", "password": "testpass"}
        )
        token = login_response.json()["access_token"]

        
        headers = {"Authorization": f"Bearer {token}"}
        response = await client.get("/auth/me", headers=headers)
        assert response.status_code == 200
        data = response.json()
        assert data["username"] == "testuser"
        assert data["email"] == "test@example.com"
