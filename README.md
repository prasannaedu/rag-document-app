#  Document RAG App

A full-stack intelligent document assistant that enables users to securely upload PDFs, CSVs, PPTs, etc., and ask natural language questions about their content. It uses advanced NLP with Retrieval-Augmented Generation (RAG) powered by LangChain and HuggingFace.

##  Features Implemented (Phase 1)

-  User registration and login (JWT-based)
-  Upload of PDF, CSV, PPT files via frontend or cURL
-  Documents are stored in MinIO (S3-compatible)
-  PDF content parsed using `unstructured.io`
-  HuggingFace embeddings + LangChain + Chroma for vector storage
-  Fast query answering with document references (RAG pipeline)
-  React frontend with protected routes using bearer token
-  Dockerized: Backend, Frontend, Redis, PostgreSQL, MinIO, Celery, Nginx

##  Tech Stack

| Layer         | Tools/Frameworks |
|---------------|------------------|
| Frontend      | React.js         |
| Backend       | FastAPI          |
| Auth          | JWT + Redis      |
| Parsing       | Unstructured.io  |
| Vector Store  | Chroma + LangChain |
| Embeddings    | HuggingFace Transformers |
| LLM           | FLAN-T5-small    |
| Queue         | Celery + Redis   |
| Storage       | MinIO (S3 API)   |
| DB            | PostgreSQL       |
| Search        | Elasticsearch    |
| Container     | Docker Compose   |
| Proxy         | Nginx            |

##  Architecture

```text
User → React (frontend) → FastAPI (backend) → MinIO + Postgres + ChromaDB
     ↘ JWT Auth         ↘ Celery workers → Parse + Embed → Store chunks
     ↘ Nginx Reverse Proxy
```

##  Local Development Setup

### 1. Clone and Configure

```bash
git clone https://github.com/YOUR_USERNAME/YOUR_REPO_NAME.git
cd RAG-APP-DOCUMENT
cp .env.example .env  # then edit credentials as needed
```

### 2. Build and Run with Docker

```bash
docker-compose up -d --build
```

This runs all services: backend, frontend, postgres, redis, minio, elasticsearch, nginx, celery.

### 3. Access Services

- Frontend: http://localhost
- API Docs: http://localhost/api/docs
- MinIO: http://localhost:9001 (user/pass in `.env`)
- PGAdmin: if added (optional)
- Elasticsearch: http://localhost:9200

##  Testing Example (cURL)

```bash
# 1. Login
curl -X POST http://localhost/api/auth/login   -F username=testuser -F password=testpassword

# 2. Upload a document
curl -X POST http://localhost/api/documents/upload   -H "Authorization: Bearer <your_token>"   -F file=@1PageStallion.pdf

# 3. Query it
curl -X POST http://localhost/api/documents/query   -H "Authorization: Bearer <your_token>"   -H "Content-Type: application/json"   -d '{"query": "What is Stallion about?"}'
```

##  Use Case

- Upload PDFs and ask questions like “What is the company's revenue?”
- Automatically parse, index and respond with relevant content
- Cited answers with document sources

##  Folder Structure

```
.
├── backend/             # FastAPI app
├── frontend/            # React app
├── docker/              # Dockerfiles
├── nginx/               # Nginx reverse proxy
├── models/              # Pretrained models (offline mode)
├── docker-compose.yml   # Compose all services
├── .env, .gitignore     # Configs
└── README.md
```

##  Work Completed So Far

-  Phase 1 done: Upload → Parse → Embed → Query
-  Nginx proxy to both backend (/api) and frontend (/)
-  Dockerized multi-container setup

##  Next Steps

- [ ] Kubernetes deployment
- [ ] Replace Chroma with Elasticsearch
- [ ] Improve LLM to GPT or Claude for answers
- [ ] Add multi-user document visibility
- [ ] UI polish & query history

##  Maintainer

- **Name:** Prasanna Edu (udumulaprasannakumar@gmail.com)
- **GitHub:** [github.com/prasannaedu](https://github.com/prasannaedu)

---

> Built with ❤️ for document understanding & NLP-powered automation.