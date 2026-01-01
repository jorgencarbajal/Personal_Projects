from src.ai.prompt_builder import PromptBuilder

def test_prompt_builder():
    print("🧪 Testing Prompt Builder...")
    print("=" * 50)
    
    # Create builder
    builder = PromptBuilder()
    
    # Sample inputs (simulating real data)
    goal = "Find the cheapest laptop under $500"
    snapshot =  """- textbox "Search" [ref=e26]
                - button "Submit" [ref=e27] [cursor=pointer]
                - link "Electronics" [ref=e28]
                """
    page_url = "https://amazon.com"
    step_number = 1
    
    # Build prompt
    prompt = builder.build(goal, snapshot, page_url, step_number)
    
    # Show result
    print("Generated Prompt:")
    print("-" * 50)
    print(prompt)
    print("-" * 50)
    print("\n✅ Prompt builder test completed!")

if __name__ == "__main__":
    test_prompt_builder()