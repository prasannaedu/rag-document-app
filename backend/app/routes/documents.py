import json
import logging
import time
import uuid
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import Document, User
from app.schemas import DocumentResponse
from app.config import settings
from app.utils.document_parser import parse_document
from app.services.rag_service import RAGService
from app.dependencies import get_rag_service
from jose import jwt, JWTError
import boto3
from botocore.client import Config
import io
from app.schemas import QueryRequest

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")

def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
        exp = payload.get("exp")
        if exp is None or time.time() > exp:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token has expired")
    except JWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")

    user = db.query(User).filter(User.username == username).first()
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found")
    return user

router = APIRouter(tags=["documents"])
__all__ = ["router"]

s3_client = boto3.client(
    "s3",
    endpoint_url=settings.S3_ENDPOINT_URL,
    aws_access_key_id=settings.S3_ACCESS_KEY,
    aws_secret_access_key=settings.S3_SECRET_KEY,
    config=Config(signature_version="s3v4")
)

def initialize_s3_bucket():
    try:
        s3_client.head_bucket(Bucket=settings.S3_BUCKET)
        logger.info(f"S3 bucket '{settings.S3_BUCKET}' already exists")
    except s3_client.exceptions.ClientError as e:
        if e.response['Error']['Code'] == '404':
            logger.info(f"S3 bucket '{settings.S3_BUCKET}' does not exist. Creating it...")
            s3_client.create_bucket(Bucket=settings.S3_BUCKET)
            logger.info(f"Created S3 bucket: {settings.S3_BUCKET}")
        else:
            logger.error(f"Failed to check or create bucket: {str(e)}")
            raise
    except Exception as e:
        logger.error(f"Error initializing S3 bucket: {str(e)}")
        raise

initialize_s3_bucket()

@router.post("/upload", response_model=DocumentResponse)
async def upload_document(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    rag_service: RAGService = Depends(get_rag_service)
):
    logger.info(f"Starting upload for file: {file.filename}")
    logger.debug(f"User ID: {current_user.id}")
    logger.info(f"Received file with content_type: {file.content_type}")
    allowed_types = [
        "application/pdf",
        "application/vnd.ms-powerpoint",
        "application/vnd.openxmlformats-officedocument.presentationml.presentation",
        "text/csv",
        "text/plain",
        "application/octet-stream"
    ]
    if file.content_type not in allowed_types:
        logger.error(f"Unsupported file type: {file.content_type}")
        raise HTTPException(status_code=400, detail="Unsupported file type")

    file_extension = file.filename.split(".")[-1].lower()
    unique_filename = f"{uuid.uuid4()}.{file_extension}"
    logger.debug(f"Generated unique filename: {unique_filename}")

    file_content = await file.read()
    logger.debug(f"Read file content, length: {len(file_content)} bytes")
    file.file.seek(0)

    try:
        logger.debug("Uploading file to S3...")
        s3_client.upload_fileobj(io.BytesIO(file_content), settings.S3_BUCKET, unique_filename)
        logger.info(f"Successfully uploaded file to S3: {unique_filename}")
    except Exception as e:
        logger.error(f"Failed to upload file to S3: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to upload file: {str(e)}")

    extracted_text = parse_document(file_content, file.content_type)
    logger.debug(f" Extracted content (first 300 chars): {extracted_text[:300]}")

    metadata = {"filename": file.filename, "content_type": file.content_type}
    logger.debug(f"Parsed metadata: {metadata}")

    db_document = Document(
        user_id=current_user.id,
        filename=unique_filename,
        original_filename=file.filename,
        content=extracted_text,
        doc_metadata=metadata
    )
    try:
        db.add(db_document)
        db.commit()
        db.refresh(db_document)
        logger.debug(f"Document committed to DB with ID: {db_document.id}")
    except Exception as e:
        logger.error(f"Failed to save document to database: {str(e)}", exc_info=True)
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to save document to database: {str(e)}")

    try:
        rag_service.index_document(
            content=db_document.content,
            source=db_document.original_filename,
            user_id=db_document.user_id
        )
        logger.info(f"Indexed document ID {db_document.id} into vector store")
    except Exception as e:
        logger.error(f"Failed to index document immediately: {str(e)}", exc_info=True)
        logger.warning("Proceeding with upload despite indexing failure")

    logger.info(f"Upload completed for file: {file.filename}")
    return DocumentResponse.from_orm(db_document)


@router.post("/query")
async def query_document(
    request: QueryRequest,
    current_user: User = Depends(get_current_user),
    rag_service: RAGService = Depends(get_rag_service),
):
    logger.debug(f"Query request: {request.query}")
    response = rag_service.query_document(current_user.id, request.query)
    return response
