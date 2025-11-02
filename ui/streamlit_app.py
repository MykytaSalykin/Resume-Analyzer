import streamlit as st
import markitdown
import sys
from pathlib import Path
import re
import plotly.graph_objects as go

# Pandas is optional for the UI table; fall back gracefully if missing
try:
    import pandas as pd  # type: ignore

    HAS_PANDAS = True
except Exception:  # pragma: no cover
    pd = None  # type: ignore
    HAS_PANDAS = False

# Ensure the repository root (that contains the `app` package) is on sys.path
# This makes running `streamlit run ui/streamlit_app.py` from the ui/ folder work.
def _ensure_repo_root_on_path():
    here = Path(__file__).resolve()
    candidates = [here.parent, here.parent.parent, here.parent.parent.parent]
    for p in candidates:
        if (p / "app" / "__init__.py").exists():
            if str(p) not in sys.path:
                sys.path.insert(0, str(p))
            return

_ensure_repo_root_on_path()

from app.chains.enhanced_matcher import (
    enhanced_match_resume_to_jd as match_resume_to_jd,
)


st.set_page_config(page_title="Resume Matcher", page_icon="🎯", layout="wide")

metric_labels = {
    "semantic": ("Semantic Match", "🎯"),
    "granular_semantic": ("Granular Semantic", "🔍"),
    "skills": ("Skills", "🛠️"),
    "smart_skills": ("Smart Skills Match", "🧠"),
    "experience": ("Experience", "💼"),
    "education": ("Education", "🎓"),
    "projects": ("Projects", "📁"),
    "tech_depth": ("Tech Depth", "⚙️"),
    "achievements": ("Achievements", "🏆"),
    "cultural": ("Cultural Fit", "🤝"),
    "requirements": ("Requirements", "✅"),
}


def _looks_gibberish(text: str) -> bool:
    t = (text or "").strip()
    if len(t) < 5:
        return True
    alpha = sum(1 for c in t if c.isalpha())
    if len(t) > 20 and alpha / max(1, len(t)) < 0.4:
        return True
    if re.search(r"(.{3,})\1{3,}", t.lower()):
        return True
    if re.search(r"(.)\1{20,}", t):
        return True
    return False


def load_resume_file(uploaded_file) -> str:
    """Extract text from an uploaded PDF using MarkItDown with safe fallbacks."""
    if not uploaded_file:
        return ""
    text = ""
    try:
        uploaded_file.seek(0)
        md = markitdown.MarkItDown()
        # convert_stream works with file-like objects from st.file_uploader
        res = md.convert_stream(uploaded_file)
        if hasattr(res, "text_content") and res.text_content:
            text = res.text_content
        elif hasattr(res, "content") and res.content:
            text = res.content
        elif isinstance(res, dict):
            text = res.get("text_content") or res.get("content") or ""
        else:
            text = str(res) if res is not None else ""
    except Exception:
        # Fallback to permissive UTF-8 decode
        try:
            uploaded_file.seek(0)
            text = uploaded_file.read().decode("utf-8", errors="ignore")
        except Exception:
            text = ""
    return text


tab1, tab2 = st.tabs(["🎯 Single Resume Analysis", "📊 Compare Multiple Resumes"])

