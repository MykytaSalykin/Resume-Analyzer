from __future__ import annotations
from typing import Dict, List, Tuple
import numpy as np
import re
import traceback


def _is_spam_or_fake(text: str) -> bool:
    """Detect spam or keyword stuffing"""
    words = text.lower().split()
    if len(words) < 10:
        return False

    word_counts = {w: words.count(w) for w in set(words) if len(w) > 3}
    if any(count / len(words) > 0.2 for count in word_counts.values()):
        return True

    spam_patterns = [
        r"(.)\1{10,}",
        r"(python|java|sql)\s*(python|java|sql)\s*(python|java|sql)",
    ]
    return any(re.search(pattern, text.lower()) for pattern in spam_patterns)


def extract_skills_fallback(text: str) -> List[str]:
    tech_skills = [
        "python",
        "java",
        "javascript",
        "typescript",
        "react",
        "node.js",
        "sql",
        "postgresql",
        "mysql",
        "mongodb",
        "docker",
        "kubernetes",
        "aws",
        "azure",
        "git",
        "tensorflow",
        "pytorch",
        "pandas",
        "numpy",
        "html",
        "css",
        "django",
    ]
    return [skill for skill in tech_skills if skill in text.lower()]


def enhanced_match_resume_to_jd(resume_text: str, jd_text: str) -> Dict:
    try:
        resume_clean = resume_text.strip()
        jd_clean = jd_text.strip()

        if len(resume_clean) < 20:
            return _minimal_score_response("Resume too short")

        if len(jd_clean) < 20:
            return _minimal_score_response("Job description too short")

        if _is_spam_or_fake(resume_clean):
            return _minimal_score_response(
                "Resume appears to be spam or artificially generated"
            )

        resume_content_score = _evaluate_content_depth(resume_clean)
        jd_content_score = _evaluate_jd_content_depth(jd_clean)

        try:
            from app.rag.embeddings import get_embedder
            embedder = get_embedder()
        except Exception as e:
            print(f"WARNING: Embedder failed: {e}")
            embedder = None

        if embedder is not None:
            try:
                semantic_score = _semantic_analysis(resume_clean, jd_clean, embedder)
            except Exception as e:
                print(f"Semantic analysis failed: {e}")
                semantic_score = _fallback_semantic_analysis(resume_clean, jd_clean)
        else:
            semantic_score = _fallback_semantic_analysis(resume_clean, jd_clean)

        try:
            skills_score, matched_skills, missing_skills = _skills_analysis(
                resume_clean, jd_clean
            )
        except Exception as e:
            print(f"Skills analysis failed: {e}")
            skills_score, matched_skills, missing_skills = _fallback_skills_analysis(
                resume_clean, jd_clean
            )

        try:
            experience_score = _experience_analysis(resume_clean, jd_clean)
        except Exception as e:
            print(f"Experience analysis failed: {e}")
            experience_score = 20.0

        try:
            qualifications_score = _qualifications_analysis(resume_clean, jd_clean)
        except Exception as e:
            print(f"Qualifications analysis failed: {e}")
            qualifications_score = 30.0

        content_multiplier = min(resume_content_score + 0.3, jd_content_score + 0.2)
        content_multiplier = min(content_multiplier, 1.0)

        base_score = (
            semantic_score * 0.30
            + skills_score * 0.35
            + experience_score * 0.20
            + qualifications_score * 0.15
        )

        overall = base_score * (0.7 + content_multiplier * 0.3)
        overall = min(overall, 95.0)

        explanation = _generate_explanation(
            semantic_score,
            skills_score,
            experience_score,
            qualifications_score,
            content_multiplier,
            matched_skills,
            missing_skills,
        )

        recommendations = _generate_recommendations(
            overall, matched_skills, missing_skills, experience_score
        )

        return {
            "overall_score": round(overall, 1),
            "breakdown": {
                "semantic": round(semantic_score, 1),
                "skills": round(skills_score, 1),
                "experience": round(experience_score, 1),
                "education": round(qualifications_score, 1),
                "content_quality": round(content_multiplier * 100, 1),
            },
            "weights": {
                "semantic": 0.30,
                "skills": 0.35,
                "experience": 0.20,
                "education": 0.15,
                "content_quality": 1.0,
            },
            "matched_skills": matched_skills,
            "missing_skills": missing_skills,
            "explanation": explanation,
            "recommendations": recommendations,
            "resume_insights": {
                "content_depth": resume_content_score,
                "word_count": len(resume_clean.split()),
                "estimated_completeness": min(100, resume_content_score * 100),
            },
        }

    except Exception as e:
        error_msg = f"Complete analysis failure: {str(e)}\n{traceback.format_exc()}"
        print(error_msg)
        return _error_score_response(f"System error: {str(e)}")


