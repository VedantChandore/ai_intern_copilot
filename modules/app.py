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
    {"icon": "📊", "label": "Analytics", "desc": "Track progress"}
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
    st.markdown('<div class="section-card fade-in">', unsafe_allow_html=True)
    st.markdown('''
        <div class="section-header">
            <div class="section-icon">📄</div>
            <div>
                <div class="section-title">Upload Your Resume</div>
                <div class="section-desc">Upload your PDF resume to get started with personalized job recommendations</div>
            </div>
        </div>
    ''', unsafe_allow_html=True)
    
    # Create upload area
    st.markdown('<div class="upload-area">', unsafe_allow_html=True)
    uploaded_file = st.file_uploader(
        "Choose your resume file", 
        type=["pdf"], 
        key="resume_upload",
        help="Upload a PDF file of your resume (max 10MB)"
    )
    st.markdown('</div>', unsafe_allow_html=True)
    
    resume_data = None
    if uploaded_file is not None:
        st.success("✅ File uploaded successfully!")
        
        # File preview
        file_size_mb = uploaded_file.size / (1024 * 1024)
        st.markdown(f'''
            <div class="file-preview">
                <span style="font-size: 1.2rem;">📄</span>
                <div>
                    <strong>{uploaded_file.name}</strong><br>
                    <small>{file_size_mb:.2f} MB • PDF Document</small>
                </div>
            </div>
        ''', unsafe_allow_html=True)
        
        # Parse resume
        parser = ResumeParser()
        with st.spinner("🔍 Analyzing your resume..."):
            with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_file:
                tmp_file.write(uploaded_file.read())
                tmp_file_path = tmp_file.name
            result = parser.parse(tmp_file_path)
            resume_data = result
        
        st.session_state.resume_data = resume_data
        
        # Show parsed data preview
        with st.expander("📋 Resume Analysis Preview", expanded=False):
            if resume_data:
                st.markdown("**Extracted Information:**")
                st.text_area("Resume Content", value=str(resume_data)[:500] + "...", height=150, disabled=True)
        
        col1, col2 = st.columns([1, 1])
        with col2:
            if st.button("Next: Get AI Suggestions →", key="next_step1"):
                go_to_step(1)
                st.rerun()
    
    st.markdown('</div>', unsafe_allow_html=True)

# --- Step 2: AI Job Suggestions ---
elif st.session_state.step == 1:
    st.markdown('<div class="section-card fade-in">', unsafe_allow_html=True)
    st.markdown('''
        <div class="section-header">
            <div class="section-icon">💡</div>
            <div>
                <div class="section-title">AI-Powered Job Suggestions</div>
                <div class="section-desc">Get personalized job role recommendations based on your resume analysis</div>
            </div>
        </div>
    ''', unsafe_allow_html=True)
    
    resume_data = st.session_state.get("resume_data", None)
    
    if not resume_data:
        st.warning("⚠️ Please upload your resume in Step 1 first.")
        col1, col2 = st.columns([1, 1])
        with col1:
            if st.button("← Back to Upload", key="back_to_upload"):
                go_to_step(0)
                st.rerun()
    else:
        # Generate suggestions
        if st.button("🤖 Generate Job Suggestions", key="generate_suggestions"):
            with st.spinner("🧠 AI is analyzing your profile and generating suggestions..."):
                llm = MCPClient()
                prompt = f"""
                Based on this resume data, suggest 5 specific job roles that would be perfect matches.
                For each role, provide:
                1. Job title
                2. Why it's a good match
                3. Key skills to highlight
                4. Salary range expectation
                
                Resume data: {resume_data}
                """
                suggestions = llm.ping(prompt)
            
            st.success("🎯 Here are your personalized job recommendations:")
            
            # Display suggestions in a nice format
            suggestions_html = suggestions.replace('\n', '<br>')
            st.markdown(f'''
                <div style="
                    background: linear-gradient(135deg, rgba(59, 130, 246, 0.1) 0%, rgba(139, 92, 246, 0.1) 100%);
                    border: 1px solid rgba(59, 130, 246, 0.3);
                    border-radius: 16px;
                    padding: 2rem;
                    margin: 1rem 0;
                    line-height: 1.8;
                ">
                    {suggestions_html}
                </div>
            ''', unsafe_allow_html=True)
            
            st.session_state.job_suggestions = suggestions
        
        # Show cached suggestions if available
        if "job_suggestions" in st.session_state:
            st.markdown("### 💼 Your Job Recommendations")
            cached_suggestions_html = st.session_state.job_suggestions.replace('\n', '<br>')
            st.markdown(f'''
                <div style="
                    background: linear-gradient(135deg, rgba(59, 130, 246, 0.1) 0%, rgba(139, 92, 246, 0.1) 100%);
                    border: 1px solid rgba(59, 130, 246, 0.3);
                    border-radius: 16px;
                    padding: 2rem;
                    margin: 1rem 0;
                    line-height: 1.8;
                ">
                    {cached_suggestions_html}
                </div>
            ''', unsafe_allow_html=True)
        
        # Navigation buttons
        col1, col2 = st.columns([1, 1])
        with col1:
            if st.button("← Back", key="back_step2", help="Go back to resume upload"):
                go_to_step(0)
                st.rerun()
        with col2:
            if st.button("Next: Search Jobs →", key="next_step2"):
                go_to_step(2)
                st.rerun()
    
    st.markdown('</div>', unsafe_allow_html=True)