with tab1:
    st.header("🎯 Resume Match Analyzer")
    st.markdown(
        "**Upload your resume and job description to get an instant compatibility score.**"
    )
    st.divider()

    col1, col2 = st.columns([1, 1])

    with col1:
        st.subheader("📄 Resume")
        resume_option = st.radio(
            "How would you like to provide your resume?",
            ["Upload File", "Paste Text"],
            horizontal=True,
        )

        resume_text = ""
        resume_file = None

        if resume_option == "Upload File":
            resume_file = st.file_uploader(
                "Upload resume (PDF)",
                type=["pdf"],
                label_visibility="collapsed",
            )

            if resume_file:
                resume_text = load_resume_file(resume_file)
                if resume_text:
                    st.success(
                        f"✅ Loaded: {resume_file.name} ({len(resume_text)} characters)"
                    )
        else:
            resume_text = st.text_area(
                "Paste your resume text here:",
                height=300,
                placeholder="John Doe\nSoftware Engineer\n...",
                label_visibility="collapsed",
            )

    with col2:
        st.subheader("💼 Job Description")
        jd_text = st.text_area(
            "Paste the job description:",
            height=400,
            placeholder="Software Engineer\n\nWe are looking for...",
            label_visibility="collapsed",
        )

    st.divider()

    if st.button(
        "🔍 Analyze Match",
        type="primary",
        use_container_width=True,
        key="analyze_single",
    ):
        if not resume_text.strip():
            st.error("Please provide your resume")
        elif not jd_text.strip():
            st.error("Please provide a job description")
        else:
            # Reject gibberish inputs early
            if _looks_gibberish(resume_text) or _looks_gibberish(jd_text):
                st.error(
                    "The provided text looks invalid. Please paste a proper resume and job description."
                )
            else:
                with st.spinner("Analyzing match..."):
                    try:
                        result = match_resume_to_jd(resume_text, jd_text)

                        # Boost display score for strong matches
                        overall_raw = float(result.get("overall_score", 0))
                        br = result.get("breakdown", {})
                        sem = float(br.get("semantic", 0))
                        skl = float(br.get("skills", 0))
                        exp = float(br.get("experience", 0))
                        edu = float(br.get("education", 0))
                        content = float(br.get("content_quality", 0))
                        boost = 0.0
                        if sem >= 70 and skl >= 70:
                            boost += 10.0
                        if exp >= 70:
                            boost += 5.0
                        if edu >= 60:
                            boost += 2.5
                        if content >= 60:
                            boost += 2.5
                        if sem >= 80 and skl >= 80 and overall_raw < 85:
                            boost += 10.0
                        overall = min(100.0, overall_raw + boost)

                        st.markdown("---")

                        st.markdown(
                            f"""
                            <div style="text-align: center; padding: 2rem; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); border-radius: 15px; color: white; margin-bottom: 2rem;">
                                <h2 style="margin: 0; color: white;">Match Score</h2>
                                <h1 style="margin: 0.5rem 0; font-size: 5rem; color: white;">{overall:.0f}/100</h1>
                                <p style="margin: 0; font-size: 1.2rem; color: rgba(255,255,255,0.9);">
                                    {"Excellent Match! 🎉" if overall >= 85 else "Good Match! 👍" if overall >= 70 else "Needs Improvement 📈" if overall >= 50 else "Poor Match 💔"}
                                </p>
                            </div>
                            """,
                            unsafe_allow_html=True,
                        )

                        st.subheader("📊 Detailed Breakdown")
                        breakdown = result["breakdown"]
                        weights = result["weights"]

                        metrics_list = []
                        for key, value in breakdown.items():
                            if key in metric_labels:
                                label, emoji = metric_labels[key]
                                weight = weights.get(key, 0) * 100
                                metrics_list.append((f"{emoji} {label}", value, weight))

                        num_cols = min(4, len(metrics_list))
                        cols = st.columns(num_cols)

                        for i, (label, score, weight) in enumerate(metrics_list):
                            col_idx = i % num_cols
                            with cols[col_idx]:
                                delta_color = "normal" if score >= 60 else "inverse"
                                st.metric(
                                    label=label,
                                    value=f"{score:.0f}%",
                                    delta=f"{weight:.0f}% weight",
                                    delta_color=delta_color,
                                )

                        # Replace bar chart with spider chart
                        st.markdown("---")
                        st.subheader("📈 Score Components")
                        categories_map = {
                            "semantic": "Semantic",
                            "skills": "Technical Skills",
                            "experience": "Experience",
                            "education": "Education",
                            "content_quality": "Content Quality",
                        }
                        categories = list(categories_map.values())
                        values = [
                            float(breakdown.get(k, 0.0)) for k in categories_map.keys()
                        ]
                        fig = go.Figure()
                        fig.add_trace(
                            go.Scatterpolar(
                                r=values,
                                theta=categories,
                                fill="toself",
                                name="Score",
                                line=dict(color="rgb(46, 204, 113)", width=2),
                                fillcolor="rgba(46, 204, 113, 0.3)",
                            )
                        )
                        fig.update_layout(
                            polar=dict(radialaxis=dict(visible=True, range=[0, 100])),
                            title=dict(
                                text=f"Resume Analysis Score: {overall:.1f}/100", x=0.5
                            ),
                            showlegend=False,
                            height=420,
                            margin=dict(l=30, r=30, t=60, b=20),
                        )
                        st.plotly_chart(fig, use_container_width=True)

                        st.markdown("---")
                        st.subheader("💡 Explanation")
                        st.info(result["explanation"])

                        matched_skills = result["matched_skills"]
                        missing_skills = result["missing_skills"]

                        col_skills_1, col_skills_2 = st.columns(2)

                        with col_skills_1:
                            st.markdown("#### ✅ Matched Skills")
                            if matched_skills:
                                st.write(", ".join(matched_skills))
                            else:
                                st.write("No skill matches found")

                        with col_skills_2:
                            st.markdown("#### ❌ Missing Skills")
                            if missing_skills:
                                st.write(", ".join(missing_skills))
                            else:
                                st.write("No missing skills!")

                        st.markdown("---")
                        st.subheader("🎯 Recommendations")
                        recs = result.get("recommendations", [])
                        if isinstance(recs, str):
                            rec_list = [
                                line.strip()
                                for line in recs.splitlines()
                                if line.strip()
                            ]
                        else:
                            rec_list = recs
                        if not rec_list:
                            st.write("No recommendations.")
                        else:
                            for rec in rec_list:
                                st.markdown(f"- {rec}")

                        st.markdown("---")
                        with st.expander("📥 Export Results"):
                            breakdown_text = (
                                "DETAILED BREAKDOWN:\n-------------------\n"
                            )
                            for key, value in breakdown.items():
                                if key in metric_labels:
                                    label, emoji = metric_labels[key]
                                    breakdown_text += f"{label}: {value:.1f}/100\n"

                            export_recs = (
                                "\n".join(f"- {r}" for r in rec_list)
                                if rec_list
                                else "None"
                            )
                            results_text = f"""
RESUME MATCH ANALYSIS
======================

Overall Match: {overall:.1f}/100

{breakdown_text}
EXPLANATION:
------------
{result["explanation"]}

MATCHED SKILLS:
--------------
{", ".join(matched_skills) if matched_skills else "None"}

MISSING SKILLS:
--------------
{", ".join(missing_skills) if missing_skills else "None"}

RECOMMENDATIONS:
---------------
{export_recs}
"""
                            st.download_button(
                                label="Download Analysis",
                                data=results_text,
                                file_name="resume_match_analysis.txt",
                                mime="text/plain",
                            )

                    except Exception as e:
                        st.error(f"Analysis failed: {e}")

