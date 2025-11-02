# main.py
import subprocess
import time
import json
import requests          # <-- IMPORT HERE
from playwright.sync_api import sync_playwright
from mcp_client import browser_navigate, browser_snapshot

# ----------------------------------------------------------------------
def kill_port(port: int = 8931):
    """Kill anything already on the port (Windows friendly)."""
    import psutil, os, signal
    for conn in psutil.net_connections():
        if conn.laddr.port == port and conn.status == "LISTEN":
            p = psutil.Process(conn.pid)
            p.send_signal(signal.SIGTERM if os.name != "nt" else signal.CTRL_C_EVENT)
            print(f"Killed PID {conn.pid} on port {port}")

def start_mcp_server(port: int = 8931):
    kill_port(port)
    proc = subprocess.Popen(
        ["npx", "@playwright/mcp@latest", "--port", str(port)],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    time.sleep(3)                     # give the server a moment
    print(f"MCP server started on port {port}")
    return proc

# ----------------------------------------------------------------------
def launch_browser_and_attach(mcp_port: int = 8931):
    pw = sync_playwright().start()

    # 1. Launch Chromium with a free CDP port
    browser = pw.chromium.launch(
        headless=False,
        args=["--remote-debugging-port=0"]   # let Chromium pick a free port
    )

    # 2. Create a page so the browser is fully initialized
    context = browser.new_context()
    page = context.new_page()

    # 3. Find the CDP websocket URL that Playwright uses internally
    #    (Playwright exposes it on the browser object after the first page)
    cdp_ws_url = None
    try:
        # Playwright 1.44+ stores it here
        cdp_ws_url = page.context.browser._impl_obj._connection._ws_url
    except AttributeError:
        pass

    if not cdp_ws_url:
        # Fallback – read the debugging port from the launch response
        debug_port = browser._impl_obj._remote_debugging_port
        cdp_ws_url = f"ws://127.0.0.1:{debug_port}/devtools/browser"

    print(f"CDP endpoint: {cdp_ws_url}")

    # 4. Attach the browser to the MCP server
    attach_payload = {
        "jsonrpc": "2.0",
        "method": "session_attach",
        "params": {"endpoint": cdp_ws_url},
        "id": 1
    }
    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json, text/event-stream"
    }
    r = requests.post(
        f"http://localhost:{mcp_port}/mcp",
        json=attach_payload,
        headers=headers,
        timeout=10,
    )
    print(f"session_attach response: {r.json()}")

    print("Browser launched & attached to MCP")
    return pw, browser, context, page

# ----------------------------------------------------------------------
def cleanup(mcp_proc, pw, browser):
    browser.close()
    pw.stop()
    mcp_proc.terminate()
    print("Cleanup done")

# ----------------------------------------------------------------------
def main():
    mcp_proc = start_mcp_server()
    time.sleep(2)                     # make sure server is up

    pw, browser, context, page = launch_browser_and_attach()

    goal = input("Enter your goal: ").strip()
    if not goal:
        cleanup(mcp_proc, pw, browser)
        return

    print(f"\n--- Running goal: {goal} ---")
    browser_navigate("https://www.google.com")
    time.sleep(3)

    snap = browser_snapshot()
    if snap:
        print(f"Snapshot received – {len(snap.get('elements', []))} elements")
    else:
        print("Failed to get snapshot")

    input("\nPress Enter to close...")
    cleanup(mcp_proc, pw, browser)

if __name__ == "__main__":
    main()