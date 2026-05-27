import json
import os

from pydantic import ValidationError, RootModel

from cv_engine.services.retriever import retriever
from langchain_ollama import OllamaLLM
from cv_engine.services.sections import SECTIONS


def generate_cv_data_llm(profile_id, offer: dict = None, progress_callback=None):
    """
    Generates a personalized resume dict for a given profile using RAG + Ollama LLM.

    Args:
        profile_id: ID of the user profile to retrieve CV chunks from.
        offer: Optional dict with job offer data (title, body, required_skills).
               If provided, RAG queries and LLM prompts are tailored to the offer.
    """
    model = OllamaLLM(
        model="qwen2.5:1.5b",
        base_url=os.environ.get("OLLAMA_BASE_URL", "http://localhost:11434"),
        num_ctx=2048,
        num_thread=8,
        temperature=0,
        format="json",
        keep_alive="2m",
    )

    # Kontekst oferty dla RAG i LLM
    offer_title = offer.get('title', '') if offer else ''
    offer_body = (offer.get('body') or offer.get('description', ''))[:800] if offer else ''
    required_skills = offer.get('required_skills', []) if offer else []
    if isinstance(required_skills, list):
        skills_str = ', '.join(
            s.get('name', str(s)) if isinstance(s, dict) else str(s)
            for s in required_skills
        )
    else:
        skills_str = str(required_skills)

    offer_context = ""
    if offer:
        offer_context = (
            f"\n\nTARGET JOB OFFER:\n"
            f"Title: {offer_title}\n"
            f"Required skills: {skills_str}\n"
            f"Job description: {offer_body}\n"
            f"IMPORTANT: Tailor the CV specifically for this job offer. "
            f"Highlight skills and experiences most relevant to '{offer_title}'. "
            f"Emphasize: {skills_str}."
        )

    new_resume = {
        "layout": {
            "text": {
                "size": "10.5pt",
                "font": "DejaVu Serif"
            },
            "section": {
                "space_above_line": "-3pt",
                "space_below_line": "-5pt",
                "space_below_desc": "-10pt",
                "above_entry_header": "-2pt",
                "above_entry_subtitle": "-2pt",
                "between_highlights": "-4pt"
            }
        }
    }

    section_list = list(SECTIONS.items())
    total_sections = len(section_list)

    for idx, (section_name, section_value) in enumerate(section_list):
        schema = section_value["schema"]
        base_rag_prompt = section_value["rag_prompt"]
        section_model_prompt = section_value["model_prompt"]

        # Wzbogać zapytanie RAG o kontekst oferty — pobierze trafniejsze chunki
        if offer and section_name in ("skills", "experience", "projects"):
            rag_query = f"{base_rag_prompt} Relevant to: {offer_title}. Skills: {skills_str}."
        else:
            rag_query = base_rag_prompt

        rag_response = retriever(rag_query, profile_id=profile_id, max_results=4)

        model_prompt = f"""
TASK: Extract information from the provided text into JSON format.
TEXT: {rag_response}
JSON SCHEMA: {schema.model_json_schema()}
{offer_context}
IMPORTANT:
    {section_model_prompt}
    Return ONLY raw JSON, You MUST wrap the values inside {{ }} .
    1. Return ONLY raw JSON, no markdown, no explanation
    3. Do NOT return empty strings for required fields
    4. Follow the exact JSON structure matching the schema
    """

        attempts = 1
        max_attempts = 5
        last_response = ""
        last_error = None
        while attempts <= max_attempts:
            if attempts == 1:
                current_prompt = model_prompt
            else:
                error_details = ""
                for err in last_error.errors():
                    field = " ".join(map(str, err['loc']))
                    msg = err['msg']
                    typ = err['type']
                    error_details += f" -field: {field} | error: {msg} | type: {typ}\n"

                current_prompt = f"""
{model_prompt}
Your last response contained error
LAST_RESPONSE :\n{last_response}
LAST_RESPONSE_ERRORS :\n{error_details}
TASK: FIX ERRORS. Keep Last_RESPONSE fields that were right and change only ones with errors.
"""
            try:
                model_response = model.invoke(current_prompt)
                last_response = model_response
                print(
                    f"\n{'-' * 20}\nsection: {section_name}\nattempts: {attempts}\n"
                    f"Last error: {str(last_error)}\nmodel_response:\n{model_response}\n{'-' * 20}\n"
                )

                # Unwrap if LLM wrapped output in section key, e.g. {"personal": {...}, "skills": [...]}
                try:
                    raw = json.loads(model_response)
                    if isinstance(raw, dict):
                        if section_name in raw and isinstance(raw[section_name], dict):
                            model_response = json.dumps(raw[section_name])
                        elif len(raw) == 1:
                            inner = next(iter(raw.values()))
                            if isinstance(inner, dict):
                                model_response = json.dumps(inner)
                except (json.JSONDecodeError, StopIteration):
                    pass

                new_section = schema.model_validate_json(model_response)
                new_resume[section_name] = new_section.model_dump()
                break
            except ValidationError as e:
                last_error = e
                attempts += 1

        if attempts > max_attempts:
            raise Exception(f"Max attempts reached for {section_name}. Last error: {str(last_error)}")

        if progress_callback:
            progress_callback(idx + 1, total_sections, section_name)

    return new_resume
