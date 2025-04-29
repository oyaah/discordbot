from crewai import Agent
from tools import LinkedInScraperTool,JobDataProcessorTool,DiscordFormatterTool
from discord_bot import DiscordPublisherTool
from dotenv import load_dotenv

from crewai import LLM

llm = LLM(
    model="groq/llama-3.2-90b-text-preview",
    temperature=0.7,
    api_key='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'
)

## creating the linkedin scraper agent 

scraper=Agent(
        role="LinkedIn Job Scraper",
        goal="Collect comprehensive data science and ML engineering job listings from LinkedIn",
        backstory=(
            "You are an expert web scraper specialized in navigating LinkedIn to find the best "
            "job opportunities in data science and machine learning fields. Your mission is to "
            "collect detailed information about available positions."
        ),
        verbose=True,
        allow_delegation=False,
        tools=[LinkedInScraperTool()],
        
        llm=llm
)
    
## creating the data processor agent   
processor=Agent(
        role="Job Data Processor",
        goal="Process and enhance raw job data to extract valuable insights",
        backstory=(
            "You are a data scientist with expertise in natural language processing. "
            "Your job is to clean job listings data, remove duplicates, and extract key "
            "information like required skills, experience level, and job categories."
        ),
        verbose=True,
        allow_delegation=False,
        tools=[JobDataProcessorTool()],
        llm=llm
    )
formatter=Agent(
        role="Discord Content Formatter",
        goal="Create engaging and informative Discord posts from job data",
        backstory=(
            "You are a content specialist who knows how to present information in the most "
            "engaging way possible. You transform dry job listings into exciting opportunities "
            "that will catch the attention of Discord users looking for their next career move."
        ),
        verbose=True,
        allow_delegation=False,
        tools=[DiscordFormatterTool()],
        llm=llm
    )

publisher=Agent(
        role="Discord Publisher",
        goal="Post job listings to Discord in an organized and timely manner",
        backstory=(
            "You are a communication expert who understands the Discord platform inside and out. "
            "Your job is to ensure that formatted job listings reach the right audience at the "
            "right time, maintaining engagement without spamming."
        ),
        verbose=True,
        allow_delegation=False,
        tools=[DiscordPublisherTool()],
        llm=llm
    )


orchestrator=Agent(
        role="Orchestrator",
        goal="Coordinate the entire job scraping and posting workflow",
        backstory=(
            "You are the project manager who oversees the entire job discovery pipeline. "
            "Your expertise lies in coordinating multiple specialized agents, handling exceptions, "
            "and ensuring the system runs smoothly to deliver valuable job opportunities."
        ),
        verbose=True,
        allow_delegation=True,
        llm=llm
    )
