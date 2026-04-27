from pydantic import ValidationError

from cv_engine.services.retriever import retriever
from langchain_ollama import OllamaLLM
from cv_engine.services.sections import SECTIONS


def generate_cv_data_llm(profile_id):
    """
    generates not personalized dict(resume) for profile using rag and ollama model
    """
    model = OllamaLLM(
        # model="gemma4:e2b",
        # model="gemma4:e2b-it-q4_K_M",
        model="qwen2.5:1.5b",
        base_url="http://ollama:11434",
        num_ctx=2048,
        num_thread=8,
        temperature=0,
        format="json",
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

    for section_name, section_value in SECTIONS.items():
        schema = section_value["schema"]
        rag_prompt = section_value["prompt"]

        rag_response = retriever(rag_prompt, profile_id=profile_id, max_results=4)
        model_prompt = f"""
                    TASK: Extract information from the provided text into JSON format.
                    TEXT: {rag_response}
                    JSON SCHEMA: {schema.model_json_schema()}
                    IMPORTANT: Return ONLY raw JSON. No conversational text.
                    IMPORTANT INSTRUCTION: You MUST wrap the values inside an object with the exact key in JSON SCHEMA to match it.
                    """

        attempts = 1
        max_attempts = 3
        error_prompt = "Fix this error in your previous response:"
        last_error = None
        while attempts <= max_attempts:
            try:
                model_response = model.invoke(model_prompt)
                print(
                    f"section: {section_name},attempts:{attempts}. Last error: {str(last_error)}, model_response:{model_response}")
                new_section = schema.model_validate_json(model_response)
                new_resume[section_name] = new_section.model_dump()
                break
            except ValidationError as e:
                last_error = e
                model_prompt += error_prompt + f"[e], \n"
                attempts += 1
        if attempts > max_attempts:
            raise Exception(f"Max attempts reached for {section_name}. Last error: {str(last_error)}")

    return new_resume
