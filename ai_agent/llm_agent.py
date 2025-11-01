# Purpose: Handle LLM interactions for generating actions
# Tasks
    # Define function to query LLM (e.g., OpenAI API) with prompt including
        # user goal, current snapshot (accessibility tree), and instructions
        # to output single next action as JSON (e.g., {"method": 
        # "browser_click", "params": {"ref": 123, "element": "description"}})
    # Parse LLM response to extract JSON action

# Imports the load_dotenv function from the python-dotenv package, which reads
# environment variables from a .env file.
from dotenv import load_dotenv
# Imports the standard os module, providing functions to interact with the
# operating system, such as reading environment variables.
import os
# Imports the standard json module, enabling conversion between Python
# objects and JSON strings.
import json
# Imports the Client class from the xai_sdk package, used to interact
# with the xAI API or service.
from xai_sdk import Client

# Load xAI API key
load_dotenv()
api_key = os.getenv("XAI_API_KEY")

# Initialize Grok client
client = Client(api_key=api_key)

def query_llm(goal, snapshot):
    # Query LLM with user goal and page snapshot, return JSON action
    # Variable prompt is assigned an f-string that formats a structured instruction
    # containing the goal, a JSON-encoded snapshot, and a directive to output the next
    # action as JSON with method (string) and params (dictionary).
    prompt = f"Goal: {goal}\nSnapshot: {json.dumps(snapshot)}\nOutput next action as JSON: {{'method': str, 'params': dict}}"
    try:
        response = client.chat.completions.create(
            model="grok-4-fast-reasoning",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=150
        )
        raw_content = response.choices[0].message.content
        action = json.loads(raw_content)
        return validate_llm_action(action)
    except Exception as e:
        print(f"LLM query failed: {e}")
        return None
    
# Ensures Grok’s response is safe to use before sending to MCP client.    
def validate_llm_action(action):
    # Validate LLM action is properly formatted JSON with required keys
    if not isinstance(action, dict):
        print("Invalid action: not a dictionary")
        return None
    if "method" not in action or "params" not in action:
        print("Invalid action: missing 'method' or 'params'")
        return None
    return action