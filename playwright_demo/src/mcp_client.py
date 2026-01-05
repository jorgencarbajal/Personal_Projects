"""
MCP Client using stdio transport

This connects to the Playwright MCP server via subprocess stdin/stdout instead of HTTP.
"""
# imports python subprocesses which lets you launch and control external programs from python script
import subprocess
# python json module that converts between python dictionaries and json strings
import json
# module that lets your run muliple pieces of code at the same time (In this case so the notifications dont get mixed with the reponses?)
import threading
# importing the data structure
from queue import Queue

# The SessionMCPClient class that is contains all the necessary functions for client objects
class SessionMCPClient:

    def __init__(self):
        """
        Constructor that initializes stdio-based MCP client variables
        """
        # Once the server starts this holds a Popen object. This is the handle to the running MCP server subprocess - it's the "remote control" that lets you talk to it.
        self.process = None
        # Used to generate unique ID's for each JSON-RPC request sent the the server.
        self.request_id = 1
        # This stores the session identifier after the MCP connection is established
        self.session_id = None
        # Thread safe data structure that stores server responses added by the backround thread and retrieved by the main thread.
        self.response_queue = Queue()
        # Holds the background Thread object that continuously reads stdout and fills response_queueariable that will continuily fill response_queue
        self.reader_thread = None
        
    def get_next_id(self):
        """
        Returns the current request ID, then increments it for the next request. Each ID matches a request to its corresponding response.
        """
        current = self.request_id
        self.request_id += 1
        return current
    
    def _start_server(self):
        """
        Launch MCP server subprocess via npx and start daemon thread to continuously read server responses from stdout and place them in response_queue.
        """
        print("=== Starting MCP Server ===")
        # "Process Open" launches a new program as a separate process and gives you control over it. 
        self.process = subprocess.Popen(
            # This line runs the npx.cmd with @playwright/mcp as an argument. Because 'shell=True' below the line knows to run this with cmd.exe
            ['npx', '@playwright/mcp'],
            # Creates a pipe communication channel for sending data TO the subprocess
            stdin=subprocess.PIPE,
            # Creates a pipe for receiving data FROM the subprocess
            stdout=subprocess.PIPE,
            # Creates a pipe for receiving ERROR messages from the subprocess
            stderr=subprocess.PIPE,
            # Tells Popen to use strings instead of bytes
            text=True,
            # bufsize=1 with text=True means line buffering - sends/receives complete lines at once when '\n' is written
            bufsize=1,
            # When shell is true this runs the first command "['npx', '@playwright/mcp']" through the system shell (cmd.exe)
            shell=True
        )
        
        # Start background thread to read responses
        # Consider the Thread object to be a backround worker that runs code in parallel.
        # Create background worker thread to continuously read server responses. 
        # target=function to run, daemon=True auto-kills thread when main program exits
        self.reader_thread = threading.Thread(target=self._read_responses, daemon=True)
        # Launch background thread - begins running _read_responses() in parallel with main code
        self.reader_thread.start()
        print("✅ Server started")
    
    def _read_responses(self):
        """
        This is a loop that continues as long as the server as been started AND it is still running. 'self.process.poll() returns None if the process is still running
        """
        while self.process and self.process.poll() is None:
            try:
                # Reads a complete line from the MCP server's stdout pipe and stores it in line
                line = self.process.stdout.readline()
                # if there was something to read, we us json loads ()
                if line:
                    # strips the whitespaces/newlines at the ends and loads the string into a dictionary
                    response = json.loads(line.strip())
                    # add the response dictionary to the back of the queue
                    self.response_queue.put(response)
            except:
                print(f"❌ Background thread error: {e}")
                break
    
    def _send_request(self, method, params=None, is_notification=False):
        """
        Send JSON-RPC request to MCP server via stdin.

        - Build JSON-RPC request dictionary with method name
        - Add unique ID if NOT a notification (notifications don't get IDs)
        - Add parameters if provided
        - Convert dictionary to JSON string and add newline
        - Write message to server's stdin
        - Flush buffer to send immediately
        - Wait for response from queue (skip for notifications)
        - Return response dictionary (or None for notifications)
        """
        
        # creating a dictionary that will become json-rpc message to send to the server
        request = {
            "jsonrpc": "2.0",
            "method": method
        }
        
        # If it is not a notification set it to the current id and increment request_id
        if not is_notification:
            request["id"] = self.get_next_id()
        
        # If there are parameters, set them
        if params:
            request["params"] = params
        # Convert request dictionary to JSON string and add newline for line buffering
        message = json.dumps(request) + '\n'
        # We then send the message to the server
        self.process.stdin.write(message)
        # Force buffered data to send immediately (don't wait for buffer to fill)
        self.process.stdin.flush()
        
        # Wait for response (skip for notifications)
        if not is_notification:
            # Wait up to 30 seconds for response from queue (responses are dictionaries)
            return self.response_queue.get(timeout=30)
        return None
    
    def establish_session(self):
        """
        Establish session with MCP server:
        - Check if server is running; start it if not
        - Send initialization request with client info and protocol version
        - Check server response for success ("result" key)
        - Return True if successful, False otherwise
        """
        print("=== Establishing Session ===")
        
        # If there isnt a server start one
        if not self.process:
            self._start_server()
        
        # These are parameters used to tell the server about the client (initial handshake)
        params = {
            # Which protocol the client speaks
            "protocolVersion": "2024-11-05",
            # Tell the server what features the client supports
            "capabilities": {},
            # Identifies who/what the client is
            "clientInfo": {
                "name": "python-stdio-client",
                "version": "1.0.0"
            }
        }
        
        # Attempt to initialize connection with MCP server 
        try:
            # Send the initilization request
            response = self._send_request("initialize", params)
            # Convert response dict to formatted JSON string for readable output
            print(f"Initialize response: {json.dumps(response, indent=2)}")
            
            # Check for "result" key to confirm successful initialization (vs error response)
            if "result" in response:
                self.session_id = "stdio-session"  # Stdio doesn't use session IDs
                print("✅ Session established")
                return True
            
            # If establishing the session fails
            print("❌ Failed to establish session")
            return False
        
        # Catch any errors during initialization (e.g., server crash, connection issues, malformed response)
        except Exception as e:
            print(f"Session establishment failed: {e}")
            return False
    
    def complete_initialization(self):
        """
        Complete MCP initialization handshake.

        - Establish the session
        - Send initialized notification to confirm readiness
        - Check for the available tools
        """
        print("\n=== Complete MCP Initialization ===")
        
        # This is the function call that establishes the session
        if not self.establish_session():
            return False
        
        # Send 'initialized' notification - required by MCP protocol to confirm client is ready
        print("\n2. Send initialized notification:")
        self._send_request("initialized", is_notification=True)
        print("✅ Initialized notification sent")
        
        # Response structure: {"result": {"tools": [...]}}
        print("\n3. Test tools/list:")
        tools_result = self._send_request("tools/list")
        
        # If there is something returned from the tools result and there is a value for the "result" key then we show success and return true.
        if tools_result and "result" in tools_result:
            print("🎉 SUCCESS! Tools working!")
            return True
        
        # If tools/list request failed or returned no result
        print("❌ Tools/list failed")
        return False
    
    def send_tool_call(self, tool_name, parameters=None):
        """
        Call an MCP tool with given parameters.

        - Check for active session
        - Build tool call parameters
        - Send request and return response
        """

        if not self.session_id:
            print("❌ No active session. Initialize first.")
            return None
        
        # Build params dict with tool name
        params = {
            "name": tool_name
        }
        # Add arguments to params if provided
        if parameters:
            params["arguments"] = parameters
        
        # Send tool call request and return response dictionary
        return self._send_request("tools/call", params)
    
    def close(self):
        """Close the server process"""
        if self.process:
            self.process.terminate()
            self.process.wait()


if __name__ == "__main__":
    client = SessionMCPClient()
    success = client.complete_initialization()
    
    if success:
        print("\n🎉 MCP Client successfully initialized!")
    else:
        print("\n❌ MCP Client initialization failed")