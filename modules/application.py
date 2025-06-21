import time
from playwright.sync_api import sync_playwright
import sys
import os
import sqlite3
from datetime import datetime
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from llm_client import MCPClient
import tempfile

# --- Analytics Logging ---
def log_application(job_title, company, job_url, status='applied'):
    conn = sqlite3.connect('job_applications.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS applications
                 (date TEXT, job_title TEXT, company TEXT, job_url TEXT, status TEXT)''')
    c.execute('INSERT INTO applications VALUES (?, ?, ?, ?, ?)',
              (datetime.now().strftime('%Y-%m-%d'), job_title, company, job_url, status))
    conn.commit()
    conn.close()

class JobApplicationBot:
    def __init__(self, resume_data, cover_letter_template=None):
        self.resume_data = resume_data
        self.cover_letter_template = cover_letter_template
        self.llm = MCPClient()

    def generate_cover_letter(self, job_title, company):
        prompt = f"Write a short, professional cover letter for the job '{job_title}' at '{company}' based on this resume: {self.resume_data}"
        return self.llm.ping(prompt)

    def apply_to_job(self, job_url, job_title=None, company=None):
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=False)
            page = browser.new_page()
            page.goto(job_url)
            page.wait_for_load_state('networkidle')
            try:
                # Fill name, email, phone (selectors may need adjustment per actual form)
                if self.resume_data.get('name'):
                    try:
                        page.fill('input[name="firstName"]', self.resume_data.get('name', ''))
                    except:
                        pass
                if self.resume_data.get('email'):
                    try:
                        page.fill('input[name="email"]', self.resume_data.get('email', ''))
                    except:
                        pass
                if self.resume_data.get('phone'):
                    try:
                        page.fill('input[name="phone"]', self.resume_data.get('phone', ''))
                    except:
                        pass
                # Upload resume (if path is available)
                if self.resume_data.get('resume_path'):
                    try:
                        page.set_input_files('input[type="file"]', self.resume_data['resume_path'])
                    except:
                        pass
                # Cover letter (if field exists)
                if job_title and company:
                    cover_letter = self.generate_cover_letter(job_title, company)
                    try:
                        page.fill('textarea[name="coverLetter"]', cover_letter)
                    except:
                        pass  # Field may not exist
                # Try to click submit (button selector may vary)
                try:
                    page.click('button[type="submit"]')
                except:
                    pass
                time.sleep(2)
                browser.close()
                # Log the application for analytics
                log_application(job_title or '', company or '', job_url, status='applied')
                return f"Applied to {job_url} (automated, fields filled where possible)"
            except Exception as e:
                browser.close()
                return f"Failed to apply: {e}"

# Example usage:
# bot = JobApplicationBot(resume_data)
# bot.apply_to_job('https://career10.successfactors.com/careers?company=yashtechnoP', job_title='Software Engineer', company='YASH Technologies')
