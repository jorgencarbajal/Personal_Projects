# import the goods...
from src.browser.browser_actions import BrowserAutomator
from src.ai.ai_client import AnthropicClient
from src.ai.prompt_builder import PromptBuilder
from src.ai.response_parser import ResponseParser
# needed for adding delays when webpages are loading
import time

class Orchestrator:
    
    def __init__(self):
        """Initialize all components (constructor)"""
        # initialize the BrowserAutomator object
        self.browser = BrowserAutomator()
        # initialize the AnthropicClient object
        self.ai_client = AnthropicClient()
        # initialize the PromptBuilder object
        self.prompt_builder = PromptBuilder()
        # initialize the ResponseParser object
        self.response_parser = ResponseParser()
        # the max number of automation iteration loops before being a quitter
        self.max_steps = 20
    
    def execute_goal(self, user_goal, start_url="https://google.com"):
        """
        Execute a user goal using AI-driven browser automation
        
        Args:
            user_goal: What the user wants (e.g., "Find cheapest laptop under $500")
            start_url: Starting URL (default: Google)
        
        Returns:
            Result string or error message
        """
        # printing out user goal...
        print(f"\n🎯 Goal: {user_goal}")
        print(f"🌐 Starting at: {start_url}")
        print("=" * 60)
        
        # Step 1: Initialize browser this uses the mcp_client.py file to orchestrate all this
        if not self.browser.initialize():
            return "❌ Failed to initialize browser"
        
        # Step 2: Navigate to starting URL, this uses the browser_actions.py file to orchestrate all this
        self.browser.navigate_to_website(start_url)
        current_url = start_url
        
        # Step 3: Main orchestration loop
        step_count = 0
        goal_achieved = False
        result = None
        
        # The loop that continues until the goal is achieved or the max # of steps is reached
        while not goal_achieved and step_count < self.max_steps:
            # increment and track the # of steps
            step_count += 1
            print(f"\n{'='*60}")
            print(f"📍 Step {step_count} of {self.max_steps}")
            print(f"{'='*60}")
            
            # 3a. Get current page state
            print("📸 Taking page snapshot...")
            # function call returns a dictionary from browser_actions/mcp_client
            snapshot_result = self.browser.take_page_snapshot()
            
            # if the snapshots not there attempt the loop again
            if not snapshot_result:
                print("⚠️ Failed to get snapshot, retrying...")
                time.sleep(2)
                continue
            
            # Extract snapshot text from result
            snapshot = self._extract_snapshot_text(snapshot_result)
            
            # Try to get current URL (fallback to last known if it fails)
            new_url = self.browser.get_current_url()
            if new_url:
                current_url = new_url
            
            print(f"📄 Current page: {current_url}")
            
            # 3b. Build prompt for AI
            print("🤖 Asking AI for next action...")
            prompt = self.prompt_builder.build(
                goal=user_goal,
                snapshot=snapshot,
                page_url=current_url,
                step_number=step_count
            )
            
            # 3c. Get AI decision
            try:
                ai_response = self.ai_client.get_next_action(prompt)
            except Exception as e:
                print(f"❌ AI call failed: {e}")
                return f"AI error: {str(e)}"
            
            # 3d. Parse AI response
            action = self.response_parser.parse(ai_response)
            
            print(f"💡 AI Decision: {action['action']}")
            if action.get('reasoning'):
                print(f"   Reasoning: {action['reasoning']}")
            
            # 3e. Execute the action
            if action["action"] == "navigate":
                url = action.get("value", "")
                print(f"🌐 Navigating to: {url}")
                self.browser.navigate_to_website(url)
                current_url = url
            
            elif action["action"] == "fill":
                ref = action.get("ref", "")
                value = action.get("value", "")
                print(f"⌨️  Filling {ref} with '{value}'")
                self.browser.fill(ref, value)
            
            elif action["action"] == "click":
                ref = action.get("ref", "")
                print(f"🖱️  Clicking {ref}")
                self.browser.click(ref)
            
            elif action["action"] == "complete":
                goal_achieved = True
                result = action.get("value", "Goal completed")
                print(f"✅ {result}")
            
            elif action["action"] == "error":
                print(f"⚠️ AI Error: {action.get('message', 'Unknown error')}")
                print("   Continuing to next step...")
            
            else:
                print(f"⚠️ Unknown action: {action['action']}")
            
            # 3f. Wait for page to settle
            time.sleep(2)
        
        # Step 4: Return result
        print(f"\n{'='*60}")
        if goal_achieved:
            print(f"🎉 SUCCESS!")
            return result
        else:
            print(f"⏱️ Reached maximum steps")
            return f"Did not complete goal within {self.max_steps} steps"
    
    def _extract_snapshot_text(self, snapshot_result):
        """Extract YAML snapshot text from result dictionary"""
        # if the snapshot is already a string, simply return it. The purpose of this function is for the case where the snapshot is a dictionary and a certain value from the dictionary need to be extracted.
        if isinstance(snapshot_result, str):
            return snapshot_result
        
        # Handle full response structure
        # Gets the result dictionary and in that result dictionary gets the contents array. Both default to nothing if not there.
        content = snapshot_result.get("result", {}).get("content", [])
        # check if content exists and has at least one item
        if content and len(content) > 0:
            # Gets the text field from the first item in content or defaults to empty string
            text = content[0].get("text", "")
            # Extract just the YAML part (after "Page Snapshot:")
            if "```yaml" in text:
                # splits the text at ... into a list of parts
                parts = text.split("```yaml")
                # ensures the list is not empty
                if len(parts) > 1:
                    # further splits collecting between the '''yaml and the '''
                    yaml_part = parts[1].split("```")[0]
                    # return the result with leading and trailing spaces removed
                    return yaml_part.strip()
            # if not YAML text was found return the text as-is
            return text
        # Or if there aint shit, return this
        return "No snapshot available"
    
    def _keepalive(self):
        """Quick action to keep browser session alive"""
        # Just check if browser is still responding
        # Don't print anything, this is just a heartbeat
        pass  # For now, just reducing wait time should be enough
