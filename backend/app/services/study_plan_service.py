import json

from google.genai import types

from app.services.llm_service import client


STUDY_PLAN_SYSTEM_PROMPT = """
You are an AI Study Companion.

Create a simple and practical study plan using ONLY the provided
retrieved document content.

Return ONLY valid JSON.

Use exactly this structure:

{
  "topic": "",
  "summary": "",
  "study_goals": [
    ""
  ],
  "study_sessions": [
    {
      "session": 1,
      "title": "",
      "topics": [
        ""
      ],
      "activities": [
        ""
      ]
    }
  ],
  "key_points": [
    ""
  ]
}

Rules:
1. Use only information from the retrieved context.
2. Do not invent information that is not present in the context.
3. Keep the study plan simple and useful.
4. Return valid JSON only.
5. Do not use markdown.
6. Do not use code fences.
7. Do not write explanations outside the JSON.
"""


def generate_study_plan(
    topic: str,
    retrieved_chunks: list[dict]
) -> dict:
    if not retrieved_chunks:
        raise ValueError(
            "No retrieved content was provided for study plan generation."
        )

    context_parts = []

    for index, item in enumerate(retrieved_chunks, start=1):
        text = item.get("text", "").strip()

        if text:
            context_parts.append(
                f"Retrieved Chunk {index}:\n{text}"
            )

    if not context_parts:
        raise ValueError(
            "Retrieved chunks do not contain readable text."
        )

    context = "\n\n".join(context_parts)

    user_prompt = f"""
STUDY TOPIC:
{topic}

RETRIEVED DOCUMENT CONTENT:
{context}

Create a basic study plan for the requested topic using only
the retrieved document content.
"""

    response = client.models.generate_content(
        model="gemini-3.6-flash",
        contents=user_prompt,
        config=types.GenerateContentConfig(
            system_instruction=STUDY_PLAN_SYSTEM_PROMPT,
            response_mime_type="application/json",
            temperature=0.2
        )
    )

    if not response.text:
        raise ValueError(
            "Gemini returned an empty study plan."
        )

    try:
        return json.loads(response.text)
    except json.JSONDecodeError as error:
        raise ValueError(
            f"Gemini returned invalid JSON: {str(error)}"
        )