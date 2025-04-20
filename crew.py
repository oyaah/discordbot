from crewai import Crew,Process
from agents import formatter,publisher,orchestrator,scraper,processor
from tasks import scraping_task,processing_task,formatiing_task,publisher_task,orchestration_task
crew=Crew(
    agents=[scraper,processor,formatter,publisher,orchestrator],
    tasks=[scraping_task,processing_task,formatiing_task,publisher_task,orchestration_task],
    process=Process.sequential,
    memory=True,
    cache=True,
    verbose=True


)

result=crew.kickoff()
print(result)
