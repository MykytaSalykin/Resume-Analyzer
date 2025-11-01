# 🚀 AI Resume Analyzer

[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-latest-green.svg)](https://fastapi.tiangolo.com/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

AI-powered resume analysis system that matches resumes to job descriptions using NLP.

## Features

- 🤖 **AI Analysis**: Semantic matching with sentence transformers
- 📊 **Multi-Dimensional Scoring**: Skills (35%), Semantic (30%), Experience (20%), Education (15%)
- 🌐 **REST API**: FastAPI backend with auto-documentation
- 💻 **Web UI**: Streamlit dashboard
- 🛡️ **Anti-Spam**: Content validation and filtering
- 🐳 **Docker Ready**: Full containerization
- 🧪 **Tested**: Comprehensive test suite

## Quick Start

### Docker (Recommended)
```bash
git clone https://github.com/MykytaSalykin/Resume-Analyzer.git
cd Resume-Analyzer
docker-compose up --build
```

### Local Development
```bash
git clone https://github.com/MykytaSalykin/Resume-Analyzer.git
cd Resume-Analyzer
pip install -r requirements.txt
uvicorn api:app --reload --port 8000
# In new terminal: streamlit run ui/streamlit_app.py
```

**Access:**
- Web UI: http://localhost:8501
- API Docs: http://localhost:8000/docs

## API Usage

```bash
curl -X POST http://localhost:8000/analyze \
  -H "Content-Type: application/json" \
  -d '{
    "resume_text": "Your resume text here...",
    "job_description": "Job description here..."
  }'
```

## Tech Stack

- **Backend**: FastAPI, sentence-transformers
- **Frontend**: Streamlit
- **Testing**: pytest
- **DevOps**: Docker, GitHub Actions

## Testing

```bash
pytest tests/ -v
```

## License
MIT License 