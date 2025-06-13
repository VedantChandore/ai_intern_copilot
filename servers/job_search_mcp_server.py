from mcp import MCPHandler, run_mcp_server
from playwright.sync_api import sync_playwright

class JobSearchHandler(MCPHandler):
    def handle(self, request):
        query = request.get("query", "")
        location = request.get("location", "")
        search_query = f"{query} jobs in {location}".strip()

        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()
            page.goto(f"https://www.google.com/search?q={search_query}")
            page.wait_for_timeout(3000)
            html = page.content()
            browser.close()

        return {"html": html[:1000]}  # Truncate for display or parse as needed

if __name__ == "__main__":
    run_mcp_server(JobSearchHandler, port=4000)
