# import time
# import random
# from datetime import datetime
# import os
# from typing import List, Dict, Any
# from selenium import webdriver
# from selenium.webdriver.chrome.options import Options
# from selenium.webdriver.common.by import By
# from selenium.webdriver.support.ui import WebDriverWait
# from selenium.webdriver.support import expected_conditions as EC
# from selenium.common.exceptions import TimeoutException, NoSuchElementException
# from webdriver_manager.chrome import ChromeDriverManager
# from dotenv import load_dotenv

# from model import JobListing

# # Load environment variables
# load_dotenv()
# LINKEDIN_EMAIL = os.getenv('LINKEDIN_EMAIL')
# LINKEDIN_PASSWORD = os.getenv('LINKEDIN_PASSWORD')

# class LinkedInScraper:
#     """Class for scraping job listings from LinkedIn"""
    
#     def setup_driver(self):
#         """Set up Selenium WebDriver with Chrome"""
#         chrome_options = Options()
#         chrome_options.add_argument("--headless")  # Run in headless mode
#         chrome_options.add_argument("--no-sandbox")
#         chrome_options.add_argument("--disable-dev-shm-usage")
#         chrome_options.add_argument("--disable-gpu")
#         chrome_options.add_argument("--window-size=1920,1080")
#         chrome_options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.212 Safari/537.36")
        
#         # Add options to avoid detection
#         chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
#         chrome_options.add_experimental_option("useAutomationExtension", False)
        
#         driver = webdriver.Chrome(ChromeDriverManager().install(), options=chrome_options)
        
#         # Execute CDP commands to avoid detection
#         driver.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {
#             "source": """
#                 Object.defineProperty(navigator, 'webdriver', {
#                     get: () => undefined
#                 })
#             """
#         })
        
#         return driver
    
#     def login_to_linkedin(self, driver):
#         """Log in to LinkedIn with credentials"""
#         try:
#             driver.get("https://www.linkedin.com/login")
#             WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "username")))
            
#             # Enter email and password
#             driver.find_element(By.ID, "username").send_keys(LINKEDIN_EMAIL)
#             driver.find_element(By.ID, "password").send_keys(LINKEDIN_PASSWORD)
            
#             # Click login button
#             driver.find_element(By.XPATH, "//button[@type='submit']").click()
            
#             # Wait for login to complete
#             WebDriverWait(driver, 10).until(
#                 EC.presence_of_element_located((By.XPATH, "//div[contains(@class, 'feed-identity-module')] | //div[contains(@class, 'profile-rail-card')]"))
#             )
            
#             print("Successfully logged in to LinkedIn")
#             return True
#         except Exception as e:
#             print(f"Failed to log in to LinkedIn: {e}")
#             return False
    
#     def extract_job_details(self, driver, job_card):
#         """Extract details from a job card"""
#         try:
#             # Extract job ID and URL
#             job_link = job_card.find_element(By.CSS_SELECTOR, "a.job-card-container__link, a.job-card-list__title")
#             job_url = job_link.get_attribute("href")
            
#             # Extract job ID from URL
#             if "currentJobId=" in job_url:
#                 job_id = job_url.split("currentJobId=")[1].split("&")[0]
#             else:
#                 job_id = job_url.split("/")[-2] if "/" in job_url else "unknown"
            
#             # Extract job title
#             job_title = job_card.find_element(By.CSS_SELECTOR, "a.job-card-list__title, h3.base-search-card__title").text.strip()
            
#             # Extract company name
#             try:
#                 company_elem = job_card.find_element(By.CSS_SELECTOR, "span.job-card-container__primary-description, h4.base-search-card__subtitle")
#                 company_name = company_elem.text.strip()
#             except:
#                 company_name = "Unknown Company"
            
#             # Extract location
#             try:
#                 location_elem = job_card.find_element(By.CSS_SELECTOR, "li.job-card-container__metadata-item, span.job-search-card__location")
#                 location = location_elem.text.strip()
#             except:
#                 location = "Location not specified"
            
#             # Check if remote
#             is_remote = "remote" in location.lower()
            
#             # Click on the job to view details
#             job_link.click()
            
#             # Wait for job details to load
#             WebDriverWait(driver, 10).until(
#                 EC.presence_of_element_located((By.CSS_SELECTOR, "div.show-more-less-html__markup, div.description__text"))
#             )
            
