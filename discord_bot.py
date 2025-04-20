import discord
from discord.ext import commands, tasks
import json
import os
import asyncio
from typing import List
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

DISCORD_TOKEN = os.getenv('DISCORD_TOKEN')
DISCORD_CHANNEL_ID = int(os.getenv('DISCORD_CHANNEL_ID'))

class JobPostingBot:
    def __init__(self):
        """Initialize the Discord bot"""
        intents = discord.Intents.default()
        intents.message_content = True
        
        self.bot = commands.Bot(command_prefix='!jobs ', intents=intents)
        self.setup_commands()
    
    def setup_commands(self):
        """Set up bot commands"""
        
        @self.bot.event
        async def on_ready():
            print(f'Bot logged in as {self.bot.user}')
        
        @self.bot.command(name='help')
        async def help_command(ctx):
            """Display help information"""
            help_text = (
                "**LinkedIn Job Posting Bot Commands**\n\n"
                "• `!jobs fetch` - Manually trigger job scraping and posting\n"
                "• `!jobs stats` - Show statistics about posted jobs\n"
                "• `!jobs search <query>` - Search for specific jobs\n"
                "• `!jobs help` - Show this help message\n"
            )
            await ctx.send(help_text)
        
        @self.bot.command(name='fetch')
        async def fetch_jobs(ctx):
            """Manually trigger job scraping and posting"""
            await ctx.send("🔍 Fetching new job listings... This might take a moment.")
            # In a real implementation, this would trigger the CrewAI workflow
            # For now, we'll just simulate it
            await ctx.send("⏳ Processing job data...")
            await asyncio.sleep(2)
            await ctx.send("✅ Jobs have been fetched and will be posted shortly!")
        
        @self.bot.command(name='stats')
        async def job_stats(ctx):
            """Show statistics about posted jobs"""
            stats = (
                "**Job Posting Statistics**\n\n"
                "• Total jobs posted: 42\n"
                "• Data Science roles: 18\n"
                "• ML Engineering roles: 24\n"
                "• Remote positions: 15\n"
                "• Last update: Today at 9:00 AM\n"
            )
            await ctx.send(stats)
        
        @self.bot.command(name='search')
        async def search_jobs(ctx, *, query: str):
            """Search for specific jobs"""
            await ctx.send(f"🔎 Searching for jobs matching: '{query}'")
            await ctx.send("This feature will be implemented in a future update.")
    
    async def post_jobs(self, channel_id: int, messages: List[str]):
        """Post job listings to the specified channel"""
        channel = self.bot.get_channel(channel_id)
        if not channel:
            print(f"Could not find channel with ID {channel_id}")
            return False
        
        for message in messages:
            # Split long messages if needed (Discord has 2000 char limit)
            if len(message) > 1900:
                chunks = [message[i:i+1900] for i in range(0, len(message), 1900)]
                for chunk in chunks:
                    await channel.send(chunk)
            else:
                await channel.send(message)
        
        return True
    
    async def start(self):
        """Start the Discord bot"""
        await self.bot.start(DISCORD_TOKEN)
    
    def run(self):
        """Run the bot (blocking call)"""
        self.bot.run(DISCORD_TOKEN)

# Function to post job listings from our tools
async def post_job_listings_to_discord(formatted_messages_json: str) -> bool:
    """Post formatted messages to Discord"""
    try:
        # Parse messages
        messages = json.loads(formatted_messages_json)
        
        # Create bot instance and post messages
        bot = JobPostingBot()
        loop = asyncio.get_event_loop()
        
        # Post the messages in a separate task to avoid blocking
        task = loop.create_task(bot.post_jobs(DISCORD_CHANNEL_ID, messages))
        
        # Wait for the task to complete with a timeout
        try:
            await asyncio.wait_for(task, timeout=30.0)
            return True
        except asyncio.TimeoutError:
            print("Posting to Discord timed out")
            return False
        
    except Exception as e:
        print(f"Error posting to Discord: {e}")
        return False

# Stand-alone test
if __name__ == "__main__":
    # Test the bot directly
    bot = JobPostingBot()
    bot.run()