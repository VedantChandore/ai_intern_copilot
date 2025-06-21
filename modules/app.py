import streamlit as st
import pandas as pd
import sqlite3
import tempfile
import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from resume_parser import ResumeParser
from llm_client import MCPClient

# --- Custom CSS for Dark Theme, Neomorphic, and Modern UI ---
st.markdown("""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;700&display=swap');
        html, body, [class*="css"]  {
            font-family: 'Inter', sans-serif;
            background: #181c24;
            color: #f3f6fa;
        }
        .stApp {background: #181c24;}
        .stepper {display: flex; justify-content: space-between; margin: 2rem 0 2.5rem 0;}
        .step {flex: 1; text-align: center; position: relative;}
        .step:not(:last-child)::after {
            content: '';
            position: absolute; top: 50%; right: 0; width: 100%; height: 4px;
            background: linear-gradient(90deg, #2563eb 0%, #7f53ac 100%);
            z-index: 0; transform: translateY(-50%);
        }
        .step-icon {
            background: linear-gradient(135deg, #2563eb 0%, #7f53ac 100%);
            color: #fff; border-radius: 50%; width: 40px; height: 40px;
            display: flex; align-items: center; justify-content: center;
            margin: 0 auto 0.5rem auto; font-size: 1.3rem; box-shadow: 0 2px 8px #0002;
        }
        .step.active .step-icon {box-shadow: 0 0 0 4px #2563eb44;}
        .step-label {font-size: 1rem; color: #b0b8c1;}
        .step.active .step-label {color: #fff; font-weight: 700;}
        .upload-area {
            border: 2px dashed #2563eb; border-radius: 12px; background: #23283a;
            padding: 2.5rem 1rem; text-align: center; transition: box-shadow 0.2s;
        }
        .upload-area:hover {box-shadow: 0 0 0 4px #2563eb44;}
        .section-card {background: #23283a; border-radius: 16px; box-shadow: 0 2px 16px #0003; padding: 2rem; margin-bottom: 2rem;}
        .section-title {font-size: 1.5rem; font-weight: 700; color: #7f53ac;}
        .section-desc {color: #b0b8c1; margin-bottom: 1rem;}
        .footer {text-align: center; color: #888; margin-top: 2rem;}
        .stButton>button {background: linear-gradient(90deg, #2563eb 0%, #7f53ac 100%); color: white; font-weight: 600; border-radius: 8px; padding: 0.5em 2em;}
        .stTextInput>div>div>input, .stFileUploader>div>div {border-radius: 8px;}
        .stExpanderHeader {font-size: 1.1rem;}
        .stMetric {background: #23283a; border-radius: 8px;}
    </style>
""", unsafe_allow_html=True)

# --- Branding Header ---
st.markdown(
    """
    <div style="display: flex; align-items: center; gap: 1rem; margin-bottom: 1.5rem;">
        <img src="https://cdn-icons-png.flaticon.com/512/4712/4712035.png" width="48"/>
        <span style="font-size:2rem; font-weight:700; letter-spacing:1px;">AI Intern Copilot</span>
    </div>
    """,
    unsafe_allow_html=True
)

# --- Stepper/Progress Bar ---
steps = [
    {"icon": "📄", "label": "Upload Resume"},
    {"icon": "💡", "label": "Suggestions"},
    {"icon": "🔎", "label": "Job Search"},
    {"icon": "🤖", "label": "Apply"},
    {"icon": "📊", "label": "Analytics"}
]
if "step" not in st.session_state:
    st.session_state.step = 0

def go_to_step(idx):
    st.session_state.step = idx

st.markdown('<div class="stepper">', unsafe_allow_html=True)
for idx, step in enumerate(steps):
    active = "active" if idx == st.session_state.step else ""
    st.markdown(
        f'''
        <div class="step {active}" onclick="window.dispatchEvent(new CustomEvent('stepper', {{detail: {idx}}}))">
            <div class="step-icon">{step["icon"]}</div>
            <div class="step-label">{step["label"]}</div>
        </div>
        ''',
        unsafe_allow_html=True
    )
st.markdown('</div>', unsafe_allow_html=True)

# --- Step 1: Resume Upload ---
if st.session_state.step == 0:
    st.markdown('<div class="section-card">', unsafe_allow_html=True)
    st.markdown('<div class="section-title">📄 Upload Your Resume</div>', unsafe_allow_html=True)
    st.markdown('<div class="section-desc">Drag and drop your PDF resume below.</div>', unsafe_allow_html=True)
    uploaded_file = st.file_uploader("", type=["pdf"], key="resume_upload", label_visibility="collapsed")
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
        st.session_state.resume_data = resume_data
        st.button("Next: Get Suggestions", on_click=lambda: go_to_step(1))
    st.markdown('</div>', unsafe_allow_html=True)

