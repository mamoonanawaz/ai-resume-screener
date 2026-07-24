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
- JSON response validation using Pydantic
- Retry logic for invalid LLM responses
- Final resume-analysis endpoint
- GitHub branches and feature-based workflow
- Meaningful Git commits
- Feature pull requests into the `dev` branch
