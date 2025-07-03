from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import User
from app.schemas import Token
from app.config import settings
from jose import jwt
from datetime import datetime, timedelta
import bcrypt
import redis
import logging
from pydantic import BaseModel

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter(tags=["auth"])

class LoginRequest(BaseModel):
    username: str
    password: str

def get_redis_client():
    try:
        client = redis.Redis.from_url(settings.REDIS_URL, decode_responses=True)
        client.ping()
        return client
    except redis.ConnectionError as e:
        logger.warning(f"Redis connection failed: {str(e)}")
        return None

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return bcrypt.checkpw(plain_password.encode("utf-8"), hashed_password.encode("utf-8"))

def create_access_token(data: dict, expires_delta: timedelta = None):
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=15))
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    ttl = int((expire - datetime.utcnow()).total_seconds())

    redis_client = get_redis_client()
    if redis_client:
        try:
            redis_client.setex(encoded_jwt, ttl, data["sub"])
            logger.info(f"Token cached in Redis: {encoded_jwt}, TTL: {ttl}")
        except redis.RedisError as e:
            logger.error(f"Failed to cache token in Redis: {str(e)}")

    return encoded_jwt

@router.post("/register")
async def register(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    db_user = db.query(User).filter(User.username == form_data.username).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Username already registered")

    hashed_password = bcrypt.hashpw(form_data.password.encode("utf-8"), bcrypt.gensalt())
    db_user = User(
        username=form_data.username,
        email=f"{form_data.username}@example.com",
        password_hash=hashed_password.decode("utf-8"),  
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    logger.info(f"User {db_user.username} registered successfully")
    return {"message": "User registered successfully", "user_id": db_user.id}

@router.post("/login", response_model=Token)
async def login(request: Request, db: Session = Depends(get_db)):
    try:
        if request.headers.get("content-type", "").startswith("application/json"):
            body = await request.json()
            form_data = LoginRequest(**body)
            username = form_data.username
            password = form_data.password
        else:
            form = await request.form()
            username = form.get("username")
            password = form.get("password")

        user = db.query(User).filter(User.username == username).first()
        if not user or not verify_password(password, user.password_hash):  
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect username or password",
                headers={"WWW-Authenticate": "Bearer"},
            )

        access_token = create_access_token(
            data={"sub": user.username},
            expires_delta=timedelta(minutes=30)
        )
        logger.info(f"User {user.username} logged in successfully")
        return {"access_token": access_token, "token_type": "bearer"}

    except Exception as e:
        logger.error(f"Login failed: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail="Login error")
