import re
from typing import Optional, List, Dict
from dataclasses import dataclass, asdict

EMAIL_RE = re.compile(r"[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}", re.I)
PHONE_RE = re.compile(r"(\+?\d[\d\s().-]{7,}\d)")
URL_RE = re.compile(r"(https?://[^\s)]+)", re.I)
LOCATION_RE = re.compile(
    r"\b(Bratislava|Slovakia|Trenčín|Trencin|Kyiv|Ukraine|Prague|Poland|Warsaw|Berlin|Germany|USA|United States|London|UK|England)\b",
    re.I,
)

SKILL_PATTERNS = {
    "programming_languages": [
        r"\bpython\b",
        r"\bjava\b",
        r"\bjavascript\b",
        r"\btypescript\b",
        r"\bgo\b",
        r"\bgolang\b",
        r"\brust\b",
        r"\bkotlin\b",
        r"\bscala\b",
        r"\bc\+\+\b",
        r"\bc#\b",
        r"\bruby\b",
        r"\bphp\b",
        r"\bswift\b",
        r"\bjulia\b",
        r"\br\b",
        r"\bperl\b",
    ],
    "ml_frameworks": [
        r"\bml\b",
        r"\bmachine learning\b",
        r"\bpytorch\b",
        r"\btensorflow\b",
        r"\bkeras\b",
        r"\bscikit-learn\b",
        r"\bsklearn\b",
        r"\btransformers\b",
        r"\bhuggingface\b",
        r"\bhf\b",
        r"\bmxnet\b",
        r"\bcaffe\b",
        r"\btorch\b",
    ],
    "data_tools": [
        r"\bpandas\b",
        r"\bnumpy\b",
        r"\bmatplotlib\b",
        r"\bseaborn\b",
        r"\bplotly\b",
        r"\baltair\b",
        r"\bpyspark\b",
        r"\bapache spark\b",
        r"\bdask\b",
        r"\bpolars\b",
    ],
    "databases": [
        r"\bmysql\b",
        r"\bpostgresql\b",
        r"\bpostgres\b",
        r"\bsqlite\b",
        r"\bmongodb\b",
        r"\bcassandra\b",
        r"\bredis\b",
        r"\belasticsearch\b",
        r"\bdynamodb\b",
        r"\bneo4j\b",
    ],
    "cloud": [
        r"\baws\b",
        r"\bamazon web services\b",
        r"\bazure\b",
        r"\bgcp\b",
        r"\bgoogle cloud\b",
        r"\bheroku\b",
        r"\bdigitalocean\b",
        r"\bkubernetes\b",
        r"\bk8s\b",
        r"\bdocker\b",
    ],
    "ai_rag": [
        r"\brag\b",
        r"\bretrieval augmented\b",
        r"\bgenerative ai\b",
        r"\bllm\b",
        r"\blarge language model\b",
        r"\bfaiss\b",
        r"\bvectorstore\b",
        r"\bembedding\b",
        r"\bprompt engineering\b",
        r"\blangchain\b",
        r"\bdeep learning\b",
        r"\bneural networks\b",
        r"\bneural network\b",
        r"\bai\b",
        r"\bartificial intelligence\b",
        r"\bcomputer vision\b",
        r"\bnlp\b",
        r"\bnatural language processing\b",
    ],
}


@dataclass
class ResumeInfo:
    """Structured resume info for UI/API."""

    email: Optional[str] = None
    phone: Optional[str] = None
    location: Optional[str] = None
    urls: List[str] = None
    programming_languages: List[str] = None
    ml_frameworks: List[str] = None
    data_tools: List[str] = None
    databases: List[str] = None
    cloud: List[str] = None
    ai_rag: List[str] = None

    def __post_init__(self):
        if self.urls is None:
            self.urls = []
        for field in [
            "programming_languages",
            "ml_frameworks",
            "data_tools",
            "databases",
            "cloud",
            "ai_rag",
        ]:
            if getattr(self, field) is None:
                setattr(self, field, [])


def extract_email(text: str) -> Optional[str]:
    """Extract email."""
    m = EMAIL_RE.search(text)
    return m.group(0) if m else None


def extract_phone(text: str) -> Optional[str]:
    """Extract phone number."""
    m = PHONE_RE.search(text)
    return m.group(0) if m else None


def extract_urls(text: str) -> List[str]:
    """Extract URLs."""
    return list({m.group(0) for m in URL_RE.finditer(text)})


def extract_location(text: str) -> Optional[str]:
    """Extract location."""
    m = LOCATION_RE.search(text)
    return m.group(0) if m else None


def extract_skills_by_category(text: str) -> Dict[str, List[str]]:
    """Extract technical skills by category."""
    text_lower = text.lower()
    skills = {}

    for category, patterns in SKILL_PATTERNS.items():
        found_skills = set()
        for pattern in patterns:
            matches = re.findall(pattern, text_lower, re.I)
            if matches:
                found_skills.update(m.strip() for m in matches if m.strip())
        skills[category] = sorted(list(found_skills))

    return skills


def parse_resume(text: str) -> Dict:
    """Return normalized resume info."""
    resume_info = ResumeInfo(
        email=extract_email(text),
        phone=extract_phone(text),
        location=extract_location(text),
        urls=extract_urls(text),
    )

    skills = extract_skills_by_category(text)
    resume_info.programming_languages = skills.get("programming_languages", [])
    resume_info.ml_frameworks = skills.get("ml_frameworks", [])
    resume_info.data_tools = skills.get("data_tools", [])
    resume_info.databases = skills.get("databases", [])
    resume_info.cloud = skills.get("cloud", [])
    resume_info.ai_rag = skills.get("ai_rag", [])

    return asdict(resume_info)
