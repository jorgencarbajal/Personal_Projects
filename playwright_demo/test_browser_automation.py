"""
Browser Automation Test - Using our working MCP client
"""
# sys module gives access to system specific parameters and functions
import sys
# provides functions for interacting with the operating systems
import os
# '__file__' a special python variable that contains the path to the current script file
# 'os.path.dirname(__file__)' gets the directory folder that contains the file
# ''..'' go up one directory (parnet folder)
# ' os.path.join()' combines path parts in a platform-safe way
# 'sys.path': a list of directories where python looks for modules
# '.append(): adds the new path to this list
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from src.mcp_client import SessionMCPClient
import json

class BrowserAutomator:
    def __init__(self):
        self.client = SessionMCPClient()
        self.initialized = False
    
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
    
    def get_page_title(self):
        """Get page title using JavaScript evaluation"""
        if not self.initialized:
            print("❌ Browser not initialized!")
            return None
        
        print("📋 Getting page title...")
        
        result = self.client.send_tool_call("browser_evaluate", {
            "function": "() => document.title"
        })
        
        if result and not result.get("error"):
            title = result.get("result", {}).get("result", "Unknown")
            print(f"✅ Page title: {title}")
            return title
        else:
            print(f"❌ Failed to get title: {result}")
            return None

def main():
    print("🚀 Starting Browser Automation Test")
    print("=" * 50)
    
    # Create browser automator
    browser = BrowserAutomator()
    
    # Initialize
    if not browser.initialize():
        return
    
    # Test 1: Navigate to a simple website
    print("\n🧪 Test 1: Navigate to example.com")
    if browser.navigate_to_website("https://example.com"):
        
        # Test 2: Get page title
        print("\n🧪 Test 2: Get page title")
        browser.get_page_title()
        
        # Test 3: Take page snapshot
        print("\n🧪 Test 3: Take accessibility snapshot")
        snapshot = browser.take_page_snapshot()
        
        if snapshot:
            # Show a preview of the snapshot data
            snapshot_result = snapshot.get("result", {})
            if snapshot_result:
                print("📊 Snapshot preview:")
                print(f"  - Type: {type(snapshot_result)}")
                if isinstance(snapshot_result, dict):
                    print(f"  - Keys: {list(snapshot_result.keys())}")
                elif isinstance(snapshot_result, str) and len(snapshot_result) > 100:
                    print(f"  - Length: {len(snapshot_result)} characters")
                    print(f"  - Preview: {snapshot_result[:100]}...")
                
    print("\n✅ Browser automation test completed!")

if __name__ == "__main__":
    main()