from fastapi import FastAPI, File, Form, HTTPException, UploadFile

from app.services.text_extractor import extract_text
from app.services.chunker import chunk_text
from app.services.embedding_service import (
    generate_embeddings,
    generate_query_embedding,
)
from app.services.qdrant_service import (
    store_chunks,
    search_chunks,
)
from app.services.study_plan_service import generate_study_plan


app = FastAPI(title="AI Study Companion API")


# --------------------------------------------------
# HOME
# --------------------------------------------------

@app.get("/")
def home():
    return {
        "message": "AI Study Companion API is running"
    }


# --------------------------------------------------
# PROJECT 1 - RESUME EXTRACTION
# --------------------------------------------------

@app.post("/extract-resume")
async def extract_resume(
    resume: UploadFile = File(...)
):
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

        extracted_text = extract_text(
            file_bytes,
            filename
        )

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


# --------------------------------------------------
# PROJECT 1 - JOB DESCRIPTION
# --------------------------------------------------

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


# --------------------------------------------------
# WEEK 3 - DOCUMENT UPLOAD
# Extract -> Chunk -> Embed -> Store in Qdrant
# --------------------------------------------------

@app.post("/upload-document")
async def upload_document(
    document: UploadFile = File(...)
):
    filename = document.filename or ""

    if not filename.lower().endswith(
        (".pdf", ".txt", ".docx")
    ):
        raise HTTPException(
            status_code=400,
            detail="Only PDF, TXT, and DOCX files are supported."
        )

    try:
        # STEP 1: Read uploaded document
        file_bytes = await document.read()

        if not file_bytes:
            raise HTTPException(
                status_code=400,
                detail="The uploaded document is empty."
            )

        # STEP 2: Extract document text
        extracted_text = extract_text(
            file_bytes,
            filename
        )

        if not extracted_text:
            raise HTTPException(
                status_code=422,
                detail="No readable text was found in the document."
            )

        # STEP 3: Split document into chunks
        chunks = chunk_text(extracted_text)

        if not chunks:
            raise HTTPException(
                status_code=422,
                detail="No chunks could be generated from the document."
            )

        # STEP 4: Generate Gemini embeddings
        embeddings = generate_embeddings(chunks)

        if not embeddings:
            raise HTTPException(
                status_code=500,
                detail="Embedding generation failed."
            )

        # STEP 5: Store embeddings + text in Qdrant
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


# --------------------------------------------------
# WEEK 3 - RETRIEVAL
# Query -> Query Embedding -> Search Qdrant
# --------------------------------------------------

@app.post("/retrieve")
async def retrieve(
    query: str = Form(...),
    limit: int = Form(3)
):
    cleaned_query = query.strip()

    if len(cleaned_query) < 3:
        raise HTTPException(
            status_code=400,
            detail="Query must contain at least 3 characters."
        )

    if limit < 1 or limit > 10:
        raise HTTPException(
            status_code=400,
            detail="Limit must be between 1 and 10."
        )

    try:
        # STEP 1: Generate query embedding
        query_embedding = generate_query_embedding(
            cleaned_query
        )

        # STEP 2: Retrieve relevant chunks from Qdrant
        results = search_chunks(
            query_embedding=query_embedding,
            limit=limit
        )

        return {
            "query": cleaned_query,
            "result_count": len(results),
            "results": results
        }

    except HTTPException:
        raise

    except Exception as error:
        raise HTTPException(
            status_code=500,
            detail=f"Retrieval failed: {str(error)}"
        )


# --------------------------------------------------
# WEEK 3 - STUDY PLAN
# Topic -> Retrieval -> Gemini -> JSON Study Plan
# --------------------------------------------------

@app.post("/study-plan")
async def create_study_plan(
    topic: str = Form(...),
    limit: int = Form(3)
):
    cleaned_topic = topic.strip()

    if len(cleaned_topic) < 3:
        raise HTTPException(
            status_code=400,
            detail="Topic must contain at least 3 characters."
        )

    if limit < 1 or limit > 10:
        raise HTTPException(
            status_code=400,
            detail="Limit must be between 1 and 10."
        )

    try:
        # STEP 1: Convert topic into query embedding
        query_embedding = generate_query_embedding(
            cleaned_topic
        )

        # STEP 2: Retrieve relevant document chunks
        retrieved_chunks = search_chunks(
            query_embedding=query_embedding,
            limit=limit
        )

        if not retrieved_chunks:
            raise HTTPException(
                status_code=404,
                detail="No relevant study material was found."
            )

        # STEP 3: Generate JSON study plan with Gemini
        study_plan = generate_study_plan(
            topic=cleaned_topic,
            retrieved_chunks=retrieved_chunks
        )

        return {
            "message": "Study plan generated successfully",
            "topic": cleaned_topic,
            "retrieved_chunk_count": len(
                retrieved_chunks
            ),
            "sources": [
                {
                    "filename": item.get("filename"),
                    "chunk_index": item.get(
                        "chunk_index"
                    ),
                    "score": item.get("score")
                }
                for item in retrieved_chunks
            ],
            "study_plan": study_plan
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
            detail=(
                f"Study plan generation failed: "
                f"{str(error)}"
            )
        )