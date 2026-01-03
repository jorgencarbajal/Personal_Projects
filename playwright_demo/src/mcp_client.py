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
        """Launch MCP server as subprocess"""
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
        """Background thread that reads server responses"""
        while self.process and self.process.poll() is None:
            try:
                line = self.process.stdout.readline()
                if line:
                    response = json.loads(line.strip())
                    self.response_queue.put(response)
            except:
                break
    
    def _send_request(self, method, params=None, is_notification=False):
        """Send JSON-RPC request via stdin"""
        request = {
            "jsonrpc": "2.0",
            "method": method
        }
        
        if not is_notification:
            request["id"] = self.get_next_id()
        
        if params:
            request["params"] = params
        
        message = json.dumps(request) + '\n'
        self.process.stdin.write(message)
        self.process.stdin.flush()
        
        # Wait for response (skip for notifications)
        if not is_notification:
            return self.response_queue.get(timeout=30)
        return None
    
    def establish_session(self):
        """Initialize connection with MCP server"""
        print("=== Establishing Session ===")
        
        if not self.process:
            self._start_server()
        
        params = {
            "protocolVersion": "2024-11-05",
            "capabilities": {},
            "clientInfo": {
                "name": "python-stdio-client",
                "version": "1.0.0"
            }
        }
        
        try:
            response = self._send_request("initialize", params)
            print(f"Initialize response: {json.dumps(response, indent=2)}")
            
            if "result" in response:
                self.session_id = "stdio-session"  # Stdio doesn't use session IDs
                print("✅ Session established")
                return True
                
            print("❌ Failed to establish session")
            return False
        except Exception as e:
            print(f"Session establishment failed: {e}")
            return False
    
    def complete_initialization(self):
        """Complete MCP initialization"""
        print("\n=== Complete MCP Initialization ===")
        
        if not self.establish_session():
            return False
        
        print("\n2. Send initialized notification:")
        self._send_request("initialized", is_notification=True)
        print("✅ Initialized notification sent")
        
        print("\n3. Test tools/list:")
        tools_result = self._send_request("tools/list")
        
        if tools_result and "result" in tools_result:
            print("🎉 SUCCESS! Tools working!")
            return True
        
        print("❌ Tools/list failed")
        return False
    
    def send_tool_call(self, tool_name, parameters=None):
        """Send a tool call"""
        if not self.session_id:
            print("❌ No active session. Initialize first.")
            return None
        
        params = {
            "name": tool_name
        }
        if parameters:
            params["arguments"] = parameters
        
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