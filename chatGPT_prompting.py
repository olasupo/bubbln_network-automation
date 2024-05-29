#import libraries
import openai
import time
import threading
import traceback
import openai
from openai.error import AuthenticationError
from playbook_extractor import playbook_extractor_function


# Function to validate the provided OpenAI API key
def validate_openai_key(api_key):
    # Set the OpenAI API key
    openai.api_key = api_key
    # Define a test message to check if the API key is correct
    messages = [
        {"role": "system", "content": "Test if the API key is correct."},
    ]
    success = False
    try:
        # Test the API key by sending a chat completion request
        openai.ChatCompletion.create(model="gpt-4", messages=messages, max_tokens=5)
        success = True
    except AuthenticationError as e:
        # Handle authentication error if the API key is invalid
        print("Invalid API key:", e)
    except Exception as e:
        # Handle other unexpected errors
        print("An unexpected error occurred:", e)
    return success


# Function responsible for prompting ChatGPT to generate playbooks
def chatGPT_prompter(prompt, model_name, conversation_history):
    # Define an inner function to make the API call asynchronously
    def api_call():
        nonlocal response
        try:
            # Create messages including the conversation history and user prompt
            messages = [
                {"role": "system", "content": "You are a network engineer trying to automate a network."},
            ]
            messages.extend(conversation_history)
            messages.append({"role": "user", "content": prompt})

            # Call ChatGPT to generate a response
            response = openai.ChatCompletion.create(
                model=model_name,
                messages=messages,
                max_tokens=1500,
            )
        except Exception as e:
            # Handle errors during playbook generation
            print("An error occurred during playbook generation:", e)
            traceback.print_exc()
            response = None

    response = None

    # Display a waiting message while generating the playbook
    print("\n\nPlease wait while a playbook is being generated", end='', flush=True)

    # Start a thread to make the API call asynchronously
    animation_thread = threading.Thread(target=api_call)
    animation_thread.start()

    # Display an animation while waiting for the response
    while animation_thread.is_alive():
        for _ in range(5):
            time.sleep(1.0)
            print('.', end='', flush=True)
        print('\b\b\b   \b\b\b', end='', flush=True)  # Erase the dots

    # Wait for the animation thread to finish
    animation_thread.join()

    # Extract relevant information from the response
    text_before_code, code, text_after_code, conversation_history = playbook_extractor_function(response,
                                                                                                conversation_history)
    return text_before_code, code, text_after_code, conversation_history
