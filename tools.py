# Web scraping imports
import time
import random
import os
import json
from datetime import datetime
import requests
from bs4 import BeautifulSoup
from dotenv import load_dotenv
from typing import Any, Dict, List, Optional, Union
from typing import Tuple
import ast
import pandas as pd


# LangChain Tool import
from langchain.tools import BaseTool
from pydantic import BaseModel, Field

# Import your data model
from model import JobListing

# Load environment variables
# Load environment variables
load_dotenv()
LINKEDIN_EMAIL = os.getenv('LINKEDIN_EMAIL')
LINKEDIN_PASSWORD = os.getenv('LINKEDIN_PASSWORD')

class LinkedInScraperTool():
    
    
    def __init__(self):
        """Initialize the scraper with session and headers"""
        self.session = requests.Session()
        # Set headers to mimic a browser
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.9',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Cache-Control': 'max-age=0',
            'Referer': 'https://www.linkedin.com/'
        }
        self.login_successful = self.login_to_linkedin()
    
    def login_to_linkedin(self) -> bool:
        """Log in to LinkedIn with credentials"""
        try:
            # First, get the login page to capture CSRF token
            login_url = "https://www.linkedin.com/login"
            response = self.session.get(login_url, headers=self.headers)
            
            # Check if the request was successful
            if response.status_code != 200:
                print(f"Failed to access login page. Status code: {response.status_code}")
                return False
            
            # Parse the login page
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Extract CSRF token and other required parameters
            csrf_token = soup.find('input', {'name': 'csrfToken'})
            if not csrf_token:
                csrf_token = soup.find('input', {'name': 'loginCsrfParam'})
            
            if not csrf_token:
                print("Could not find CSRF token on login page")
                return False
                
            csrf_value = csrf_token.get('value', '')
            
            # Prepare login data
            login_data = {
                'session_key': LINKEDIN_EMAIL,
                'session_password': LINKEDIN_PASSWORD,
                'csrfToken': csrf_value,
                'loginCsrfParam': csrf_value
            }
            
            # Perform login
            login_response = self.session.post(
                'https://www.linkedin.com/checkpoint/lg/login-submit',
                data=login_data,
                headers=self.headers,
                allow_redirects=True
            )
            
            # Check if login was successful by checking for certain elements on the home page
            if 'feed' in login_response.url or 'feed' in self.session.get('https://www.linkedin.com/feed/').url:
                print("Successfully logged in to LinkedIn")
                return True
            else:
                print("Failed to log in to LinkedIn. Check your credentials.")
                return False
                
        except Exception as e:
            print(f"Error during login: {e}")
            return False
    
    def get_job_listings(self, keywords: List[str], location: str = "", limit: int = 10) -> List[Dict]:
        """Get job listings from LinkedIn search results"""
        if not self.login_successful:
            print("Login was not successful. Cannot proceed with job search.")
            return []
            
        all_jobs = []
        jobs_per_keyword = max(1, limit // len(keywords)) if keywords else limit
        
        for keyword in keywords:
            try:
                # Construct search URL
                search_url = f"https://www.linkedin.com/jobs/search/?keywords={keyword}&f_TPR=r604800"  # Last 7 days
                if location:
                    search_url += f"&location={location}"
                
                response = self.session.get(search_url, headers=self.headers)
                if response.status_code != 200:
                    print(f"Failed to retrieve search results for '{keyword}'. Status code: {response.status_code}")
                    continue
                
                soup = BeautifulSoup(response.text, 'html.parser')
                
                # Find job cards
                job_cards = soup.find_all('div', class_='base-card')
                if not job_cards:
                    job_cards = soup.find_all('li', class_='jobs-search-results__list-item')
                
                if not job_cards:
                    print(f"No job cards found for keyword: {keyword}")
                    continue
                
                jobs_added = 0
                for card in job_cards[:jobs_per_keyword]:
                    # Extract basic job information from card
                    try:
                        # Find job link and ID
                        job_link_elem = card.find('a', class_='base-card__full-link') or card.find('a', class_='job-card-list__title')
                        if not job_link_elem:
                            continue
                            
                        job_url = job_link_elem.get('href', '').split('?')[0]  # Remove query parameters
                        job_id = job_url.split('/')[-2] if '/' in job_url else 'unknown'
                        
                        # Get job title
                        job_title_elem = card.find('h3', class_='base-search-card__title') or card.find('h3', class_='job-card-list__title')
                        job_title = job_title_elem.get_text(strip=True) if job_title_elem else "Unknown Title"
                        
                        # Get company name
                        company_elem = card.find('h4', class_='base-search-card__subtitle') or card.find('a', class_='job-card-container__company-name')
                        company = company_elem.get_text(strip=True) if company_elem else "Unknown Company"
                        
                        # Get location
                        location_elem = card.find('span', class_='job-search-card__location') or card.find('li', class_='job-card-container__metadata-item')
                        location_text = location_elem.get_text(strip=True) if location_elem else "Location not specified"
                        is_remote = "remote" in location_text.lower()
                        
                        # Get job details by visiting the job page
                        job_details = self.get_job_details(job_url)
                        
                        # Create job listing
                        job = JobListing(
                            id=job_id,
                            title=job_title,
                            company=company,
                            location=location_text,
                            url=job_url,
                            description=job_details.get('description', ''),
                            requirements=job_details.get('requirements', []),
                            salary=job_details.get('salary', 'Not specified'),
                            is_remote=is_remote,
                            extracted_skills=[],  # Will be filled by processor
                            level="Not specified",  # Will be filled by processor
                            timestamp=datetime.now().isoformat()
                        )
                        
                        # Convert to dictionary for easier processing
                        job_dict = job.__dict__
                        all_jobs.append(job_dict)
                        jobs_added += 1
                        
                        # Sleep to avoid rate limiting
                        time.sleep(random.uniform(2.0, 4.0))
                        
                        # Check if we've reached the limit
                        if len(all_jobs) >= limit:
                            break
                            
                    except Exception as e:
                        print(f"Error processing job card: {e}")
                        continue
                
                print(f"Added {jobs_added} jobs for keyword: {keyword}")
                
                # Sleep between keywords
                time.sleep(random.uniform(3.0, 5.0))
                
                # Check if we've reached the overall limit
                if len(all_jobs) >= limit:
                    break
                    
            except Exception as e:
                print(f"Error searching for jobs with keyword '{keyword}': {e}")
        
        return all_jobs
    
    def get_job_details(self, job_url: str) -> Dict:
        """Get detailed job information from the job page"""
        try:
            # Add a delay before making the request
            time.sleep(random.uniform(1.0, 2.0))
            
            response = self.session.get(job_url, headers=self.headers)
            if response.status_code != 200:
                print(f"Failed to retrieve job details. Status code: {response.status_code}")
                return {'description': '', 'requirements': [], 'salary': 'Not specified'}
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Find job description
            description_elem = soup.find('div', class_='show-more-less-html__markup') or soup.find('div', class_='description__text')
            description = description_elem.get_text(strip=True) if description_elem else "No description available"
            
            # Extract requirements
            requirements = []
            if description_elem:
                # Find list items in the description
                list_items = description_elem.find_all('li')
                for item in list_items[:10]:  # Limit to 10 requirements
                    text = item.get_text(strip=True)
                    if text and len(text) > 10:  # Filter out very short items
                        requirements.append(text)
                
                # If no requirements found as list items, look for key paragraphs
                if not requirements:
                    paragraphs = description_elem.find_all('p')
                    for p in paragraphs:
                        text = p.get_text(strip=True).lower()
                        if any(keyword in text for keyword in ["require", "qualif", "skill"]) and len(text) > 15:
                            requirements.append(p.get_text(strip=True))
                            if len(requirements) >= 5:  # Limit to 5 requirements
                                break
            
            # If still no requirements, extract from description
            if not requirements and description:
                for paragraph in description.split('\n'):
                    if any(keyword in paragraph.lower() for keyword in ["require", "qualif", "skill", "experience", "knowledge"]):
                        requirements.append(paragraph.strip())
                        if len(requirements) >= 5:
                            break
            
            # Look for salary information
            salary = "Not specified"
            salary_keywords = ["salary", "compensation", "pay", "stipend", "wage", "$", "€", "£", "usd", "eur", "gbp"]
            
            for paragraph in description.lower().split('\n'):
                if any(keyword in paragraph for keyword in salary_keywords):
                    salary = "Mentioned in description"
                    break
            
            return {
                'description': description,
                'requirements': requirements,
                'salary': salary
            }
            
        except Exception as e:
            print(f"Error retrieving job details: {e}")
            return {'description': '', 'requirements': [], 'salary': 'Not specified'}
    
    def scrape_jobs(self, keywords: List[str], location: str = "", limit: int = 10) -> List[JobListing]:
        """Main method to scrape LinkedIn jobs"""
        job_dicts = self.get_job_listings(keywords, location, limit)
        
        # Convert dictionaries back to JobListing objects
        jobs = []
        for job_dict in job_dicts:
            job = JobListing(
                id=job_dict['id'],
                title=job_dict['title'],
                company=job_dict['company'],
                location=job_dict['location'],
                url=job_dict['url'],
                description=job_dict['description'],
                requirements=job_dict['requirements'],
                salary=job_dict['salary'],
                is_remote=job_dict['is_remote'],
                extracted_skills=job_dict['extracted_skills'],
                level=job_dict['level'],
                timestamp=job_dict['timestamp']
            )
            jobs.append(job)
        
        print(f"Successfully scraped {len(jobs)} jobs from LinkedIn")
        return jobs

    
    def _run(self, keywords: str, location: str = "", limit: int = 10) -> str:
        try:
            # Parse keywords
            keyword_list = [k.strip() for k in keywords.split(',')]
            
            # Convert limit to integer if it's a string
            if isinstance(limit, str):
                try:
                    limit = int(limit)
                except ValueError:
                    limit = 10
            
            # Login to LinkedIn - no need to login again if __init__ already did it
            if self.login_successful:
                # Search for jobs - use the correct method name
                jobs = self.scrape_jobs(keyword_list, location, limit)
                
                # Convert JobListing objects to dictionaries for JSON serialization
                job_dicts = [job.__dict__ for job in jobs]
                return json.dumps(job_dicts)
            else:
                return json.dumps({"error": "Failed to log in to LinkedIn"})
                
        except Exception as e:
            return json.dumps({"error": f"Error in LinkedIn scraping: {str(e)}"})
        
      
class JobDataProcessorTool(BaseTool):
    name:str = "Job Data Processor"
    description: str = "Processes and filters raw job data"
    
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
            
            # # Remove duplicates
            # df = df.drop_duplicates(subset=['id'])
            
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
            return json.dumps(processed_jobs)
            
        except Exception as e:
            return f"Error processing job data: {str(e)}"


class DiscordFormatterTool(BaseTool):
    name: str = "Discord Content Formatter"
    description: str = "Formats job listings for Discord posting"
    
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
            
            return json.dumps(formatted_messages)
            
        except Exception as e:
            return f"Error formatting job data: {str(e)}"