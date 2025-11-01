import pytest
import os
import numpy as np
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent.parent))

from app.rag.embeddings import get_embedder, embed_texts
from app.rag.bm25 import BM25Store
from app.chains.extractors import (
    extract_email,
    extract_phone,
    extract_urls,
    extract_skills_by_category,
    parse_resume,
)


class TestEmbeddings:
    """Test embedding functionality."""

    def test_get_embedder(self):
        """Test embedder initialization."""
        embedder = get_embedder()
        assert embedder is not None

    def test_embed_texts(self):
        """Test text embedding."""
        texts = ["This is a test", "Another test"]
        embeddings = embed_texts(texts)
        assert embeddings.shape[0] == 2
        assert embeddings.shape[1] > 0

    def test_embedding_normalization(self):
        """Test that embeddings are normalized."""
        texts = ["Test text"]
        embeddings = embed_texts(texts)
        norm = np.linalg.norm(embeddings[0])
        assert abs(norm - 1.0) < 0.1


class TestBM25:
    """Test BM25 keyword search."""

    def test_bm25_build(self):
        """Test BM25 index building."""
        bm25 = BM25Store()
        texts = ["Python developer with ML experience", "Java backend engineer"]
        metadata = [{"source": "doc1"}, {"source": "doc2"}]
        bm25.build(texts, metadata)
        assert bm25.bm25 is not None

    def test_bm25_search(self):
        """Test BM25 search."""
        bm25 = BM25Store()
        texts = [
            "Python developer with machine learning experience",
            "Java backend engineer",
            "Python and JavaScript full stack",
        ]
        metadata = [
            {"source": "doc1"},
            {"source": "doc2"},
            {"source": "doc3"},
        ]
        bm25.build(texts, metadata)

        results = bm25.search("Python machine learning", top_k=2)
        assert len(results) == 2
        assert "Python" in results[0]["text"]


class TestExtractors:
    """Test resume parsing and extraction."""

    def test_extract_email(self):
        """Test email extraction."""
        text = "Contact me at john.doe@example.com"
        email = extract_email(text)
        assert email == "john.doe@example.com"

        text_no_email = "No email here"
        assert extract_email(text_no_email) is None

    def test_extract_phone(self):
        """Test phone extraction."""
        text = "Call me at +1 (555) 123-4567"
        phone = extract_phone(text)
        assert phone is not None
        assert "555" in phone

    def test_extract_urls(self):
        """Test URL extraction."""
        text = "Visit https://github.com/myuser and https://linkedin.com/in/profile"
        urls = extract_urls(text)
        assert len(urls) == 2
        assert "github.com" in urls[0]
        assert "linkedin.com" in urls[1]

    def test_extract_skills_by_category(self):
        """Test skill extraction by category."""
        text = """
        I'm a Python developer with experience in PyTorch, TensorFlow, and scikit-learn.
        I use pandas and numpy for data analysis, and I've deployed models on AWS.
        I also have RAG experience with FAISS and LangChain.
        """
        skills = extract_skills_by_category(text)

        assert "python" in skills.get("programming_languages", [])
        assert "pytorch" in skills.get("ml_frameworks", [])
        assert "pandas" in skills.get("data_tools", [])
        assert "aws" in skills.get("cloud", [])
        assert "rag" in skills.get("ai_rag", [])

    def test_parse_resume_comprehensive(self):
        """Test full resume parsing."""
        text = """
        John Doe
        Email: john@example.com
        Phone: +1-555-1234
        
        Skills: Python, PyTorch, AWS, FastAPI
        
        Location: New York, USA
        Website: https://johndoe.com
        """
        parsed = parse_resume(text)

        assert parsed["email"] == "john@example.com"
        assert parsed["phone"] is not None
        assert "python" in parsed["programming_languages"]
        assert "pytorch" in parsed["ml_frameworks"]
        assert "aws" in parsed["cloud"]
        assert "https://johndoe.com" in parsed["urls"]


class TestIntegration:
    """Integration tests."""

    def test_end_to_end_parsing(self):
        """Test that embedding + parsing works together."""
        text = "Python developer with PyTorch experience"
        embeddings = embed_texts([text])
        parsed = parse_resume(text)

        assert embeddings.shape[0] == 1
        assert len(parsed["programming_languages"]) > 0

    def test_bm25_and_embeddings(self):
        """Test that BM25 and embeddings complement each other."""
        texts = [
            "Python ML engineer",
            "Java backend developer",
            "Python data scientist",
        ]

        bm25 = BM25Store()
        bm25.build(texts, [{"source": f"doc{i}"} for i in range(len(texts))])
        bm25_results = bm25.search("Python", top_k=2)

        embeddings = embed_texts(texts)
        query_embedding = embed_texts(["Python machine learning"])[0]

        similarities = np.dot(embeddings, query_embedding)
        top_k_indices = np.argsort(similarities)[-2:][::-1]

        assert len(bm25_results) == 2
        assert len(top_k_indices) == 2
        assert all("Python" in texts[idx] for idx in top_k_indices)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