def _fallback_semantic_analysis(resume_text: str, jd_text: str) -> float:
    try:
        stop_words = {
            "the",
            "and",
            "or",
            "in",
            "on",
            "at",
            "to",
            "for",
            "of",
            "with",
            "a",
            "an",
            "is",
            "are",
            "be",
        }
        resume_words = set(re.findall(r"\b\w+\b", resume_text.lower())) - stop_words
        jd_words = set(re.findall(r"\b\w+\b", jd_text.lower())) - stop_words

        if not jd_words:
            return 15.0
        overlap_ratio = len(resume_words & jd_words) / len(jd_words)
        return min(overlap_ratio * 70, 60.0)
    except Exception:
        return 15.0


def _fallback_skills_analysis(
    resume_text: str, jd_text: str
) -> Tuple[float, List[str], List[str]]:
    """Fallback skills analysis."""
    try:
        resume_skills = extract_skills_fallback(resume_text)
        jd_skills = extract_skills_fallback(jd_text)

        if not jd_skills:
            return 20.0, [], ["No technical requirements identified"]

        if not resume_skills:
            return 5.0, [], jd_skills[:5]

        matched = []
        for jd_skill in jd_skills:
            if any(_skills_match(jd_skill, r_skill) for r_skill in resume_skills):
                matched.append(jd_skill)

        missing = [skill for skill in jd_skills if skill not in matched]

        coverage = len(matched) / len(jd_skills) if jd_skills else 0
        score = coverage * 60

        return min(score, 60.0), matched[:8], missing[:8]

    except Exception:
        return 10.0, [], ["Skills analysis failed"]


def _evaluate_jd_content_depth(text: str) -> float:
    """Evaluate if JD has substantial content."""
    try:
        text_lower = text.lower()

        requirement_indicators = [
            "experience",
            "skills",
            "requirements",
            "qualifications",
            "responsibilities",
            "must have",
            "required",
            "preferred",
            "bachelor",
            "master",
            "years",
            "knowledge",
            "proficient",
            "familiar",
            "expertise",
        ]

        tech_indicators = [
            "python",
            "java",
            "sql",
            "aws",
            "docker",
            "react",
            "node",
            "machine learning",
            "data",
            "software",
            "development",
            "programming",
        ]

        company_indicators = [
            "company",
            "team",
            "we are",
            "our",
            "join",
            "opportunity",
            "role",
        ]

        req_count = sum(1 for word in requirement_indicators if word in text_lower)
        tech_count = sum(1 for word in tech_indicators if word in text_lower)
        company_count = sum(1 for word in company_indicators if word in text_lower)

        word_count = len(text.split())

        if word_count < 20:
            return 0.1

        score = 0.0
        score += min(0.5, req_count * 0.08)
        score += min(0.3, tech_count * 0.05)
        score += min(0.2, company_count * 0.05)

        return min(1.0, score)

    except Exception:
        return 0.3


