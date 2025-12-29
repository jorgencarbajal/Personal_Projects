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

from src.browser.browser_actions import BrowserAutomator

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
    if browser.navigate_to_website("https://www.theodinproject.com/paths/full-stack-javascript"):
        print(f"Session ID after navigation: {browser.client.session_id}")
        
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