with tab2:
    st.header("📊 Compare Multiple Resumes")
    st.markdown(
        "**Upload multiple resumes to compare their match scores side-by-side.**"
    )
    st.divider()

    st.subheader("💼 Job Description")
    jd_text_multi = st.text_area(
        "Paste the job description:",
        height=200,
        placeholder="Software Engineer\n\nWe are looking for...",
        label_visibility="collapsed",
        key="jd_multi",
    )

    st.subheader("📄 Resumes to Compare")
    uploaded_files = st.file_uploader(
        "Upload multiple resumes",
        type=["pdf"],
        accept_multiple_files=True,
    )

    if st.button(
        "🔍 Analyze All", type="primary", use_container_width=True, key="analyze_multi"
    ):
        if not jd_text_multi.strip():
            st.error("Please provide a job description")
        elif not uploaded_files:
            st.error("Please upload at least one resume")
        else:
            results_list = []

            with st.spinner(f"Analyzing {len(uploaded_files)} resumes..."):
                for uploaded_file in uploaded_files:
                    resume_text = load_resume_file(uploaded_file)
                    if resume_text:
                        try:
                            # Skip gibberish resumes
                            if _looks_gibberish(resume_text):
                                st.warning(
                                    f"Skipped {uploaded_file.name}: Gibberish resume"
                                )
                            else:
                                result = match_resume_to_jd(resume_text, jd_text_multi)
                                results_list.append(
                                    {
                                        "name": uploaded_file.name,
                                        "score": result["overall_score"],
                                        "result": result,
                                    }
                                )
                        except Exception as e:
                            st.warning(f"Failed to analyze {uploaded_file.name}: {e}")

            if results_list:
                results_list.sort(key=lambda x: x["score"], reverse=True)

                st.markdown("---")
                st.subheader("📊 Comparison Results")

                comparison_data = []
                for r in results_list:
                    row_data = {
                        "Resume": r["name"],
                        "Overall Score": r["score"],
                    }
                    breakdown = r["result"]["breakdown"]
                    top_keys = sorted(
                        breakdown.keys(), key=lambda k: breakdown[k], reverse=True
                    )[:4]
                    for key in top_keys:
                        if key in metric_labels:
                            label, emoji = metric_labels[key]
                            row_data[label] = breakdown[key]
                    comparison_data.append(row_data)

                if HAS_PANDAS:
                    comparison_df = pd.DataFrame(comparison_data)
                    st.dataframe(
                        comparison_df, use_container_width=True, hide_index=True
                    )

                st.markdown("---")
                st.subheader("📋 Detailed Breakdowns")

                for i, r in enumerate(results_list, 1):
                    with st.expander(
                        f"🏆 Rank #{i}: {r['name']} ({r['score']:.1f}/100)"
                    ):
                        breakdown = r["result"]["breakdown"]

                        metrics_list = []
                        for key, value in breakdown.items():
                            if key in metric_labels:
                                label, emoji = metric_labels[key]
                                metrics_list.append((f"{emoji} {label}", value))

                        num_cols = min(4, len(metrics_list))
                        cols = st.columns(num_cols)

                        for i, (label, score) in enumerate(metrics_list):
                            col_idx = i % num_cols
                            with cols[col_idx]:
                                st.metric(label, f"{score:.0f}%")

                        st.info(r["result"]["explanation"])

                        col_matched, col_missing = st.columns(2)
                        with col_matched:
                            st.write(
                                "**Matched Skills:**",
                                ", ".join(r["result"]["matched_skills"]) or "None",
                            )
                        with col_missing:
                            st.write(
                                "**Missing Skills:**",
                                ", ".join(r["result"]["missing_skills"]) or "None",
                            )

                        # Spider chart for each resume in the comparison
                        st.markdown("---")
                        st.subheader("📈 Score Components")
                        categories_map = {
                            "semantic": "Semantic",
                            "skills": "Technical Skills",
                            "experience": "Experience",
                            "education": "Education",
                            "content_quality": "Content Quality",
                        }
                        categories = list(categories_map.values())
                        values = [
                            float(breakdown.get(k, 0.0)) for k in categories_map.keys()
                        ]
                        fig = go.Figure()
                        fig.add_trace(
                            go.Scatterpolar(
                                r=values,
                                theta=categories,
                                fill="toself",
                                name="Score",
                                line=dict(color="rgb(46, 204, 113)", width=2),
                                fillcolor="rgba(46, 204, 113, 0.3)",
                            )
                        )
                        fig.update_layout(
                            polar=dict(radialaxis=dict(visible=True, range=[0, 100])),
                            title=dict(
                                text=f"Resume Analysis Score: {r['score']:.1f}/100",
                                x=0.5,
                            ),
                            showlegend=False,
                            height=420,
                            margin=dict(l=30, r=30, t=60, b=20),
                        )
                        st.plotly_chart(fig, use_container_width=True)

st.divider()
st.markdown(
    """
    <div style='text-align: center; color: #666; padding: 1rem;'>
        Built by Mykyta Salykin | 
        Analyze your resume compatibility in seconds
    </div>
    """,
    unsafe_allow_html=True,
)
