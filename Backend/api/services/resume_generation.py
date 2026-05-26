import os
import json
import tempfile
from pathlib import Path
from django.conf import settings
from .profile_mockup import MY_PROFILE


TYPST_TEMPLATE = Path(settings.TYPST_ROOT) / 'resume.typ'
OUTPUT_DIR = Path(settings.MEDIA_ROOT) / 'generated_cvs'


def _build_resume_json(offer: dict) -> dict:
    """
    Buduje słownik JSON zgodny ze strukturą oczekiwaną przez resume.typ.
    Używa danych z MY_PROFILE + informacji o ofercie.
    """
    profile = MY_PROFILE

    # Umiejętności wymagane przez ofertę jako osobna kategoria
    required_skills = offer.get('required_skills', [])
    if isinstance(required_skills, list) and required_skills:
        skill_items = [s.get('name', s) if isinstance(s, dict) else str(s) for s in required_skills]
    else:
        skill_items = []

    skills_entries = [
        {
            "category": "Programming",
            "items": profile.get('skills', [])
        }
    ]
    if skill_items:
        skills_entries.append({
            "category": "Required by offer",
            "items": skill_items
        })

    education_entries = [
        {
            "school": e.get('institution', ''),
            "years": e.get('years', ''),
            "degree": e.get('degree', ''),
            "highlights": [e.get('description', '')] if e.get('description') else []
        }
        for e in profile.get('education', [])
    ]

    experience_entries = [
        {
            "position": f"{e.get('role', '')} @ {e.get('company', '')}",
            "years": e.get('years', ''),
            "highlights": [e.get('description', '')] if e.get('description') else []
        }
        for e in profile.get('experience', [])
    ]

    offer_title = offer.get('title', 'Developer')
    offer_body = offer.get('description') or offer.get('body', '')

    return {
        "personal": {
            "first_name": profile.get('first_name', ''),
            "last_name": profile.get('last_name', ''),
            "subtitle": f"{offer_title}",
            "about": {
                "description": profile.get('summary', '')
            },
            "info": {
                "telephone_label": profile.get('phone', ''),
                "telephone_link": f"tel:{profile.get('phone', '').replace(' ', '')}",
                "email": profile.get('email', ''),
                "github_label": profile.get('github_label', 'github.com/user'),
                "github_link": profile.get('github_link', 'https://github.com/user'),
                "linkedin_label": profile.get('linkedin_label', 'linkedin.com/in/user'),
                "linkedin_link": profile.get('linkedin_link', 'https://www.linkedin.com/in/user'),
            }
        },
        "skills": {
            "entries": skills_entries
        },
        "education": {
            "entries": education_entries
        },
        "experience": {
            "entries": experience_entries
        },
        "projects": {
            "entries": [
                {
                    "name": f"Application for: {offer_title}",
                    "tech": ", ".join(skill_items[:5]) if skill_items else "See offer",
                    "highlights": [
                        offer_body[:300] + ("..." if len(offer_body) > 300 else "")
                    ] if offer_body else ["See job description"]
                }
            ]
        },
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


def generate_cv_for_offer(offer: dict) -> str:
    """
    Generuje CV w formacie PDF (lub .typ jako fallback) dla podanej oferty.

    Tworzy plik info.json w katalogu szablonu Typst, kompiluje resume.typ → PDF,
    a następnie usuwa tymczasowy JSON.

    Returns:
        Ścieżka do wygenerowanego pliku (PDF lub .typ jako fallback).
    """
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    pdf_dir = OUTPUT_DIR / 'pdf'
    pdf_dir.mkdir(parents=True, exist_ok=True)

    offer_title = offer.get('title', 'Developer').replace(' ', '_').replace('/', '_')
    slug = offer.get('slug', offer_title)[:50]
    profile = MY_PROFILE
    filename = f"CV_{profile.get('first_name', '')}_{profile.get('last_name', '')}_{slug}"
    pdf_path = pdf_dir / f"{filename}.pdf"

    resume_json = _build_resume_json(offer)

    # info.json musi być w tym samym katalogu co resume.typ (Typst rozwiązuje ścieżki relatywnie)
    json_path = TYPST_TEMPLATE.parent / 'info.json'

    try:
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(resume_json, f, ensure_ascii=False, indent=2)

        import typst
        typst.compile(str(TYPST_TEMPLATE), output=str(pdf_path))
        return str(pdf_path)

    except Exception as e:
        print(f"Typst compilation error: {e}")
        # Fallback: zapisz .typ z JSON w środku jako komentarz debugowy
        typ_dir = OUTPUT_DIR / 'typ'
        typ_dir.mkdir(parents=True, exist_ok=True)
        typ_path = typ_dir / f"{filename}.typ"
        with open(typ_path, 'w', encoding='utf-8') as f:
            f.write(f"// ERROR: {e}\n// JSON that was generated:\n")
            f.write(json.dumps(resume_json, indent=2, ensure_ascii=False))
        return str(typ_path)

    finally:
        # Usuń tymczasowy info.json
        if json_path.exists():
            json_path.unlink()


def compile_json_to_pdf(resume_json: dict, slug: str) -> str:
    """
    Kompiluje gotowy słownik JSON (z LLM lub statyczny) do PDF przez Typst.

    Args:
        resume_json: Słownik zgodny ze strukturą resume.typ.
        slug: Identyfikator oferty używany w nazwie pliku.

    Returns:
        Ścieżka do wygenerowanego PDF (lub .typ jako fallback przy błędzie kompilacji).
    """
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    pdf_dir = OUTPUT_DIR / 'pdf'
    pdf_dir.mkdir(parents=True, exist_ok=True)

    profile = MY_PROFILE
    safe_slug = str(slug)[:50].replace(' ', '_').replace('/', '_')
    filename = f"CV_{profile.get('first_name', '')}_{profile.get('last_name', '')}_{safe_slug}"
    pdf_path = pdf_dir / f"{filename}.pdf"

    # info.json musi być obok resume.typ (Typst rozwiązuje ścieżki relatywnie)
    json_path = TYPST_TEMPLATE.parent / 'info.json'

    try:
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(resume_json, f, ensure_ascii=False, indent=2)

        import typst
        typst.compile(str(TYPST_TEMPLATE), output=str(pdf_path))
        return str(pdf_path)

    except Exception as e:
        print(f"[Typst] Compilation error for {slug}: {e}")
        typ_dir = OUTPUT_DIR / 'typ'
        typ_dir.mkdir(parents=True, exist_ok=True)
        typ_path = typ_dir / f"{filename}_debug.typ"
        with open(typ_path, 'w', encoding='utf-8') as f:
            f.write(f"// COMPILE ERROR: {e}\n// Generated JSON:\n")
            f.write(json.dumps(resume_json, indent=2, ensure_ascii=False))
        return str(typ_path)

    finally:
        if json_path.exists():
            json_path.unlink()
