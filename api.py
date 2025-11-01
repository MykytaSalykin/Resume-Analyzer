"""
FastAPI REST API for Resume Analysis
Provides enterprise-ready endpoints for resume matching
"""

from fastapi import FastAPI, HTTPException, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, field_validator
from typing import Dict, Any, List
import uvicorn
import logging
import traceback

# Import our analysis engine
from app.chains.enhanced_matcher import enhanced_match_resume_to_jd
from app.rag.embeddings import get_embedder

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="Resume Analysis API",
    description="AI-powered resume matching and analysis service",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)


# Pydantic models for request/response
class AnalysisRequest(BaseModel):
    resume_text: str
    job_description: str

    def validate_text_fields(self):
        """Validate text fields after initialization"""
        for field_name in ["resume_text", "job_description"]:
            value = getattr(self, field_name)
            if len(value.strip()) < 20:
                raise ValueError(f"{field_name} must be at least 20 characters long")
            if len(value) > 50000:
                raise ValueError(f"{field_name} too long (max 50,000 characters)")
            setattr(self, field_name, value.strip())


class AnalysisResponse(BaseModel):
    overall_score: float
    breakdown: Dict[str, float]
    weights: Dict[str, float]
    matched_skills: List[str]
    missing_skills: List[str]
    explanation: str
    recommendations: str
    resume_insights: Dict[str, Any]


class HealthResponse(BaseModel):
    status: str
    version: str
    model_loaded: bool


# Global model instance
embeddings_model = None


@app.on_event("startup")
async def startup_event():
    """Initialize the embeddings model on startup"""
    global embeddings_model
    try:
        embeddings_model = get_embedder()
        logger.info("✅ Embeddings model loaded successfully")
    except Exception as e:
        logger.error(f"❌ Failed to load embeddings model: {e}")


@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint"""
    return HealthResponse(
        status="healthy", version="1.0.0", model_loaded=embeddings_model is not None
    )


@app.post("/analyze", response_model=AnalysisResponse)
async def analyze_resume(request: AnalysisRequest):
    """
    Analyze resume against job description

    Returns detailed matching score and recommendations
    """
    try:
        # Validate request
        request.validate_text_fields()

        logger.info(
            f"Analyzing resume ({len(request.resume_text)} chars) against JD ({len(request.job_description)} chars)"
        )

        # Perform analysis
        result = enhanced_match_resume_to_jd(
            request.resume_text, request.job_description
        )

        logger.info(f"Analysis complete - Score: {result['overall_score']:.1f}")

        return AnalysisResponse(**result)

    except ValueError as e:
        logger.warning(f"Validation error: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Analysis failed: {e}\n{traceback.format_exc()}")
        raise HTTPException(
            status_code=500, detail="Internal server error during analysis"
        )


@app.post("/analyze-file")
async def analyze_resume_file(
    resume_file: UploadFile = File(...), job_description: str = None
):
    """
    Analyze uploaded resume file against job description

    Supports PDF, DOCX, and TXT files
    """
    if not job_description or len(job_description.strip()) < 10:
        raise HTTPException(
            status_code=400,
            detail="Job description is required and must be at least 10 characters",
        )

    # Validate file type
    allowed_types = [
        "application/pdf",
        "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        "text/plain",
    ]
    if resume_file.content_type not in allowed_types:
        raise HTTPException(
            status_code=400, detail="Unsupported file type. Allowed: PDF, DOCX, TXT"
        )

    try:
        # Read file content
        file_content = await resume_file.read()

        # Convert to text (simplified - in production use proper document parsers)
        if resume_file.content_type == "text/plain":
            resume_text = file_content.decode("utf-8")
        else:
            # For PDF/DOCX, you'd use libraries like PyPDF2, python-docx, etc.
            raise HTTPException(
                status_code=400,
                detail="PDF/DOCX parsing not implemented in this demo. Please use text files.",
            )

        # Analyze
        result = enhanced_match_resume_to_jd(resume_text, job_description)

        return AnalysisResponse(**result)

    except UnicodeDecodeError:
        raise HTTPException(status_code=400, detail="Invalid text encoding")
    except Exception as e:
        logger.error(f"File analysis failed: {e}")
        raise HTTPException(status_code=500, detail="File processing failed")


@app.get("/skills")
async def get_available_skills():
    """Get list of skills that the system can detect"""
    from app.chains.extractors import SKILL_PATTERNS

    skills = []
    for category, patterns in SKILL_PATTERNS.items():
        for pattern in patterns:
            # Extract skill names from regex patterns (simplified)
            skill_name = pattern.replace(r"\b", "").replace("|", ", ")
            skills.append({"category": category, "skills": skill_name})

    return {"available_skills": skills}


# CORS middleware for web frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify actual frontend URLs
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

if __name__ == "__main__":
    uvicorn.run("api:app", host="0.0.0.0", port=8000, reload=True, log_level="info")
