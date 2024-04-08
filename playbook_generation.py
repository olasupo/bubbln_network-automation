
import openai
import time
import threading

# This function is responsible for prompting chatGPT to generate playbooks
def generate_playbook(prompt, model_name, conversation_history):
    def api_call():
        nonlocal response
        messages = [
            {"role": "system", "content": "You are a network engineer trying to automate a network."},
        ]
        messages.extend(conversation_history)
        messages.append({"role": "user", "content": prompt})
        
        response = openai.ChatCompletion.create(
            model=model_name,
            messages=messages,
            max_tokens=1500,
        )

    response = None

    print("\n\nPlease wait while a playbook is being generated", end='', flush=True)
    animation_thread = threading.Thread(target=api_call)
    animation_thread.start()

    while animation_thread.is_alive():
        for _ in range(5):
            time.sleep(1.0)
            print('.', end='', flush=True)
        print('\b\b\b   \b\b\b', end='', flush=True)  # Erase the dots

    animation_thread.join()

    # Lines 38 to 54 are responsible for extracting the generated playbooks from the raw response from ChatGPT.

    full_response = response['choices'][0]['message']['content']
    
    conversation_history.append({'role': 'assistant', 'content': full_response})
    
    code_start_index = full_response.find('---')
    code_end_index = full_response.find('...', code_start_index)

    if code_start_index != -1 and code_end_index != -1:
        text_before_code = full_response[:code_start_index]
        code = full_response[code_start_index:code_end_index + 3]  # Include '---' and '...' in the code
        text_after_code = full_response[code_end_index + 3:]
    else:
        text_before_code = full_response
        code = ""
        text_after_code = ""

    return text_before_code.strip(), code.strip(), text_after_code.strip(), conversation_history