# --- Step 3: Automated Job Search ---
elif st.session_state.step == 2:
    st.markdown('<div class="section-card fade-in">', unsafe_allow_html=True)
    st.markdown('''
        <div class="section-header">
            <div class="section-icon">🔎</div>
            <div>
                <div class="section-title">Automated Job Search</div>
                <div class="section-desc">Search for jobs across multiple platforms with intelligent automation</div>
            </div>
        </div>
    ''', unsafe_allow_html=True)
    
    # Search parameters
    col1, col2 = st.columns(2)
    with col1:
        job_title = st.text_input(
            "🎯 Job Title", 
            value="Software Developer Intern", 
            key="job_title",
            help="Enter the job title you're looking for"
        )
    with col2:
        job_location = st.text_input(
            "📍 Location", 
            value="Remote", 
            key="job_location",
            help="Enter your preferred location or 'Remote'"
        )
    
    # Additional filters
    with st.expander("🔧 Advanced Search Options", expanded=False):
        col3, col4 = st.columns(2)
        with col3:
            experience_level = st.selectbox(
                "Experience Level",
                ["Entry Level", "Internship", "Mid Level", "Senior Level"],
                index=1
            )
        with col4:
            job_type = st.selectbox(
                "Job Type",
                ["Full-time", "Part-time", "Internship", "Contract"],
                index=2
            )
    
    # Search button
    if st.button("🚀 Start Job Search", key="search_jobs"):
        with st.spinner("🔍 Searching across multiple job platforms..."):
            try:
                from modules.job_search import JobSearchPlaywrightHandler
                handler = JobSearchPlaywrightHandler()
                result = handler.handle('search', query=job_title, location=job_location)
                
                # Generate search URLs
                indeed_url = f"https://www.indeed.com/jobs?q={'+'.join(job_title.split())}&l={'+'.join(job_location.split())}"
                linkedin_url = f"https://www.linkedin.com/jobs/search/?keywords={'+'.join(job_title.split())}&location={'+'.join(job_location.split())}"
                glassdoor_url = f"https://www.glassdoor.com/Job/jobs.htm?sc.keyword={'+'.join(job_title.split())}&locT=&locId="
                
                st.success("✅ Job search completed successfully!")
                
                # Display search results
                st.markdown("### 🌐 Search Results")
                
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    st.markdown(f'''
                        <div style="
                            background: linear-gradient(135deg, rgba(59, 130, 246, 0.1) 0%, rgba(37, 99, 235, 0.1) 100%);
                            border: 1px solid rgba(59, 130, 246, 0.3);
                            border-radius: 12px;
                            padding: 1.5rem;
                            text-align: center;
                        ">
                            <div style="font-size: 2rem; margin-bottom: 0.5rem;">🔵</div>
                            <strong>Indeed</strong><br>
                            <a href="{indeed_url}" target="_blank" style="color: #3b82f6; text-decoration: none;">
                                View Jobs →
                            </a>
                        </div>
                    ''', unsafe_allow_html=True)
                
                with col2:
                    st.markdown(f'''
                        <div style="
                            background: linear-gradient(135deg, rgba(59, 130, 246, 0.1) 0%, rgba(37, 99, 235, 0.1) 100%);
                            border: 1px solid rgba(59, 130, 246, 0.3);
                            border-radius: 12px;
                            padding: 1.5rem;
                            text-align: center;
                        ">
                            <div style="font-size: 2rem; margin-bottom: 0.5rem;">💼</div>
                            <strong>LinkedIn</strong><br>
                            <a href="{linkedin_url}" target="_blank" style="color: #3b82f6; text-decoration: none;">
                                View Jobs →
                            </a>
                        </div>
                    ''', unsafe_allow_html=True)
                
                with col3:
                    st.markdown(f'''
                        <div style="
                            background: linear-gradient(135deg, rgba(59, 130, 246, 0.1) 0%, rgba(37, 99, 235, 0.1) 100%);
                            border: 1px solid rgba(59, 130, 246, 0.3);
                            border-radius: 12px;
                            padding: 1.5rem;
                            text-align: center;
                        ">
                            <div style="font-size: 2rem; margin-bottom: 0.5rem;">🏢</div>
                            <strong>Glassdoor</strong><br>
                            <a href="{glassdoor_url}" target="_blank" style="color: #3b82f6; text-decoration: none;">
                                View Jobs →
                            </a>
                        </div>
                    ''', unsafe_allow_html=True)
                
                st.info(f"🎯 Search completed for: **{job_title}** in **{job_location}**")
                
            except Exception as e:
                st.error(f"❌ Search failed: {str(e)}")
    
    # Navigation buttons
    col1, col2 = st.columns([1, 1])
    with col1:
        if st.button("← Back", key="back_step3"):
            go_to_step(1)
            st.rerun()
    with col2:
        if st.button("Next: Auto Apply →", key="next_step3"):
            go_to_step(3)
            st.rerun()
    
    st.markdown('</div>', unsafe_allow_html=True)

