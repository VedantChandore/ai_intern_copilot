import streamlit as st
from resume_parser import ResumeParser
import tempfile
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from llm_client import MCPClient

st.set_page_config(page_title="AI Intern Copilot - Resume Parser", layout="centered")
st.title("\U0001F4C4 AI Intern Copilot - Resume Parser")

uploaded_file = st.file_uploader("Upload your resume (PDF only)", type=["pdf"])

if uploaded_file is not None:
    st.success("✅ File uploaded successfully")
    parser = ResumeParser()
    with st.spinner("🔍 Parsing your resume..."):
        # Save uploaded file to a temporary file
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_file:
            tmp_file.write(uploaded_file.read())
            tmp_file_path = tmp_file.name
        result = parser.parse(tmp_file_path)

    st.subheader("👤 Candidate Profile")
    st.write(f"**Name:** {result.get('name')}")
    st.write(f"**Email:** {result.get('email')}")
    st.write(f"**Phone:** {result.get('phone')}")
    st.write(f"**Skills:** {', '.join(result.get('skills', []))}")
    st.write(f"**Summary:** {result.get('summary')}")

    # Job Suggestions
    st.subheader("💡 AI Job Suggestions")
    llm = MCPClient()
    prompt = f"Suggest 5 job roles based on this resume:\n{result}"
    with st.spinner("🤖 Generating job suggestions..."):
        suggestions = llm.ping(prompt)
    st.write(suggestions)
