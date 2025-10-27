# Purpose: Handle LLM interactions for generating actions
# Tasks
    # Define function to query LLM (e.g., OpenAI API) with prompt including
        # user goal, current snapshot (accessibility tree), and instructions
        # to output single next action as JSON (e.g., {"method": 
        # "browser_click", "params": {"ref": 123, "element": "description"}})
    # Parse LLM response to extract JSON action