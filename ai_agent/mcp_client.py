# Purpose: Helper module for interacting with MCP server via HTTP
# Tasks: 
    # Define function to send MCP requests (e.g., browser_navigate, 
        # browser_snapshot, browser_click) using requests.post to 
        # http://localhost:8931/mcp.
    # Parse responses and handle errors

import requests  # Enables HTTP requests to communicate with MCP server at http://localhost:8931/mcp
import json      # Handles parsing and formatting JSON data for MCP requests and responses

# method represents the actions that the client tells the mcp server what to do
# method: what to do; params: how to do it
# def send_mcp_request(method: str, params: dict | None=None):

#     # url now helps connect to the server
#     url = "http://localhost:8931/mcp"

#     # payload is essentially a map of all the methods and params
#     payload = {"method": method}
#     if params:
#         payload["params"] = params
#     # the data being sent out and what we expect in return
#     #headers = {"Content-Type": "application/json", "Accept": "application/json"}

#     try:
#         # make a server request and get a reply
#         #response = requests.post(url, json=payload, headers=headers)
#         response = requests.post(
#             url,
#             json=payload,  # ← sends correct JSON + Content-Type
#             headers={"Content-Type": "application/json", "Accept": "application/json"},
#             timeout=10
#         )

#         # immediately turns HTTP errors (like 404, 500) into Python exceptions
#         #response.raise_for_status()

#         # response.json() sends back the data from the response object, parsed from JSON format 
#             # into a Python dictionary or list, if the request was successful.
#         return parse_mcp_response(response.json())
    
#     except requests.RequestException as e:
#         print(f"MCP request (ahh shet) failed: {e}")
#         return None


def send_mcp_request(method: str, params: dict | None = None):
    url = "http://localhost:8931/mcp"
    payload = {
        "jsonrpc": "2.0",          # REQUIRED
        "method": method,
        "params": params or {},
        "id": 1                    # REQUIRED
    }
    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json, text/event-stream"
    }
    print("\n=== MCP REQUEST DEBUG ===")
    print(f"URL: {url}")
    print(f"Payload: {payload}")   # Now shows jsonrpc and id
    print(f"Headers: {headers}")
    try:
        response = requests.post(url, json=payload, headers=headers, timeout=10)
        print(f"Status: {response.status_code}")
        print(f"Response Body: {response.text[:500]}")
        print("=======================\n")

        response.raise_for_status()
        data = response.json()
        return parse_mcp_response(data)

    except requests.exceptions.HTTPError as e:
        print(f"HTTP ERROR: {e}")
        return None
    except json.JSONDecodeError:
        print("NOT JSON RESPONSE")
        return None
    except Exception as e:
        print(f"Request failed: {e}")
        return None


    
# def browser_snapshot():
#     # Request current page snapshot from MCP server
#     return send_mcp_request("browser_snapshot")
def browser_snapshot():
    print("[MCP] Requesting snapshot...")
    result = send_mcp_request("browser_snapshot")
    if result is None:
        print("[MCP] FAILED to get snapshot")
    else:
        print(f"[MCP] Got snapshot with {len(result.get('elements', []))} elements")
    return result
    
def browser_click(ref, element):
    # Send click action to MCP server for element with given ref and description
    params = {"ref": ref, "element": element}
    return send_mcp_request("browser_click", params)

# def browser_navigate(url):
#     # Navigate to specified URL via MCP server
#     params = {"url": url}
#     return send_mcp_request("browser_navigate", params)
def browser_navigate(url: str):
    print(f"[MCP] Navigating to: {url}")
    result = send_mcp_request("browser_navigate", {"url": url})
    if result is None:
        print(f"[MCP] FAILED to navigate to {url}")
    else:
        print(f"[MCP] SUCCESS: Navigated to {url}")
    return result

def browser_type(ref, element, text):
    # Send text input action to MCP server for element with given ref and description
    params = {"ref": ref, "element": element, "text": text}
    return send_mcp_request("browser_type", params)

def parse_mcp_response(response):
    # Parse MCP response, check for errors, and return result
    if response and "result" in response:
        return response["result"]
    print("Error: Invalid MCP response")
    return None

def initialize_mcp():
    print("[MCP] Initializing server...")
    result = send_mcp_request("initialize", {"capabilities": {}})
    if result is None:
        print("[MCP] FAILED to initialize")
    else:
        print("[MCP] Server initialized successfully")
    return result
