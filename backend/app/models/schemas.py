from pydantic import BaseModel, ConfigDict, Field


class ResumeAnalysis(BaseModel):
    model_config = ConfigDict(extra="forbid")

    match_score: int = Field(
        ge=0,
        le=100,
        description="Resume and job-description match score"
    )

    missing_keywords: list[str]

    suggestions: list[str] = Field(min_length=1)
    