
import random
import uuid
from datetime import datetime, timedelta
from model import JobListing

# Sample data to generate fake job listings
COMPANIES = [
    "TechGiant Inc.", "DataCorp", "AI Solutions", "Machine Learning Ltd.", 
    "Neural Networks Co.", "Data Science Experts", "Algorithm Masters",
    "Predictive Analytics Inc.", "Deep Learning Solutions", "Model Trainers LLC"
]

JOB_TITLES = [
    "Data Scientist", "Machine Learning Engineer", "ML Engineer", 
    "AI Engineer", "Data Engineer", "NLP Engineer", 
    "Computer Vision Engineer", "MLOps Engineer", "AI Researcher",
    "Deep Learning Specialist"
]

LOCATIONS = [
    "San Francisco, CA", "New York, NY", "Seattle, WA", "Boston, MA",
    "Austin, TX", "Remote", "Chicago, IL", "Los Angeles, CA",
    "Toronto, Canada", "London, UK"
]

REQUIREMENTS = [
    "Python", "PyTorch", "TensorFlow", "SQL", "Spark", "Hadoop",
    "Kubernetes", "Docker", "AWS", "Azure", "GCP", "Computer Vision",
    "NLP", "Deep Learning", "Reinforcement Learning", "Statistics",
    "Mathematics", "PhD", "Master's Degree", "3+ years experience",
    "5+ years experience", "Data visualization", "Git", "CI/CD"
]

SALARY_OPTIONS = [
    "Not specified", "$100,000 - $130,000", "$130,000 - $160,000",
    "$160,000 - $200,000", "$200,000+", "£60,000 - £80,000",
    "€70,000 - €90,000", "$80,000 - $100,000", "Competitive"
]

DESCRIPTIONS = [
    """We are looking for a talented {title} to join our team. You will work on cutting-edge projects 
    that involve analyzing large datasets and developing machine learning models. The ideal candidate 
    will have strong programming skills and experience with {req1} and {req2}.""",
    
    """Join our innovative team as a {title}! In this role, you will develop and implement machine 
    learning solutions to solve complex business problems. Experience with {req1} is required, 
    and knowledge of {req2} is a plus.""",
    
    """Exciting opportunity for a {title} to drive our AI initiatives forward. You will be responsible 
    for designing and implementing ML models, working with {req1} and {req2} technologies.""",
    
    """We're seeking an experienced {title} with strong skills in {req1} and {req2}. You will be 
    responsible for developing and maintaining our data pipeline and ML infrastructure."""
]

def generate_fake_job_listings(count=20):
    """Generate a list of fake job listings"""
    job_listings = []
    
    for _ in range(count):
        # Generate random data
        title = random.choice(JOB_TITLES)
        company = random.choice(COMPANIES)
        location = random.choice(LOCATIONS)
        is_remote = location == "Remote" or random.random() < 0.3
        
        # If both location is specified and is_remote is True, adjust the location string
        if is_remote and location != "Remote":
            location = f"{location} (Remote)"
        elif is_remote:
            location = "Remote"
        
        # Generate requirements and skills
        num_requirements = random.randint(3, 8)
        requirements = random.sample(REQUIREMENTS, num_requirements)
        
        # Generate random skills (subset of requirements + maybe some extras)
        skills = requirements[:random.randint(2, min(5, len(requirements)))]
        
        # Determine level based on requirements
        if "PhD" in requirements or "5+ years experience" in requirements:
            level = "Senior"
        elif "Master's Degree" in requirements or "3+ years experience" in requirements:
            level = "Mid-level"
        else:
            level = "Junior"
        
        # Randomize salary information
        salary = random.choice(SALARY_OPTIONS)
        
        # Generate job ID and URL
        job_id = str(uuid.uuid4())[:8]
        url = f"https://www.linkedin.com/jobs/view/{job_id}/"
        
        # Generate description with random requirements
        req_sample = random.sample(requirements, 2)
        description = random.choice(DESCRIPTIONS).format(
            title=title, req1=req_sample[0], req2=req_sample[1]
        )
        
        # Generate random timestamp within the last week
        days_ago = random.randint(0, 7)
        timestamp = (datetime.now() - timedelta(days=days_ago)).isoformat()
        
        # Create job listing
        job = JobListing(
            id=job_id,
            title=title,
            company=company,
            location=location,
            url=url,
            description=description,
            requirements=requirements,
            salary=salary,
            is_remote=is_remote,
            extracted_skills=skills,
            level=level,
            timestamp=timestamp
        )
        
        job_listings.append(job)
    
    return job_listings

# Function to get a batch of fake job listings
def get_fake_linkedin_jobs(keywords=None, count=10):
    """Get fake LinkedIn jobs, optionally filtered by keywords"""
    all_jobs = generate_fake_job_listings(count * 2)
    
    if keywords:
        filtered_jobs = []
        for job in all_jobs:
            # Check if any keyword is in the title
            if any(kw.lower() in job.title.lower() for kw in keywords):
                filtered_jobs.append(job)
            
            # Stop once we have enough jobs
            if len(filtered_jobs) >= count:
                break
        
        return filtered_jobs[:count]
    
    return all_jobs[:count]