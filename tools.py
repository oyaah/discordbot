from crewai.tools import BaseTool
from typing import List, Dict, Any, Optional
import pandas as pd
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
import json
import ast

# Import the fake data generator
from fake_data import get_fake_linkedin_jobs
# Import JSON utilities
from json_utils import save_jobs_to_json, save_formatted_messages_to_json

class LinkedInScraperTool(BaseTool):
    name = "LinkedIn Job Scraper"
    description = "Scrapes LinkedIn for data science and ML engineering jobs"
    
    def _run(self, keywords: str, location: str = "", limit: int = 30) -> str:
        """Get LinkedIn jobs based on keywords and location"""
        try:
            # Parse keywords
            keyword_list = [k.strip() for k in keywords.split(',')]
            
            # Get fake jobs for now
            jobs = get_fake_linkedin_jobs(keywords=keyword_list, count=limit)
            
            # Convert to dictionaries for easier serialization
            job_dicts = [job.to_dict() for job in jobs]
            
            # Save to JSON file
            json_file = save_jobs_to_json(job_dicts, "raw_jobs.json")
            print(f"Raw job data saved to {json_file}")
            
            return json.dumps(job_dicts)
            
        except Exception as e:
            return f"Error scraping LinkedIn jobs: {str(e)}"


class JobDataProcessorTool(BaseTool):
    name = "Job Data Processor"
    description = "Processes and filters raw job data"
    
    def _run(self, jobs_data: str) -> str:
        """Process and filter job listings"""
        try:
            # Parse the input data
            if isinstance(jobs_data, str):
                try:
                    jobs = json.loads(jobs_data)
                except:
                    # Try alternative parsing if JSON fails
                    jobs = ast.literal_eval(jobs_data)
            else:
                jobs = jobs_data
                
            # Create DataFrame
            df = pd.DataFrame(jobs)
            
            # Remove duplicates
            df = df.drop_duplicates(subset=['id'])
            
            # Extract salary information if not already present
            if 'description' in df.columns and 'salary' in df.columns:
                for idx, row in df.iterrows():
                    if row['salary'] == "Not mentioned" or row['salary'] == "Not specified":
                        description = row['description'].lower()
                        
                        # Look for salary patterns in description
                        if '$' in description or '€' in description or '£' in description:
                            # This is simplified - in a real implementation you'd use regex patterns
                            if '$' in description:
                                df.at[idx, 'salary'] = "Paid (see description for details)"
            
            # Further process the requirements if they're strings
            if 'requirements' in df.columns:
                for idx, row in df.iterrows():
                    if isinstance(row['requirements'], str):
                        try:
                            df.at[idx, 'requirements'] = ast.literal_eval(row['requirements'])
                        except:
                            # If parsing fails, keep as is
                            pass
            
            # Do the same for extracted_skills
            if 'extracted_skills' in df.columns:
                for idx, row in df.iterrows():
                    if isinstance(row['extracted_skills'], str):
                        try:
                            df.at[idx, 'extracted_skills'] = ast.literal_eval(row['extracted_skills'])
                        except:
                            # If parsing fails, keep as is
                            pass
            
            # If level is not specified, try to infer it from the title
            if 'level' in df.columns:
                for idx, row in df.iterrows():
                    if row['level'] == "Not specified":
                        title = row['title'].lower()
                        if 'senior' in title or 'sr' in title or 'lead' in title:
                            df.at[idx, 'level'] = 'Senior'
                        elif 'junior' in title or 'jr' in title:
                            df.at[idx, 'level'] = 'Junior'
                        else:
                            df.at[idx, 'level'] = 'Mid-level'
            
            # Convert back to list of dicts
            processed_jobs = df.to_dict('records')
            
            # Save to JSON file
            json_file = save_jobs_to_json(processed_jobs, "processed_jobs.json")
            print(f"Processed job data saved to {json_file}")
            
            return json.dumps(processed_jobs)
            
        except Exception as e:
            return f"Error processing job data: {str(e)}"


class DiscordFormatterTool(BaseTool):
    name = "Discord Content Formatter"
    description = "Formats job listings for Discord posting"
    
    def _run(self, processed_jobs: str) -> str:
        """Format jobs for Discord posting"""
        try:
            # Parse the input data
            if isinstance(processed_jobs, str):
                try:
                    jobs = json.loads(processed_jobs)
                except:
                    # Try alternative parsing if JSON fails
                    jobs = ast.literal_eval(processed_jobs)
            else:
                jobs = processed_jobs
                
            formatted_messages = []
            
            for job in jobs:
                # Create a Discord embed-like format using markdown
                message = (
                    f"## 🚀 **{job['title']}**\n"
                    f"### 🏢 {job['company']}\n\n"
                )
                
                # Add location with remote indicator
                location_text = job['location']
                if job.get('is_remote', False) and 'remote' not in location_text.lower():
                    message += f"📍 {location_text} | 🏠 Remote\n\n"
                else:
                    message += f"📍 {location_text}\n\n"
                
                # Add requirements
                if 'requirements' in job and job['requirements']:
                    requirements = job['requirements']
                    if isinstance(requirements, list):
                        message += f"**Requirements:**\n"
                        for req in requirements[:5]:  # Limit to top 5 requirements
                            message += f"• {req}\n"
                        message += "\n"
                
                # Add salary information
                if 'salary' in job and job['salary'] not in ["Not mentioned", "Not specified"]:
                    message += f"💰 **Salary:** {job['salary']}\n\n"
                else:
                    message += f"💰 **Salary:** Not specified\n\n"
                
                # Add level if available
                if 'level' in job and job['level'] != "Not specified":
                    level_emoji = {"Senior": "👑", "Mid-level": "⚙️", "Junior": "🌱"}.get(job['level'], "🔍")
                    message += f"**Level:** {level_emoji} {job['level']}\n\n"
                
                # Add link
                message += f"**Apply here:** {job['url']}\n\n"
                
                # Add separator
                message += "---\n\n"
                
                formatted_messages.append(message)
            
            # Save to JSON file
            json_file = save_formatted_messages_to_json(formatted_messages, "formatted_messages.json")
            print(f"Formatted messages saved to {json_file}")
            
            return json.dumps(formatted_messages)
            
        except Exception as e:
            return f"Error formatting job data: {str(e)}"