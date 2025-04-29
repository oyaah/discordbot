
from crewai import Task
from typing import List
from agents import scraper,formatter,publisher,orchestrator,processor 

scraping_task=Task(
        description=(
            "Search LinkedIn for data science and machine learning engineering jobs. "
            "Use the following keywords: 'data scientist, machine learning engineer, ML engineer, "
            "AI engineer, data engineer, NLP engineer, computer vision engineer'. "
            "Focus on recent postings within the last week. Limit to 30 results total."
        ),
        agent=scraper,
        expected_output="A comprehensive list of job listings with titles, companies, locations, and URLs."
    )
processing_task=Task(
        description=(
            "Process the raw job listings data. Remove duplicates, extract key skills from job descriptions, "
            "categorize jobs by seniority level, and filter out any irrelevant listings. "
            "Make sure to identify and extract salary information when available, "
            "and properly format requirements as bullet points."
        ),
        agent=processor,
        expected_output="A processed list of job listings with additional metadata and categorization."
    )
formatiing_task=Task(
        description=(
            "Format the processed job listings for Discord. Create engaging messages with proper "
            "formatting, emojis, and organization. Include job title, company, location (with remote indicator), "
            "requirements, salary information (if available), level, and application link. "
            "Ensure all important information is included and formatting is Discord-friendly."
        ),
        agent=formatter,
        expected_output="A list of Discord-ready formatted messages for each job listing."
    )
publisher_task=Task(
        description=(
            "Post the formatted job listings to the Discord channel. Ensure proper spacing "
            "between posts and avoid hitting rate limits. Track which jobs have been posted."
        ),
        agent=publisher,
        expected_output="Confirmation that jobs have been successfully posted to Discord."
    )
orchestration_task=Task(
        description=(
            "Oversee the entire workflow from scraping to publishing. Handle any errors or "
            "exceptions that arise. Provide a summary report of the operation including number "
            "of jobs found, processed, and posted."
        ),
        agent=orchestrator,
        expected_output="A summary report of the entire operation with metrics and status."
    )

