import json

class ResponseParser:
    
    def parse(self, ai_response):
        """
        Parse Claude's JSON response into a Python dictionary
        
        Args:
            ai_response: String response from Claude (should be JSON)
        
        Returns:
            Dictionary with action details, or error action if parsing fails
        """
        
        # Try to parse JSON
        try:
            # Convert JSON string to Python dictionary
            action_dict = json.loads(ai_response)
            
            # Validate required fields exist
            if "action" not in action_dict:
                # Return error action - missing required field
                return {
                    "action": "error",
                    "message": "Response missing 'action' field",
                    "goal_complete": False
                }
            
            # Validate action type is valid
            valid_actions = ["navigate", "click", "fill", "complete", "error"]
            if action_dict["action"] not in valid_actions:
                # Return error action - invalid action type
                return {
                    "action": "error",
                    "message": f"Invalid action type: {action_dict['action']}",
                    "goal_complete": False
                }
            
            # Return the parsed dictionary
            return action_dict
            
        except json.JSONDecodeError as e:
            # JSON parsing failed - return error action
            return {
                "action": "error",
                "message": f"Failed to parse JSON: {str(e)}",
                "goal_complete": False
            }
        
        except Exception as e:
            # Some other error - return error action
            return {
                "action": "error",
                "message": f"Unexpected error: {str(e)}",
                "goal_complete": False
            }