#             # Extract job description
#             try:
#                 description_elem = driver.find_element(By.CSS_SELECTOR, "div.show-more-less-html__markup, div.description__text")
#                 description = description_elem.text.strip()
#             except:
#                 description = "No description available"
            
#             # Extract requirements
#             requirements = []
#             try:
#                 # Try to find list items in the description
#                 req_elements = description_elem.find_elements(By.TAG_NAME, "li")
#                 for elem in req_elements[:10]:  # Limit to 10 requirements
#                     req_text = elem.text.strip()
#                     if req_text and len(req_text) > 10:  # Filter out very short items
#                         requirements.append(req_text)
                        
#                 # If no requirements found as list items, try to identify them in paragraphs
#                 if not requirements:
#                     paragraphs = description_elem.find_elements(By.TAG_NAME, "p")
#                     for p in paragraphs:
#                         text = p.text.lower().strip()
#                         if ("require" in text or "qualif" in text or "skill" in text) and len(text) > 15:
#                             requirements.append(p.text.strip())
#             except:
#                 pass
            
#             # If still no requirements, extract some from the description
#             if not requirements and description:
#                 # Split description into paragraphs and look for requirement-like sentences
#                 for paragraph in description.split('\n'):
#                     if any(keyword in paragraph.lower() for keyword in ["require", "qualif", "skill", "experience", "knowledge"]):
#                         requirements.append(paragraph.strip())
#                         if len(requirements) >= 5:  # Limit to 5 requirements from paragraphs
#                             break
            
#             # Look for salary information in the description
#             salary = "Not specified"
#             salary_keywords = ["salary", "compensation", "pay", "stipend", "wage", "$", "€", "£", "usd", "eur", "gbp"]
            
#             for paragraph in description.lower().split('\n'):
#                 if any(keyword in paragraph for keyword in salary_keywords):
#                     # Found potential salary information
#                     salary = "Mentioned in description"
#                     break
            
#             # Create job listing
#             job = JobListing(
#                 id=job_id,
#                 title=job_title,
#                 company=company_name,
#                 location=location,
#                 url=job_url,
#                 description=description,
#                 requirements=requirements,
#                 salary=salary,
#                 is_remote=is_remote,
#                 extracted_skills=[],  # Will be filled by processor
#                 level="Not specified",  # Will be filled by processor
#                 timestamp=datetime.now().isoformat()
#             )
            
#             return job
            
#         except Exception as e:
#             print(f"Error extracting job details: {e}")
#             return None
    
#     def scrape_jobs(self, keywords: List[str], location: str = "", limit: int = 10) -> List[JobListing]:
#         """Scrape LinkedIn jobs based on keywords and location"""
#         jobs = []
        
#         # Initialize the driver
#         driver = self.setup_driver()
        
#         try:
#             # Login to LinkedIn
#             if not self.login_to_linkedin(driver):
#                 print("Failed to log in, returning empty results")
#                 driver.quit()
#                 return []
            
#             # Total jobs per keyword, adjusted to meet the overall limit
#             jobs_per_keyword = max(1, limit // len(keywords))
            
#             # Search for each keyword
#             for keyword in keywords:
#                 try:
#                     # Construct search URL with filters for recent jobs
#                     search_url = f"https://www.linkedin.com/jobs/search/?keywords={keyword}&f_TPR=r604800"  # Last 7 days
#                     if location:
#                         search_url += f"&location={location}"
                    
#                     driver.get(search_url)
                    
#                     # Wait for job results to load
#                     try:
#                         WebDriverWait(driver, 10).until(
#                             EC.presence_of_element_located((By.CSS_SELECTOR, "ul.jobs-search__results-list"))
#                         )
#                     except TimeoutException:
#                         print(f"No jobs found for keyword: {keyword}")
#                         continue
                    
#                     # Scroll to load more jobs
#                     for _ in range(min(2, jobs_per_keyword // 5)):
#                         driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
#                         time.sleep(2)  # Wait for jobs to load
                    
#                     # Get all job cards
#                     job_cards = driver.find_elements(By.CSS_SELECTOR, "li.jobs-search-results__list-item")
                    
#                     # Process jobs for this keyword
#                     jobs_added = 0
#                     for i in range(min(jobs_per_keyword, len(job_cards))):
#                         # Re-find job cards as the DOM might have changed
#                         job_cards = driver.find_elements(By.CSS_SELECTOR, "li.jobs-search-results__list-item")
                        
