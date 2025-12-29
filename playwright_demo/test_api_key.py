# talking to claudes api
from anthropic import Anthropic
# interact with operating systems, specifically for reading env variables
import os
# lets us load variables from .env
from dotenv import load_dotenv

# read file and load all variables making them accessible via os.getenv()
load_dotenv()
# create a client instance by getting the api key, then creating the client object with the key and finally storing this object in client variable
client = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

# This calls the messages.create() method to send a message to claude.
message = client.messages.create(
    # pick model
    model="claude-sonnet-4-20250514",
    # limit usage
    max_tokens=100,
    # The message that was sent by who and the content.
    messages=[{"role": "user", "content": "Say hello!"}]
)
# print out the reply
print(message.content[0].text)