# --- Step 2: AI Job Suggestions ---
elif st.session_state.step == 1:
    st.markdown('<div class="section-card">', unsafe_allow_html=True)
    st.markdown('<div class="section-title">💡 AI Job Suggestions</div>', unsafe_allow_html=True)
    st.markdown('<div class="section-desc">Get personalized job role suggestions based on your resume.</div>', unsafe_allow_html=True)
    resume_data = st.session_state.get("resume_data", None)
    if not resume_data:
        st.info("Please upload your resume in Step 1.")
        st.button("Back", on_click=lambda: go_to_step(0))
    else:
        with st.spinner("🤖 Generating job suggestions..."):
            llm = MCPClient()
            prompt = f"Suggest 5 job roles based on this resume:\n{resume_data}"
            suggestions = llm.ping(prompt)
        st.success("Here are some roles you might be interested in:")
        st.markdown(f"<div style='background-color:#23283a; border-radius:8px; padding:16px; margin-bottom:16px;'>{suggestions}</div>", unsafe_allow_html=True)
        st.button("Next: Job Search", on_click=lambda: go_to_step(2))
        st.button("Back", on_click=lambda: go_to_step(0))
    st.markdown('</div>', unsafe_allow_html=True)

# --- Step 3: Automated Job Search ---
elif st.session_state.step == 2:
    st.markdown('<div class="section-card">', unsafe_allow_html=True)
    st.markdown('<div class="section-title">🔎 Automated Job Search</div>', unsafe_allow_html=True)
    st.markdown('<div class="section-desc">Search for jobs on Indeed and LinkedIn. The search will open in your browser, and links will be provided below.</div>', unsafe_allow_html=True)
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
    st.button("Next: Apply", on_click=lambda: go_to_step(3))
    st.button("Back", on_click=lambda: go_to_step(1))
    st.markdown('</div>', unsafe_allow_html=True)

# --- Step 4: Automated Job Application ---
elif st.session_state.step == 3:
    st.markdown('<div class="section-card">', unsafe_allow_html=True)
    st.markdown('<div class="section-title">🤖 Automated Job Application (Experimental)</div>', unsafe_allow_html=True)
    st.markdown('<div class="section-desc">Paste a direct job application URL (e.g., SuccessFactors, Indeed) to autofill and submit your application. The browser will open for you to review and complete the process.</div>', unsafe_allow_html=True)
    job_url = st.text_input("Job Application URL", key="job_url")
    apply_clicked = st.button("🤖 Apply Automatically")
    resume_data = st.session_state.get("resume_data", None)
    if apply_clicked:
        if not resume_data:
            st.warning("Please upload and parse your resume first (in Step 1).")
        elif not job_url:
            st.warning("Please enter a job application URL.")
        else:
            from modules.application import JobApplicationBot
            with st.spinner("Filling and submitting the job application in your browser..."):
                bot = JobApplicationBot(resume_data)
                apply_result = bot.apply_to_job(job_url)
            st.success(apply_result)
    st.button("Next: Analytics", on_click=lambda: go_to_step(4))
    st.button("Back", on_click=lambda: go_to_step(2))
    st.markdown('</div>', unsafe_allow_html=True)

# --- Step 5: Analytics & Insights ---
elif st.session_state.step == 4:
    st.markdown('<div class="section-card">', unsafe_allow_html=True)
    st.markdown('<div class="section-title">📊 Analytics & Insights</div>', unsafe_allow_html=True)
    st.markdown('<div class="section-desc">Track your job search and application progress with real-time analytics.</div>', unsafe_allow_html=True)
    conn = sqlite3.connect('job_applications.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS applications
                 (date TEXT, job_title TEXT, company TEXT, job_url TEXT, status TEXT)''')
    conn.commit()
    df = pd.read_sql_query('SELECT * FROM applications', conn)
    conn.close()
    if not df.empty:
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric('Total Applications', len(df))
        with col2:
            st.metric('Unique Job Titles', df["job_title"].nunique())
        with col3:
            st.metric('Unique Companies', df["company"].nunique())
        st.subheader('Applications by Job Title')
        st.bar_chart(df['job_title'].value_counts())
        st.subheader('Applications by Company')
        st.bar_chart(df['company'].value_counts())
        df['date'] = pd.to_datetime(df['date'])
        st.subheader('Applications Over Time')
        st.line_chart(df.groupby('date').size())
        st.subheader('All Applications')
        st.dataframe(df)
    else:
        st.info('No application data yet. Start applying to jobs to see analytics!')
    st.button("Back", on_click=lambda: go_to_step(3))
    st.markdown('</div>', unsafe_allow_html=True)

# --- Footer ---
st.markdown('<div class="footer">Made with ❤️ by AI Intern Copilot</div>', unsafe_allow_html=True)
