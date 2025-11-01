# Purpose: Helper module for interacting with MCP server via HTTP
# Tasks: 
    # Define function to send MCP requests (e.g., browser_navigate, 
        # browser_snapshot, browser_click) using requests.post to 
        # http://localhost:8931/mcp.
    # Parse responses and handle errors

import requests  # Enables HTTP requests to communicate with MCP server at http://localhost:8931/mcp
import json      # Handles parsing and formatting JSON data for MCP requests and responses

# method is a variable representing the name of the action or operation to perform (e.g., "get", "set"), 
    # passed as an argument to the send_mcp_request function.
# params is an optional variable (default None) representing a dictionary of parameters or data to send 
    # with the method, used to customize the request (e.g., {"id": 123}); if None, it defaults to an empty 
    # dictionary {} in the payload.
def send_mcp_request(method, params=None):

    # Send HTTP POST request to MCP server with method and optional params
    # Variable url is assigned the string "http://localhost:8931/mcp", representing a local server 
        # address (port 8931) for accessing a specific resource or page.
    url = "http://localhost:8931/mcp"

    # Variable payload is assigned a dictionary with keys "method" (set to the method variable) 
        # and "params" (set to params if it exists, otherwise an empty dictionary {}), used to structure 
        # data for an API or request. A POST request is a method to send data (e.g., payload) to a server 
        # to create or update a resource, and the result typically includes the server’s response status 
        # (e.g., 200 for success) and data (e.g., JSON, text) if provided.
    # The requests library is a popular Python module for making HTTP requests (e.g., GET, POST) to 
        # interact with web servers or APIs. It simplifies sending requests and handling responses compared 
        # to lower-level methods.
    payload = {"method": method, "params": params or {}}
    headers = {"Content-Type": "application/json", "Accept": "application/json"}  # ADD THIS LINE

    try:
        # The response = requests.post(url, json=payload) line sends an HTTP POST request to the specified 
            # url using the requests library, encoding the payload dictionary as JSON data for the server. 
            # The requests library is a Python module that simplifies making HTTP requests and handling 
            # responses, while the result is a response object containing the server’s reply, including 
            # status and data. JSON encoding converts the payload dictionary into a JSON-formatted string 
            # for data exchange with the server.
        response = requests.post(url, json=payload, headers=headers)  # ADD headers

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

def parse_mcp_response(response):
    # Parse MCP response, check for errors, and return result
    if response and "result" in response:
        return response["result"]
    print("Error: Invalid MCP response")
    return None

def browser_type(ref, element, text):
    # Send text input action to MCP server for element with given ref and description
    params = {"ref": ref, "element": element, "text": text}
    return send_mcp_request("browser_type", params)