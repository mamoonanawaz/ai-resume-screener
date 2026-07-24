from fastapi import FastAPI, File, HTTPException, UploadFile

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