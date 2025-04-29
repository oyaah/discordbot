import os
from dotenv import load_dotenv

# Print current working directory
print(f"Current working directory: {os.getcwd()}")

# Try to find .env file
env_path = os.path.join(os.getcwd(), '.env')
print(f"Looking for .env file at: {env_path}")
print(f"File exists: {os.path.exists(env_path)}")

# Load the .env file
print("Attempting to load .env file...")
load_dotenv()

# Check if variables were loaded
token = os.getenv('DISCORD_TOKEN')
channel_id = os.getenv('DISCORD_CHANNEL_ID')

print(f"DISCORD_TOKEN loaded: {'✓' if token else '✗'}")
if token:
    # Show first 5 and last 3 characters for verification
    print(f"Token preview: {token[:5]}...{token[-3:]}")

print(f"DISCORD_CHANNEL_ID loaded: {'✓' if channel_id else '✗'}")
if channel_id:
    print(f"Channel ID: {channel_id}")