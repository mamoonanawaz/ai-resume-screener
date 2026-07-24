from fastapi import FastAPI, File, Form, HTTPException, UploadFile

from app.services.analysis_service import analyze_with_retry
from app.services.text_extractor import extract_text


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


@app.post("/analyze")
async def analyze_resume(
    resume: UploadFile = File(...),
    job_description: str = Form(...)
):
    filename = resume.filename or ""
    cleaned_description = job_description.strip()

    if not filename.lower().endswith((".pdf", ".docx")):
        raise HTTPException(
            status_code=400,
            detail="Only PDF and DOCX resume files are supported."
        )

    if len(cleaned_description) < 20:
        raise HTTPException(
            status_code=400,
            detail="Job description must contain at least 20 characters."
        )

    try:
        file_bytes = await resume.read()

        if not file_bytes:
            raise HTTPException(
                status_code=400,
                detail="The uploaded resume is empty."
            )

        resume_text = extract_text(file_bytes, filename)

        if not resume_text:
            raise HTTPException(
                status_code=422,
                detail="No readable text was found in the resume."
            )

        result = analyze_with_retry(
            resume_text=resume_text,
            job_description=cleaned_description
        )

        return result.model_dump()

    except HTTPException:
        raise

    except ValueError as error:
        raise HTTPException(
            status_code=422,
            detail=str(error)
        )

    except Exception as error:
        raise HTTPException(
            status_code=500,
            detail=f"Resume analysis failed: {str(error)}"
        )