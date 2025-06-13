# ai_intern_copilot

AI Intern Copilot is an AI-powered assistant to help students and job seekers parse resumes, get job suggestions, search and apply for jobs, and send follow-up emails—all automated with LLMs and browser automation.

## Features
- **Resume Parsing:** Extracts name, email, phone, skills, and summary from PDF resumes.
- **AI Job Suggestions:** Uses LLM to suggest job roles based on your resume.
- **Job Search Automation:** Opens job searches on Indeed, LinkedIn, and Google using Playwright.
- **Job Application Automation:** Autofills job application forms and generates cover letters.
- **Email Follow-Up:** Sends follow-up emails to recruiters/companies after applying.
- **Web UI:** Streamlit app for uploading resumes and viewing results.
- **Terminal UI:** CLI for resume parsing and job suggestions.

## Setup
1. Clone the repo and install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
2. Set up your `.env` file with API keys and email credentials (see `config.py`).
3. (Optional) Activate the virtual environment:
   ```bash
   source .venv/bin/activate
   ```

## Usage
- **Web App:**
  ```bash
  streamlit run modules/app.py
  ```
- **Terminal:**
  ```bash
  python main.py
  ```
- **Job Search/Apply Server:**
  ```bash
  python servers/playwright_server.py
  ```

## Extending
- Add more job boards or application logic in `modules/job_search.py` and `modules/application.py`.
- Customize email templates in `modules/email_followup.py`.

---
MIT License