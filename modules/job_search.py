# servers/job_search_playwright_mcp.py
from mcp import MCPHandler, run_mcp_server
from playwright.sync_api import sync_playwright

class JobSearchPlaywrightHandler(MCPHandler):
    def handle(self, command: str, **kwargs):
        query = kwargs.get("query", "software developer")
        location = kwargs.get("location", "India")

        search_query = f"{query} jobs in {location}"
        indeed_url = f"https://www.indeed.com/jobs?q={'+'.join(query.split())}&l={'+'.join(location.split())}"
        linkedin_url = f"https://www.linkedin.com/jobs/search/?keywords={'+'.join(query.split())}&location={'+'.join(location.split())}"

        with sync_playwright() as p:
            browser = p.chromium.launch(headless=False)  # Visible browser
            page = browser.new_page()
            page.goto(indeed_url)
            print("✅ Opened Indeed:", indeed_url)

            page2 = browser.new_page()
            page2.goto(linkedin_url)
            print("✅ Opened LinkedIn:", linkedin_url)

            return f"Opened job searches for '{query}' in '{location}' on Indeed and LinkedIn."

if __name__ == "__main__":
    run_mcp_server(JobSearchPlaywrightHandler())
