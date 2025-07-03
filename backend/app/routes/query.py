from fastapi import APIRouter, Depends
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session  
from ..schemas import QueryRequest
from ..services.rag_service import query_document
from ..database import get_db


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")

def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
    except JWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
    
    user = db.query(User).filter(User.username == username).first()
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found")
    return user


from ..config import SECRET_KEY, ALGORITHM
from ..models import User
from fastapi import HTTPException

router = APIRouter(prefix="/documents", tags=["documents"])
@router.post("/query")
async def query(request: QueryRequest, user=Depends(get_current_user)):
    response = query_document(request.query, user.id)  
    return response