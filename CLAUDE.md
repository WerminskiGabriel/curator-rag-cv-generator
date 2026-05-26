# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Running the project

The entire stack runs via Docker Compose from the repo root:

```bash
docker compose up --build
```

This starts three services:
- `db` — PostgreSQL 17 with pgvector extension (port 5432)
- `django-web` — Django app via Gunicorn (port 8000)
- `ollama` — Local LLM server that pulls `qwen2.5:1.5b` on startup (port 11434)

For local development without Docker, run from `Backend/`:

```bash
cd Backend
python manage.py migrate
python manage.py runserver
```

## Django management commands

All `manage.py` commands must be run from `Backend/` with `PYTHONPATH` set:

```bash
cd Backend
python manage.py migrate
python manage.py makemigrations
python manage.py createsuperuser
python manage.py test                        # run all tests
python manage.py test cv_engine              # run tests for a single app
```

## Environment

The `.env` file lives at the repo root and is loaded both by Docker Compose and by `Backend/Backend/settings.py` (which has a custom `_load_dotenv` that reads it at import time). Required variables: `DJANGO_SECRET_KEY`, `DEBUG`, `DJANGO_ALLOWED_HOSTS`, `DATABASE_ENGINE`, `DATABASE_NAME`, `DATABASE_USERNAME`, `DATABASE_PASSWORD`, `DATABASE_HOST`, `DATABASE_PORT`, `DJANGO_LOGLEVEL`.

In Docker, `DATABASE_HOST` should be `db`; locally it should be `localhost`.

## Architecture

### Django apps

There are three apps:

**`api`** — REST API for auth, documents, and job offers.
- `api/models.py`: `Profile` (extends `User` 1:1), `Documents` (uploaded CV files), `JobOffer` (scraped job listings).
- `api/views/`: `authorization.py` (JWT register/profile), `document_views.py` (upload/delete/status), `offer_views.py` (scrape/list offers).
- `api/services/`: `parser.py` (PDF/DOCX/image → text via PyMuPDF + Tesseract OCR), `documents_logic.py` (upload orchestration + triggers embedding), `scraper_service.py` (JustJoin.it scraping), `offers_logic.py`, `resume_generation.py`.

**`cv_engine`** — Resume generation pipeline.
- `cv_engine/models.py`: `CVAnalysis` (pgvector-backed embeddings of document chunks, 384 dimensions), `GeneratedResume` (LLM-generated JSON + rendered PDF path).
- `cv_engine/services/`: core pipeline described below.
- `cv_engine/templates_cv/resume.typ`: Typst template used to render PDFs.

**`frontend`** — Minimal Django template app serving `home.html` at `/`.

### CV generation pipeline

The full flow when a user generates a resume:

1. **Upload** — User uploads PDF/DOCX/image via `POST /api/documents/import-file/`. `parser.py` extracts text; `embedder.py` chunks it (`chunker.py`) and stores each chunk with a 384-dim HuggingFace embedding (`all-MiniLM-L6-v2`) into `CVAnalysis`.

2. **Generate JSON** — `POST /cv-engine/fill-cv/<profile_id>/` calls `generate_cv_data_llm.py`. For each CV section defined in `sections.py` (`personal`, `skills`, `education`, `experience`, `projects`), it:
   - Queries pgvector via cosine distance (`retriever.py`) for the most relevant chunks.
   - Prompts the local Ollama `qwen2.5:1.5b` model with a Pydantic schema from `templateJsonDesc.py`.
   - Retries up to 5 times on Pydantic `ValidationError`, feeding back error details.
   - Saves a `GeneratedResume` with the assembled JSON dict.

3. **Render PDF** — `POST /cv-engine/create-resume-pdf/<generatedResume_id>/` calls `generate_save_cv.py`, which writes the JSON to a temp file in `TYPST_ROOT`, compiles `resume.typ` via the `typst` Python binding, and saves the PDF to `media/resumes/`.

### Authentication

JWT via `djangorestframework-simplejwt`. Obtain tokens at `POST /api/token/`, refresh at `POST /api/token/refresh/`, register at `POST /api/register/`. All protected API endpoints require `Authorization: Bearer <token>`.

### Scraping

`GET /api/offers/scrape/` calls `scraper_service.py`, which hits the JustJoin.it candidate API (up to 100 offers), strips HTML from body text, and upserts `JobOffer` records. The standalone scripts in `Backend/offers/` (`scan_all_offers.py`, `save_to_postgres.py`) are predecessors to the service layer and can be run independently.

### Database

PostgreSQL with the `pgvector` extension. The `CVAnalysis.embedding` field uses `pgvector.django.VectorField(dimensions=384)`. Queries use `pgvector.django.CosineDistance` for semantic similarity search. Migrations live in `api/migrations/` and `cv_engine/migrations/`.
