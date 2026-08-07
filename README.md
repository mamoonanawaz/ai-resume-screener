# AI Resume Screener & Feedback

## Project Overview

AI Resume Screener & Feedback is a backend-based application that compares a candidate's resume with a job description.

The application extracts text from PDF and DOCX resumes, sends the resume and job description to the Gemini LLM, and returns structured feedback in JSON format.

The generated result includes:

- Resume and job-description match score from 0 to 100
- Important missing keywords
- Resume improvement and rewrite suggestions

This project was completed individually as part of the Week 2 task.

---

## Current Project Status

### Completed

- FastAPI backend setup
- PDF resume upload and text extraction
- DOCX resume upload and text extraction
- Extraction of text from DOCX paragraphs and tables
- Job-description input endpoint
- JSON-only LLM prompt template
- Gemini API integration
- API key management through `.env`


# AI Study Companion — Week 3

AI & Generative AI Fellowship — Week 3 Project

## Overview

The AI Study Companion is a retrieval-based learning assistant built using FastAPI, Gemini, and Qdrant.

The application allows a user to upload study notes or syllabus documents, extract their text, divide the content into meaningful chunks, generate vector embeddings, store those embeddings in Qdrant, retrieve relevant information based on a study topic, and generate a structured study plan using Gemini.

This project builds the retrieval foundation required for the AI Study Companion.

---

## Features

- Upload PDF, TXT, and DOCX study documents
- Extract text from uploaded documents
- Split documents into meaningful chunks
- Generate embeddings for every chunk using Gemini
- Store embeddings and original chunk text in Qdrant
- Generate embeddings for user search queries
- Retrieve the most relevant chunks from Qdrant
- Generate a structured study plan using retrieved content
- Return study plans as JSON
- FastAPI Swagger documentation for testing endpoints
- API keys stored securely using environment variables

---

## Tech Stack

### Backend
- Python
- FastAPI
- Uvicorn

### AI / LLM
- Google Gemini
- Gemini Embeddings

### Vector Database
- Qdrant Cloud

### Document Processing
- PyPDF
- python-docx

### Version Control
- Git
- GitHub

---

## Retrieval Pipeline

The application follows this pipeline:

1. Upload study document
2. Extract document text
3. Split text into chunks
4. Generate embeddings for every chunk
5. Store embeddings in Qdrant
6. Receive a study topic/query
7. Generate query embedding
8. Search Qdrant for relevant chunks
9. Send retrieved chunks to Gemini
10. Generate a structured JSON study plan

Flow:

Upload Document  
↓  
Text Extraction  
↓  
Chunking  
↓  
Gemini Embeddings  
↓  
Qdrant Vector Database  
↓  
User Query  
↓  
Query Embedding  
↓  
Semantic Retrieval  
↓  
Gemini  
↓  
JSON Study Plan

---

## Project Structure

```text
ai-resume-screener/
│
├── backend/
│   ├── app/
│   │   ├── main.py
│   │   │
│   │   └── services/
│   │       ├── chunker.py
│   │       ├── embedding_service.py
│   │       ├── llm_service.py
│   │       ├── prompt.py
│   │       ├── qdrant_service.py
│   │       ├── study_plan_service.py
│   │       └── text_extractor.py
│   │
│   ├── requirements.txt
│   └── .env
│
├── .gitignore
└── README.md
- JSON response validation using Pydantic
- Retry logic for invalid LLM responses
- Final resume-analysis endpoint
- GitHub branches and feature-based workflow
- Meaningful Git commits
- Feature pull requests into the `dev` branch