# --- Step 4: Automated Job Application ---
elif st.session_state.step == 3:
    st.markdown('<div class="section-card fade-in">', unsafe_allow_html=True)
    st.markdown('''
        <div class="section-header">
            <div class="section-icon">🤖</div>
            <div>
                <div class="section-title">Automated Job Application</div>
                <div class="section-desc">Let AI handle your job applications with intelligent form filling</div>
            </div>
        </div>
    ''', unsafe_allow_html=True)
    
    # Warning notice
    st.markdown('''
        <div style="
            background: linear-gradient(135deg, rgba(245, 158, 11, 0.1) 0%, rgba(217, 119, 6, 0.1) 100%);
            border: 1px solid rgba(245, 158, 11, 0.3);
            border-radius: 12px;
            padding: 1.5rem;
            margin: 1rem 0;
        ">
            <strong>⚠️ Experimental Feature</strong><br>
            This feature automatically fills job application forms. Please review all information before submitting.
        </div>
    ''', unsafe_allow_html=True)
    
    # Application URL input
    job_url = st.text_input(
        "🔗 Job Application URL",
        key="job_url",
        placeholder="https://company.com/careers/apply/job-id",
        help="Paste the direct link to the job application form"
    )
    
    # Application settings
    with st.expander("⚙️ Application Settings", expanded=False):
        col1, col2 = st.columns(2)
        with col1:
            auto_submit = st.checkbox("Auto-submit application", value=False)
            cover_letter = st.checkbox("Generate cover letter", value=True)
        with col2:
            follow_up = st.checkbox("Set follow-up reminder", value=True)
            save_application = st.checkbox("Save to database", value=True)
    
    # Apply button
    resume_data = st.session_state.get("resume_data", None)
    
    if st.button("🚀 Start Auto Application", key="auto_apply"):
        if not resume_data:
            st.warning("⚠️ Please upload and parse your resume first (Step 1).")
        elif not job_url:
            st.warning("⚠️ Please enter a job application URL.")
        else:
            with st.spinner("🤖 AI is filling out your job application..."):
                try:
                    from modules.application import JobApplicationBot
                    bot = JobApplicationBot(resume_data)
                    apply_result = bot.apply_to_job(job_url)
                    
                    st.success("✅ Application process completed!")
                    
                    # Show application summary
                    st.markdown("### 📋 Application Summary")
                    st.markdown(f'''
                        <div style="
                            background: linear-gradient(135deg, rgba(16, 185, 129, 0.1) 0%, rgba(5, 150, 105, 0.1) 100%);
                            border: 1px solid rgba(16, 185, 129, 0.3);
                            border-radius: 12px;
                            padding: 1.5rem;
                            margin: 1rem 0;
                        ">
                            <strong>Application Status:</strong> {apply_result}<br>
                            <strong>URL:</strong> {job_url}<br>
                            <strong>Timestamp:</strong> {pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S')}
                        </div>
                    ''', unsafe_allow_html=True)
                    
                    # Save to database if enabled
                    if save_application:
                        conn = sqlite3.connect('job_applications.db')
                        c = conn.cursor()
                        c.execute('''CREATE TABLE IF NOT EXISTS applications
                                     (date TEXT, job_title TEXT, company TEXT, job_url TEXT, status TEXT)''')
                        
                        # Extract job title and company from URL (simplified)
                        job_title_extracted = job_url.split('/')[-1].replace('-', ' ').title()
                        company_extracted = job_url.split('/')[2].split('.')[0].title()
                        
                        c.execute("INSERT INTO applications VALUES (?, ?, ?, ?, ?)",
                                (pd.Timestamp.now().strftime('%Y-%m-%d'), 
                                 job_title_extracted, 
                                 company_extracted, 
                                 job_url, 
                                 "Applied"))
                        conn.commit()
                        conn.close()
                        
                        st.info("💾 Application saved to your database.")
                    
                except Exception as e:
                    st.error(f"❌ Application failed: {str(e)}")
                    st.info("💡 Tip: Make sure the URL is a direct link to an application form.")
    
    # Recent applications
    if st.checkbox("Show Recent Applications", value=False):
        try:
            conn = sqlite3.connect('job_applications.db')
            recent_apps = pd.read_sql_query(
                'SELECT * FROM applications ORDER BY date DESC LIMIT 5', 
                conn
            )
            conn.close()
            
            if not recent_apps.empty:
                st.markdown("### 📝 Recent Applications")
                st.dataframe(recent_apps, use_container_width=True)
            else:
                st.info("No recent applications found.")
        except:
            st.info("No application history available.")
    
    # Navigation buttons
    col1, col2 = st.columns([1, 1])
    with col1:
        if st.button("← Back", key="back_step4"):
            go_to_step(2)
            st.rerun()
    with col2:
        if st.button("Next: Analytics →", key="next_step4"):
            go_to_step(4)
            st.rerun()
    
    st.markdown('</div>', unsafe_allow_html=True)

