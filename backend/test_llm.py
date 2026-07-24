from app.services.llm_service import compare_resume


resume_text = """
Python developer with experience in FastAPI,
machine learning, REST APIs, and Git.
"""

job_description = """
We need a Python developer with FastAPI,
machine learning, SQL, Docker, and AWS experience.
"""

result = compare_resume(
    resume_text=resume_text,
    job_description=job_description
)

print(result)