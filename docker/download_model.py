from sentence_transformers import SentenceTransformer

model = SentenceTransformer('all-MiniLM-L6-v2')
model.save('/home/udumularahul/RAG-APP-DOCUMENT/models/all-MiniLM-L6-v2')
print("Model downloaded and saved successfully!")