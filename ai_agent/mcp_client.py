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
def send_mcp_request(method, params=None):

    # url now helps connect to the server
    url = "http://localhost:8931/mcp"

    # payload is essentially a map of all the methods and params
    payload = {"method": method, "params": params or {}}
    # the data being sent out and what we expect in return
    headers = {"Content-Type": "application/json", "Accept": "application/json"}

    try:
        # make a server request and get a reply
        response = requests.post(url, json=payload, headers=headers)

        # Variable response.raise_for_status() checks the HTTP status code of the response object and raises 
            # an exception (e.g., requests.HTTPError) if the request failed (e.g., 404 or 500), ensuring the 
            # program handles errors appropriately.
        response.raise_for_status()

        # Variable return response.json() sends back the data from the response object, parsed from JSON format 
            # into a Python dictionary or list, if the request was successful.
        return parse_mcp_response(response.json())
    
    except requests.RequestException as e:
        print(f"MCP request failed: {e}")
        return None
    
def browser_snapshot():
    # Request current page snapshot from MCP server
    return send_mcp_request("browser_snapshot")
    
# Variable def browser_click(ref, element): defines a function named browser_click that takes two 
    # parameters, ref (likely a reference to a page or context) and element (the element to click), to 
    # encapsulate browser clicking logic.
def browser_click(ref, element):

    # Send click action to MCP server for element with given ref and description
    # Variable params is assigned a dictionary with keys "ref" and "element", set to the values of 
        # ref and element respectively, structuring them as data to be passed in a request or operation.
    params = {"ref": ref, "element": element}

    return send_mcp_request("browser_click", params)

def browser_navigate(url):
    # Navigate to specified URL via MCP server
    params = {"url": url}
    return send_mcp_request("browser_navigate", params)

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
