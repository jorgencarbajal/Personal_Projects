# test_mcp_full.py
from main import start_mcp_server, launch_browser, cleanup
from mcp_client import browser_navigate
import time

print("Starting MCP + Browser...")
mcp_proc = start_mcp_server()
pw, browser, ctx, page = launch_browser()

time.sleep(3)  # Wait for server

print("\n--- TESTING NAVIGATION ---")
browser_navigate("https://www.google.com")

input("\nPress Enter to close...")
cleanup(mcp_proc, pw, browser)