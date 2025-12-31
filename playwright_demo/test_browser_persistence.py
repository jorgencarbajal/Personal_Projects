from src.mcp_client import SessionMCPClient
import time

def test_browser_stays_open():
    print("🧪 Testing if browser stays open...")
    print("=" * 50)
    
    # Initialize MCP client
    client = SessionMCPClient()
    if not client.complete_initialization():
        print("❌ Failed to initialize")
        return
    
    # Navigate to Google
    print("\n1. Navigate to Google...")
    result = client.send_tool_call("browser_navigate", {"url": "https://google.com"})
    print(f"Result: {result}")
    
    # Wait and watch if browser closes
    print("\n2. Waiting 10 seconds... (watch if browser closes)")
    for i in range(10, 0, -1):
        print(f"   {i} seconds remaining...")
        time.sleep(1)
    
    # Try another action
    print("\n3. Try to take snapshot (will fail if browser closed)...")
    result = client.send_tool_call("browser_snapshot", {})
    
    if result:
        print("✅ Browser still alive!")
    else:
        print("❌ Browser is gone!")
    
    print("\n4. Waiting another 10 seconds...")
    for i in range(10, 0, -1):
        print(f"   {i} seconds remaining...")
        time.sleep(1)
    
    print("\n✅ Test complete - did browser stay open the whole time?")

if __name__ == "__main__":
    test_browser_stays_open()