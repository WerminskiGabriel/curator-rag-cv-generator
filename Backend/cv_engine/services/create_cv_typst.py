from ..models import GeneratedResume
from pathlib import Path
from django.conf import settings
import typst
from django.shortcuts import get_object_or_404
import tempfile
import os
import json


# TODO temporary json files

def create_cv_typst(generatedResume_id, template_typst="resume.typ"):
    resume_instance = get_object_or_404(GeneratedResume, id=generatedResume_id)

    typst_path = Path(settings.TYPST_ROOT) / template_typst
    json_path = Path(settings.MEDIA_ROOT) / 'json_templates' / f"{str(generatedResume_id)}.json"
    output_path = Path(settings.MEDIA_ROOT) / 'resumes/' / f"{str(generatedResume_id)}.pdf"

    json_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with open(json_path, 'w', encoding="utf8") as json_file:
        json.dump(resume_instance.generatedJson, json_file, ensure_ascii=False, indent=4)

    try:
        typst.compile(typst_path, output=output_path)
        return output_path
    except Exception as e:
        print(f"Typst compilation error: {str(e)}")
        return output_path
