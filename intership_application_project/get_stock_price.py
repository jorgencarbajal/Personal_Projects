# Import necessary libraries
# sync_playwright: Provides synchronous Playwright API to control a web browser.
# Exception class for handling timeout errors in Playwright operations.
from playwright.sync_api import sync_playwright, TimeoutError
# datetime: Class for handling dates and times.
# timedelta: Class for representing duration or difference between dates/times.
from datetime import datetime, timedelta

# Function to determine the last trading day
def get_last_trading_day():
    today = datetime.now()
    if today.weekday() == 6:  # Sunday
        return today - timedelta(days=2)  # Friday
    elif today.weekday() == 0:  # Monday
        return today - timedelta(days=3)  # Friday
    return today - timedelta(days=1)  # Yesterday

# Main function to fetch SPY's last closing price
def fetch_spy_close():
    # Initializes a Playwright instance using sync_playwright() for synchronous browser control.
    # 'with' ensures the Playwright instance is properly managed (e.g., resources are cleaned up after use).
    # as p assigns the Playwright instance to the variable p for use within the block.
    with sync_playwright() as p:
        # Variable browser is assigned to a Chromium browser instance launched by the Playwright instance 
        # p with the UI visible for debugging.
        browser = p.chromium.launch(headless=True)
        # Variable page is assigned to a new browser page (tab) created by the browser instance for 
        # interacting with a web page.
        page = browser.new_page()

        try:
            # The variable page, a Playwright page object, uses its goto method to navigate to the 
            # URL https://finance.yahoo.com/quote/SPY/, 
            # with timeout=30000 setting a 30-second limit (in milliseconds) for loading, raising a 
            # TimeoutError if exceeded.
            page.goto("https://finance.yahoo.com/quote/SPY/", timeout=60000)

            # to speed things up lets select the right container
            # A CSS selector is a pattern used to target and style HTML elements on a webpage, like 
            # 'section.quote-statistics-container', where section is the element type and 
            # quote-statistics-container is a class, allowing your program to locate specific parts of 
            # the page.
            container_selector = 'section.quote-statistics-container'
            # Variable page calls wait_for_selector to wait up to 30 seconds (timeout=30000) for the 
            # element matching container_selector to become visible (state="visible") on the page, raising 
            # a TimeoutError if not found or visible within that time.
            page.wait_for_selector(container_selector, timeout=30000, state="visible")

            # Find price within container
            # "f'" is a f string, this essentially combines the string literals
            price_selector = f'{container_selector} fin-streamer[data-field="regularMarketPreviousClose"]'
            # Variable price_element is assigned a Playwright Locator object created by 
            # page.locator(price_selector), which represents the element(s) matching price_selector on 
            # the page, enabling further actions like retrieving text or checking visibility.
            price_element = page.locator(price_selector)

            # Variable price_element.count() returns the number of elements matching price_selector found 
            # by the price_element locator,
            if price_element.count() > 0:
                # Variable price is assigned the text content of the first element matched by price_element, 
                # retrieved using the inner_text() method of the Playwright locator.
                price = price_element.inner_text()
                print(f"Spy's last closing price was: ${price}")
            else:
                print("Error: Could not find SPY's closing price on the page.")

        except TimeoutError:
            print("Error: Page took too long to load or element not found.")
        except Exception as e:
            print(f"Error: An unexpected issue occurred: {str(e)}")

        # Close the browser
        browser.close()

# Run the script
if __name__ == "__main__":
    last_trading_day = get_last_trading_day()
    print(f"Fetching closing price for last trading day: {last_trading_day.strftime('%Y-%m-%d')}")
    fetch_spy_close()
