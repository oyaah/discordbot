import os
import json
from dotenv import load_dotenv
from tools import LinkedInScraperTool, JobDataProcessorTool, DiscordFormatterTool
from json_utils import load_jobs_from_json, load_formatted_messages_from_json

# Load environment variables
load_dotenv()

def run_linkedin_scraper(keywords="data scientist, machine learning engineer", location="", limit=10):
    """Run the LinkedIn scraper tool and return the results"""
    print(f"Scraping LinkedIn for jobs with keywords: {keywords}")
    tool = LinkedInScraperTool()
    result = tool._run(keywords, location, limit)
    print("LinkedIn scraping completed!")
    return result

def process_job_data(jobs_data):
    """Process the job data and return the results"""
    print("Processing job data...")
    tool = JobDataProcessorTool()
    result = tool._run(jobs_data)
    print("Job data processing completed!")
    return result

def format_for_discord(processed_jobs):
    """Format the processed jobs for Discord and return the results"""
    print("Formatting jobs for Discord...")
    tool = DiscordFormatterTool()
    result = tool._run(processed_jobs)
    print("Formatting completed!")
    return result

def display_sample_message(formatted_messages_json):
    """Display a sample formatted message"""
    try:
        messages = json.loads(formatted_messages_json)
        if messages:
            print("\n==== SAMPLE FORMATTED MESSAGE ====\n")
            print(messages[0])
            print("\n=================================\n")
    except Exception as e:
        print(f"Error displaying sample message: {e}")

def run_full_pipeline():
    """Run the full pipeline from scraping to formatting"""
    # Step 1: Scrape LinkedIn
    jobs_data = run_linkedin_scraper()
    
    # Step 2: Process job data
    processed_jobs = process_job_data(jobs_data)
    
    # Step 3: Format for Discord
    formatted_messages = format_for_discord(processed_jobs)
    
    # Display a sample of the formatted message
    display_sample_message(formatted_messages)
    
    print("\nAll steps completed successfully!")
    print("Check the generated JSON files in the job_data/ and message_data/ directories.")

def run_from_existing_data(filename="raw_jobs.json"):
    """Run the pipeline starting from existing JSON data"""
    try:
        # Load existing jobs data
        jobs = load_jobs_from_json(filename)
        jobs_data = json.dumps(jobs)
        
        # Process and format
        processed_jobs = process_job_data(jobs_data)
        formatted_messages = format_for_discord(processed_jobs)
        
        # Display a sample
        display_sample_message(formatted_messages)
        
        print("\nProcessing from existing data completed successfully!")
        
    except Exception as e:
        print(f"Error running from existing data: {e}")

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Run the LinkedIn job scraper locally")
    parser.add_argument("--from-file", "-f", help="Run from existing JSON file")
    parser.add_argument("--keywords", "-k", default="data scientist, machine learning engineer", 
                        help="Keywords for job search")
    parser.add_argument("--location", "-l", default="", 
                        help="Location for job search")
    parser.add_argument("--limit", "-n", type=int, default=10, 
                        help="Maximum number of jobs to scrape")
    
    args = parser.parse_args()
    
    if args.from_file:
        run_from_existing_data(args.from_file)
    else:
        run_full_pipeline()