

from src.mcp_client import SessionMCPClient

import json

class BrowserAutomator:
    
    def __init__(self):
        """
        Special constructor that runs when creating new instance of the class. It creates an instance variable names client and assigns it a new SessionMCPClient object. We then create and initialized variable and assign it to false which tracks whether the browser connection has been setup.
        """
        self.client = SessionMCPClient()
        self.initialized = False
    
    def initialize(self):
        """
        This method initializes the mcp server by calling the method from the mcp_client file. First starts by calling the 'complete_initialization' method on the self.client and stores the return value (true/false) in the success variable. If success is true then set initialized to true and return true if not return false.
        """
        print("🔧 Initializing browser automation...")
        success = self.client.complete_initialization()
        if success:
            self.initialized = True
            print("✅ Browser automation ready!")
            return True
        else:
            print("❌ Failed to initialize browser automation")
            return False
    
    def navigate_to_website(self, url):
        """
        First we ensure that the server/browser is initialized. We then call the 'send_tool_call' function that uses the browser_navigate tool to navigate to the appropriate website. This function ultimately returns a dictionary. We test to see if the dictionary exists and the 'error' key does not exist (or is falsy).
        """
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
    
    def take_page_snapshot(self):
        """
        First we start by again ensuring that a session is initialized. We then call the 'browser_snapshot' tool with the send_tool_call function. Finally an if else statement that helps determine whether the screen capture was successfull or not. We return the dictionary if true or false if anything fails. As compared to the navigate function, this function actually returns a dictionary since the page_snapshot function will provide useful details for moving through the program.
        Take an accessibility snapshot of the current page"""
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
    
    def get_page_title(self):
        """
        Get the page title by executing JavaScript in the browser.
        Uses browser_evaluate tool to run document.title.
        Returns the title string or None if it fails.
        """
        if not self.initialized:
            print("❌ Browser not initialized!")
            return None
        
        print("📋 Getting page title...")
        
        try:
            result = self.client.send_tool_call("browser_evaluate", {
                "function": "() => document.title"
            })
            
            print(f"🔍 DEBUG - get_page_title() raw result: {result}")
            
            if result and not result.get("error"):
                # Safely navigate the nested response structure
                content = result.get("result", {}).get("content", [])
                
                if content and len(content) > 0:
                    text = content[0].get("text", "")
                    lines = text.split('\n')
                    
                    # Check that we have at least 2 lines before accessing index 1
                    if len(lines) > 1:
                        title = lines[1].strip('"')
                        print(f"✅ Page title: {title}")
                        return title
                
                # If we got here, response structure was unexpected
                print(f"⚠️ Unexpected response structure")
                return None
            else:
                print(f"❌ Failed to get title: {result}")
                return None
            
        except Exception as e:
            print(f"❌ Exception getting title: {e}")
            return None
        







    # Needs defining/understanding

    def click(self, ref):
        """Click an element using its ref ID"""
        if not self.initialized:
            print("❌ Browser not initialized!")
            return False
        
        print(f"🖱️ Clicking element: {ref}")
        
        try:
            result = self.client.send_tool_call("browser_click", {
                "element": "clickable element",
                "ref": ref
            })
            
            print(f"🔍 DEBUG - click() raw result: {result}")
            
            if result and not result.get("error"):
                print(f"✅ Successfully clicked {ref}")
                return True
            else:
                print(f"❌ Failed to click: {result}")
                return False
                
        except Exception as e:
            # Timeout is expected during navigation
            print(f"⚠️ Click timeout (navigation in progress) - treating as success")
            return True  # Changed from False to True
        
    def fill(self, ref, text):
        """Fill a text field with the given text"""
        if not self.initialized:
            print("❌ Browser not initialized!")
            return False
        
        print(f"⌨️ Filling element {ref} with: {text}")
        
        try:
            result = self.client.send_tool_call("browser_type", {
                "element": "text input field",
                "ref": ref, 
                "text": text
            })
            
            # DEBUG - now it's after assignment
            print(f"🔍 DEBUG - fill() raw result: {result}")
            
            if result and not result.get("error"):
                print(f"✅ Successfully filled {ref}")
                return True
            else:
                print(f"❌ Failed to fill: {result}")
                return False
                
        except Exception as e:
            print(f"❌ EXCEPTION in fill(): {e}")
            import traceback
            traceback.print_exc()
            return False
        
    def press_enter(self):
        """
        - Ensure the browser is initialized
        - Try sending the tool call
        - Was it successful or not? Returns True or False
        """

        # Ensure the browser is initialized
        if not self.initialized:
            print("❌ Browser not initialized!")
            return False
        
        print("⌨️ Pressing Enter...")
        
        # Try sending the tool call using the correct method
        try:
            # Send the tool call using "browser_press_key"
            result = self.client.send_tool_call("browser_press_key", {"key": "Enter"})
            
            # result will be a dictionary and this will print the dictionary
            print(f"🔍 DEBUG - press_enter() raw result: {result}")
            
            # If there was success
            if result and not result.get("error"):
                print("✅ Successfully pressed Enter")
                return True
            # If there wasnt
            else:
                print(f"❌ Failed to press Enter: {result}")
                return False
                
        # Catch any exception - most commonly a timeout when Enter triggers navigation
        except Exception:
            # Enter often triggers form submission/navigation
            print(f"⚠️ Press Enter timeout (navigation in progress) - treating as success")
            return True

    def get_current_url(self):
        if not self.initialized:
            print("❌ Browser not initialized!")
            return None
        
        print("🔗 Getting current URL...")
        
        result = self.client.send_tool_call("browser_evaluate", {
            "function": "() => document.location.href"
        })
        
        print(f"DEBUG - Full result: {result}")
        
        if result and not result.get("error"):
            # Check if we have the full response structure
            content = result.get("result", {}).get("content", [])
            if content and len(content) > 0:
                text = content[0].get("text", "")
                lines = text.split('\n')
                if len(lines) > 1:
                    url = lines[1].strip('"')
                    print(f"✅ Current URL: {url}")
                    return url
            
            # If no content, the response might just be {'success': True}
            # This means the evaluate ran but didn't return structured data
            print("⚠️ Got success but no URL data")
            return None
        
        print("❌ Failed to get URL")
        return None
