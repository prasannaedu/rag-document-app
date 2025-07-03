import time
import logging
from typing import Optional

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from jose import jwt, JWTError
import redis

from app.database import get_db
from app.models import User
from app.config import settings
from app.services.rag_service import RAGService

logger = logging.getLogger(__name__)

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

def get_redis_client() -> Optional[redis.Redis]:
    """Lazily initialize Redis client."""
    try:
        client = redis.Redis.from_url(settings.REDIS_URL, decode_responses=True)
        client.ping()
        logger.debug("Connected to Redis")
        return client
    except redis.ConnectionError as e:
        logger.warning(f"Redis connection failed: {str(e)}")
        return None

def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    """Authenticate user using JWT, Redis cache, and DB fallback."""
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        username: str = payload.get("sub")

        if username is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token: missing subject",
                headers={"WWW-Authenticate": "Bearer"},
            )

        exp = payload.get("exp")
        if exp is None or time.time() > exp:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token has expired",
                headers={"WWW-Authenticate": "Bearer"},
            )

        redis_client = get_redis_client()
        if redis_client:
            cached_user = redis_client.get(token)
            if cached_user == username:
                logger.debug(f"User {username} validated from Redis cache")
                return db.query(User).filter(User.username == username).first()

        user = db.query(User).filter(User.username == username).first()
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found",
                headers={"WWW-Authenticate": "Bearer"},
            )

        if redis_client:
            redis_client.setex(token, 3600, username) 

        return user

    except JWTError as e:
        logger.warning(f"JWT validation failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

def get_rag_service(db: Session = Depends(get_db)) -> RAGService:
    """Provide an instance of RAGService."""
    return RAGService(minimal_mode=False)
