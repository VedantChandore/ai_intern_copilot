import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from config import SMTP_USER, SMTP_PASSWORD
from llm_client import MCPClient

class EmailFollowUp:
    def __init__(self):
        self.llm = MCPClient()

    def generate_followup(self, job_title, company, recipient_name=None):
        prompt = f"Write a polite follow-up email for a job application to '{job_title}' at '{company}'."
        if recipient_name:
            prompt += f" Address it to {recipient_name}."
        return self.llm.ping(prompt)

    def send_email(self, to_email, subject, body):
        msg = MIMEMultipart()
        msg['From'] = SMTP_USER
        msg['To'] = to_email
        msg['Subject'] = subject
        msg.attach(MIMEText(body, 'plain'))
        try:
            with smtplib.SMTP('smtp.gmail.com', 587) as server:
                server.starttls()
                server.login(SMTP_USER, SMTP_PASSWORD)
                server.send_message(msg)
            return True
        except Exception as e:
            print(f"Failed to send email: {e}")
            return False

# Example usage:
# efu = EmailFollowUp()
# body = efu.generate_followup('Software Engineer', 'ExampleCorp', 'Jane Doe')
# efu.send_email('recruiter@example.com', 'Follow-up on Job Application', body)
