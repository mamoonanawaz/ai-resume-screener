import os
from pathlib import Path

from dotenv import load_dotenv
from google import genai
from google.genai import types

from app.services.prompt import SYSTEM_PROMPT, build_comparison_prompt


# backend/.env ko load karega
ENV_FILE = Path(__file__).resolve().parents[2] / ".env"
load_dotenv(ENV_FILE)

api_key = os.getenv("GEMINI_API_KEY")

if not api_key:
    raise RuntimeError(
        "GEMINI_API_KEY was not found. Check the backend/.env file."
    )

client = genai.Client(api_key=api_key)


def compare_resume(
    resume_text: str,
    job_description: str
) -> str:
    user_prompt = build_comparison_prompt(
        resume_text=resume_text,
        job_description=job_description
    )

    response = client.models.generate_content(
        model="gemini-3.6-flash",
        contents=user_prompt,
        config=types.GenerateContentConfig(
            system_instruction=SYSTEM_PROMPT,
            response_mime_type="application/json",
            temperature=0.2
        )
    )

    if not response.text:
        raise ValueError("Gemini returned an empty response.")

    return response.text.strip()