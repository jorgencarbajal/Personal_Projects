"""
MCP Client using session ID from initial connection

This script creates a Python client that connects to your MCP server (running on localhost:3000) and establishes a persistent session with it. It handles the MCP initialization handshake, manages session IDs so the server knows who you are across multiple requests, and provides methods to send tool calls (like Playwright browser commands) to the server. Essentially, it's the bridge between your Python code and the Playwright MCP server—it manages the conversation protocol, tracks request IDs, parses responses, and keeps you authenticated throughout the interaction.

"""
# libary for making HTTP requests, (GET, POST, PUT, DELETE, etc.), to web servers
# using this to send JSON-RPC messages to MCP server (python programs talking to mcp servers)
import requests

# conversion between Pyton objects and json (a text format for data)
# used to parse the the servers responses and format outgoing requests
import json

# the client object... everything in one place
class SessionMCPClient:

    # set up client with the server url. initialize empty session id and requests id counter
    # __init__ is Python's special constructor method—it automatically runs whenever you create a new instance of the class
    # self refers to the instance being created
    # base_url defined and initailized in this parameter list
    def __init__(self, base_url="http://localhost:3000"):
        # create variable for the url
        self.base_url = base_url
        # creates url's of the endpoints
        self.mcp_url = f"{base_url}/mcp"
        self.sse_url = f"{base_url}/sse"
        # creating a persistent HTTP session that remembers things across multiple requests—cookies, connection pooling, headers you've set before
        self.session = requests.Session()
        # Initializes session ID as empty; gets filled in once you establish the connection
        self.session_id = None
        # request counte needed for JSON-RPC protocol, when you send a request with an ID, the server includes that same ID in its response so you know which response matches which request
        self.request_id = 1
    
    # increments and returns the next request id (used to track which response belongs to which request in the JSON-RPC protocol)
    def get_next_id(self):
        self.request_id += 1
        return self.request_id
    
    # extracts and converts the sse (server sent events) formatted text response from the server into a python dictionary
    def parse_sse_response(self, response_text):
        """Parse Server-Sent Events format response"""
        # organizes the response into newlines starting with "data". converting the SSE-formatted text into clean JSON that Python's json library can actually understand and convert into a usable dictionary
        lines = response_text.strip().split('\n')
        # list comprehension... further parses the data into lines that start with 'data:'. 'line' is like variable in the auto for loop c++
        data_lines = [line for line in lines if line.startswith('data: ')]
        # check if data_lines has any items
        if data_lines:
            # starting with the last item in the list, '-1', and skipping the first 6 characters '[6:]' removing data prefix, 
            json_str = data_lines[-1][6:]
            try:
                # tries to convert the json string into pyton dictionary, json is a module/library for handling json data, load s is a function "load string"
                return json.loads(json_str)
            # if json.loads() fails this exception is thrown
            except json.JSONDecodeError:
                return None
        return None
    
    # sends initialization handshake to the server and captures the session id from the response header
    def establish_session(self):
        """First establish a session via MCP endpoint"""
        print("=== Establishing Session ===")
        
        # creates a json-rpc request dictionary
        # In plain English: You're saying to the server: "Hi, I'm a Python client version 1.0.0 that speaks MCP 2024-11-05. Please initialize our connection.
        payload = {
            # json protocol
            "jsonrpc": "2.0",
            # a unique request id
            "id": self.get_next_id(),
            # telling the server what method/action to perform
            "method": "initialize",
            # arguments for the initialize method, nested dictionary
            "params": {
                # version of the mcp protocol
                "protocolVersion": "2024-11-05",
                # special features the client supports
                "capabilities": {},
                # client info
                "clientInfo": {
                    "name": "python-session-client",
                    "version": "1.0.0"
                }
            }
        }
        
        # creates an HTTP headers dicitonary the tells the server what kind of data youre sending and what your willing to recieve
        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json, text/event-stream"
        }
        
        try:
            # send request and recieve response and store in response
            # for the mcp protocol the initialization happens on the mcp endpoint
            response = self.session.post(self.mcp_url, json=payload, headers=headers)
            # checks the status code
            print(f"Initialize status: {response.status_code}")
            
            if response.status_code == 200:
                # Extract session ID
                # response.headers is a dictionary like object in all HTTP responses containing metadata headers sent by the server. Here we are checking if the server included 'mcp-session-id as a header
                if 'mcp-session-id' in response.headers:
                    # extracting that specific header value
                    self.session_id = response.headers['mcp-session-id']
                    print(f"✅ Session established: {self.session_id}")
                    
                    parsed_data = self.parse_sse_response(response.text)
                    if parsed_data:
                        # Does the opposite of 'json.loads', this takes a python dictionary and converts it back to json string for printing. 'indent=2' makes it nice and cute
                        print(f"Initialize response: {json.dumps(parsed_data, indent=2)}")
                        return True
            # got response but something is missing...
            print("❌ Failed to establish session")
            return False
        # this is thrown when something went wrong before we get reponse  
        except Exception as e:
            print(f"Session establishment failed: {e}")
            return False
    
    # builds json-rpc request payload, include the session id, and posts it to the server, then handles and prints reponses
    def send_with_session(self, method, params=None, is_notification=False, use_sse=False):
        """Send request with session ID"""
        # sets the payload
        payload = {
            "jsonrpc": "2.0",
            "method": method
        }
        
        # Is this a response or a notification? If notification, skip, else creat and set the session id for the payload
        if not is_notification:
            payload["id"] = self.get_next_id()
        
        # if there are parameters add them
        if params:
            payload["params"] = params
        
        # Add session ID for SSE endpoint
        if use_sse and self.session_id:
            payload["sessionId"] = self.session_id
        
        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json, text/event-stream"
        }
        
        # Add session ID to headers if we have it
        if self.session_id:
            headers["mcp-session-id"] = self.session_id
        
        endpoint = self.sse_url if use_sse else self.mcp_url
        endpoint_name = "SSE" if use_sse else "MCP"
        
        try:
            response = self.session.post(endpoint, json=payload, headers=headers)
            print(f"{endpoint_name} Method: {method} {'(notification)' if is_notification else ''}")
            print(f"Status: {response.status_code}")
            
            if response.status_code == 200:
                parsed_data = self.parse_sse_response(response.text)
                if parsed_data:
                    print(f"Response: {json.dumps(parsed_data, indent=2)}")
                    return parsed_data
                else:
                    print(f"Raw response: {response.text}")
                    return {"success": True}
            else:
                try:
                    error_data = json.loads(response.text)
                    print(f"Error: {json.dumps(error_data, indent=2)}")
                    return error_data
                except:
                    print(f"Error response: {response.text}")
            
            return None
        except Exception as e:
            print(f"Request failed: {e}")
            return None
    
    # orchastrates the full setup process be establishing a session, sending initialization notifications, and testing tools/list to confirm everything works
    def complete_initialization(self):
        """Complete the full MCP initialization"""
        print("\n=== Complete MCP Initialization ===")
        
        # Step 1: 'establich_session' returns true or false if the session was established
        if not self.establish_session():
            return False
        
        # Step 2: Try initialized notification with session
        print("\n2. Send initialized notification (MCP endpoint):")
        notification_result = self.send_with_session("initialized", is_notification=True, use_sse=False)
        
        if notification_result and not notification_result.get("error"):
            print("✅ Initialized notification successful (MCP)")
        else:
            print("⚠ Initialized notification failed (MCP), trying SSE...")
            
            # Try SSE endpoint
            print("\n2b. Send initialized notification (SSE endpoint):")
            sse_notification = self.send_with_session("initialized", is_notification=True, use_sse=True)
            
            if not sse_notification or sse_notification.get("error"):
                print("❌ Initialized notification failed on both endpoints")
        
        # Step 3: Test tools/list on both endpoints
        print("\n3. Test tools/list (MCP endpoint):")
        tools_result = self.send_with_session("tools/list", use_sse=False)
        
        if tools_result and not tools_result.get("error"):
            print("🎉 SUCCESS! Tools working via MCP endpoint!")
            return True
        
        print("\n3b. Test tools/list (SSE endpoint):")
        sse_tools_result = self.send_with_session("tools/list", use_sse=True)
        
        if sse_tools_result and not sse_tools_result.get("error"):
            print("🎉 SUCCESS! Tools working via SSE endpoint!")
            return True
        
        print("❌ Tools/list failed on both endpoints")
        return False
    
    # a convenience wrapper that formats a tool call (like a playwright command) and sends it via "send_with_session"
    def send_tool_call(self, tool_name, parameters=None):
        """Send a tool call (tools/call method)"""
        if not self.session_id:
            print("❌ No active session. Initialize first.")
            return None
        
        params = {
            "name": tool_name
        }
        if parameters:
            params["arguments"] = parameters
        
        return self.send_with_session("tools/call", params, use_sse=False)

if __name__ == "__main__":
    client = SessionMCPClient()
    success = client.complete_initialization()
    
    if success:
        print("\n🎉 MCP Client successfully initialized!")
    else:
        print("\n❌ MCP Client initialization failed")