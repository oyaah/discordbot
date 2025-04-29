# test_scraper.py
from tools import LinkedInScraperTool

tool = LinkedInScraperTool()
result = tool._run("data scientist", "", 5)
print(f"Result length: {len(result)}")
print(f"Result sample: {result[:200]}")

with open("test_scrape.json", "w") as f:
    f.write(result)