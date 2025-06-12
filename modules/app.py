import streamlit as st
from resume_parser import ResumeParser

st.set_page_config(page_title="AI Intern Copilot - Resume Parser", layout="centered")
st.title("📄 AI Intern Copilot - Resume Parser")

uploaded_file = st.file_uploader("Upload your resume (PDF only)", type=["pdf"])

if uploaded_file is not None:
    st.success("✅ File uploaded successfully")
    parser = ResumeParser()
    with st.spinner("🔍 Parsing your resume..."):
        result = parser.parse(uploaded_file)

    st.subheader("👤 Candidate Profile")
    st.write(f"**Name:** {result.get('name')}")
    st.write(f"**Email:** {result.get('email')}")
    st.write(f"**Phone:** {result.get('phone')}")
    st.write(f"**Skills:** {', '.join(result.get('skills', []))}")
    st.write(f"**Summary:** {result.get('summary')}")
