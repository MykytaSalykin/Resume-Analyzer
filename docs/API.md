# API Documentation

## Resume Analysis API

### Base URL
```
http://localhost:8000
```

### Authentication
Currently no authentication required (add API keys for production).

## Endpoints

### Health Check
```http
GET /health
```

**Response:**
```json
{
  "status": "healthy",
  "version": "1.0.0", 
  "model_loaded": true
}
```

### Analyze Resume (Text)
```http
POST /analyze
Content-Type: application/json
```

**Request Body:**
```json
{
  "resume_text": "John Smith - Python Developer...",
  "job_description": "Looking for Python developer with 3+ years..."
}
```

**Response:**
```json
{
  "overall_score": 67.8,
  "breakdown": {
    "semantic_analysis": 72.5,
    "skills_match": 85.0,
    "experience_analysis": 60.0,
    "qualifications": 45.0
  },
  "weights": {
    "semantic_analysis": 0.3,
    "skills_match": 0.35,
    "experience_analysis": 0.2,
    "qualifications": 0.15
  },
  "matched_skills": ["python", "django", "postgresql"],
  "missing_skills": ["aws", "kubernetes"],
  "explanation": "Strong technical match with good experience...",
  "recommendations": "Consider gaining cloud platform experience...",
  "resume_insights": {
    "experience_years": 5,
    "education_level": "Masters",
    "key_strengths": ["Python", "Team Leadership"]
  }
}
```

### Analyze Resume (File Upload)
```http
POST /analyze-file
Content-Type: multipart/form-data
```

**Parameters:**
- `resume_file`: File (PDF, DOCX, TXT)
- `job_description`: String

**Response:** Same format as text analysis.

### Get Available Skills
```http
GET /skills
```

**Response:**
```json
{
  "available_skills": [
    {
      "category": "programming",
      "skills": "python, java, javascript, c++"
    },
    {
      "category": "frameworks", 
      "skills": "django, react, angular, spring"
    }
  ]
}
```

## Error Responses

### 400 Bad Request
```json
{
  "detail": "Text must be at least 10 characters long"
}
```

### 500 Internal Server Error
```json
{
  "detail": "Internal server error during analysis"
}
```

## Rate Limiting
- No limits in development
- Production: 100 requests/minute per IP

## Examples

### cURL
```bash
# Health check
curl http://localhost:8000/health

# Analyze resume
curl -X POST http://localhost:8000/analyze \
  -H "Content-Type: application/json" \
  -d '{
    "resume_text": "Python developer with 3 years experience",
    "job_description": "Looking for Python developer"
  }'
```

### Python
```python
import requests

response = requests.post('http://localhost:8000/analyze', json={
    'resume_text': 'Python developer with 3 years experience',
    'job_description': 'Looking for Python developer'
})

result = response.json()
print(f"Score: {result['overall_score']}")
```

### JavaScript
```javascript
const response = await fetch('http://localhost:8000/analyze', {
  method: 'POST',
  headers: {'Content-Type': 'application/json'},
  body: JSON.stringify({
    resume_text: 'Python developer with 3 years experience',
    job_description: 'Looking for Python developer'
  })
});

const result = await response.json();
console.log('Score:', result.overall_score);
```
