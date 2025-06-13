from modules.job_search import JobSearchPlaywrightHandler
from modules.application import JobApplicationBot
from mcp import run_mcp_server, MCPHandler

class PlaywrightServerHandler(MCPHandler):
    def handle(self, request):
        action = request.get('action')
        if action == 'job_search':
            query = request.get('query', 'software developer')
            location = request.get('location', 'India')
            return JobSearchPlaywrightHandler().handle('search', query=query, location=location)
        elif action == 'apply_job':
            job_url = request.get('job_url')
            resume_data = request.get('resume_data', {})
            job_title = request.get('job_title')
            company = request.get('company')
            bot = JobApplicationBot(resume_data)
            return bot.apply_to_job(job_url, job_title, company)
        else:
            return {'error': 'Unknown action'}

if __name__ == "__main__":
    run_mcp_server(PlaywrightServerHandler, port=5000)
