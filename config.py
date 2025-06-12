import os
from dotenv import load_dotenv

load_dotenv()

# Gemini-specific API key
OPENAI_API_KEY = os.getenv("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")
LLM_MODEL = os.getenv("LLM_MODEL", "gpt-4o")
# Email creds
SMTP_USER = os.getenv("vedant.chandore24@vit.edu")
SMTP_PASSWORD = os.getenv("12420260")