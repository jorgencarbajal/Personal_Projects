import subprocess
import time
import json
from playwright.sync_api import sync_playwright
from mcp_client import browser_navigate, browser_snapshot, browser_click, browser_type
from llm_agent import query_llm

def start_mcp_server(port=8931):
    # Use npm exec (works on Windows, avoids npx.ps1)
    import shutil
    npm = shutil.which("npm")
    if not npm:
        raise RuntimeError("npm not found. Verify Node.js installation.")
    
    process = subprocess.Popen(
        [npm, "exec", "--", "@playwright/mcp@latest", "--port", str(port)],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )
    time.sleep(3)
    print(f"MCP server started on port {port}")
    return process

# def launch_browser():
#     playwright = sync_playwright().start()
#     browser = playwright.chromium.launch(headless=False)
#     context = browser.new_context(
#         viewport={"width": 1366, "height": 900},
#         locale="en-US",
#         timezone_id="UTC"
#     )
#     page = context.new_page()
#     print("Browser launched")
#     return playwright, browser, context, page
def launch_browser_and_attach(mcp_port=8931):
    pw = sync_playwright().start()
    browser = pw.chromium.launch(headless=False)
    
    # Create a context and page FIRST
    context = browser.new_context()
    page = context.new_page()
    
    # Now get CDP URL from the browser
    # Playwright exposes CDP via the browser's connection
    cdp_url = browser._connection._transport._ws._url if hasattr(browser._connection, '_transport') else None
    if not cdp_url:
        # Fallback: use the browser's CDP endpoint from launch
        cdp_url = f"ws://127.0.0.1:{browser._impl_obj._remote_debugging_port}/devtools/browser/{browser._impl_obj._browser_id}"
    
    print(f"CDP URL: {cdp_url}")

    # Attach to MCP
    attach_payload = {
        "jsonrpc": "2.0",
        "method": "session_attach",
        "params": {"endpoint": cdp_url},
        "id": 1
    }
    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json, text/event-stream"
    }
    response = requests.post(f"http://localhost:{mcp_port}/mcp", json=attach_payload, headers=headers)
    print(f"Attach response: {response.json()}")

    print("Browser launched and attached to MCP")
    return pw, browser, context, page

def is_goal_complete(goal, snapshot):
    goal_lower = goal.lower()
    page_text = " ".join([elem.get("text", "") for elem in snapshot.get("elements", [])]).lower()
    return any(keyword in page_text for keyword in goal_lower.split())

def cleanup(mcp_process, playwright, browser):
    browser.close()
    playwright.stop()
    mcp_process.terminate()
    print("Cleanup complete")

# def main():
#     mcp_process = start_mcp_server()
#     playwright, browser, context, page = launch_browser()
    
#     goal = input("Enter your goal: ").strip()
#     if not goal:
#         print("Goal required.")
#         cleanup(mcp_process, playwright, browser)
#         return

#     browser_navigate("https://www.google.com")
#     time.sleep(2)
#     print(f"Starting AI agent for goal: {goal}")

#     max_steps = 20
#     for step in range(max_steps):
#         snapshot = browser_snapshot()
#         if not snapshot:
#             print("Failed to get page snapshot")
#             break

#         if is_goal_complete(goal, snapshot):
#             print("Goal achieved!")
#             print("Final page text:", " ".join([elem.get("text", "") for elem in snapshot.get("elements", [])])[:200])
#             break

#         action = query_llm(goal, snapshot)
#         if not action:
#             print("LLM failed to return action")
#             break

#         print(f"Step {step + 1}: {action['method']} → {action['params']}")

#         if action["method"] == "browser_click":
#             result = browser_click(**action["params"])
#         elif action["method"] == "browser_type":
#             result = browser_type(**action["params"])
#         elif action["method"] == "browser_navigate":
#             result = browser_navigate(**action["params"])
#         else:
#             print(f"Unknown method: {action['method']}")
#             break

#         if not result:
#             print("Action failed")
#             break

#         time.sleep(1)

#     cleanup(mcp_process, playwright, browser)
def main():
    mcp_proc = start_mcp_server()
    time.sleep(3)

    pw, browser, context, page = launch_browser_and_attach()

    goal = input("Enter your goal: ").strip()
    if not goal:
        cleanup(mcp_proc, pw, browser)
        return

    print(f"Starting AI agent for goal: {goal}")

    browser_navigate("https://www.google.com")
    time.sleep(3)

    snap = browser_snapshot()
    print(f"Snapshot elements: {len(snap.get('elements', [])) if snap else 0}")

    input("Press Enter to close...")
    cleanup(mcp_proc, pw, browser)

if __name__ == "__main__":
    main()