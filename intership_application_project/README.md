# SPY Closing Price Automation

This Python program uses Playwright to automate fetching the previous trading day's closing price for the SPY ETF from Yahoo Finance.

## Prerequisites
- Python: 3.7+
- Git

## Setup
1. Clone the Repository
   ```bash
   git clone https://github.com/jorgencarbajal/Personal_Projects.git
   cd Personal_Projects/intership_application_project
   ```
2. Install Dependencies
   ```bash
   pip install playwright
   playwright install
   ```
   
3. Run the Script
   ```bash
   python get_stock_price.py
   ```
## Expected Output
- Console prints, e.g, "Fetching closing price for last trading day: 2025-10-17" and "Spy's last closing price was: $580.76".

## Notes
- Only the intership_application_project folder is needed; other files in Personal_Projects are unrelated.
- Script targets finance.yahoo.com/quote/SPY/, no credentials required.