def _evaluate_content_depth(text: str) -> float:
    try:
        text_lower = text.lower()
        word_count = len(text.split())

        if word_count < 30:
            return 0.15
        elif word_count < 50:
            return 0.25
        elif word_count < 100:
            return 0.35

        experience_indicators = [
            "experience",
            "work",
            "employment",
            "position",
            "role",
            "job",
            "developed",
            "managed",
            "led",
            "created",
            "implemented",
            "designed",
            "built",
            "maintained",
            "collaborated",
            "responsible",
            "achieved",
        ]
        skills_indicators = [
            "skills",
            "technologies",
            "tools",
            "programming",
            "software",
            "proficient",
            "experienced",
            "familiar",
            "expertise",
        ]
        education_indicators = [
            "education",
            "degree",
            "university",
            "college",
            "bachelor",
            "master",
            "phd",
            "certification",
            "course",
            "training",
            "graduate",
        ]
        project_indicators = [
            "project",
            "projects",
            "portfolio",
            "github",
            "application",
            "system",
            "website",
            "platform",
            "solution",
        ]

        exp_count = sum(1 for word in experience_indicators if word in text_lower)
        skills_count = sum(1 for word in skills_indicators if word in text_lower)
        edu_count = sum(1 for word in education_indicators if word in text_lower)
        proj_count = sum(1 for word in project_indicators if word in text_lower)

        date_patterns = [
            r"20\d{2}",
            r"\b\d{1,2}/20\d{2}",
            r"(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\s+20\d{2}",
        ]
        date_count = sum(len(re.findall(pattern, text)) for pattern in date_patterns)

        score = 0.0
        score += min(0.35, exp_count * 0.05)
        score += min(0.25, skills_count * 0.04)
        score += min(0.20, edu_count * 0.08)
        score += min(0.15, proj_count * 0.05)
        score += min(0.05, date_count * 0.01)

        return min(1.0, score)

    except Exception:
        return 0.25


def _semantic_analysis(resume_text: str, jd_text: str, embedder) -> float:
    """Semantic similarity with error handling."""
    try:
        resume_chunks = _split_text_semantically(resume_text)
        jd_chunks = _split_text_semantically(jd_text)

        if not resume_chunks or not jd_chunks:
            return _fallback_semantic_analysis(resume_text, jd_text)

        try:
            all_chunks = resume_chunks + jd_chunks
            embeddings = embedder.encode(all_chunks, normalize_embeddings=True)

            if embeddings is None or len(embeddings) == 0:
                return _fallback_semantic_analysis(resume_text, jd_text)

        except Exception as e:
            print(f"Embedding generation failed: {e}")
            return _fallback_semantic_analysis(resume_text, jd_text)

        resume_embs = embeddings[: len(resume_chunks)]
        jd_embs = embeddings[len(resume_chunks) :]

        similarities = []
        for jd_emb in jd_embs:
            best_sim = 0.0
            for resume_emb in resume_embs:
                sim = float(np.dot(jd_emb, resume_emb))
                best_sim = max(best_sim, sim)
            similarities.append(best_sim)

        avg_similarity = np.mean(similarities)

        if avg_similarity < 0.3:
            return avg_similarity * 33
        elif avg_similarity < 0.6:
            return 10 + (avg_similarity - 0.3) * 67
        elif avg_similarity < 0.8:
            return 30 + (avg_similarity - 0.6) * 100
        else:
            return 50 + (avg_similarity - 0.8) * 150

    except Exception as e:
        print(f"Semantic analysis error: {e}")
        return _fallback_semantic_analysis(resume_text, jd_text)


def _extract_skills_comprehensive(text: str) -> List[str]:
    """Extract skills with comprehensive error handling."""
    try:
        from app.chains.extractors import extract_skills_by_category

        skills_dict = extract_skills_by_category(text)
        all_skills = []
        for category_skills in skills_dict.values():
            if isinstance(category_skills, list):
                all_skills.extend(category_skills)
        return list(set(all_skills))
    except Exception as e:
        print(f"Skills extraction failed: {e}")
        return extract_skills_fallback(text)


