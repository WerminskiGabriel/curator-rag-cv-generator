# The Curator — Intelligent CV Generation Platform

A web application that lets users upload their CV (PDF, DOCX, image) and automatically generate a professional PDF CV
tailored to a selected job offer. The system scrapes offers from JustJoin.it, intelligently matches them to the user's
skills, and generates personalized CVs using a local LLM model.

## Tech Stack

| Layer          | Technology                                      |
|----------------|-------------------------------------------------|
| Backend        | Django + Django REST Framework                  |
| Database       | PostgreSQL 17 + pgvector                        |
| LLM            | Ollama (qwen2.5:1.5b) — local                   |
| Embeddings     | HuggingFace `all-MiniLM-L6-v2` (384 dimensions) |
| File parsing   | PyMuPDF (fitz) + Tesseract OCR                  |
| PDF rendering  | Typst                                           |
| Frontend       | HTML + Tailwind CSS + vanilla JS                |
| Infrastructure | Docker Compose                                  |

## Getting Started

```bash
docker compose up --build
```

Three containers start:

- **`db`** — PostgreSQL with pgvector (port 5432)
- **`django-web`** — Django app via Gunicorn (port 8000)
- **`ollama`** — LLM server that pulls the `qwen2.5:1.5b` model on startup (port 11434)

Application available at: **http://localhost:8000**

### Environment Variables

`.env` file in the project root:

```env
DJANGO_SECRET_KEY=...
DEBUG=True
DJANGO_ALLOWED_HOSTS=localhost,127.0.0.1
DATABASE_ENGINE=django.db.backends.postgresql
DATABASE_NAME=DB
DATABASE_USERNAME=dbuser
DATABASE_PASSWORD=dbpassword
DATABASE_HOST=db
DATABASE_PORT=5432
```

## How It Works

### 1. Reading CV from File

After uploading a file (PDF, DOCX, PNG/JPG), the system extracts text from it:

```
User file
     │
     ▼
┌──────────────┐
│   parser.py  │ → detects format by extension
└──────────────┘
     │
     ├── PDF  → PyMuPDF (fitz) — extracts text blocks page by page
     ├── DOCX → python-docx — iterates over paragraphs
     └── Image → PyMuPDF OCR (pdfocr_tobytes) + Tesseract — converts image to PDF in memory, then OCR
```

The extracted text is stored in the `Documents` model in the database.

### 2. Chunking and Embeddings (Vectorization)

After the text is saved, the embedding pipeline runs automatically (via Django `post_save` signal):

1. **Chunking** — text is split into ~400-character fragments with 200-character overlap (`CharacterTextSplitter` from
   LangChain)
2. **Embedding** — each fragment is vectorized with the `all-MiniLM-L6-v2` model (384 dimensions)
3. **Storage** — chunks with vectors are saved to the `CVAnalysis` table in PostgreSQL (`VectorField` with pgvector)

```
CV text → [chunk₁, chunk₂, ..., chunkₙ] → [vec₁, vec₂, ..., vecₙ] → PostgreSQL (pgvector)
```

### 3. Matching Offers to Skills

The user enters their skills (e.g. "Python, React, Docker"), and the system matches them to offers:

**Matching mechanism (`offers_logic.py`):**

- For each offer in the database, the system compares the user's skills with the offer's `required_skills`
- Matching is not just exact-match — a **skill families** system (`SKILL_FAMILIES`) is used:
    - `python` covers: `django`, `flask`, `fastapi`, `pandas`, `numpy`
    - `javascript` covers: `react`, `vue`, `angular`, `node.js`, `typescript`
    - `docker` covers: `kubernetes`, `k8s`, `helm`, `docker compose`
    - etc.
- Additionally: substring match (`react` ↔ `react.js`)
- Result: **match percentage** = (skills covered / required) × 100%
- Offers sorted descending by `match_pct`, top N returned to the frontend

