# main.py
from modules.resume_parser import ResumeParser
#from modules.job_search import suggest_jobs
from llm_client import MCPClient

def main():
    print("🧠 Welcome to AI Intern Copilot (Terminal Edition)")
    print("---------------------------------------------------")
    file_path = input("📄 Enter the path to your resume PDF: ").strip()

    try:
        parser = ResumeParser()
        extracted_data = parser.parse(file_path)

        print("\n📋 Extracted Resume Info:")
        for key, value in extracted_data.items():
            print(f" - {key}: {value}")

        llm = MCPClient()
        prompt = f"Suggest 5 job roles based on this resume:\n{extracted_data}"
        response = llm.ping(prompt)

        print("\n🤖 AI Job Suggestions:")
        print(response)

    except Exception as e:
        print("❌ Error:", e)

if __name__ == "__main__":
    main()