def _skills_analysis(
    resume_text: str, jd_text: str
) -> Tuple[float, List[str], List[str]]:
    """Skills analysis with error handling."""
    try:
        jd_skills = _extract_skills_comprehensive(jd_text)
        resume_skills = _extract_skills_comprehensive(resume_text)

        if not jd_skills:
            return 15.0, [], ["No specific technical requirements identified"]

        if not resume_skills:
            return 3.0, [], jd_skills[:8]

        matched_skills = []
        for jd_skill in jd_skills:
            if any(_skills_match(jd_skill, r_skill) for r_skill in resume_skills):
                matched_skills.append(jd_skill)

        missing_skills = [skill for skill in jd_skills if skill not in matched_skills]

        jd_lower = jd_text.lower()
        if any(
            word in jd_lower
            for word in ["team", "collaborate", "communication", "work with"]
        ):
            soft_skills = ["communication", "teamwork", "collaboration"]
            for skill in soft_skills:
                if (
                    skill not in [s.lower() for s in matched_skills + missing_skills]
                    and skill.lower() not in resume_text.lower()
                ):
                    missing_skills.append(skill)

        coverage = len(matched_skills) / max(1, len(jd_skills))

        if coverage == 0:
            score = 5
        elif coverage < 0.2:
            score = 5 + coverage * 50
        elif coverage < 0.5:
            score = 15 + (coverage - 0.2) * 67
        elif coverage < 0.8:
            score = 35 + (coverage - 0.5) * 67
        else:
            score = 55 + (coverage - 0.8) * 125

        return (
            min(score, 85.0),
            matched_skills[:10],
            missing_skills[:15],
        )

    except Exception as e:
        print(f"Skills analysis error: {e}")
        return _fallback_skills_analysis(resume_text, jd_text)


def _experience_analysis(resume_text: str, jd_text: str) -> float:
    """Experience analysis."""
    try:
        jd_years = _extract_years_required(jd_text)
        resume_years = _extract_years_experience(resume_text)

        score = 0.0

        if jd_years > 0:
            if resume_years >= jd_years:
                score = 80.0
            elif resume_years >= jd_years * 0.7:
                score = 50.0
            elif resume_years > 0:
                score = 25.0 * (resume_years / jd_years)
        else:
            if resume_years > 0:
                score = 50.0
            else:
                score = 20.0

        return min(score, 85.0)

    except Exception:
        return 25.0


def _qualifications_analysis(resume_text: str, jd_text: str) -> float:
    """Basic qualifications analysis."""
    try:
        resume_lower = resume_text.lower()
        jd_lower = jd_text.lower()

        education_terms = [
            "bachelor",
            "master",
            "phd",
            "degree",
            "university",
            "college",
        ]

        resume_has_education = any(term in resume_lower for term in education_terms)
        jd_requires_education = any(term in jd_lower for term in education_terms)

        if jd_requires_education:
            return 70.0 if resume_has_education else 20.0
        else:
            return 50.0 if resume_has_education else 40.0

    except Exception:
        return 35.0


def _split_text_semantically(text: str) -> List[str]:
    """Split text into chunks."""
    try:
        sentences = re.split(r"[.!?]+", text)
        chunks = []
        current_chunk = ""

        for sentence in sentences:
            sentence = sentence.strip()
            if not sentence:
                continue

            if len(current_chunk) + len(sentence) < 300:
                current_chunk += " " + sentence
            else:
                if current_chunk:
                    chunks.append(current_chunk.strip())
                current_chunk = sentence

        if current_chunk:
            chunks.append(current_chunk.strip())

        return chunks if chunks else [text]

    except Exception:
        return [text]


def _skills_match(skill1: str, skill2: str) -> bool:
    """Check if skills match."""
    try:
        skill1_lower = skill1.lower().strip()
        skill2_lower = skill2.lower().strip()

        if skill1_lower == skill2_lower:
            return True

        synonyms = {
            "ml": "machine learning",
            "ai": "artificial intelligence",
            "js": "javascript",
            "ts": "typescript",
            "py": "python",
            "sklearn": "scikit-learn",
            "tf": "tensorflow",
            "torch": "pytorch",
        }

        normalized1 = synonyms.get(skill1_lower, skill1_lower)
        normalized2 = synonyms.get(skill2_lower, skill2_lower)

        return normalized1 == normalized2

    except Exception:
        return False


