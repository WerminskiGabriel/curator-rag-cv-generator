# The Curator — Platforma do inteligentnego generowania CV

Aplikacja webowa, która pozwala użytkownikowi wgrać swoje CV (PDF, DOCX, obraz), a następnie automatycznie wygenerować profesjonalne CV w formacie PDF — dopasowane do wybranej oferty pracy. System scrapuje oferty z JustJoin.it, inteligentnie dopasowuje je do umiejętności użytkownika i generuje spersonalizowane CV przy pomocy lokalnego modelu LLM.

## Stos technologiczny

| Warstwa | Technologia |
|---------|-------------|
| Backend | Django + Django REST Framework |
| Baza danych | PostgreSQL 17 + pgvector |
| LLM | Ollama (qwen2.5:1.5b) — lokalnie |
| Embeddingi | HuggingFace `all-MiniLM-L6-v2` (384 wymiary) |
| Parsowanie plików | PyMuPDF (fitz) + Tesseract OCR |
| Renderowanie PDF | Typst |
| Frontend | HTML + Tailwind CSS + vanilla JS |
| Infrastruktura | Docker Compose |

## Uruchomienie

```bash
docker compose up --build
```

Startują trzy kontenery:
- **`db`** — PostgreSQL z pgvector (port 5432)
- **`django-web`** — aplikacja Django przez Gunicorn (port 8000)
- **`ollama`** — serwer LLM, który na starcie pobiera model `qwen2.5:1.5b` (port 11434)

Aplikacja dostępna pod: **http://localhost:8000**

### Zmienne środowiskowe

Plik `.env` w katalogu głównym:

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

## Jak to działa

### 1. Odczytywanie CV z pliku

Po wgraniu pliku (PDF, DOCX, PNG/JPG) system wyciąga z niego tekst:

```
Plik użytkownika
     │
     ▼
┌──────────────┐
│   parser.py  │ → rozpoznaje format po rozszerzeniu
└──────────────┘
     │
     ├── PDF  → PyMuPDF (fitz) — wyciąga bloki tekstowe strona po stronie
     ├── DOCX → python-docx — iteruje po paragrafach
     └── Obraz → PyMuPDF OCR (pdfocr_tobytes) + Tesseract — konwertuje obraz na PDF w pamięci, potem OCR
```

Wyekstrahowany tekst trafia do modelu `Documents` w bazie danych.

### 2. Chunking i embeddingi (wektoryzacja)

Po zapisaniu tekstu, automatycznie (przez Django signal `post_save`) uruchamia się pipeline embeddingowy:

1. **Chunking** — tekst dzielony jest na fragmenty po ~400 znaków z 200-znakowym overlapem (`CharacterTextSplitter` z LangChain)
2. **Embedding** — każdy fragment jest wektoryzowany modelem `all-MiniLM-L6-v2` (384 wymiary)
3. **Zapis** — chunki z wektorami trafiają do tabeli `CVAnalysis` w PostgreSQL (pole `VectorField` z pgvector)

```
Tekst CV → [chunk₁, chunk₂, ..., chunkₙ] → [vec₁, vec₂, ..., vecₙ] → PostgreSQL (pgvector)
```

### 3. Dopasowywanie ofert do umiejętności

Użytkownik wpisuje swoje umiejętności (np. "Python, React, Docker"), a system dopasowuje je do ofert:

**Mechanizm dopasowania (`offers_logic.py`):**

- Dla każdej oferty z bazy system porównuje umiejętności użytkownika z `required_skills` oferty
- Porównywanie nie jest tylko exact-match — działa **system rodzin umiejętności** (`SKILL_FAMILIES`):
  - `python` pokrywa: `django`, `flask`, `fastapi`, `pandas`, `numpy`
  - `javascript` pokrywa: `react`, `vue`, `angular`, `node.js`, `typescript`
  - `docker` pokrywa: `kubernetes`, `k8s`, `helm`, `docker compose`
  - itd.
- Dodatkowo: substring match (`react` ↔ `react.js`)
- Wynik: **procent dopasowania** = (umiejętności pokryte / wymagane) × 100%
- Oferty sortowane malejąco po `match_pct`, top N zwracane do frontendu

**Przykład:**
```
Użytkownik: Python, Docker
Oferta wymaga: Django, Flask, Kubernetes, React

→ Django ✓ (rodzina Python)
→ Flask ✓ (rodzina Python)  
→ Kubernetes ✓ (rodzina Docker)
→ React ✗

Wynik: 75% dopasowania (3/4)
```

