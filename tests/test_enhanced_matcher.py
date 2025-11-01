import pytest
from app.chains.enhanced_matcher import enhanced_match_resume_to_jd


class TestEnhancedMatcher:
    """Test suite for the enhanced resume matcher"""

    def test_minimal_inputs_return_zero(self):
        """Test that minimal/invalid inputs return 0 score"""
        test_cases = [
            (".", "."),
            ("", ""),
            ("x", "y"),
            ("a" * 19, "b" * 19),  # Below 20 char limit
        ]

        for resume, jd in test_cases:
            result = enhanced_match_resume_to_jd(resume, jd)
            assert result["overall_score"] == 0.0

    def test_spam_detection(self):
        """Test anti-spam protection"""
        spam_cases = [
            "python " * 50,  # Keyword stuffing
            "aaaaaaaaaaaaaaaaaaaaaa",  # Character repetition
            "python java python java python java python java",  # Pattern repetition
        ]

        for spam_text in spam_cases:
            result = enhanced_match_resume_to_jd(spam_text, "Python Developer")
            assert result["overall_score"] == 0.0

    def test_legitimate_resume_scoring(self):
        """Test that legitimate resumes get reasonable scores"""
        good_resume = """
        John Smith - Senior Python Developer
        5+ years experience at Google, Amazon
        Expert in Python, Django, PostgreSQL, AWS, Docker
        MS Computer Science from Stanford University
        Led teams of 10+ engineers, built systems serving millions
        """

        good_jd = """
        Senior Python Developer position
        5+ years experience required
        Python, Django, PostgreSQL experience needed
        AWS and Docker knowledge preferred
        Team leadership experience valued
        """

        result = enhanced_match_resume_to_jd(good_resume, good_jd)
        assert result["overall_score"] >= 30.0  # Should get reasonable score
        assert len(result["matched_skills"]) > 0  # Should find some skills
        assert "recommendations" in result
        assert "explanation" in result

    def test_return_structure(self):
        """Test that all required fields are present in response"""
        result = enhanced_match_resume_to_jd(
            "Valid resume text here", "Valid job description"
        )

        required_fields = [
            "overall_score",
            "breakdown",
            "weights",
            "matched_skills",
            "missing_skills",
            "explanation",
            "recommendations",
            "resume_insights",
        ]

        for field in required_fields:
            assert field in result

    def test_skills_matching(self):
        """Test skills detection and matching"""
        resume = "Python developer with Django and PostgreSQL experience"
        jd = "Looking for Python developer with Django knowledge"

        result = enhanced_match_resume_to_jd(resume, jd)
        assert "python" in [s.lower() for s in result["matched_skills"]]

    def test_edge_case_unicode(self):
        """Test handling of unicode characters"""
        resume = "João Silva - Python Developer 🐍"
        jd = "Python Developer needed"

        result = enhanced_match_resume_to_jd(resume, jd)
        # Should not crash and should return valid structure
        assert isinstance(result["overall_score"], (int, float))


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
