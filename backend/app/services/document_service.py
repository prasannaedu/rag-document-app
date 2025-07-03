import os
from unstructured.partition.auto import partition
from .rag_service import index_document
from ..config import UPLOAD_DIR

def save_and_parse_document(file, filename, user_id):
    filepath = os.path.join(UPLOAD_DIR, filename)
    with open(filepath, "wb") as f:
        f.write(file.read())
    
    
    elements = partition(filename=filepath)
    text = " ".join([str(el) for el in elements])
    
    
    index_document(text, filename, user_id)
    
    return filepath