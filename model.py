from dataclasses import dataclass, field
from typing import List, Optional
from datetime import datetime

@dataclass
class JobListing:
    """Data class to represent a job listing"""
    id: str
    title: str
    company: str
    location: str
    url: str
    description: str = ""
    requirements: List[str] = field(default_factory=list)
    salary: str = "Not mentioned"
    is_remote: bool = False
    extracted_skills: List[str] = field(default_factory=list)
    level: str = "Not specified"
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
    
    def to_dict(self):
        """Convert to dictionary for easier serialization"""
        return {
            "id": self.id,
            "title": self.title,
            "company": self.company,
            "location": self.location,
            "url": self.url,
            "description": self.description,
            "requirements": self.requirements,
            "salary": self.salary,
            "is_remote": self.is_remote,
            "extracted_skills": self.extracted_skills,
            "level": self.level,
            "timestamp": self.timestamp
        }
    
    @classmethod
    def from_dict(cls, data):
        """Create JobListing from dictionary"""
        return cls(**data)