import fitz  # PyMuPDF
import re
from cohere import Client as CohereClient


class ResumeParser:
    def __init__(self, cohere_api_key=None):
        self.cohere = CohereClient(api_key=cohere_api_key) if cohere_api_key else None

    def extract_text(self, pdf_path):
        doc = fitz.open(pdf_path)
        text = "\n".join(page.get_text() for page in doc)
        doc.close()
        return text

    def extract_name(self, text):
        lines = text.splitlines()
        for line in lines[:5]:
            if line.strip() and len(line.strip().split()) <= 4:
                return line.strip()
        return ""

    def extract_email(self, text):
        match = re.search(r"[\w\.-]+@[\w\.-]+", text)
        return match.group(0) if match else ""

    def extract_phone(self, text):
        match = re.search(r"(?:\+\d{1,3}[\s-]?)?\(?\d{3}\)?[\s.-]?\d{3}[\s.-]?\d{4}", text)
        return match.group(0) if match else ""

    def extract_skills(self, text):
        skills_keywords = ["Python", "Java", "SQL", "Machine Learning", "Data Analysis", "AWS", "React"]
        found = [skill for skill in skills_keywords if skill.lower() in text.lower()]
        return found

    def extract_summary_with_llm(self, text):
        if not self.cohere:
            return "LLM not configured."
        response = self.cohere.chat(
            model="command-r-plus",
            message=f"Extract a short professional summary and key highlights from the following resume:\n{text}"
        )
        return response.text

    def parse(self, pdf_path):
        text = self.extract_text(pdf_path)
        return {
            "name": self.extract_name(text),
            "email": self.extract_email(text),
            "phone": self.extract_phone(text),
            "skills": self.extract_skills(text),
            "summary": self.extract_summary_with_llm(text) if self.cohere else "(summary disabled)"
        }


if __name__ == "__main__":
    parser = ResumeParser(cohere_api_key="YOUR_COHERE_API_KEY")
    result = parser.parse("sample_resume.pdf")
    for key, value in result.items():
        print(f"{key.capitalize()}: {value}\n")
