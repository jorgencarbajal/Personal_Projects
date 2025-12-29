

from src.mcp_client import SessionMCPClient

import json

class BrowserAutomator:

    """
    Special constructor that runs when creating new instance of the class. It creates an instance variable names client and assigns it a new SessionMCPClient object. We then create and initialized variable and assign it to false which tracks whether the browser connection has been setup.
    """
    def __init__(self):
        self.client = SessionMCPClient()
        self.initialized = False
    
    """
    This method initializes the mcp server by calling the method from the mcp_client file. First starts by calling the 'complete_initialization' method on the self.client and stores the return value (true/false) in the success variable. If success is true then set initialized to true and return true if not return false.
    """
    def initialize(self):
        """Initialize the MCP connection"""
        print("🔧 Initializing browser automation...")
        success = self.client.complete_initialization()
        if success:
            self.initialized = True
            print("✅ Browser automation ready!")
            return True
        else:
            print("❌ Failed to initialize browser automation")
            return False
    
    """
    First we ensure that the server/browser is initialized. We then call the 'send_tool_call' function that uses the browser_navigate tool to navigate to the appropriate website. This function ultimately returns a dictionary. We test to see if the dictionary exists and the 'error' key does not exist (or is falsy).
    """
    def navigate_to_website(self, url):
        """Navigate to a specific website"""
        if not self.initialized:
            print("❌ Browser not initialized!")
            return False
        
        print(f"🌐 Navigating to: {url}")
        
        result = self.client.send_tool_call("browser_navigate", {"url": url})
        if result and not result.get("error"):
            print(f"✅ Successfully navigated to {url}")
            return True
        else:
            print(f"❌ Failed to navigate: {result}")
            return False
    
    """
    First we start by again ensuring that a session is initialized. We then call the 'browser_snapshot' tool with the send_tool_call function. Finally an if else statement that helps determine whether the screen capture was successfull or not. We return the dictionary if true or false if anything fails. As compared to the navigate function, this function actually returns a dictionary since the page_snapshot function will provide useful details for moving through the program.
    """
    def take_page_snapshot(self):
        """Take an accessibility snapshot of the current page"""
        if not self.initialized:
            print("❌ Browser not initialized!")
            return None
        
        print("📸 Taking page snapshot...")
        
        result = self.client.send_tool_call("browser_snapshot", {})
        if result and not result.get("error"):
            print("✅ Page snapshot captured!")
            return result
        else:
            print(f"❌ Failed to capture snapshot: {result}")
            return None
    
    """
    Note: The reason we include 'self' is because when we call the function like this... client.get_page_title(), Python automatically passes client as the first argument. Without self, we get an error.

    A method that obtains the page title by calling the browser_evaluate tool. The dictionary parameter {"function": "() => document.title"} contains JavaScript code that browser_evaluate executes in the browser to retrieve the page title. JavaScript code is required when using the browser_evaluate tool.
    """
    def get_page_title(self):
        """Get page title using JavaScript evaluation"""
        if not self.initialized:
            print("❌ Browser not initialized!")
            return None
        
        print("📋 Getting page title...")
        
        # result is a variable that stores the return value from the send_tool_call function, which returns a dictionary if successful. When send_tool_call is invoked, its arguments are "browser_evaluate" (a tool provided by the MCP server) and the dictionary {"function": "() => document.title"} (the parameters). The string "browser_evaluate" becomes the tool_name parameter, while the dictionary {"function": "() => document.title"} becomes the parameters argument, where "function" is the key expected by the browser_evaluate tool and "() => document.title" is the value - a JavaScript arrow function that retrieves the page title.
        # browser_evaluate is a tool that executes javascript code. It specifically always needs a function parameter.
        result = self.client.send_tool_call("browser_evaluate", {
            "function": "() => document.title"
        })
        
        if result and not result.get("error"):
            # Navigate the nested response structure (result->result) to extract the title. Use .get() with defaults as a safeguard if keys are missing.
            title = result["result"]["content"][0]["text"]
            # Split by newlines, get second line (index 1)
            lines = title.split('\n')
            title_line = lines[1]  # "Federal Reserve Economic Data..."
            # Remove the quotes
            title = title_line.strip('"')
            print(f"✅ Page title: {title}")
            return title
        else:
            print(f"❌ Failed to get title: {result}")
            return None