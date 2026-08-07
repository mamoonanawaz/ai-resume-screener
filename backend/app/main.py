from fastapi import FastAPI, File, Form, HTTPException, UploadFile

from app.services.text_extractor import extract_text
from app.services.chunker import chunk_text
from app.services.embedding_service import generate_embeddings
from app.services.qdrant_service import store_chunks


app = FastAPI(title="AI Study Companion API")


@app.get("/")
def home():
    return {
        "message": "AI Study Companion API is running"
    }


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
        # Read uploaded file
        file_bytes = await document.read()

        if not file_bytes:
            raise HTTPException(
                status_code=400,
                detail="The uploaded document is empty."
            )

        # Step 1: Extract text
        extracted_text = extract_text(
            file_bytes,
            filename
        )

        if not extracted_text:
            raise HTTPException(
                status_code=422,
                detail="No readable text was found in the document."
            )

        # Step 2: Chunk the document
        chunks = chunk_text(extracted_text)

        if not chunks:
            raise HTTPException(
                status_code=422,
                detail="No chunks could be generated from the document."
            )

        # Step 3: Generate Gemini embeddings
        embeddings = generate_embeddings(chunks)

        if not embeddings:
            raise HTTPException(
                status_code=500,
                detail="Embedding generation failed."
            )

        # Step 4: Store embeddings in Qdrant
        stored_count = store_chunks(
            chunks=chunks,
            embeddings=embeddings,
            filename=filename
        )

        return {
            "message": (
                "Document uploaded, chunked, embedded, "
                "and stored successfully"
            ),
            "filename": filename,
            "character_count": len(extracted_text),
            "chunk_count": len(chunks),
            "embedding_dimension": (
                len(embeddings[0])
                if embeddings
                else 0
            ),
            "stored_in_qdrant": stored_count,
            "chunks": [
                {
                    "chunk_id": index,
                    "text": chunk,
                    "embedding_preview": embeddings[index][:5]
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
            detail=f"Document processing failed: {str(error)}"
        )