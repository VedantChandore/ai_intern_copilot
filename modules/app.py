import streamlit as st
import pandas as pd
import sqlite3
import tempfile
import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from resume_parser import ResumeParser
from llm_client import MCPClient

# Configure page
st.set_page_config(
    page_title="AI Intern Copilot",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# --- Enhanced Custom CSS for Premium UI/UX ---
st.markdown("""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&family=JetBrains+Mono:wght@400;500&display=swap');
        
        /* Global Styles */
        html, body, [class*="css"] {
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
            background: linear-gradient(135deg, #0f1419 0%, #1a1f2e 50%, #2d1b69 100%);
            color: #e2e8f0;
            line-height: 1.6;
        }
        
        .stApp {
            background: transparent;
        }
        
        /* Custom Scrollbar */
        ::-webkit-scrollbar {
            width: 8px;
        }
        ::-webkit-scrollbar-track {
            background: #1e293b;
            border-radius: 4px;
        }
        ::-webkit-scrollbar-thumb {
            background: linear-gradient(135deg, #3b82f6, #8b5cf6);
            border-radius: 4px;
        }
        ::-webkit-scrollbar-thumb:hover {
            background: linear-gradient(135deg, #2563eb, #7c3aed);
        }
        
        /* Header Branding */
        .brand-header {
            background: linear-gradient(135deg, #1e293b 0%, #334155 100%);
            border-radius: 24px;
            padding: 2rem;
            margin-bottom: 3rem;
            border: 1px solid #334155;
            box-shadow: 0 20px 40px rgba(0, 0, 0, 0.3);
            position: relative;
            overflow: hidden;
        }
        
        .brand-header::before {
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            height: 2px;
            background: linear-gradient(90deg, #3b82f6, #8b5cf6, #ec4899);
        }
        
        .brand-content {
            display: flex;
            align-items: center;
            gap: 1.5rem;
            position: relative;
            z-index: 1;
        }
        
        .brand-icon {
            width: 64px;
            height: 64px;
            background: linear-gradient(135deg, #3b82f6, #8b5cf6);
            border-radius: 16px;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 2rem;
            box-shadow: 0 8px 32px rgba(59, 130, 246, 0.3);
        }
        
        .brand-text {
            flex: 1;
        }
        
        .brand-title {
            font-size: 2.5rem;
            font-weight: 800;
            background: linear-gradient(135deg, #3b82f6, #8b5cf6, #ec4899);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
            margin: 0;
            letter-spacing: -0.02em;
        }
        
        .brand-subtitle {
            color: #94a3b8;
            font-size: 1.1rem;
            margin: 0.5rem 0 0 0;
            font-weight: 400;
        }
        
        /* Enhanced Stepper */
        .stepper-container {
            background: rgba(30, 41, 59, 0.5);
            backdrop-filter: blur(10px);
            border-radius: 20px;
            padding: 2rem;
            margin: 2rem 0 3rem 0;
            border: 1px solid rgba(148, 163, 184, 0.1);
        }
        
        .stepper {
            display: flex;
            justify-content: space-between;
            position: relative;
        }
        
        .stepper::before {
            content: '';
            position: absolute;
            top: 28px;
            left: 28px;
            right: 28px;
            height: 3px;
            background: linear-gradient(90deg, #1e293b 0%, #334155 100%);
            border-radius: 2px;
            z-index: 0;
        }
        
        .step {
            flex: 1;
            text-align: center;
            position: relative;
            cursor: pointer;
            transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
            z-index: 1;
        }
        
        .step-icon {
            width: 56px;
            height: 56px;
            background: linear-gradient(135deg, #1e293b, #334155);
            color: #64748b;
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            margin: 0 auto 1rem auto;
            font-size: 1.5rem;
            border: 3px solid #334155;
            transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
            position: relative;
            z-index: 2;
        }
        
        .step.active .step-icon {
            background: linear-gradient(135deg, #3b82f6, #8b5cf6);
            color: white;
            border-color: #3b82f6;
            box-shadow: 0 0 0 4px rgba(59, 130, 246, 0.2), 0 8px 32px rgba(59, 130, 246, 0.3);
            transform: scale(1.1);
        }
        
        .step.completed .step-icon {
            background: linear-gradient(135deg, #10b981, #059669);
            color: white;
            border-color: #10b981;
        }
        
        .step-label {
            font-size: 0.95rem;
            color: #64748b;
            font-weight: 500;
            transition: all 0.3s ease;
        }
        
        .step.active .step-label {
            color: #e2e8f0;
            font-weight: 600;
        }
        
        .step.completed .step-label {
            color: #10b981;
        }
        
        /* Enhanced Section Cards */
        .section-card {
            background: linear-gradient(135deg, rgba(30, 41, 59, 0.8) 0%, rgba(51, 65, 85, 0.6) 100%);
            backdrop-filter: blur(20px);
            border-radius: 24px;
            padding: 3rem;
            margin-bottom: 2rem;
            border: 1px solid rgba(148, 163, 184, 0.1);
            box-shadow: 0 25px 50px rgba(0, 0, 0, 0.25);
            transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
            position: relative;
            overflow: hidden;
        }
        
        .section-card::before {
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            height: 1px;
            background: linear-gradient(90deg, transparent, rgba(59, 130, 246, 0.5), transparent);
        }
        
        .section-card:hover {
            transform: translateY(-4px);
            box-shadow: 0 32px 64px rgba(0, 0, 0, 0.3);
            border-color: rgba(59, 130, 246, 0.3);
        }
        
        .section-header {
            display: flex;
            align-items: center;
            gap: 1rem;
            margin-bottom: 2rem;
        }
        
        .section-icon {
            width: 48px;
            height: 48px;
            background: linear-gradient(135deg, #3b82f6, #8b5cf6);
            border-radius: 12px;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 1.5rem;
            box-shadow: 0 8px 32px rgba(59, 130, 246, 0.3);
        }
        
        .section-title {
            font-size: 1.8rem;
            font-weight: 700;
            color: #000000;
            margin: 0;
            letter-spacing: -0.01em;
        }
        
        .section-desc {
            color: #94a3b8;
            font-size: 1.1rem;
            margin: 1rem 0 2rem 0;
            line-height: 1.6;
        }
        
        /* Enhanced Upload Area */
        .upload-area {
            border: 2px dashed rgba(59, 130, 246, 0.3);
            border-radius: 20px;
            background: linear-gradient(135deg, rgba(59, 130, 246, 0.05) 0%, rgba(139, 92, 246, 0.05) 100%);
            padding: 3rem 2rem;
            text-align: center;
            transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
            margin: 2rem 0;
            position: relative;
            overflow: hidden;
        }
        
        .upload-area::before {
            content: '';
            position: absolute;
            top: -50%;
            left: -50%;
            width: 200%;
            height: 200%;
            background: linear-gradient(45deg, transparent, rgba(59, 130, 246, 0.1), transparent);
            transform: rotate(45deg);
            transition: all 0.6s ease;
            opacity: 0;
        }
        
        .upload-area:hover {
            border-color: rgba(59, 130, 246, 0.6);
            background: linear-gradient(135deg, rgba(59, 130, 246, 0.1) 0%, rgba(139, 92, 246, 0.1) 100%);
            transform: translateY(-2px);
        }
        
        .upload-area:hover::before {
            opacity: 1;
            animation: shimmer 2s infinite;
        }
        
        @keyframes shimmer {
            0% { transform: translateX(-100%) translateY(-100%) rotate(45deg); }
            100% { transform: translateX(100%) translateY(100%) rotate(45deg); }
        }
        
        /* Enhanced Buttons */
        .stButton > button {
            background: linear-gradient(135deg, #3b82f6 0%, #8b5cf6 100%);
            color: white;
            font-weight: 600;
            border-radius: 12px;
            padding: 0.75rem 2rem;
            font-size: 1rem;
            border: none;
            box-shadow: 0 4px 16px rgba(59, 130, 246, 0.3);
            transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
            position: relative;
            overflow: hidden;
        }
        
        .stButton > button::before {
            content: '';
            position: absolute;
            top: 0;
            left: -100%;
            width: 100%;
            height: 100%;
            background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.2), transparent);
            transition: left 0.5s;
        }
        
        .stButton > button:hover {
            background: linear-gradient(135deg, #2563eb 0%, #7c3aed 100%);
            box-shadow: 0 8px 32px rgba(59, 130, 246, 0.4);
            transform: translateY(-2px);
        }
        
        .stButton > button:hover::before {
            left: 100%;
        }
        
        .stButton > button:active {
            transform: translateY(0);
        }
        
        /* Secondary Button Style */
        .secondary-btn {
            background: rgba(51, 65, 85, 0.8) !important;
            border: 1px solid rgba(148, 163, 184, 0.3) !important;
            box-shadow: 0 4px 16px rgba(0, 0, 0, 0.2) !important;
        }
        
        .secondary-btn:hover {
            background: rgba(71, 85, 105, 0.9) !important;
            border-color: rgba(148, 163, 184, 0.5) !important;
        }
        
        /* Enhanced Form Elements */
        .stTextInput > div > div > input,
        .stSelectbox > div > div > select {
            background: rgba(30, 41, 59, 0.8);
            border: 1px solid rgba(148, 163, 184, 0.2);
            border-radius: 12px;
            color: #e2e8f0;
            padding: 0.75rem 1rem;
            font-size: 1rem;
            transition: all 0.3s ease;
        }
        
        .stTextInput > div > div > input:focus,
        .stSelectbox > div > div > select:focus {
            border-color: #3b82f6;
            box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
            outline: none;
        }
        
        /* File Preview */
        .file-preview {
            background: linear-gradient(135deg, rgba(16, 185, 129, 0.1) 0%, rgba(5, 150, 105, 0.1) 100%);
            border: 1px solid rgba(16, 185, 129, 0.3);
            border-radius: 12px;
            padding: 1rem 1.5rem;
            margin: 1rem 0;
            color: #10b981;
            font-weight: 500;
            display: flex;
            align-items: center;
            gap: 0.75rem;
        }
        
        /* Enhanced Metrics */
        .stMetric {
            background: linear-gradient(135deg, rgba(30, 41, 59, 0.8) 0%, rgba(51, 65, 85, 0.6) 100%);
            border-radius: 16px;
            padding: 1.5rem;
            border: 1px solid rgba(148, 163, 184, 0.1);
            box-shadow: 0 8px 32px rgba(0, 0, 0, 0.2);
        }
        
        /* Success/Info Messages */
        .stSuccess {
            background: linear-gradient(135deg, rgba(16, 185, 129, 0.1) 0%, rgba(5, 150, 105, 0.1) 100%);
            border: 1px solid rgba(16, 185, 129, 0.3);
            border-radius: 12px;
        }
        
        .stInfo {
            background: linear-gradient(135deg, rgba(59, 130, 246, 0.1) 0%, rgba(37, 99, 235, 0.1) 100%);
            border: 1px solid rgba(59, 130, 246, 0.3);
            border-radius: 12px;
        }
        
        .stWarning {
            background: linear-gradient(135deg, rgba(245, 158, 11, 0.1) 0%, rgba(217, 119, 6, 0.1) 100%);
            border: 1px solid rgba(245, 158, 11, 0.3);
            border-radius: 12px;
        }
        
        /* Enhanced Dataframe */
        .stDataFrame {
            border-radius: 12px;
            overflow: hidden;
            box-shadow: 0 8px 32px rgba(0, 0, 0, 0.2);
        }
        
        /* Loading Spinner Enhancement */
        .stSpinner {
            color: #3b82f6;
        }
        
        /* Footer */
        .footer {
            text-align: center;
            color: #64748b;
            margin: 4rem 0 2rem 0;
            font-size: 1rem;
            padding: 2rem;
            border-top: 1px solid rgba(148, 163, 184, 0.1);
        }
        
        /* Responsive Design */
        @media (max-width: 768px) {
            .brand-content {
                flex-direction: column;
                text-align: center;
            }
            
            .brand-title {
                font-size: 2rem;
            }
            
            .section-card {
                padding: 2rem 1.5rem;
            }
            
            .stepper {
                flex-wrap: wrap;
                gap: 1rem;
            }
            
            .step {
                flex: 1 1 calc(50% - 0.5rem);
                min-width: 120px;
            }
            
            .step-icon {
                width: 48px;
                height: 48px;
                font-size: 1.2rem;
            }
            
            .step-label {
                font-size: 0.85rem;
            }
        }
        
        /* Animation Classes */
        .fade-in {
            animation: fadeIn 0.6s ease-out;
        }
        
        @keyframes fadeIn {
            from {
                opacity: 0;
                transform: translateY(20px);
            }
            to {
                opacity: 1;
                transform: translateY(0);
            }
        }
        
        .slide-up {
            animation: slideUp 0.8s cubic-bezier(0.4, 0, 0.2, 1);
        }
        
        @keyframes slideUp {
            from {
                opacity: 0;
                transform: translateY(40px);
            }
            to {
                opacity: 1;
                transform: translateY(0);
            }
        }
    </style>
""", unsafe_allow_html=True)

# --- Enhanced Branding Header ---
st.markdown("""
    <div class="brand-header fade-in">
        <div class="brand-content">
            <div class="brand-icon">🚀</div>
            <div class="brand-text">
                <h1 class="brand-title">AI Intern Copilot</h1>
                <p class="brand-subtitle">Your intelligent companion for landing the perfect internship</p>
            </div>
        </div>
    </div>
""", unsafe_allow_html=True)

# --- Enhanced Stepper/Progress Bar ---
steps = [
    {"icon": "📄", "label": "Upload Resume", "desc": "Upload your resume"},
    {"icon": "💡", "label": "AI Suggestions", "desc": "Get job recommendations"},
    {"icon": "🔎", "label": "Job Search", "desc": "Find opportunities"},
    {"icon": "🤖", "label": "Auto Apply", "desc": "Apply automatically"},
    {"icon": "📊", "label": "Analytics", "desc": "Track progress"},
    {"icon": "💬", "label": "Career Copilot", "desc": "Ask anything about job search, resume, interview prep, or career planning"}
]

if "step" not in st.session_state:
    st.session_state.step = 0

def go_to_step(idx):
    st.session_state.step = idx

st.markdown('<div class="stepper-container slide-up">', unsafe_allow_html=True)
st.markdown('<div class="stepper">', unsafe_allow_html=True)

for idx, step in enumerate(steps):
    status_class = ""
    if idx < st.session_state.step:
        status_class = "completed"
    elif idx == st.session_state.step:
        status_class = "active"
    
    st.markdown(f'''
        <div class="step {status_class}">
            <div class="step-icon">{step["icon"]}</div>
            <div class="step-label">{step["label"]}</div>
        </div>
    ''', unsafe_allow_html=True)

st.markdown('</div></div>', unsafe_allow_html=True)

# --- Step 1: Resume Upload ---
if st.session_state.step == 0:
    st.markdown('<div class="section-card" style="background:#23283a;border-radius:20px;box-shadow:0 4px 24px #0004;padding:2.5rem;margin-bottom:2rem;">', unsafe_allow_html=True)
    st.markdown('<div class="section-title">📄 Upload Your Resume</div>', unsafe_allow_html=True)
    st.markdown('<div class="section-desc">Drag and drop your PDF resume below.</div>', unsafe_allow_html=True)
    uploaded_file = st.file_uploader("", type=["pdf"], key="resume_upload", label_visibility="collapsed")
    resume_data = None
    if uploaded_file is not None:
        st.success("✅ File uploaded successfully")
        st.markdown(
            f'<div class="file-preview">📄 <b>{uploaded_file.name}</b> ({uploaded_file.size//1024} KB)</div>',
            unsafe_allow_html=True
        )
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
    st.markdown('<div class="section-card" style="background:#23283a;border-radius:20px;box-shadow:0 4px 24px #0004;padding:2.5rem;margin-bottom:2rem;">', unsafe_allow_html=True)
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
        st.markdown(f"<div style='background:#23283a; border-radius:8px; padding:16px; margin-bottom:16px;'>{suggestions}</div>", unsafe_allow_html=True)
        st.button("Next: Job Search", on_click=lambda: go_to_step(2))
        st.button("Back", on_click=lambda: go_to_step(0))
    st.markdown('</div>', unsafe_allow_html=True)

# --- Step 3: Automated Job Search ---
elif st.session_state.step == 2:
    st.markdown('<div class="section-card" style="background:#23283a;border-radius:20px;box-shadow:0 4px 24px #0004;padding:2.5rem;margin-bottom:2rem;">', unsafe_allow_html=True)
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
    st.markdown('<div class="section-card" style="background:#23283a;border-radius:20px;box-shadow:0 4px 24px #0004;padding:2.5rem;margin-bottom:2rem;">', unsafe_allow_html=True)
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
    st.markdown('<div class="section-card" style="background:#23283a;border-radius:20px;box-shadow:0 4px 24px #0004;padding:2.5rem;margin-bottom:2rem;">', unsafe_allow_html=True)
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
    st.button("Next: Career Copilot", on_click=lambda: go_to_step(5))
    st.button("Back", on_click=lambda: go_to_step(3))
    st.markdown('</div>', unsafe_allow_html=True)

# --- Step 6: Conversational Copilot/Chatbot ---
elif st.session_state.step == 5:
    st.markdown('<div class="section-card">', unsafe_allow_html=True)
    st.markdown('<div class="section-title">💬 Career Copilot Chatbot</div>', unsafe_allow_html=True)
    st.markdown('<div class="section-desc">Ask anything about job search, resume, interview prep, or career planning. You can also upload your resume for more personalized advice.</div>', unsafe_allow_html=True)

    # Chatbot resume upload
    if "chat_resume_data" not in st.session_state:
        st.session_state.chat_resume_data = None
    chat_uploaded_file = st.file_uploader("Upload Resume for Chatbot (PDF)", type=["pdf"], key="chat_resume_upload")
    if chat_uploaded_file is not None:
        parser = ResumeParser()
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_file:
            tmp_file.write(chat_uploaded_file.read())
            tmp_file_path = tmp_file.name
        chat_resume_data = parser.parse(tmp_file_path)
        st.session_state.chat_resume_data = chat_resume_data
        st.success("Resume uploaded for chatbot context!")
        st.markdown(f'<div class="file-preview">📄 <b>{chat_uploaded_file.name}</b> ({chat_uploaded_file.size//1024} KB)</div>', unsafe_allow_html=True)
        st.session_state.chat_history = []  # Optionally clear chat on new resume

    # Chat history
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []

    def get_chat_response(history, user_message, resume_data=None):
        try:
            history_text = "\n".join([f"User: {msg['user']}\nAI: {msg['ai']}" for msg in history])
            resume_context = f"\nHere is my resume data: {resume_data}" if resume_data else ""
            prompt = f"You are a helpful career copilot. Here is the conversation so far:\n{history_text}\nUser: {user_message}{resume_context}\nAI:"
            llm = MCPClient()
            response = llm.ping(prompt)
            return response.strip()
        except Exception as e:
            return f"Sorry, I couldn't process your request. ({e})"

    # Chat input
    with st.form("chat_form", clear_on_submit=True):
        user_message = st.text_input("Type your question or message...", key="chat_input")
        submitted = st.form_submit_button("Send")
        if submitted and user_message:
            with st.spinner("Copilot is typing..."):
                ai_response = get_chat_response(
                    st.session_state.chat_history,
                    user_message,
                    st.session_state.chat_resume_data
                )
            st.session_state.chat_history.append({"user": user_message, "ai": ai_response})

    # Chat UI (messenger style, always after input for real-time feel)
    st.markdown('<div style="background:#23283a;border-radius:12px;padding:1.5em 1em;min-height:250px;max-height:350px;overflow-y:auto;">', unsafe_allow_html=True)
    for msg in st.session_state.chat_history:
        st.markdown(f'''<div style="display:flex;align-items:flex-end;margin-bottom:1.2em;">
            <div style="background:#2563eb;color:#fff;padding:0.7em 1.2em;border-radius:18px 18px 4px 18px;max-width:70%;margin-right:auto;font-size:1.08em;box-shadow:0 2px 8px #0002;">{msg['user']}</div>
        </div>''', unsafe_allow_html=True)
        st.markdown(f'''<div style="display:flex;align-items:flex-end;margin-bottom:1.2em;justify-content:flex-end;">
            <div style="background:#23283a;color:#7f53ac;padding:0.7em 1.2em;border-radius:18px 18px 18px 4px;max-width:70%;margin-left:auto;font-size:1.08em;box-shadow:0 2px 8px #0002;">{msg['ai']}</div>
        </div>''', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

    col1, col2 = st.columns([1, 1])
    with col1:
        st.button("Back", on_click=lambda: go_to_step(4))
    with col2:
        if st.button("Clear Chat"):
            st.session_state.chat_history = []
    st.markdown('</div>', unsafe_allow_html=True)

# --- Enhanced Footer ---
st.markdown('''
    <div class="footer">
        <div style="margin-bottom: 1rem;">
            <strong>AI Intern Copilot</strong> - Your intelligent job search companion
        </div>
        <div style="font-size: 0.9rem; color: #64748b;">
            Made with ❤️ using Streamlit • Powered by AI • 
            <a href="#" style="color: #3b82f6; text-decoration: none;">Privacy Policy</a> • 
            <a href="#" style="color: #3b82f6; text-decoration: none;">Terms of Service</a>
        </div>
    </div>
''', unsafe_allow_html=True)