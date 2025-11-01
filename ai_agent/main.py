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

def launch_browser():
    playwright = sync_playwright().start()
    browser = playwright.chromium.launch(headless=True)
    context = browser.new_context(
        viewport={"width": 1366, "height": 900},
        locale="en-US",
        timezone_id="UTC"
    )
    page = context.new_page()
    print("Browser launched")
    return playwright, browser, context, page

def is_goal_complete(goal, snapshot):
    goal_lower = goal.lower()
    page_text = " ".join([elem.get("text", "") for elem in snapshot.get("elements", [])]).lower()
    return any(keyword in page_text for keyword in goal_lower.split())

def cleanup(mcp_process, playwright, browser):
    browser.close()
    playwright.stop()
    mcp_process.terminate()
    print("Cleanup complete")

def main():
    mcp_process = start_mcp_server()
    playwright, browser, context, page = launch_browser()
    
    goal = input("Enter your goal: ").strip()
    if not goal:
        print("Goal required.")
        cleanup(mcp_process, playwright, browser)
        return

    browser_navigate("https://www.google.com")
    time.sleep(2)
    print(f"Starting AI agent for goal: {goal}")

    max_steps = 20
    for step in range(max_steps):
        snapshot = browser_snapshot()
        if not snapshot:
            print("Failed to get page snapshot")
            break

        if is_goal_complete(goal, snapshot):
            print("Goal achieved!")
            print("Final page text:", " ".join([elem.get("text", "") for elem in snapshot.get("elements", [])])[:200])
            break

        action = query_llm(goal, snapshot)
        if not action:
            print("LLM failed to return action")
            break

        print(f"Step {step + 1}: {action['method']} → {action['params']}")

        if action["method"] == "browser_click":
            result = browser_click(**action["params"])
        elif action["method"] == "browser_type":
            result = browser_type(**action["params"])
        elif action["method"] == "browser_navigate":
            result = browser_navigate(**action["params"])
        else:
            print(f"Unknown method: {action['method']}")
            break

        if not result:
            print("Action failed")
            break

        time.sleep(1)

    cleanup(mcp_process, playwright, browser)

if __name__ == "__main__":
    main()