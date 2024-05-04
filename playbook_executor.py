import os
import pickle
from ansible_runner import run
from tenacity import retry, stop_after_attempt, wait_random_exponential
from cryptography.fernet import Fernet
from utility import print_blue, print_colored_code

# Get the path of the current script or module
current_path = os.path.dirname(os.path.abspath(__file__))


# This is the function to execute the generated playbooks which were dynamically stored.
@retry(wait=wait_random_exponential(min=1, max=60), stop=stop_after_attempt(10))
def execute_playbook(playbook_file, model_name, router_number, text_before_code, text_after_code, conversation_history):
    try:
        while True:
            with open(playbook_file, "r") as file:
                playbook_content = file.read()

            print(f"\n\nGenerated Playbook for Router {router_number} has been Saved To: {playbook_file}\n")
            print_blue(text_before_code)
            print()
            print_colored_code(playbook_content)
            print()
            print_blue(text_after_code)
            print()

            # Dynamically decrypt ansible_user and ansible_ssh_pass before running the playbook
            decrypt_ansible_credentials()

            r = run(
                playbook=playbook_file,
                inventory=os.path.join(current_path, '.hosts.yml'),
                private_data_dir=current_path,
                quiet=False
            )
            print()
            return playbook_content

    except Exception as e:
        print("Error executing Ansible playbook:", e)


# Function to decrypt ansible credentials
def decrypt_ansible_credentials():
    try:
        # Read the encrypted credentials from the hosts.yml file
        with open(os.path.join(current_path, '.hosts.yml'), 'r') as hosts_file:
            encrypted_hosts_content = hosts_file.read()

        # Load user_config from pickle file
        with open(os.path.join(current_path, "user_config.pkl"), "rb") as decrypt_source:
            user_config = pickle.load(decrypt_source)

        # Load fernet key from user_config
        fernet_key = user_config.get("fernet_key")

        if fernet_key:
            cipher_suite = Fernet(fernet_key)

            # Decode and decrypt the credentials
            decrypted_username = cipher_suite.decrypt(user_config["ansible_user"]).decode('utf-8')
            decrypted_password = cipher_suite.decrypt(user_config["ansible_ssh_pass"]).decode('utf-8')
        else:
            print("Fernet key not found in user_config!")
            return

        decrypted_hosts_content = encrypted_hosts_content.replace(f"b'{user_config['ansible_user'].decode()}'",
                                                                  decrypted_username
                                                                  ).replace(
            f"b'{user_config['ansible_ssh_pass'].decode()}'", decrypted_password)

        # Write the decrypted content back to the hosts.yml file
        with open(os.path.join(current_path, '.hosts.yml'), 'w') as hosts_file:
            hosts_file.write(decrypted_hosts_content)

    except Exception as e:
        print("Error decrypting ansible credentials:", e)