# --- Step 5: Analytics & Insights ---
elif st.session_state.step == 4:
    st.markdown('<div class="section-card fade-in">', unsafe_allow_html=True)
    st.markdown('''
        <div class="section-header">
            <div class="section-icon">📊</div>
            <div>
                <div class="section-title">Analytics & Insights</div>
                <div class="section-desc">Track your job search progress with comprehensive analytics</div>
            </div>
        </div>
    ''', unsafe_allow_html=True)
    
    # Initialize database
    conn = sqlite3.connect('job_applications.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS applications
                 (date TEXT, job_title TEXT, company TEXT, job_url TEXT, status TEXT)''')
    conn.commit()
    
    # Load data
    try:
        df = pd.read_sql_query('SELECT * FROM applications', conn)
        conn.close()
        
        if not df.empty:
            # Convert date column
            df['date'] = pd.to_datetime(df['date'])
            
            # Key metrics
            st.markdown("### 📈 Key Metrics")
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric(
                    label="Total Applications",
                    value=len(df),
                    delta=f"+{len(df[df['date'] >= pd.Timestamp.now() - pd.Timedelta(days=7)])}" if len(df) > 0 else None
                )
            
            with col2:
                st.metric(
                    label="Unique Companies",
                    value=df["company"].nunique(),
                    delta=None
                )
            
            with col3:
                st.metric(
                    label="Job Categories",
                    value=df["job_title"].nunique(),
                    delta=None
                )
            
            with col4:
                success_rate = len(df[df['status'].str.contains('Success|Applied', case=False, na=False)]) / len(df) * 100
                st.metric(
                    label="Success Rate",
                    value=f"{success_rate:.1f}%",
                    delta=None
                )
            
            # Charts
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("### 📊 Applications by Company")
                company_counts = df['company'].value_counts().head(10)
                st.bar_chart(company_counts)
            
            with col2:
                st.markdown("### 🎯 Applications by Job Title")
                job_counts = df['job_title'].value_counts().head(10)
                st.bar_chart(job_counts)
            
            # Timeline
            st.markdown("### 📅 Application Timeline")
            daily_apps = df.groupby(df['date'].dt.date).size()
            st.line_chart(daily_apps)
            
            # Recent applications table
            st.markdown("### 📝 Recent Applications")
            recent_df = df.sort_values('date', ascending=False).head(10)
            st.dataframe(
                recent_df[['date', 'job_title', 'company', 'status']], 
                use_container_width=True,
                hide_index=True
            )
            
            # Export data
            if st.button("📥 Export Data", key="export_data"):
                csv = df.to_csv(index=False)
                st.download_button(
                    label="Download CSV",
                    data=csv,
                    file_name=f"job_applications_{pd.Timestamp.now().strftime('%Y%m%d')}.csv",
                    mime="text/csv"
                )
        
        else:
            # Empty state
            st.markdown('''
                <div style="
                    text-align: center;
                    padding: 3rem;
                    color: #64748b;
                ">
                    <div style="font-size: 4rem; margin-bottom: 1rem;">📊</div>
                    <h3>No Application Data Yet</h3>
                    <p>Start applying to jobs to see your analytics here!</p>
                </div>
            ''', unsafe_allow_html=True)
            
            # Sample data button for demo
            if st.button("📊 Generate Sample Data", key="sample_data"):
                sample_data = [
                    ('2024-01-15', 'Software Developer Intern', 'Google', 'https://google.com/careers', 'Applied'),
                    ('2024-01-16', 'Frontend Developer', 'Microsoft', 'https://microsoft.com/careers', 'Applied'),
                    ('2024-01-17', 'Data Analyst Intern', 'Amazon', 'https://amazon.com/careers', 'Applied'),
                    ('2024-01-18', 'Product Manager Intern', 'Meta', 'https://meta.com/careers', 'Applied'),
                    ('2024-01-19', 'UX Designer Intern', 'Apple', 'https://apple.com/careers', 'Applied'),
                ]
                
                conn = sqlite3.connect('job_applications.db')
                c = conn.cursor()
                c.executemany("INSERT INTO applications VALUES (?, ?, ?, ?, ?)", sample_data)
                conn.commit()
                conn.close()
                
                st.success("✅ Sample data generated! Refresh to see analytics.")
                st.rerun()
    
    except Exception as e:
        st.error(f"❌ Error loading analytics: {str(e)}")
    
    # Navigation
    col1, col2 = st.columns([1, 1])
    with col1:
        if st.button("← Back", key="back_step5"):
            go_to_step(3)
            st.rerun()
    with col2:
        if st.button("🔄 Refresh Data", key="refresh_analytics"):
            st.rerun()
    
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