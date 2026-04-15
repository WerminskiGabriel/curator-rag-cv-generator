from pydantic import ValidationError

from cv_engine.services.retriever import retriever
from langchain_ollama import OllamaLLM
from cv_engine.services.sections import SECTIONS


def generate_cv_data_llm(profile_id):
    model = OllamaLLM(
        # model="gemma4:e2b",
        # model="gemma4:e2b-it-q4_K_M",
        model="qwen2.5:1.5b",
        base_url="http://host.docker.internal:11434",
        num_ctx=2048,
        num_thread=8,
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

    for section in SECTIONS.values():
        schema = section["schema"]
        rag_prompt = section["prompt"]

        rag_response = retriever(rag_prompt, profile_id=profile_id, max_results=4)

        model_prompt = f"""
                    Extract information from: [{rag_response}]
                    Output format ( JSON schema ): [{section["schema"]}]
                    Return only valid Json.
                    """

        attempts = 1
        max_attempts = 3
        error_prompt = "Fix this error in your previous response:"

        while attempts <= max_attempts:
            try:
                model_response = model.invoke(model_prompt)
                new_section = schema.model_validate_json(model_response)
                new_resume[section] = new_section
            except ValidationError as e:
                model_prompt += error_prompt + f"[e], \n"
                attempts += 1
        if attempts > max_attempts:
            raise Exception("max-attempts exceeded")

    return new_resume
