import requests
import json

def send_mcp_request(method, params=None):
    # Send HTTP POST request to MCP server with method and optional params
    url = "http://localhost:8931/mcp"
    payload = {"method": method, "params": params or {}}
    try:
        response = requests.post(url, json=payload)
        response.raise_for_status()
        return parse_mcp_response(response.json())
    except requests.RequestException as e:
        print(f"MCP request failed: {e}")
        return None

def parse_mcp_response(response):
    # Parse MCP response, check for errors, and return result
    if response and "result" in response:
        return response["result"]
    print("Error: Invalid MCP response")
    return None

def browser_snapshot():
    # Request current page snapshot from MCP server
    return send_mcp_request("browser_snapshot")

def browser_click(ref, element):
    # Send click action to MCP server for element with given ref and description
    params = {"ref": ref, "element": element}
    return send_mcp_request("browser_click", params)

def browser_navigate(url):
    # Navigate to specified URL via MCP server
    params = {"url": url}
    return send_mcp_request("browser_navigate", params)