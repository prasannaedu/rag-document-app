import logging
import os
from typing import Dict, Any

from langchain.chains import RetrievalQA
from langchain_community.vectorstores import Chroma
from langchain_community.llms import HuggingFacePipeline
from langchain_huggingface import HuggingFaceEmbeddings
from transformers import pipeline, AutoModelForSeq2SeqLM, AutoTokenizer
from sqlalchemy.orm import Session

from app.models import Document
from app.config import settings

logger = logging.getLogger(__name__)
CHROMA_DB_DIR = settings.CHROMA_DB_DIR


class RAGService:
    def __init__(self, minimal_mode: bool = False):
        self.minimal_mode = minimal_mode
        self.embeddings = None
        self.vector_store = None
        self.qa_chain = None

        if self.minimal_mode:
            logger.info(" RAGService running in minimal mode.")
            return

        try:
            logger.info(" Initializing HuggingFace embeddings...")
            self.embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")

            logger.info(" Loading or creating Chroma vector store...")
            self.vector_store = Chroma(
                persist_directory=CHROMA_DB_DIR,
                embedding_function=self.embeddings,
            )

            logger.info(" Loading HuggingFace LLM pipeline...")
            model_name = os.getenv("HF_MODEL_NAME", "google/flan-t5-small")

            model = AutoModelForSeq2SeqLM.from_pretrained(model_name)
            tokenizer = AutoTokenizer.from_pretrained(model_name)

            llm_pipeline = pipeline(
                "text2text-generation",
                model=model,
                tokenizer=tokenizer,
                device=-1,
                max_new_tokens=256
            )
            llm = HuggingFacePipeline(pipeline=llm_pipeline)

            retriever = self.vector_store.as_retriever(search_kwargs={"k": 3})
            self.qa_chain = RetrievalQA.from_chain_type(
                llm=llm,
                chain_type="map_reduce",
                retriever=retriever
            )

            logger.info(" RAGService initialized successfully.")

        except Exception as e:
            logger.error(" RAGService initialization failed", exc_info=True)
            self.minimal_mode = True

    def get_status(self) -> Dict[str, bool]:
        return {
            "embeddings_initialized": self.embeddings is not None or self.minimal_mode,
            "vector_store_initialized": self.vector_store is not None or self.minimal_mode,
            "qa_chain_initialized": self.qa_chain is not None or self.minimal_mode,
        }

    def index_document(self, content: str, source: str, user_id: int):
        if self.minimal_mode:
            logger.warning(" Skipping indexing: RAGService is in minimal mode.")
            return

        try:
            logger.info(f" Indexing document: {source} | User ID: {user_id}")
            self.vector_store.add_texts(
                texts=[content],
                metadatas=[{"source": source, "user_id": user_id}],
            )
            self.vector_store.persist()
            logger.info(" Document indexed successfully.")
        except Exception as e:
            logger.error(" Document indexing failed", exc_info=True)

    def query_document(self, user_id: int, query: str) -> Dict[str, Any]:
        if self.minimal_mode:
            logger.warning(" Skipping query: RAGService is in minimal mode.")
            return {"answer": "RAGService is in minimal mode", "sources": []}

        try:
            logger.info(f" Query from User {user_id}: {query}")

            retriever = self.vector_store.as_retriever(
                search_kwargs={"k": 3, "filter": {"user_id": user_id}}
            )
            self.qa_chain.retriever = retriever

            #  Manually retrieve documents
            source_docs = retriever.get_relevant_documents(query)

            # Run the QA chain
            result = self.qa_chain.invoke({"query": query})
            answer = result.get("result", "No answer generated.")

            sources = [doc.metadata.get("source", "unknown") for doc in source_docs]

            logger.info(" Query answered.")
            return {"answer": answer, "sources": sources}

        except Exception as e:
            logger.error(" Query failed", exc_info=True)
            return {"answer": f"Error: {e}", "sources": []}

    def reindex_all_documents(self, db: Session):
        if self.minimal_mode:
            logger.warning(" Skipping reindex: RAGService is in minimal mode.")
            return

        try:
            logger.info(" Reindexing all documents from DB...")

            documents = db.query(Document).all()
            if not documents:
                logger.info("ℹ No documents found in DB.")
                return

            for doc in documents:
                if doc.content:
                    self.vector_store.add_texts(
                        texts=[doc.content],
                        metadatas=[{"source": doc.original_filename, "user_id": doc.user_id}],
                    )

            self.vector_store.persist()
            logger.info(f" Reindexed {len(documents)} documents.")

        except Exception as e:
            logger.error(" Reindexing failed", exc_info=True)
