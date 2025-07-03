from celery import Celery
from app.config import settings

celery_app = Celery(
    "rag_tasks",
    broker=settings.REDIS_URL,
    backend=settings.REDIS_URL
)

@celery_app.task(name="process_document")
def process_document(document_id: int, user_id: int):
    from app.database import SessionLocal
    from app.services.rag_service import RAGService
    from app.utils.document_parser import parse_document
    from app.models import Document
    import boto3
    from botocore.client import Config
    import io
    import logging

    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)

    db = SessionLocal()
    try:
        doc = db.query(Document).filter(Document.id == document_id).first()
        if not doc:
            logger.error(f"Document {document_id} not found")
            return {"error": f"Document {document_id} not found"}

        # Download file from S3
        s3 = boto3.client(
            "s3",
            endpoint_url=settings.S3_ENDPOINT_URL,
            aws_access_key_id=settings.S3_ACCESS_KEY,
            aws_secret_access_key=settings.S3_SECRET_KEY,
            config=Config(signature_version="s3v4")
        )
        file_obj = io.BytesIO()
        s3.download_fileobj(settings.S3_BUCKET, doc.filename, file_obj)
        file_obj.seek(0)

        # Extract text
        content = parse_document(file_obj.read(), doc.doc_metadata["content_type"])
        doc.content = content
        db.commit()
        logger.info(f" Saved extracted content for Document {document_id}")

        # Now index into RAG
        rag_service = RAGService()
        rag_service.index_document(content, doc.original_filename, user_id)
        logger.info(f" Indexed document {document_id} into vector store")

        return {"status": "success"}
    except Exception as e:
        logger.exception(" Failed to process document")
        return {"error": str(e)}
    finally:
        db.close()
