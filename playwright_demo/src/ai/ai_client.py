"""
The purpose of this file is to connect to the claude api and handle all the ai communications. We will need to initialize API key. Find a way to send prompts to claude. Recieve and return responses. And handle any API errors.
"""

from anthropic import Anthropic
import os
from dotenv import load_dotenv


def __init__(self):
    load_dotenv()
    self.client = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
    self.model = "claude-sonnet-4-20250514"

def get_next_action(self, prompt):
    