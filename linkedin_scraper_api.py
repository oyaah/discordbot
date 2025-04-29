import time
import random
from datetime import datetime
import os
import re
import json
from typing import List, Dict, Any
import requests
from bs4 import BeautifulSoup
from dotenv import load_dotenv

Custom model for job listings
class JobListing:
    def __init__(
        self, 
        id: str, 
        title: str, 
        company: str, 
        location: str, 
        url: str, 
        description: str = "", 
        requirements: List[str] = None, 
        salary: str = "Not specified", 
        is_remote: bool = False, 
        extracted_skills: List[str] = None, 
        level: str = "Not specified", 
        timestamp: str = None
    ):
        self.id = id
        self.title = title
        self.company = company
        self.location = location
        self.url = url
        self.description = description
        self.requirements = requirements or []
        self.salary = salary
        self.is_remote = is_remote
        self.extracted_skills = extracted_skills or []
        self.level = level
        self.timestamp = timestamp or datetime.now().isoformat()

# Load environment variables
load_dotenv()
LINKEDIN_EMAIL = os.getenv('LINKEDIN_EMAIL')
LINKEDIN_PASSWORD = os.getenv('LINKEDIN_PASSWORD')

class LinkedInScraper:
    """Class for scraping job listings from LinkedIn using Beautiful Soup"""
    
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

# For testing
if __name__ == "__main__":
    # Test the scraper
    scraper = LinkedInScraper()
    jobs = scraper.scrape_jobs(["data scientist", "machine learning engineer"], limit=5)
    for job in jobs:
        print(f"Title: {job.title}")
        print(f"Company: {job.company}")
        print(f"Location: {job.location}")
        print(f"URL: {job.url}")
        print(f"Requirements: {job.requirements[:2]}...")
        print("-" * 50)

# from tools import LinkedInScraperTool

# scraper=LinkedInScraperTool()
# result=scraper._run("data scientist","",5)
# print(f"Result length: {len(result)}")
# print(f"Result sample: {result[:200]}") 
# jobs = scraper.scrape_jobs(["data scientist", "machine learning engineer"], limit=5)
# for job in jobs:
#     print(f"Title: {job.title}")
#     print(f"Company: {job.company}")
#     print(f"Location: {job.location}")
#     print(f"URL: {job.url}")
#     print(f"Requirements: {job.requirements[:2]}...")
#     print("-" * 50)
# def run_linkedin_scraper(keywords="data scientist, machine learning engineer", location="", limit=10):
#     """Run the LinkedIn scraper tool and return the results"""
#     print(f"Scraping LinkedIn for jobs with keywords: {keywords}")
#     tool = LinkedInScraperTool()
#     result = tool._run(keywords, location, limit)
    
#     # Debug check
#     if not result or result.strip() == "":
#         print("WARNING: LinkedIn scraper returned empty data!")
#     else:
#         print(f"LinkedIn scraper returned {len(result)} bytes of data")
#         print(result[:200])
        
#     print("LinkedIn scraping completed!")
#     return result
# run_linkedin_scraper()
