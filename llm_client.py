import cohere

# 🔑 Hardcoded API key and model
COHERE_API_KEY = "T3bIAXUjZNYPmBKHxKUbqo4bLdkzQauShDkzfr6Y"  # Replace with your actual Cohere API key
LLM_MODEL = "command-r-plus"  # Other options: "command-r", "command-light", etc.

class MCPClient:
    def __init__(self):
        self.client = cohere.Client(COHERE_API_KEY)
        print(f"✅ Cohere client initialized using model: {LLM_MODEL}")

    def ping(self, prompt: str):
        print("📨 Sending prompt to Cohere...")
        try:
            response = self.client.chat(
                model=LLM_MODEL,
                message=prompt,
            )
            print("✅ Response received")
            return response.text
        except Exception as e:
            print("❌ Error:", str(e))
            return "Failed to get response."

if __name__ == "__main__":
    client = MCPClient()
    reply = client.ping("Hello AI Intern Copilot, are you ready to help me?")
    print("🤖 AI says:", reply)
