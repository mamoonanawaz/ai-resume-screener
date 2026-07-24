import json

from pydantic import ValidationError

from app.models.schemas import ResumeAnalysis


def validate_analysis(raw_response: str) -> ResumeAnalysis:
    try:
        parsed_response = json.loads(raw_response)

    except json.JSONDecodeError as error:
        raise ValueError(
            f"LLM response is not valid JSON: {error}"
        ) from error

    try:
        return ResumeAnalysis.model_validate(parsed_response)

    except ValidationError as error:
        raise ValueError(
            f"LLM response does not match the required structure: {error}"
        ) from error
    