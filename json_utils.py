import json
import os
from datetime import datetime
from typing import List, Dict, Any

def save_jobs_to_json(jobs: List[Dict[str, Any]], filename: str = None) -> str:
    """
    Save job listings to a JSON file
    
    Args:
        jobs: List of job dictionaries
        filename: Optional custom filename
        
    Returns:
        Path to the saved file
    """
    # Create a directory for job data if it doesn't exist
    os.makedirs('job_data', exist_ok=True)
    
    # Create default filename with timestamp if not provided
    if not filename:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"job_data/jobs_{timestamp}.json"
    elif not filename.startswith("job_data/"):
        filename = f"job_data/{filename}"
    
    # Make sure the filename ends with .json
    if not filename.endswith('.json'):
        filename += '.json'
    
    # Save the data to the file
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(jobs, f, indent=2, ensure_ascii=False)
    
    return filename

def save_formatted_messages_to_json(messages: List[str], filename: str = None) -> str:
    """
    Save formatted Discord messages to a JSON file
    
    Args:
        messages: List of formatted message strings
        filename: Optional custom filename
        
    Returns:
        Path to the saved file
    """
    # Create a directory for formatted messages if it doesn't exist
    os.makedirs('message_data', exist_ok=True)
    
    # Create default filename with timestamp if not provided
    if not filename:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"message_data/messages_{timestamp}.json"
    elif not filename.startswith("message_data/"):
        filename = f"message_data/{filename}"
    
    # Make sure the filename ends with .json
    if not filename.endswith('.json'):
        filename += '.json'
    
    # Create a dictionary with messages and metadata
    data = {
        "timestamp": datetime.now().isoformat(),
        "message_count": len(messages),
        "messages": messages
    }
    
    # Save the data to the file
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    
    return filename

def load_jobs_from_json(filename: str) -> List[Dict[str, Any]]:
    """
    Load job listings from a JSON file
    
    Args:
        filename: Path to the JSON file
        
    Returns:
        List of job dictionaries
    """
    # Add directory prefix if not provided
    if not filename.startswith("job_data/") and not os.path.exists(filename):
        filename = f"job_data/{filename}"
        
    # Make sure the filename ends with .json
    if not filename.endswith('.json'):
        filename += '.json'
    
    # Load the data from the file
    with open(filename, 'r', encoding='utf-8') as f:
        jobs = json.load(f)
    
    return jobs

def load_formatted_messages_from_json(filename: str) -> List[str]:
    """
    Load formatted Discord messages from a JSON file
    
    Args:
        filename: Path to the JSON file
        
    Returns:
        List of formatted message strings
    """
    # Add directory prefix if not provided
    if not filename.startswith("message_data/") and not os.path.exists(filename):
        filename = f"message_data/{filename}"
        
    # Make sure the filename ends with .json
    if not filename.endswith('.json'):
        filename += '.json'
    
    # Load the data from the file
    with open(filename, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    return data["messages"]