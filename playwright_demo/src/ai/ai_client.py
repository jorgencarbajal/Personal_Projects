"""
The purpose of this file is to connect to the claude api and handle all the ai communications. We will need to initialize API key. Find a way to send prompts to claude. Recieve and return responses. And handle any API errors.
"""

from anthropic import Anthropic
import os
from dotenv import load_dotenv

class AnthropicClient:

    def __init__(self):
        load_dotenv()
        self.client = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
        self.model = "claude-sonnet-4-20250514"

    def get_next_action(self, prompt):
        try:
            response = self.client.messages.create(
                model=self.model,
                max_tokens = 1024,
                messages = [{"role": "user", "content": prompt}]
            )
            return response.content[0].text

        except Exception as e:
            print(f"❌ AI API call failed: {e}")
            raise

    