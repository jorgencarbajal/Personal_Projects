## What is this project?

This project is an MCP (Model Context Protocol) server that wraps Playwright's browser automation capabilities. MCP is a standardized protocol that allows AI models like Claude to interact with tools and data sources. By exposing Playwright's functionality through MCP, we enable AI agents to perform complex browser automation tasks autonomously.

The key difference from traditional scripted automation is the agentic loop: the AI observes the results of each action, reasons about the current state, and decides what to do next. For example, if you ask the AI to "buy the cheapest Dell laptop on Amazon," it would:

1. Navigate to Amazon
2. Search for "Dell laptop"
3. Analyze the search results
4. Sort by price
5. Identify the cheapest option
6. Add it to cart and proceed through checkout

Each step informs the next, allowing the AI to adapt to dynamic page states and handle unexpected scenarios without pre-programmed instructions.

## Installation

### 1. Install Node.js Dependencies
```bash
npm install
```

### 2. Set Up Python Environment
```bash
python -m venv python_client
.\python_client\Scripts\Activate.ps1  # Windows
# or: source python_client/bin/activate  # Mac/Linux
```

### 3. Install Python Dependencies
```bash
pip install -r requirements.txt
```

### 4. Configure API Key
Create a `.env` file in the project root:
```
ANTHROPIC_API_KEY=your_api_key_here
```




## CURRENT TASKS

- Go through old read me and see if there is any pertinent info you want to keep...
- review and write notes in all code
- update readme with a breakdown of how all the code works, or in a notes file
- continue testing and debugging
	better snapshot_parser?
	better prompt?
   why is there no tool list function in mcp_client
   when calling a tool, having an error for when an incorrect tool is called...


## What You Need to Add for AI Integration

### 1. Snapshot Parser
```python
class SnapshotParser:
    def parse_yaml(self, snapshot_text):
        # Parse YAML from snapshot
        # Extract elements with ref IDs
        # Return structured data
        pass
    
    def find_element(self, snapshot, criteria):
        # Find element by text, role, etc.
        # Return ref ID for targeting
        pass
```

### 2. AI Client
```python
class AIClient:
    def __init__(self, api_key):
        # Initialize OpenAI or Claude
        pass
    
    def plan_next_action(self, goal, current_snapshot):
        # Send snapshot to AI
        # Get next action recommendation
        # Parse AI response into tool call
        pass
```

### 3. Orchestrator
```python
class BrowserOrchestrator:
    def __init__(self, browser_client, ai_client):
        self.browser = browser_client
        self.ai = ai_client
    
    def execute_goal(self, user_goal):
        while not goal_complete:
            # 1. Get page snapshot
            # 2. Ask AI for next action
            # 3. Execute action via MCP
            # 4. Check if goal achieved
            pass