#                         if i < len(job_cards):
#                             # Extract job details
#                             job = self.extract_job_details(driver, job_cards[i])
                            
#                             if job:
#                                 # Add job to the list
#                                 jobs.append(job)
#                                 jobs_added += 1
                                
#                                 # Sleep between jobs to avoid rate limiting
#                                 time.sleep(random.uniform(1.5, 3.0))
                        
#                         # Check if we've reached the overall limit
#                         if len(jobs) >= limit:
#                             break
                    
#                     print(f"Added {jobs_added} jobs for keyword: {keyword}")
                    
#                     # Sleep between keywords
#                     time.sleep(random.uniform(3.0, 5.0))
                    
#                     # Check if we've reached the overall limit
#                     if len(jobs) >= limit:
#                         break
                    
#                 except Exception as e:
#                     print(f"Error searching for jobs with keyword '{keyword}': {e}")
            
#         except Exception as e:
#             print(f"Error during job scraping: {e}")
        
#         finally:
#             # Always close the driver
#             driver.quit()
        
#         print(f"Successfully scraped {len(jobs)} jobs from LinkedIn")
#         return jobs

# # For testing
# if __name__ == "__main__":
#     # Test the scraper
#     scraper = LinkedInScraper()
#     jobs = scraper.scrape_jobs(["data scientist", "machine learning engineer"], limit=5)
#     for job in jobs:
#         print(f"Title: {job.title}")
#         print(f"Company: {job.company}")
#         print(f"Location: {job.location}")
#         print(f"URL: {job.url}")
#         print(f"Requirements: {job.requirements[:2]}...")
#         print("-" * 50)

import os
from datetime import datetime
from typing import List

from linkedin_api import Linkedin
from dotenv import load_dotenv

from model import JobListing

# Load environment variables\load_dotenv()
LINKEDIN_EMAIL = os.getenv('LINKEDIN_EMAIL')
LINKEDIN_PASSWORD = os.getenv('LINKEDIN_PASSWORD')

class LinkedInScraper:
    """Scrape LinkedIn jobs using the unofficial linkedin-api (no Selenium)."""

    def __init__(self):
        # Authenticate via the linkedin-api package
        self.api = Linkedin(LINKEDIN_EMAIL, LINKEDIN_PASSWORD)

    def scrape_jobs(
        self,
        keywords: List[str],
        location: str = "",
        limit: int = 10,
        posted_within_seconds: int = 7 * 24 * 3600,
    ) -> List[JobListing]:
        """
        Search and fetch job listings from LinkedIn.

        Args:
          keywords: list of search keywords
          location: e.g. "India", "Bangalore"
          limit: maximum total jobs to return
          posted_within_seconds: only jobs posted in this timeframe

        Returns:
          A list of JobListing objects, populated with basic details.
        """
        jobs: List[JobListing] = []
        per_kw = max(1, limit // len(keywords))

        for kw in keywords:
            # Use linkedin-api's search_jobs endpoint
            results = self.api.search_jobs(
                keywords=kw,
                location_name=location,
                listed_at=posted_within_seconds,
                limit=per_kw,
            )
            for job_data in results:
                job_id = str(job_data.get("jobId"))
                # Fetch full job details
                details = self.api.get_job(job_id)

                # Build JobListing
                job = JobListing(
                    id=job_id,
                    title=job_data.get("title", ""),
                    company=job_data.get("companyName", ""),
                    location=job_data.get("locationName", ""),
                    url=f"https://www.linkedin.com/jobs/view/{job_id}",
                    description=details.get("description", ""),
                    requirements=[],  # post-process if needed
                    salary=details.get("salary", "Not specified"),
                    is_remote="remote" in job_data.get("locationName", "").lower(),
                    extracted_skills=[],
                    level=details.get("jobLevel", "Not specified"),
                    timestamp=datetime.now().isoformat(),
                )
                jobs.append(job)
                if len(jobs) >= limit:
                    return jobs
        return jobs


if __name__ == "__main__":
    scraper = LinkedInScraper()
    sample = scraper.scrape_jobs(
        ["data scientist", "machine learning engineer"],
        location="India",
        limit=5,
    )
    for job in sample:
        print(f"{job.title} @ {job.company} ({job.location})")
        print(job.url)
        print("---")