def _extract_years_required(text: str) -> int:
    """Extract required years."""
    try:
        patterns = [
            r"(\d+)\+?\s*years?\s+(?:of\s+)?experience",
            r"minimum\s+of\s+(\d+)\s+years?",
            r"at\s+least\s+(\d+)\s+years?",
        ]

        for pattern in patterns:
            matches = re.findall(pattern, text.lower())
            if matches:
                return max(int(match) for match in matches)

        return 0

    except Exception:
        return 0


def _extract_years_experience(text: str) -> int:
    """Extract years from resume."""
    try:
        year_ranges = re.findall(r"(20\d{2})\s*[-–—]\s*(20\d{2})", text)
        if year_ranges:
            total_years = sum(int(end) - int(start) for start, end in year_ranges)
            return total_years

        explicit_years = re.findall(
            r"(\d+)\+?\s*years?\s+(?:of\s+)?experience", text.lower()
        )
        if explicit_years:
            return max(int(year) for year in explicit_years)

        return 0

    except Exception:
        return 0


def _minimal_score_response(reason: str) -> Dict:
    return {
        "overall_score": 0.0,
        "breakdown": {
            "semantic": 0.0,
            "skills": 0.0,
            "experience": 0.0,
            "education": 0.0,
            "content_quality": 10.0,
        },
        "weights": {
            "semantic": 0.30,
            "skills": 0.35,
            "experience": 0.20,
            "education": 0.15,
            "content_quality": 1.0,
        },
        "matched_skills": [],
        "missing_skills": ["Insufficient content for analysis"],
        "explanation": f"Very low score: {reason}. A complete resume should include detailed work experience, technical skills, education, and project descriptions.",
        "recommendations": "Provide comprehensive resume with work history\nList specific technical skills and tools used\nInclude education background and certifications\nDescribe concrete projects and achievements\nEnsure both resume and job description are detailed",
        "resume_insights": {
            "content_depth": 0.03,
            "word_count": len(reason.split()),
            "estimated_completeness": 3,
        },
    }


def _error_score_response(reason: str) -> Dict:
    return {
        "overall_score": 0.0,
        "breakdown": {
            "semantic": 0.0,
            "skills": 0.0,
            "experience": 0.0,
            "education": 0.0,
            "content_quality": 0.0,
        },
        "weights": {
            "semantic": 0.30,
            "skills": 0.35,
            "experience": 0.20,
            "education": 0.15,
            "content_quality": 1.0,
        },
        "matched_skills": [],
        "missing_skills": ["Analysis failed"],
        "explanation": f"Analysis failed: {reason}. Please check your input and try again.",
        "recommendations": "Verify proper text formatting\nCheck for special characters\nTry with plain text versions",
        "resume_insights": {
            "content_depth": 0.0,
            "word_count": 0,
            "estimated_completeness": 0,
        },
    }


