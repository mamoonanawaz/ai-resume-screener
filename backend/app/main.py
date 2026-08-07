from fastapi import FastAPI, File, Form, HTTPException, UploadFile

from app.services.text_extractor import extract_text
from app.services.chunker import chunk_text


app = FastAPI(title="AI Resume Screener API")


@app.get("/")
def home():
    return {"message": "AI Resume Screener API is running"}


@app.post("/extract-resume")
async def extract_resume(resume: UploadFile = File(...)):
    filename = resume.filename or ""

    if not filename.lower().endswith((".pdf", ".docx")):
        raise HTTPException(
            status_code=400,
            detail="Only PDF and DOCX files are supported."
        )

    try:
        file_bytes = await resume.read()

        if not file_bytes:
            raise HTTPException(
                status_code=400,
                detail="The uploaded file is empty."
            )

        extracted_text = extract_text(file_bytes, filename)

        if not extracted_text:
            raise HTTPException(
                status_code=422,
                detail="No readable text was found in the resume."
            )

        return {
            "filename": filename,
            "text": extracted_text
        }

    except HTTPException:
        raise

    except ValueError as error:
        raise HTTPException(
            status_code=400,
            detail=str(error)
        )

    except Exception as error:
        raise HTTPException(
            status_code=500,
            detail=f"Text extraction failed: {str(error)}"
        )


@app.post("/job-description")
async def submit_job_description(
    job_description: str = Form(...)
):
    cleaned_description = job_description.strip()

    if len(cleaned_description) < 20:
        raise HTTPException(
            status_code=400,
            detail="Job description must contain at least 20 characters."
        )

    return {
        "job_description": cleaned_description,
        "character_count": len(cleaned_description)
    }


@app.post("/upload-document")
async def upload_document(document: UploadFile = File(...)):
    filename = document.filename or ""

    if not filename.lower().endswith((".pdf", ".txt", ".docx")):
        raise HTTPException(
            status_code=400,
            detail="Only PDF, TXT, and DOCX files are supported."
        )

    try:
        file_bytes = await document.read()

        if not file_bytes:
            raise HTTPException(
                status_code=400,
                detail="The uploaded document is empty."
            )

        extracted_text = extract_text(file_bytes, filename)

        if not extracted_text:
            raise HTTPException(
                status_code=422,
                detail="No readable text was found in the document."
            )

        chunks = chunk_text(extracted_text)

        return {
            "message": "Document uploaded and chunked successfully",
            "filename": filename,
            "character_count": len(extracted_text),
            "chunk_count": len(chunks),
            "chunks": [
                {
                    "chunk_id": index,
                    "text": chunk
                }
                for index, chunk in enumerate(chunks)
            ]
        }

    except HTTPException:
        raise

    except ValueError as error:
        raise HTTPException(
            status_code=400,
            detail=str(error)
        )

    except Exception as error:
        raise HTTPException(
            status_code=500,
            detail=f"Document upload failed: {str(error)}"
        )