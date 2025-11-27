from fastapi import FastAPI, HTTPException, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Dict, Any, List
import uvicorn
import logging
import traceback
import os

from app.chains.enhanced_matcher import enhanced_match_resume_to_jd
from app.embeddings.embeddings import get_embedder

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Resume Analysis API",
    description="AI-powered resume matching and analysis",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)


class AnalysisRequest(BaseModel):
    resume_text: str
    job_description: str

    def validate_text_fields(self):
        """Basic input validation."""
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


embeddings_model = None


@app.on_event("startup")
async def startup_event():
    """Load embeddings unless disabled (SKIP_EMBEDDINGS_LOAD)."""
    global embeddings_model
    try:
        if os.getenv("SKIP_EMBEDDINGS_LOAD", "0") in {"1", "true", "True"}:
            logger.info("Skipping embeddings model load (SKIP_EMBEDDINGS_LOAD)")
            return
        embeddings_model = get_embedder()
        logger.info("Embeddings model loaded")
    except Exception as e:
        logger.error(f"Failed to load embeddings model: {e}")


@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Basic health status."""
    return HealthResponse(
        status="healthy", version="1.0.0", model_loaded=embeddings_model is not None
    )


@app.post("/analyze", response_model=AnalysisResponse)
async def analyze_resume(request: AnalysisRequest):
    """Analyze resume vs job description."""
    try:
        request.validate_text_fields()
        logger.info(
            f"Analyzing resume ({len(request.resume_text)} chars) vs JD ({len(request.job_description)} chars)"
        )
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
    resume_file: UploadFile = File(...), job_description: str = Form(...)
):
    """Analyze uploaded file against JD (supports PDF, DOCX, TXT)."""
    if not job_description or len(job_description.strip()) < 10:
        raise HTTPException(
            status_code=400,
            detail="Job description is required and must be at least 10 characters",
        )

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
        file_content = await resume_file.read()

        if resume_file.content_type == "text/plain":
            resume_text = file_content.decode("utf-8")
            logger.info(f"Extracted text from TXT: {len(resume_text)} chars")
        elif resume_file.content_type == "application/pdf":
            import PyPDF2
            from io import BytesIO

            logger.info(f"Processing PDF file: {resume_file.filename}")
            try:
                pdf_reader = PyPDF2.PdfReader(BytesIO(file_content))
                resume_text = ""

                logger.info(f"PDF has {len(pdf_reader.pages)} pages")

                for i, page in enumerate(pdf_reader.pages):
                    try:
                        page_text = page.extract_text()
                        if page_text:
                            logger.info(
                                f"Page {i + 1} extracted {len(page_text)} chars"
                            )
                            resume_text += page_text + "\n"
                        else:
                            logger.warning(f"Page {i + 1} returned empty text")
                    except Exception as page_error:
                        logger.error(f"Error extracting page {i + 1}: {page_error}")
                        continue

                # Clean up the text - remove extra whitespace
                resume_text = " ".join(resume_text.split())
                logger.info(f"Total extracted from PDF: {len(resume_text)} chars")

                if len(resume_text) < 20:
                    logger.error(
                        f"PDF text extraction failed - only got: '{resume_text}'"
                    )
                    raise HTTPException(
                        status_code=400,
                        detail="Failed to extract text from PDF. The PDF might be image-based or encrypted.",
                    )

            except PyPDF2.errors.PdfReadError as pdf_error:
                logger.error(f"PDF read error: {pdf_error}")
                raise HTTPException(
                    status_code=400, detail=f"Failed to read PDF file: {str(pdf_error)}"
                )

        elif (
            resume_file.content_type
            == "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
        ):
            import docx
            from io import BytesIO

            logger.info(f"Processing DOCX file: {resume_file.filename}")
            doc = docx.Document(BytesIO(file_content))
            resume_text = "\n".join([paragraph.text for paragraph in doc.paragraphs])
            logger.info(f"Extracted text from DOCX: {len(resume_text)} chars")
        else:
            raise HTTPException(
                status_code=400,
                detail="Unsupported file format",
            )

        if len(resume_text.strip()) < 20:
            logger.warning(f"Extracted text too short: {len(resume_text)} chars")
            logger.warning(f"Text preview: {resume_text[:200]}")
            raise HTTPException(
                status_code=400,
                detail=f"Could not extract meaningful text from the file. Only {len(resume_text)} characters extracted.",
            )

        logger.info(
            f"Analyzing file resume ({len(resume_text)} chars) vs JD ({len(job_description)} chars)"
        )
        result = enhanced_match_resume_to_jd(resume_text, job_description)
        logger.info(f"File analysis complete - Score: {result['overall_score']:.1f}")
        return AnalysisResponse(**result)

    except UnicodeDecodeError:
        raise HTTPException(status_code=400, detail="Invalid text encoding")
    except Exception as e:
        logger.error(f"File analysis failed: {e}")
        raise HTTPException(status_code=500, detail=f"File processing failed: {str(e)}")


@app.get("/skills")
async def get_available_skills():
    """List detectable skills (regex-based)."""
    from app.chains.extractors import SKILL_PATTERNS

    skills = []
    for category, patterns in SKILL_PATTERNS.items():
        for pattern in patterns:
            skill_name = pattern.replace(r"\b", "").replace("|", ", ")
            skills.append({"category": category, "skills": skill_name})

    return {"available_skills": skills}


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

if __name__ == "__main__":
    uvicorn.run("api:app", host="0.0.0.0", port=8000, reload=True, log_level="info")
