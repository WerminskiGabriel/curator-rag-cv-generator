from cv_engine.models import GeneratedResume
from pathlib import Path
from django.conf import settings
import typst
from django.shortcuts import get_object_or_404
import json
from django.core.files import File


# TODO temporary json files
def generate_save_cv(generatedResume_id, template_typst="resume.typ"):
    resume_instance = get_object_or_404(GeneratedResume, id=generatedResume_id)

    typst_path = Path(settings.TYPST_ROOT) / template_typst
    json_path = Path(settings.MEDIA_ROOT) / 'json_templates' / f"{str(generatedResume_id)}.json"
    output_path = Path(settings.MEDIA_ROOT) / 'resumes/' / f"{str(generatedResume_id)}.pdf"

    json_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    info_json_path = Path(settings.TYPST_ROOT) / "info.json"
    try:
        with open(info_json_path, 'w', encoding="utf8") as json_file:
            json.dump(resume_instance.generatedJson, json_file, ensure_ascii=False, indent=4)
        typst.compile(typst_path, output=output_path)
        with open(output_path, 'rb') as file:
            resume_name = f"{generatedResume_id}.pdf"
            resume_instance.pdf_file.save(resume_name, File(file), save=True)
        return resume_instance.pdf_file.url
    except Exception as e:
        print(f"Typst compilation error: {e}")
        return None
    finally:
        info_json_path.unlink(missing_ok=True)
