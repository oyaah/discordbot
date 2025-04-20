import os
from dotenv import load_dotenv
from crew import run_job_scraping

# Load environment variables
load_dotenv()

if __name__ == "__main__":
    # Run job scraping once, which will post all the fake data to Discord
    print("Running job scraping with fake data...")
    run_job_scraping()
    print("Process completed!")