### 4. Generowanie CV (RAG + LLM)

To główny pipeline aplikacji. Łączy Retrieval-Augmented Generation z lokalnym modelem LLM:

```
                    ┌─────────────────────────────┐
                    │  Sekcje CV do wypełnienia:   │
                    │  personal, skills, education,│
                    │  experience, projects        │
                    └──────────────┬──────────────┘
                                   │
                    ┌──────────────▼──────────────┐
                    │    Dla każdej sekcji:        │
                    │                              │
                    │  1. RAG query → pgvector     │
                    │     (cosine distance)        │
                    │     → najlepsze chunki CV    │
                    │                              │
                    │  2. Prompt do LLM:           │
                    │     chunki + schemat JSON    │
                    │     + kontekst oferty        │
                    │                              │
                    │  3. LLM (qwen2.5:1.5b)      │
                    │     → JSON z danymi sekcji   │
                    │                              │
                    │  4. Walidacja Pydantic       │
                    │     (retry do 5x jeśli błąd) │
                    └──────────────┬──────────────┘
                                   │
                    ┌──────────────▼──────────────┐
                    │  Złożony JSON CV             │
                    │  → szablon Typst (resume.typ)│
                    │  → kompilacja do PDF         │
                    └─────────────────────────────┘
```

**Krok po kroku:**

1. **Retrieval (RAG)** — dla każdej sekcji CV (np. "experience") system buduje zapytanie semantyczne, wektoryzuje je i szuka najbliższych chunków w pgvector (cosine distance). Jeśli generujemy CV pod konkretną ofertę — zapytanie RAG jest wzbogacone o kontekst oferty (tytuł, wymagane umiejętności)

2. **Generowanie JSON przez LLM** — model Ollama `qwen2.5:1.5b` dostaje prompt z: wyciągniętymi chunkami, schematem JSON (Pydantic), i opcjonalnie kontekstem oferty. Zwraca strukturalny JSON pasujący do schematu

3. **Walidacja i retry** — odpowiedź LLM jest walidowana przez Pydantic. Jeśli walidacja nie przechodzi, system wysyła do LLM informację o błędach i prosi o poprawkę — do 5 prób

4. **Renderowanie PDF** — gotowy JSON trafia do szablonu Typst (`resume.typ`), który jest kompilowany do PDF przez binding Pythona do Typst

### 5. Scrapowanie ofert

System pobiera oferty z JustJoin.it:

1. Pobiera listę ofert z API kandydackiego JustJoin.it (do 100 ofert)
2. Dla każdego sluga pobiera szczegóły oferty (tytuł, body, required_skills)
3. Zapisuje/aktualizuje w lokalnej bazie PostgreSQL (`JobOffer`)

## Struktura projektu

```
Backend/
├── api/                    # REST API — auth, dokumenty, oferty
│   ├── models.py           # Profile, Documents, JobOffer
│   ├── views/              # authorization, document_views, offer_views
│   └── services/           # parser, scraper, offers_logic
│
├── cv_engine/              # Pipeline generowania CV
│   ├── models.py           # CVAnalysis (embeddingi), GeneratedResume
│   ├── services/
│   │   ├── chunker.py      # Dzielenie tekstu na fragmenty
│   │   ├── embedder.py     # Wektoryzacja chunków
│   │   ├── retriever.py    # Wyszukiwanie semantyczne (pgvector)
│   │   ├── generate_cv_data_llm.py  # RAG + LLM pipeline
│   │   ├── generate_save_cv.py      # Kompilacja Typst → PDF
│   │   └── sections.py     # Definicje sekcji CV
│   └── templates_cv/
│       └── resume.typ       # Szablon Typst
│
├── frontend/               # Django templates
│   └── templates/
│       └── home.html        # Single-page aplikacja
│
├── offers/                 # Standalone skrypty scrapingu
├── Dockerfile
└── requirements.txt
```

## Autentykacja

JWT przez `djangorestframework-simplejwt`:
- Rejestracja → `POST /api/register/`
- Logowanie → `POST /api/token/`
- Odświeżanie tokenu → `POST /api/token/refresh/`
- Dane profilu (zapis/odczyt) → `GET/PUT /api/profile/`

## Licencja

MIT — patrz [LICENSE.md](LICENSE.md)
