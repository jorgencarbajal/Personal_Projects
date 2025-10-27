# Purpose: Handle LLM interactions for generating actions
# Tasks
    # Define function to query LLM (e.g., OpenAI API) with prompt including
        # user goal, current snapshot (accessibility tree), and instructions
        # to output single next action as JSON (e.g., {"method": 
        # "browser_click", "params": {"ref": 123, "element": "description"}})
    # Parse LLM response to extract JSON action

from dotenv import load_dotenv
import os
import json
from xai_sdk import Client

# Load xAI API key
load_dotenv()
api_key = os.getenv("XAI_API_KEY")

# Initialize Grok client
client = Client(api_key=api_key)

def query_llm(goal, snapshot):
    # Query LLM with user goal and page snapshot, return JSON action
    prompt = f"Goal: {goal}\nSnapshot: {json.dumps(snapshot)}\nOutput next action as JSON: {{'method': str, 'params': dict}}"
    try:
        response = client.chat.completions.create(
            model="grok-beta",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=150
        )
        return json.loads(response.choices[0].message.content)
    except Exception as e:
        print(f"LLM query failed: {e}")
        return None