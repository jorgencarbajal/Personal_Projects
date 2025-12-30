""""
The purpose of this file is to format information into a prompt that Claude can understand and respond to properly
Input:
    user goal
    page snapshot
    current url
Output: A formatted prompt string that tells Claude...
    what the user wants
    whats on the current page
    what actions it can take
    how to respond (JSON format)
"""

class PromptBuilder:
    
    def build(self, goal, snapshot, page_url, step_number):
        """
        Build a prompt for Claude to analyze page and decide next action
        
        Args:
            goal: User's goal (e.g., "Find cheapest laptop under $500")
            snapshot: Page structure in YAML format from browser
            page_url: Current page URL
            step_number: Current step number
        
        Returns:
            Formatted prompt string for Claude

        FLOW
            1. Client builds prompt with PromptBuilder
            2. Client sends prompt to Claude (LLM)
            3. Claude (LLM) reads the prompt and decides: "I should click element e26"
            4. Claude responds with JSON: {"action": "click", "ref": "e26", ...}
            5. Client parses that JSON response
            6. Client executes the action by calling MCP tools (like playwright_click on ref e26)
        """
        
        prompt = f"""You are a browser automation assistant helping achieve this goal:
        {goal}

        Current page: {page_url}
        Step: {step_number} of 20

        Here is the current page structure:
        {snapshot}

        You can perform these actions:
        - navigate: Go to a new URL (provide URL in "value")
        - click: Click an element (provide ref ID in "ref")
        - fill: Type text into an element (provide ref ID in "ref" and text in "value")
        - complete: Mark goal as finished (provide result in "value")

        Respond ONLY with valid JSON in this exact format:
        {{
        "action": "click",
        "ref": "e26",
        "value": "laptop",
        "reasoning": "why you're doing this",
        "goal_complete": false
        }}

        For complete action:
        {{
        "action": "complete",
        "value": "The result/answer",
        "reasoning": "Goal achieved because...",
        "goal_complete": true
        }}
        """
        
        return prompt
