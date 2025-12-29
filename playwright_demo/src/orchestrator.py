class Orchestrator:
    
    def __init__(self):
        # Initialize components
        self.browser = BrowserActions()  # Wraps mcp_client
        self.ai_client = AnthropicClient()  # Connects to Claude
        self.prompt_builder = PromptBuilder()
        self.response_parser = ResponseParser()
        self.max_steps = 20  # Safety limit
    
    def execute_goal(self, user_goal):
        """
        Main entry point
        Input: "Find cheapest laptop under $500 on Amazon"
        Output: Result or error message
        """
        
        # Step 1: Initialize
        success = self.browser.initialize()
        if not success:
            return "Failed to initialize browser"
        
        # Step 2: Start at Amazon (or let AI navigate?)
        self.browser.navigate("https://amazon.com")
        
        # Step 3: Main orchestration loop
        step_count = 0
        goal_achieved = False
        
        while not goal_achieved and step_count < self.max_steps:
            step_count += 1
            
            # 3a. Get current page state
            snapshot = self.browser.get_snapshot()
            page_url = self.browser.get_current_url()
            
            # 3b. Build prompt for AI
            prompt = self.prompt_builder.build(
                goal=user_goal,
                snapshot=snapshot,
                page_url=page_url,
                step_number=step_count
            )
            
            # 3c. Ask AI what to do next
            ai_response = self.ai_client.get_next_action(prompt)
            
            # 3d. Parse AI response into structured action
            action = self.response_parser.parse(ai_response)
            
            # 3e. Execute the action
            if action.type == "navigate":
                self.browser.navigate(action.url)
            
            elif action.type == "fill":
                self.browser.fill(action.ref, action.value)
            
            elif action.type == "click":
                self.browser.click(action.ref)
            
            elif action.type == "complete":
                goal_achieved = True
                result = action.result
            
            elif action.type == "error":
                return f"AI encountered error: {action.message}"
            
            # 3f. Small delay to let page load
            wait(2)
        
        # Step 4: Return result
        if goal_achieved:
            return result
        else:
            return f"Reached max steps ({self.max_steps}) without completing goal"