**Example:**

```
User: Python, Docker
Offer requires: Django, Flask, Kubernetes, React

→ Django ✓ (Python family)
→ Flask ✓ (Python family)  
→ Kubernetes ✓ (Docker family)
→ React ✗

Result: 75% match (3/4)
```

### 4. CV Generation (RAG + LLM)

This is the main application pipeline. It combines Retrieval-Augmented Generation with a local LLM model:

```
                    ┌──────────────────────────────┐
                    │  CV sections to fill:        │
                    │  personal, skills, education,│
                    │  experience, projects        │
                    └──────────────┬───────────────┘
                                   │
                    ┌──────────────▼───────────────┐
                    │    For each section:         │
                    │                              │
                    │  1. RAG query → pgvector     │
                    │     (cosine distance)        │
                    │     → best CV chunks         │
                    │                              │
                    │  2. Prompt to LLM:           │
                    │     chunks + JSON schema     │
                    │     + offer context          │
                    │                              │
                    │  3. LLM (qwen2.5:1.5b)       │
                    │     → section JSON data      │
                    │                              │
                    │  4. Pydantic validation      │
                    │     (retry up to 5x on error)│
                    └──────────────┬───────────────┘
                                   │
                    ┌──────────────▼────────────────┐
                    │  Assembled CV JSON            │
                    │  → Typst template (resume.typ)│
                    │  → compile to PDF             │
                    └───────────────────────────────┘
```

**Step by step:**

1. **Retrieval (RAG)** — for each CV section (e.g. "experience"), the system builds a semantic query, vectorizes it, and
   searches for the nearest chunks in pgvector (cosine distance). When generating a CV for a specific offer — the RAG
   query is enriched with offer context (title, required skills)

2. **JSON generation via LLM** — the Ollama `qwen2.5:1.5b` model receives a prompt with: retrieved chunks, JSON schema (
   Pydantic), and optionally offer context. It returns structured JSON matching the schema

3. **Validation and retry** — the LLM response is validated by Pydantic. If validation fails, the system sends error
   details back to the LLM and requests a fix — up to 5 attempts

4. **PDF rendering** — the finished JSON is passed to the Typst template (`resume.typ`), which is compiled to PDF via
   the Python Typst binding

### 5. Offer Scraping

The system fetches offers from JustJoin.it:

1. Fetches the offer list from the JustJoin.it candidate API (up to 100 offers)
2. For each slug, fetches offer details (title, body, required_skills)
3. Saves/updates in the local PostgreSQL database (`JobOffer`)

## Project Structure

```
Backend/
├── api/                    # REST API — auth, documents, offers
│   ├── models.py           # Profile, Documents, JobOffer
│   ├── views/              # authorization, document_views, offer_views
│   └── services/           # parser, scraper, offers_logic
│
├── cv_engine/              # CV generation pipeline
│   ├── models.py           # CVAnalysis (embeddings), GeneratedResume
│   ├── services/
│   │   ├── chunker.py      # Text splitting into fragments
│   │   ├── embedder.py     # Chunk vectorization
│   │   ├── retriever.py    # Semantic search (pgvector)
│   │   ├── generate_cv_data_llm.py  # RAG + LLM pipeline
│   │   ├── generate_save_cv.py      # Typst → PDF compilation
│   │   └── sections.py     # CV section definitions
│   └── templates_cv/
│       └── resume.typ       # Typst template
│
├── frontend/               # Django templates
│   └── templates/
│       └── home.html        # Single-page application
│
├── offers/                 # Standalone scraping scripts
├── Dockerfile
└── requirements.txt
```

## Authentication

JWT via `djangorestframework-simplejwt`:

- Register → `POST /api/register/`
- Login → `POST /api/token/`
- Refresh token → `POST /api/token/refresh/`
- Profile data (read/write) → `GET/PUT /api/profile/`

## License

This project is licensed under the MIT License.
