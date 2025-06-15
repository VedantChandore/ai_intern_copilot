import streamlit as st
from resume_parser import ResumeParser
import tempfile
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from llm_client import MCPClient

st.set_page_config(page_title="AI Intern Copilot", layout="wide", page_icon="🤖")
st.markdown("""
<style>
    .main {background-color: #f7f9fa;}
    .stButton>button {background-color: #4F8BF9; color: white; font-weight: bold; border-radius: 8px;}
    .stTextInput>div>div>input {border-radius: 8px;}
    .stFileUploader>div>div {border-radius: 8px;}
    .stMarkdown {font-size: 1.1rem;}
</style>
""", unsafe_allow_html=True)

st.title("🤖 AI Intern Copilot")
st.markdown("""
Welcome to **AI Intern Copilot**! This tool helps you parse your resume, get AI-powered job suggestions, search for jobs, and even automate job applications—all in one place.
""")

# --- Section 1: Resume Parsing ---
st.header("1️⃣ Resume Parsing")
st.markdown("Upload your resume (PDF) to extract your profile details.")

with st.container():
    uploaded_file = st.file_uploader("Upload your resume (PDF only)", type=["pdf"], key="resume_upload")
    resume_data = None
    if uploaded_file is not None:
        st.success("✅ File uploaded successfully")
        parser = ResumeParser()
        with st.spinner("🔍 Parsing your resume..."):
            with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_file:
                tmp_file.write(uploaded_file.read())
                tmp_file_path = tmp_file.name
            result = parser.parse(tmp_file_path)
            resume_data = result
        with st.expander("👤 View Extracted Profile", expanded=True):
            st.markdown(f"**Name:** {result.get('name')}")
            st.markdown(f"**Email:** {result.get('email')}")
            st.markdown(f"**Phone:** {result.get('phone')}")
            st.markdown(f"**Skills:** {', '.join(result.get('skills', []))}")
            st.markdown(f"**Summary:** {result.get('summary')}")

# --- Section 2: AI Job Suggestions ---
st.header("2️⃣ AI Job Suggestions")
st.markdown("Get personalized job role suggestions based on your resume.")

if uploaded_file is not None and resume_data:
    with st.spinner("🤖 Generating job suggestions..."):
        llm = MCPClient()
        prompt = f"Suggest 5 job roles based on this resume:\n{resume_data}"
        suggestions = llm.ping(prompt)
    st.success("Here are some roles you might be interested in:")
    st.markdown(f"<div style='background-color:#e8f0fe; border-radius:8px; padding:16px; margin-bottom:16px;'>{suggestions}</div>", unsafe_allow_html=True)
else:
    st.info("Please upload your resume above to get job suggestions.")

# --- Section 3: Automated Job Search ---
st.header("3️⃣ Automated Job Search")
st.markdown("Search for jobs on Indeed and LinkedIn. The search will open in your browser, and links will be provided below.")

col1, col2 = st.columns(2)
with col1:
    job_title = st.text_input("Job Title", value="Software Developer", key="job_title")
with col2:
    job_location = st.text_input("Location", value="India", key="job_location")

search_clicked = st.button("🔎 Search Jobs")
if search_clicked:
    from modules.job_search import JobSearchPlaywrightHandler
    with st.spinner("Opening job search in browser..."):
        handler = JobSearchPlaywrightHandler()
        result = handler.handle('search', query=job_title, location=job_location)
        indeed_url = f"https://www.indeed.com/jobs?q={'+'.join(job_title.split())}&l={'+'.join(job_location.split())}"
        linkedin_url = f"https://www.linkedin.com/jobs/search/?keywords={'+'.join(job_title.split())}&location={'+'.join(job_location.split())}"
    st.success(result)
    st.markdown(f"🔗 [Opened Indeed]({indeed_url})")
    st.markdown(f"🔗 [Opened LinkedIn]({linkedin_url})")

# --- Section 4: Automated Job Application ---
st.header("4️⃣ Automated Job Application (Experimental)")
st.markdown("Paste a direct job application URL (e.g., SuccessFactors, Indeed) to autofill and submit your application. The browser will open for you to review and complete the process.")

job_url = st.text_input("Job Application URL", key="job_url")
apply_clicked = st.button("🤖 Apply Automatically")

if apply_clicked:
    if not resume_data:
        st.warning("Please upload and parse your resume first.")
    elif not job_url:
        st.warning("Please enter a job application URL.")
    else:
        from modules.application import JobApplicationBot
        with st.spinner("Filling and submitting the job application in your browser..."):
            bot = JobApplicationBot(resume_data)
            apply_result = bot.apply_to_job(job_url)
        st.success(apply_result)

st.markdown("---")
st.markdown("<center>Made with ❤️ by AI Intern Copilot</center>", unsafe_allow_html=True)
