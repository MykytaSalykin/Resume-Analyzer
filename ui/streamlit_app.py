import streamlit as st
import markitdown
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from app.chains.enhanced_matcher import (
    enhanced_match_resume_to_jd as match_resume_to_jd,
)
import pandas as pd


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


def load_resume_file(uploaded_file):
    """Load resume from uploaded file."""
    try:
        if uploaded_file.type in [
            "application/pdf",
            "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        ]:
            md = markitdown.MarkItDown()
            result = md.convert(uploaded_file)
            return result.text_content
        else:
            return str(uploaded_file.read(), "utf-8")
    except Exception as e:
        st.error(f"Error loading file: {e}")
        return ""


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
            with st.spinner("Analyzing match..."):
                try:
                    result = match_resume_to_jd(resume_text, jd_text)

                    overall = result["overall_score"]
                    st.markdown("---")

                    st.markdown(
                        f"""
                        <div style="text-align: center; padding: 2rem; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); border-radius: 15px; color: white; margin-bottom: 2rem;">
                            <h2 style="margin: 0; color: white;">Match Score</h2>
                            <h1 style="margin: 0.5rem 0; font-size: 5rem; color: white;">{overall:.0f}/100</h1>
                            <p style="margin: 0; font-size: 1.2rem; color: rgba(255,255,255,0.9);">
                                {"Excellent Match! 🎉" if overall >= 80 else "Good Match! 👍" if overall >= 60 else "Needs Improvement 📈" if overall >= 40 else "Poor Match 💔"}
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

                    st.markdown("---")
                    st.subheader("📈 Score Components")

                    chart_data = []
                    for key, value in breakdown.items():
                        if key in metric_labels:
                            label, emoji = metric_labels[key]
                            chart_data.append({"Component": label, "Score": value})

                    breakdown_df = pd.DataFrame(chart_data)
                    st.bar_chart(breakdown_df.set_index("Component")[["Score"]])

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
                    for rec in result["recommendations"]:
                        st.markdown(f"- {rec}")

                    st.markdown("---")
                    with st.expander("📥 Export Results"):
                        breakdown_text = "DETAILED BREAKDOWN:\n-------------------\n"
                        for key, value in breakdown.items():
                            if key in metric_labels:
                                label, emoji = metric_labels[key]
                                breakdown_text += f"{label}: {value:.1f}/100\n"

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
{chr(10).join("• " + r for r in result["recommendations"])}
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

                comparison_df = pd.DataFrame(comparison_data)
                st.dataframe(comparison_df, use_container_width=True, hide_index=True)

                st.markdown("---")
                st.subheader("📈 Score Visualization")
                chart_df = comparison_df.set_index("Resume")
                st.bar_chart(chart_df[["Overall Score"]])

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
