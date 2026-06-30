---
title: RBI Chatbot
emoji: 🏦
colorFrom: blue
colorTo: indigo
sdk: docker
pinned: false
---





# 🏦 RBI Chatbot

An AI-powered Retrieval-Augmented Generation (RAG) chatbot that answers RBI-related queries using semantic search and document retrieval.


## 🚀 Live Demo

**Hugging Face Space:**
https://dhruv021-rbi-chatbot.hf.space/

---

## 📖 Project Overview

RBI Chatbot is a document-aware conversational AI system that enables users to ask questions about Reserve Bank of India policies, regulations, banking concepts, and financial guidelines.

The application leverages:

* FastAPI for backend APIs
* FAISS for vector similarity search
* Retrieval-Augmented Generation (RAG)
* Docker-based deployment
* Hugging Face Spaces hosting

---

## ✨ Features

* Semantic search over RBI documents
* Context-aware question answering
* FastAPI REST API backend
* Interactive web interface
* FAISS vector database
* Containerized deployment using Docker
* Hosted on Hugging Face Spaces

---

## 🏗️ Architecture

```text
User
  │
  ▼
Frontend (HTML/CSS/JavaScript)
  │
  ▼
FastAPI Backend
  │
  ▼
FAISS Vector Store
  │
  ▼
Relevant Context Retrieval
  │
  ▼
Generated Response
  │
  ▼
User
```

---

## 🛠️ Tech Stack

### Backend

* Python 3.11
* FastAPI
* Uvicorn

### AI & Retrieval

* FAISS
* Sentence Transformers
* Retrieval-Augmented Generation (RAG)

### Frontend

* HTML
* CSS
* JavaScript

### Deployment

* Docker
* Hugging Face Spaces

---

## 📂 Project Structure

```text
RBI_CHATBOT/
│
├── Backend/
│   ├── api.py
│   ├── chatbot.py
│   ├── config.py
│   ├── vector_store.py
│   ├── data_processing.py
│   └── faiss_vector_db/
│
├── Frontend/
│   ├── index.html
│   ├── script.js
│   └── styles.css
│
├── Dockerfile
├── requirements.txt
├── README.md
└── rbi_textbook.pdf
```

---

## ⚙️ Local Setup

```bash
git clone https://github.com/DhruvChaudhary13/RBI_Chatbot.git
cd RBI_Chatbot

python -m venv .venv
.venv\Scripts\activate

pip install -r requirements.txt
```

---

## ▶️ Run Locally

```bash
uvicorn Backend.api:app --host 0.0.0.0 --port 8000 --reload
```

Application URL:

```text
http://localhost:8000
```

---

## 🐳 Docker Deployment

### Build Docker Image

```bash
docker build -t rbi-chatbot .
```

### Run Docker Container

```bash
docker run -p 7860:7860 rbi-chatbot
```

### Docker Configuration

```dockerfile
FROM python:3.11

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 7860

CMD ["uvicorn", "Backend.api:app", "--host", "0.0.0.0", "--port", "7860"]
```

---

## 🤗 Hugging Face Spaces Deployment

The application is deployed as a Docker Space on Hugging Face.

### Live Application

https://dhruv021-rbi-chatbot.hf.space/

### Deployment Workflow

1. Push code to the Hugging Face Space repository.
2. Docker image builds automatically.
3. FastAPI server starts on port `7860`.
4. The application becomes publicly accessible.

---

## 🎯 Use Cases

* RBI policy understanding
* Banking regulations lookup
* Financial education
* Academic learning
* Quick information retrieval from RBI resources

---

## 👨‍💻 Author

**Dhruv Chaudhary**

GitHub: https://github.com/DhruvChaudhary13

---

## ⭐ Support

If you found this project useful, consider giving the repository a star.
