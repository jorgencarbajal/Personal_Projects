from src.orchestrator import Orchestrator

def test_simple_goal():
    print("🧪 Testing Orchestrator with Simple Goal")
    print("=" * 60)
    
    # Create orchestrator
    orchestrator = Orchestrator()
    
    # Simple test goal
    goal = "Go to Google and search for 'Python programming'"
    
    # Execute
    result = orchestrator.execute_goal(goal, start_url="https://google.com")
    
    print("\n" + "=" * 60)
    print(f"Final Result: {result}")
    print("=" * 60)

if __name__ == "__main__":
    test_simple_goal()