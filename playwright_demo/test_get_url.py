from src.browser.browser_actions import BrowserAutomator
import time

def test_get_url():
    print("🧪 Testing get_current_url()...")
    print("=" * 50)
    
    # Test 1: Amazon (fresh browser)
    print("\n📍 Test 1: Amazon")
    browser1 = BrowserAutomator()
    browser1.initialize()
    browser1.navigate_to_website("https://amazon.com")
    time.sleep(5)
    url1 = browser1.get_current_url()
    print(f"Result: {url1}")
    
    # Test 2: Google (fresh browser)
    print("\n📍 Test 2: Google")
    browser2 = BrowserAutomator()
    browser2.initialize()
    browser2.navigate_to_website("https://google.com")
    time.sleep(5)
    url2 = browser2.get_current_url()
    print(f"Result: {url2}")
    
    # Test 3: GitHub (fresh browser)
    print("\n📍 Test 3: GitHub")
    browser3 = BrowserAutomator()
    browser3.initialize()
    browser3.navigate_to_website("https://github.com")
    time.sleep(5)
    url3 = browser3.get_current_url()
    print(f"Result: {url3}")
    
    print("\n✅ Test completed!")

if __name__ == "__main__":
    test_get_url()