def _generate_explanation(
    semantic: float,
    skills: float,
    experience: float,
    qualifications: float,
    content: float,
    matched: List[str],
    missing: List[str],
) -> str:
    try:
        parts = []
        overall_weighted = (
            semantic * 0.3 + skills * 0.35 + experience * 0.2 + qualifications * 0.15
        ) * content

        if overall_weighted < 15:
            parts.append(
                "🚨 CRITICAL MISMATCH: This resume does not align with the job requirements"
            )
        elif overall_weighted < 30:
            parts.append(
                "⚠️ POOR MATCH: Significant improvements needed for this position"
            )
        elif overall_weighted < 50:
            parts.append("📊 MODERATE MATCH: Some alignment but major gaps exist")
        elif overall_weighted < 70:
            parts.append("✅ GOOD MATCH: Strong alignment with room for improvement")
        else:
            parts.append("🎯 EXCELLENT MATCH: Strong candidate for this position")

        if content < 0.2:
            parts.append(
                "📝 RESUME QUALITY: Resume appears incomplete or lacks professional detail"
            )
        elif content < 0.4:
            parts.append(
                "📝 RESUME QUALITY: Resume lacks comprehensive professional information"
            )
        elif content < 0.6:
            parts.append(
                "📝 RESUME QUALITY: Resume has basic information but could be more detailed"
            )

        if semantic < 15:
            parts.append("🎯 RELEVANCE: Extremely poor content alignment")
        elif semantic < 25:
            parts.append("🎯 RELEVANCE: Poor content match")
        elif semantic < 40:
            parts.append("🎯 RELEVANCE: Some alignment but significant gaps")
        elif semantic < 60:
            parts.append("🎯 RELEVANCE: Moderate alignment")
        else:
            parts.append("🎯 RELEVANCE: Strong content alignment")

        if skills < 10:
            skill_msg = "🛠️ TECHNICAL SKILLS: Critical skills shortage - appears to lack most/all required technical competencies"
            if not matched and missing:
                skill_msg += f". ZERO matches found for required skills: {', '.join(missing[:5])}"
            parts.append(skill_msg)
        elif skills < 25:
            skill_msg = f"🛠️ TECHNICAL SKILLS: Major skills gap - only {len(matched)}/{len(matched) + len(missing)} required skills present"
            if matched:
                skill_msg += f". Has: {', '.join(matched[:3])}"
            if missing:
                skill_msg += f". CRITICALLY MISSING: {', '.join(missing[:5])}"
            parts.append(skill_msg)
        elif skills < 50:
            parts.append(
                f"🛠️ TECHNICAL SKILLS: Partial match - has {len(matched)} relevant skills but missing {len(missing)} key requirements"
            )
        else:
            parts.append(
                f"🛠️ TECHNICAL SKILLS: Good coverage - {len(matched)} relevant skills identified"
            )

        if experience < 20:
            parts.append(
                "💼 EXPERIENCE: Insufficient relevant experience demonstrated or no clear work history provided"
            )
        elif experience < 40:
            parts.append(
                "💼 EXPERIENCE: Limited relevant experience or experience level below job requirements"
            )
        elif experience < 60:
            parts.append(
                "💼 EXPERIENCE: Adequate experience level with some relevant background"
            )
        else:
            parts.append(
                "💼 EXPERIENCE: Strong relevant experience matching job requirements"
            )

        if qualifications < 30:
            parts.append(
                "🎓 QUALIFICATIONS: Education/certification requirements not clearly met"
            )
        elif qualifications < 60:
            parts.append(
                "🎓 QUALIFICATIONS: Basic educational requirements partially satisfied"
            )
        else:
            parts.append(
                "🎓 QUALIFICATIONS: Educational background aligns well with requirements"
            )

        return " | ".join(parts)

    except Exception:
        return "Analysis completed with limited detail due to processing constraints."


def _generate_recommendations(
    overall: float, matched: List[str], missing: List[str], experience: float
) -> str:
    """Generate detailed, actionable recommendations based on score."""
    try:
        recs = []

        if overall < 20:
            recs = [
                "🚨 Resume needs major overhaul",
                "📝 Add detailed work experience",
                "🛠️ List technical skills",
                "🎓 Include education",
            ]
        elif overall < 35:
            recs = [
                "📈 Significant improvements needed",
                "🎯 Focus on missing skills",
                "📝 Highlight relevant experience",
            ]
        elif overall < 50:
            recs = [
                "✨ Moderate improvements needed",
                "🛠️ Strengthen technical skills",
                "📝 Add quantified achievements",
            ]
        else:
            recs = ["🎯 Good foundation", "📝 Add more detail", "🛠️ Highlight projects"]

        if missing and len(missing) > 0:
            recs.append(f"🎯 Missing skills: {', '.join(missing[:3])}")

        if experience < 20:
            recs.append("📈 Build more relevant experience")

        if overall < 30:
            recs.extend(
                ["📋 Improve resume structure", "📊 Add quantified achievements"]
            )

        return "\n".join(recs[:5])

    except Exception:
        return (
            "Focus on improving resume completeness and technical skills alignment\n"
            "Add detailed work experience with specific achievements\n"
            "Develop the technical skills mentioned in job requirements"
        )
