import os
import pickle
from chatGPT_prompting import validate_openai_key
from parameter_input import parameter_input_function
import openai
import time
from colorama import init
from cryptography.fernet import Fernet
import getpass
from utility import animate_message, print_line, load_user_config, save_user_config, encrypt_key, decrypt_key

# Initialize colorama
init()

os.system('clear')

# Get the path of the current script or module
current_path = os.path.dirname(os.path.abspath(__file__))

# Create a unique folder for each program execution based on timestamp
timestamp = time.strftime('%Y%m%d%H%M%S')
execution_folder = os.path.join(current_path, f"execution_{timestamp}")
os.makedirs(execution_folder, exist_ok=True)

# Move to the execution folder
os.chdir(execution_folder)

user_config = load_user_config()

def welcome_message_feature():
    # Welcome message animation and logic to decide if it should be displayed, i.e display logic message only at
    # first-time execution of the program. Do not display it afterwards.
    welcome_message = (
        "\n\nWelcome. My name is Bubbln. I was developed to aid a research on the potentials of automating "
        "a Network using Large Language Models (Specifically, ChatGPT). This research is being undertaken "
        "by Olasupo Okunaiya as part of his Masters degree project on the CMP7200 course in the School of "
        "Computing and Digital Technology at Birmingham City University. The project is being supervised "
        "by Associate Professor Ron Austin (https://www.linkedin.com/in/ronaustin1]) during the period "
        "June 2023 to 28th September, 2023. The research will be written up and submitted for assessment "
        "in September, 2023 and may be used for external publication for a further 12 months. Thank you. "
        "\n\n-    Olasupo Okunaiya (linkedin.com/in/olasupoo)\n\n")

    existing_config_file = os.path.join(current_path, "user_config.pkl")

    # Load or create user configuration
    if os.path.exists(existing_config_file):
        with open(existing_config_file, "rb") as file:
            user_config = pickle.load(file)
            show_full_message = user_config.get("show_full_message", False)
    else:
        user_config = {}
        show_full_message = False

    # Display welcome message if required
    if not show_full_message:
        print_line()
        print("\n\t\t----------THIS IS A ONE-TIME WELCOME MESSAGE----------\n")
        animate_message(welcome_message)
        animate_message(
            "\nThis is an experiment to assess the potential of using chatGPT to generate ansible playbooks in network "
            "automation\n\n")

        print_line()
        user_config["show_full_message"] = True
        with open(existing_config_file, "wb") as file:
            pickle.dump(user_config, file)

# This is the main function of the program responsible for taking user inputs, forming prompts and calling other
# functions
def main():
    welcome_message_feature()
    elapsed_time = 0
    program_start_time = time.time()  # Useful to track program execution time

    # Checks if there is an existing configuration file. If so, then that is loaded
    config_file = os.path.join(current_path, "user_config.pkl")
    if os.path.exists(config_file):
        with open(config_file, "rb") as file:
            user_config = pickle.load(file)
    else:
        user_config = {}
    openai_key = user_config.get("openai_key")
    if not openai_key:
        print("\n\n\t\t==========This is a One-time Requirement==========\n\n")
        while True:
            openai_key = getpass.getpass("Please enter your OpenAI API Key: ")
            if validate_openai_key(openai_key):
                break
            else:
                print("Invalid API key! You can obtain a key from your OpenAI account.")

        # Generate or load Fernet key
        fernet_key = user_config.get("fernet_key")
        if fernet_key:
            cipher_suite = Fernet(fernet_key)
        else:
            fernet_key = Fernet.generate_key()
            cipher_suite = Fernet(fernet_key)
            user_config["fernet_key"] = fernet_key

        encrypted_openai_key = encrypt_key(openai_key, cipher_suite)
        user_config["openai_key"] = encrypted_openai_key
        save_user_config(user_config)
    else:
        # Load Fernet key
        fernet_key = user_config.get("fernet_key")
        cipher_suite = Fernet(fernet_key)
        openai_key = decrypt_key(openai_key, cipher_suite)

    openai.api_key = openai_key

    # Function to read SSH IP addresses from a file
    def read_ssh_ips(filename):
        with open(filename, 'r') as file:
            ssh_ips = [line.strip() for line in file.readlines() if line.strip()]
        return ssh_ips

    # Read SSH IP addresses from a file
    ssh_file = os.path.join(current_path, 'ssh_ip_addresses.txt')
    ssh_ips = read_ssh_ips(ssh_file)

    # Initialize an empty dictionary to store router details
    router_details = {}

    # Assign SSH IP addresses to routers
    for i in range(len(ssh_ips)):
        router_details[f"R{i + 1}"] = {"ansible_host": ssh_ips[i]}

    # Load or create fernet key
    fernet_key = user_config.get("fernet_key")
    if fernet_key:
        cipher_suite = Fernet(fernet_key)
    else:
        key = Fernet.generate_key()
        cipher_suite = Fernet(key)
        user_config["fernet_key"] = key

    # Prompt user for username and password
    while True:
        try:
            username = input("Please input the SSH username: ")
            password = getpass.getpass("Please input the SSH password: ")

            # Encrypt username and password

            encrypted_username = cipher_suite.encrypt(username.encode())
            encrypted_password = cipher_suite.encrypt(password.encode())
            user_config["ansible_user"] = encrypted_username
            user_config["ansible_ssh_pass"] = encrypted_password

            # Update the vars section of the hosts.yml file with encrypted credentials
            host_file = os.path.join(current_path, '.hosts.yml')

            with open(host_file, 'w') as hosts_file:
                # Write router details
                hosts_file.write("routers:\n  hosts:\n")
                for router, details in router_details.items():
                    hosts_file.write(f"    {router}:\n")
                    hosts_file.write(f"      ansible_host: {details['ansible_host']}\n")
                hosts_file.write(f"  vars:\n")
                hosts_file.write(f"     ansible_connection: network_cli\n")
                hosts_file.write(f"     ansible_network_os: ios\n")
                hosts_file.write(f"     ansible_action_warnings: False\n")
                hosts_file.write(f"     ansible_user: {encrypted_username}\n")
                hosts_file.write(f"     ansible_ssh_pass: {encrypted_password}\n")

            # Successfully got username and password, break out of loop
            break

        except Exception as e:
            print("An error occurred while processing your input:", e)
            print("Please try again.")

    # The inventory file is loaded
    inventory_file = user_config.get("inventory_file")
    if not inventory_file:
        inventory_file = '.hosts.yml'
        user_config["inventory_file"] = inventory_file

    with open(config_file, "wb") as file:
        pickle.dump(user_config, file)

    openai.api_key = openai_key
    model_name = "gpt-4"

    #Call function to begin inputting parameters
    parameter_input_function(execution_folder, model_name, elapsed_time, program_start_time)

if __name__ == "__main__":

    main()
    # Delete the hidden hosts.yml file after the program ends
    os.remove(os.path.join(current_path, '.hosts.yml'))