import logging
from fastapi import FastAPI
from app.routes import auth, documents, rag_router
from app.database import get_db, verify_connection, initialize_models
from app.services.rag_service import RAGService


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

print(">>> Starting FastAPI app <<<")


app = FastAPI()


app.include_router(auth.router, prefix="/auth", tags=["Auth"])
app.include_router(documents.router, prefix="/documents", tags=["Documents"])
app.include_router(rag_router.router, prefix="", tags=["RAG"])

@app.on_event("startup")
async def startup_event():
    logger.info(" Application startup initiated")

    try:
        verify_connection()
        initialize_models()
        logger.info(" Database connected and models initialized")

        db_gen = get_db()
        db = next(db_gen)

        try:
            
            rag_service = RAGService(minimal_mode=False)

            
            rag_service.reindex_all_documents(db)
            logger.info(" RAGService reindexing completed in full mode")

        except Exception as e:
            logger.warning(f" Failed to initialize RAGService in full mode: {e}")
            

        finally:
            try:
                next(db_gen, None) 
            except StopIteration:
                pass

        logger.info(" Application startup completed")

    except Exception as e:
        logger.critical(" Application failed to start", exc_info=True)
        raise

@app.get("/")
async def root():
    return {"message": "Welcome to the RAG API"}
