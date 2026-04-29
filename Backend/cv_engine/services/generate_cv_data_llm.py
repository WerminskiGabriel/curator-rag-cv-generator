from pydantic import ValidationError, RootModel

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
        keep_alive="2m",
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
        rag_prompt = section_value["rag_prompt"]
        model_prompt = section_value["model_prompt"]
        rag_response = retriever(rag_prompt, profile_id=profile_id, max_results=4)

        model_prompt = f"""
                    TASK: Extract information from the provided text into JSON format.\n
                    TEXT: {rag_response}\n
                    JSON SCHEMA: {schema.model_json_schema()}\n
                    IMPORTANT: 
                        {model_prompt}
                        Return ONLY raw JSON, You MUST wrap the values inside {{ }} .\n
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
                            {model_prompt}\n
                            Your last response contained error\n
                            LAST_RESPONSE :\n{last_response}\n
                            LAST_RESPONSE_ERRORS :\n{error_details}\n
                            TASK: FIX ERRORS. Keep Last_RESPONSE fields that were right and change only ones with errors.\n
                            """
            try:
                model_response = model.invoke(current_prompt)
                last_response = model_response
                print(
                    f"\n{"-" * 20}\nprompt:\n{current_prompt}\nsection:\n {section_name}\nattempts:\n{attempts}\n Last error: \n{str(last_error)}\n model_response:\n{model_response}\n{"-" * 20}\n")

                new_section = schema.model_validate_json(model_response)

                new_resume[section_name] = new_section.model_dump()
                break
            except ValidationError as e:
                last_error = e
                attempts += 1
        if attempts > max_attempts:
            raise Exception(f"Max attempts reached for {section_name}. Last error: {str(last_error)}")

    return new_resume
