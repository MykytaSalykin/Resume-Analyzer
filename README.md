# 🎯 Resume Analyzer

<p align="left">
  <img alt="Python" src="https://img.shields.io/badge/Python-3.11%2F3.12-blue" />
  <img alt="FastAPI" src="https://img.shields.io/badge/FastAPI-ready-brightgreen" />
  <img alt="Streamlit" src="https://img.shields.io/badge/Streamlit-UI-orange" />
  <img alt="Docker" src="https://img.shields.io/badge/Docker-ready-blue" />
  <img alt="GitHub Actions" src="https://img.shields.io/badge/GitHub%20Actions-passing-success" />
</p>

AI-powered resume analysis that matches resumes to job descriptions with a clean Streamlit UI and FastAPI backend.

## Features
- Multi-dimensional scoring: Semantic, Skills, Experience, Education, Content Quality
- Clean recommendations without special bullets; readable explanations
- Spider (radar) chart visualization; matched/missing skills
- Compare multiple resumes side-by-side
- Robust PDF-to-text via MarkItDown with safe fallback
- API with OpenAPI docs; Docker-ready; CI with tests, lint, and container health

## Screenshots

![Home](docs/images/ui_home.png)

![Breakdown](docs/images/ui_breakdown.png)

![Spider Chart](docs/images/ui_spider.png)

![Comparison](docs/images/ui_compare.png)

![Export](docs/images/ui_export.png)

## Quick Start (Local)
1) Create env and install deps
```
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```
2) Run API (terminal 1)
```
uvicorn api:app --reload --host 0.0.0.0 --port 8000
```
3) Run UI (terminal 2)
```
streamlit run ui/streamlit_app.py
```
Access:
- UI: http://localhost:8501
- API docs: http://localhost:8000/docs

Tip: If launching from the `ui/` folder directly, set PYTHONPATH or run from repo root.
```
export PYTHONPATH="$(pwd)"
```

## Docker / Compose
Build and run with Docker Compose:
```
docker compose up --build
```
Defaults:
- API on 8000 (health: /health)
- UI on 8501
- In Compose, the API skips heavy embedding model load on startup for faster dev (can be removed by changing env).

## Environment Variables
- EMBED_MODEL: sentence-transformers model (default: multi-qa-mpnet-base-dot-v1)
- SKIP_EMBEDDINGS_LOAD: set to 1 to skip model load at API startup (useful in CI/containers)

## Project Structure
```
app/
  chains/              # Matching logic and skills extraction
  rag/                 # Embedding utilities
ui/
  streamlit_app.py     # Streamlit UI
api.py                 # FastAPI application
requirements.txt
Dockerfile
.github/workflows/ci.yml
```

## Testing & Lint
```
pytest -v
```
CI runs:
- Unit tests (pytest)
- flake8 lint
- Docker build + health check

## Troubleshooting
- ModuleNotFoundError: app when running UI → run from repo root or set PYTHONPATH.
- PDF parsing issues → paste text as fallback; MarkItDown stream conversion + UTF-8 fallback is used.
- Slow startup in container → set SKIP_EMBEDDINGS_LOAD=1 (already set in CI/Compose).

## License
MIT