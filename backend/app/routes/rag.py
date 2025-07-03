from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from langchain.docstore.document import Document as LangChainDoc

embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
vector_store = None

def index_document(doc_id: int, content: str, content_type: str = "text"):
    global vector_store
    doc = LangChainDoc(page_content=content, metadata={"doc_id": doc_id, "content_type": content_type})
    if vector_store is None:
        vector_store = FAISS.from_documents([doc], embeddings)
    else:
        vector_store.add_documents([doc])

def query_documents(query: str, k: int = 3):
    global vector_store
    if vector_store is None:
        return None
    
    docs = vector_store.similarity_search(query, k=k)
    
    for doc in docs:
        if "company name" in query.lower() and doc.metadata.get("content_type") == "application/pdf":
            return [doc]
    
    return [docs[0]] if docs else None