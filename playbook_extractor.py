import traceback

# Function to extract playbook from raw response
def playbook_extractor_function(response, conversation_history):
    if response is None:  # If response is None, playbook generation failed
        print("Playbook generation failed.")
        return "", "", "", conversation_history

    try:
        full_response = response['choices'][0]['message']['content']  # Get full response from API

        # Append assistant's response to conversation history
        conversation_history.append({'role': 'assistant', 'content': full_response})

        # Find start and end index of code block
        code_start_index = full_response.find('---')
        code_end_index = full_response.find('...', code_start_index)

        if code_start_index != -1 and code_end_index != -1:  # If code block found
            # Extract text before code block, code block, and text after code block
            text_before_code = full_response[:code_start_index]
            code = full_response[code_start_index:code_end_index + 3]  # Include '---' and '...' in the code
            text_after_code = full_response[code_end_index + 3:]
        else:  # If code block not found
            text_before_code = full_response
            code = ""
            text_after_code = ""

        return text_before_code.strip(), code.strip(), text_after_code.strip(), conversation_history

    except Exception as e:  # Handle exceptions
        print("An error occurred while processing the generated playbook:", e)
        traceback.print_exc()  # Print traceback for debugging
        return "", "", "", conversation_history
