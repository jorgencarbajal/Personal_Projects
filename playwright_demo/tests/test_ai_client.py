# import the necessary class

# the function

    # initialize the client

    # send a simple prompt

    # get the response

# main

from src.ai.ai_client import AnthropicClient

def test_client():

    print("Testing AI client connection...")

    client = AnthropicClient()

    print("Initialization successfull")

    prompt = "Say 'Hello! I am working correctly.' and nothing else."
    print("Sending prompt...")

    response = client.get_next_action(prompt)
    print(f"Response: {response}")

    print("AI client test complete!")


if __name__ == "__main__":
    test_client()