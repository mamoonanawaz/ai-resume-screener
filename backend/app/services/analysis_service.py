from app.models.schemas import ResumeAnalysis
from app.services.llm_service import compare_resume
from app.services.validator import validate_analysis


def analyze_with_retry(
    resume_text: str,
    job_description: str,
    maximum_attempts: int = 3
) -> ResumeAnalysis:
    last_error: Exception | None = None

    for attempt in range(1, maximum_attempts + 1):
        raw_response = compare_resume(
            resume_text=resume_text,
            job_description=job_description
        )

        try:
            return validate_analysis(raw_response)

        except ValueError as error:
            last_error = error
            print(
                f"Invalid JSON response on attempt "
                f"{attempt}/{maximum_attempts}: {error}"
            )

    raise ValueError(
        "Gemini failed to return a valid JSON response "
        f"after {maximum_attempts} attempts. "
        f"Last error: {last_error}"
    )