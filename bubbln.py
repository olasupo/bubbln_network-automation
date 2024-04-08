import os
import pickle
from ansible_runner import run
from tenacity import retry, stop_after_attempt, wait_random_exponential
from input_validation import validate_inputs
from playbook_generation import generate_playbook
from interface_configuration import get_router_interface_configuration
import openai
from fpdf import FPDF
import time
import textwrap
import shutil
from colorama import init
from pygments import highlight
from pygments.lexers import get_lexer_by_name
from pygments.formatters import TerminalFormatter
import psutil

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


# Function to format the Network configuration report file generated during the program execution
class PDF(FPDF):
    def header(self):
        self.set_font('Arial', 'B', 12)
        self.cell(0, 10, 'Network Configuration Report', 0, 1, 'C')

    def chapter_title(self, title):
        self.set_font('Arial', 'B', 14)
        self.cell(0, 10, title, 0, 1, 'L')
        self.ln(5)

    def chapter_body(self, content):
        self.set_font('Arial', '', 12)
        self.multi_cell(0, 10, content)
        self.ln(10)


# Function for animating the welcome message
def animate_message(message):
    for char in message:
        print(char, end='', flush=True)
        # time.sleep(0.008)
    # print()


# Function to get the terminal width
def get_terminal_width():
    try:
        _, columns = shutil.get_terminal_size()
        return columns
    except:
        return 80


# Function to print a line with "=" based on the terminal width
def print_line():
    width = get_terminal_width()
    print("=" * 80)


# Welcome message animation and logic to decide if it should be displayed, i.e display logic message only at
# first-time execution of the program. Do not display it afterwards.
welcome_message = ("\n\nWelcome. My name is Bubbln. I was developed to aid a research on the potentials of automating "
                   "a Network using Large Language Models (Specifically, ChatGPT). This research is being undertaken "
                   "by Olasupo Okunaiya as part of his Masters degree project on the CMP7200 course in the School of "
                   "Computing and Digital Technology at Birmingham City University. The project is being supervised "
                   "by Associate Professor Ron Austin (https://www.linkedin.com/in/ronaustin1]) during the period "
                   "June 2023 to 28th September, 2023. The research will be written up and submitted for assessment "
                   "in September, 2023 and may be used for external publication for a further 12 months. Thank you. "
                   "\n\n-    Olasupo Okunaiya (linkedin.com/in/olasupoo)\n\n")
wrapped_welcome_message = textwrap.fill(welcome_message, width=get_terminal_width())
existing_config_file = os.path.join(current_path, "user_config.pkl")

if os.path.exists(existing_config_file):
    with open(existing_config_file, "rb") as file:
        user_config = pickle.load(file)
        show_full_message = user_config.get("show_full_message", False)
else:
    user_config = {}
    show_full_message = False

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

            r = run(
                playbook=playbook_file,
                inventory=os.path.join(current_path, 'hosts.yml'),
                private_data_dir=current_path,
                quiet=False
            )
            print()
            return playbook_content

    except Exception as e:
        print("Error executing Ansible playbook:", e)


# This function validates a user's input to ensure it is of integer value e.g OSPF Area value inputted by a user must
# be an integer
def get_positive_integer_input(prompte):
    while True:
        try:
            value = int(input(prompte))
            if value > 0:
                return value
            else:
                animate_message("Sorry, that is an invalid input! Please enter a positive integer\n")
        except ValueError:
            animate_message("Sorry, that is an invalid input! Please enter a valid integer\n")


# This function saves the router parameters inputted by a user for easy reloading in future execution of the program
def save_configuration(configurations):
    config_file = os.path.join(current_path, "router_configurations.pkl")
    with open(config_file, "wb") as file:
        pickle.dump(configurations, file)


# This function is responsible for reloading saved router parameters when prompted during execution of the program
def load_configuration():
    config_file = os.path.join(current_path, "router_configurations.pkl")
    if os.path.exists(config_file):
        with open(config_file, "rb") as file:
            return pickle.load(file)
    else:
        return None


# This function generates an animated blue colored font.
def print_blue(text):
    animate_message("\033[94m{}\033[0m".format(text))


# This function ensures that playbooks in the stored playbook files and reports are formatted in accordance to yaml
# rules
def print_colored_code(code):
    lexer = get_lexer_by_name("yaml")  # Set the appropriate lexer for the code language
    formatter = TerminalFormatter()
    colored_code = highlight(code, lexer, formatter)
    print(colored_code)


# This function outputs a summary of the execution time for key tasks
def print_summary(input_router_duration, generate_playbooks_duration, execute_playbooks_duration, summary_duration):
    print_blue("\n\n********** Below is a Summary of How Long It Took Us To Setup Your Network **********")
    print_blue("\n1. We spent {:.2f} seconds to input the various router parameters.".format(input_router_duration))
    print_blue(
        "\n2. The process for generating all the playbooks took {:.2f} seconds.".format(generate_playbooks_duration))
    print_blue("\n3. We spent {:.2f} seconds to execute all the generated playbooks".format(execute_playbooks_duration))
    # print_blue("\n4. And to generate and execute playbook for adjacency checks took us {:.2f} seconds".format(
    # check_adjacency_duration))
    print_blue("\n4. In Total, it has taken {:.2f} seconds to automate your network from start to finish".format(
        summary_duration))


# This function is executed to run a ping test and track the status whether failed or successful
def execute_ping_playbook(playbook_file, inventory_file):
    try:
        # Run the Ansible playbook for pinging prefixes
        r = run(
            playbook=playbook_file,
            inventory=inventory_file,
            private_data_dir=current_path,
            quiet=False
        )

        ping_result_dict = {}

        # Check if the playbook execution was successful and stdout is available
        if r.rc == 0 and r.stdout:
            ping_result_dict['success'] = True
            ping_result_dict['output'] = r.stdout.decode('utf-8')  # Convert bytes to string
        else:
            ping_result_dict['success'] = False
            ping_result_dict[
                'error'] = f"Error executing Ansible playbook for ping prefixes: {r.stderr.decode('utf-8')}"

        return ping_result_dict
    except Exception as e:
        print("Error executing Ansible playbook for ping prefixes:", e)
        return {'success': False, 'error': str(e)}


# This is the main function of the program responsible for taking user inputs, forming prompts and calling other
# functions
def main():
    elapsed_time = 0
    program_start_time = time.time()  # Useful to track program execution time

    # Checks if there is an existing configuration file. If so, then that is loaded
    config_file = os.path.join(current_path, "user_config.pkl")
    if os.path.exists(config_file):
        with open(config_file, "rb") as file:
            user_config = pickle.load(file)
    else:
        user_config = {}

    openai_key = "Insert Your OpenAI key here"  # You need to register to openai.com to obtain an API key.
    
    # The inventory file is loaded
    inventory_file = user_config.get("inventory_file")
    if not inventory_file:
        inventory_file = 'hosts.yml'
        user_config["inventory_file"] = inventory_file

    with open(config_file, "wb") as file:
        pickle.dump(user_config, file)

    openai.api_key = openai_key
    model_name = "gpt-4"

    # Logic to get router parameters from user
    while True:
        animate_message("\n\n\t\t\tLet's Begin Setup of Your Network")
        print("\n\t\t\t===================================\n\n")

        input_param_start_time = time.time()

        interface_configurations = load_configuration()
        if interface_configurations is None:
            interface_configurations = []
            router_count = get_positive_integer_input("How many routers do you want to configure: ")
            for i in range(router_count):
                print(f"\n\nWe will now take the configuration parameters for Router {i + 1} : \n\n")
                router_interface_count = get_positive_integer_input(f"How many interfaces are to be configured?: ")
                protocol_count = get_positive_integer_input(f"And how many protocols: ")
                interface_configurations.append(
                    get_router_interface_configuration(protocol_count, router_interface_count))

            save_configuration(interface_configurations)
        else:

            response = input("\nWe found a previous configuration. Would you like to load it? (y/n): ")
            # response = 'y'
            if response.lower() == "n":
                interface_configurations = []
                router_count = get_positive_integer_input("\nHow many routers do you want to configure: ")
                for i in range(router_count):
                    print(f"\n\nWe will now take the configuration parameters for Router {i + 1} : \n\n")
                    router_interface_count = get_positive_integer_input(
                        f"How many interfaces are to be configured?: ")
                    protocol_count = get_positive_integer_input(f"...And how many protocols?: ")
                    interface_configurations.append(
                        get_router_interface_configuration(protocol_count, router_interface_count))

                save_configuration(interface_configurations)

        os.system('clear')

        print("\n\n**********Please review and validate your inputs**********")

        if validate_inputs(interface_configurations):
            input_param_end_time = time.time()
            input_param_duration = input_param_end_time - input_param_start_time

            # Create a PDF object
            pdf = PDF()
            pdf.set_auto_page_break(auto=True, margin=15)

            # Add a chapter for router configurations
            pdf.add_page()
            pdf.chapter_title("Router Configurations")
            pdf.chapter_body("Explanation and details about router configurations.")

            generate_playbooks_start_time = time.time()  # Start time for generating playbooks

            # Logic to generate prompts and save them.
            for i, router_config in enumerate(interface_configurations):

                conversation_history = []
                # Add a subheading for the current router
                pdf.set_font('Arial', 'B', 12)
                pdf.cell(0, 10, f"Router {i + 1} Configurations", 0, 1, 'L')
                pdf.ln(5)

                prompt = ("Requirements: Strictly adhere to the following explicitly stated requirements; Write a "
                          "simple Ansible playbook with separate tasks for each protocol and interface configurations "
                          "with the following details;")
                prompt += f" hosts: R{i + 1}"
                prompt += " Do not worry about the inventory file;"
                prompt += " Ensure each Task is named;"
                prompt += " Never provide explanations for the generated playbook;"
                prompt += " Do not use variables and templates to generate the playbooks;"
                prompt += ("Ensure all generated playbooks adhere to yaml's rule of always starting a playbook with "
                           "`---` and ending the playbook with a new line containing `...`;")
                prompt += " Always use ios_config module and ensure unsupported parameters are not generated;;"
                prompt += " Use `parents` argument to implement stanzas;"
                # prompt += " When configuring interfaces, ensure interface-type and port numbers are combined. e.g
                # loopback 90, should be loopback90;"
                prompt += ("when configuring interfaces, ensure you generate codes for only provided interfaces and "
                           "always implement 'No Shutdown' for each interface;")
                prompt += ("when configuring routing protocols, ensure you generate codes for only provided protocols "
                           "and that the protocol is initialized only under the parents argument using the format "
                           "`router protocol-type xx`. Also, DO NOT configure router id;")
                prompt += " set `replace` argument to block. `replace` argument should always be child to `ios_config`;"

                # prompt += " Implement one task to save config when there is modification. Exclude 'commit' and
                # 'confirm' arguments"

                redistribute_required = False

                for protocol_config in router_config:
                    if 'protocol' in protocol_config:
                        protocol = protocol_config['protocol']

                        prompt += f" Protocol: {protocol}"

                        if protocol.lower() == 'ospf':
                            area = protocol_config['area']
                            process_id = protocol_config['process_id']
                            num_networks = len(protocol_config['networks'])
                            prompt += f" OSPF Area: {area}, Process ID: {process_id}, Number of networks to advertise: {num_networks}"
                            for j, network in enumerate(protocol_config['networks']):
                                pdf.set_font('Arial', '', 12)
                                pdf.cell(0, 10, f"network: {network}", 0, 1, 'L')
                                pdf.ln(5)
                                prompt += f" network{j + 1}: {network}"
                        elif protocol.lower() == 'eigrp':
                            as_number = protocol_config['as_number']
                            num_networks = len(protocol_config['networks'])
                            prompt += f" EIGRP AS Number: {as_number}, Number of networks to advertise: {num_networks}"
                            for j, network in enumerate(protocol_config['networks']):
                                pdf.set_font('Arial', '', 12)
                                pdf.cell(0, 10, f"network: {network}", 0, 1, 'L')
                                pdf.ln(5)
                                prompt += f" network{j + 1}: {network}"
                        # Check if both EIGRP and OSPF are configured
                        if protocol.lower() == 'eigrp':
                            for other_protocol_config in router_config:
                                if 'protocol' in other_protocol_config and other_protocol_config[
                                    'protocol'].lower() == 'ospf':
                                    redistribute_required = True

                if redistribute_required:
                    prompt += (f"; Using dedicated tasks, Please redistribute the routing protocols using "
                               f"'redistribute ospf {process_id} metric 1000 33 255 1 1500' for redistributing OSPF "
                               f"into EIGRP and 'redistribute eigrp {as_number} subnets' for redistributing EIGRP "
                               f"into OSPF;")
                    prompt += ("The redistribution tasks, should be generated after the routing protocol configuration "
                               "tasks have been generated;")

                for interface_config in router_config:
                    if 'interface' in interface_config and 'ip' in interface_config:
                        interface_name = interface_config['interface']
                        ip_address = interface_config['ip']
                        pdf.set_font('Arial', '', 12)
                        pdf.cell(0, 10, f"Interface: {interface_name}, IP: {ip_address}", 0, 1, 'L')
                        pdf.ln(5)
                        prompt += f" Interface: {interface_name}, IP: {ip_address}"

                prompt = prompt.rstrip(";")  # Remove the trailing semicolon

                # Add a chapter for the prompt used to generate each playbook
                pdf.add_page()
                pdf.chapter_title(f"Prompt for Router {i + 1}")
                pdf.chapter_body(prompt)

                print(f"\n\nPrompt:\n\n")
                print_blue(prompt)
                text_before_code, playbook, text_after_code, conversation_history = generate_playbook(prompt,
                                                                                                      model_name,
                                                                                                      conversation_history)
                generate_playbooks_duration = time.time() - generate_playbooks_start_time
                # Add a chapter for the generated playbook
                pdf.add_page()
                pdf.chapter_title(f"Generated Playbook for Router {i + 1}")
                pdf.chapter_body(playbook)
                playbook_file = os.path.join(execution_folder, f"Router_{i + 1}_Playbook.yml")
                with open(playbook_file, "w") as file:
                    file.write(playbook)
                start_time = time.time()
                execute_playbook(playbook_file, model_name, i + 1, text_before_code, text_after_code,
                                 conversation_history)
                elapsed_time = time.time() - start_time
            # Save the PDF document
            # pdf.output(os.path.join(current_path, "network_configuration_report.pdf"), "F")
            pdf.output(os.path.join(execution_folder, "network_configuration_report.pdf"), "F")

            # Print summary
            # execute_playbooks_duration = sum([elapsed_time for _ in range(len(interface_configurations))])
            execute_playbooks_duration = elapsed_time
            summary_duration = time.time() - program_start_time
            print_summary(input_param_duration, generate_playbooks_duration, execute_playbooks_duration,
                          summary_duration)
            experiment_summary_file = f"experiment_summary_{time.strftime('%Y%m%d%H%M%S')}.txt"
            with open(experiment_summary_file, "w") as file:
                file.write(f"Input Router Duration: {input_param_duration}\n")
                file.write(f"Generate Playbooks Duration: {generate_playbooks_duration}\n")
                file.write(f"Execute Playbooks Duration: {execute_playbooks_duration}\n")
                file.write(f"Total Summary Duration: {summary_duration}\n")

            print()
            break
        else:
            print("\n\nPlease update your inputs:\n")


if __name__ == "__main__":
    main()
    # Execute Ansible playbook for pinging specified prefixes on R1
    print()
    print("Waiting for the Network to Converge before Running a Ping Test...")
    print()
    time.sleep(40)
    ping_playbook_r1_content = """
           - name: Ping prefixes on R1
             hosts: R1
             gather_facts: false
             tasks:
               - name: Ping prefixes on R1
                 command: ping -c 4 "{{ item }}"
                 with_items:
                   - 192.168.10.1
                   - 192.168.20.1
                   - 192.168.30.1
                   - 192.168.40.1
                   - 192.168.50.1
                   - 192.168.60.1
                   - 192.168.70.1
                   - 192.168.80.1
                   - 172.168.1.17
                   - 192.168.2.2
                   - 192.168.4.2
                   - 192.168.6.2
             """

    ping_playbook_r1_file = os.path.join(execution_folder, "ping_playbook_R1.yml")

    with open(ping_playbook_r1_file, "w") as file:
        file.write(ping_playbook_r1_content)

    # Execute Ansible playbook for pinging prefixes on R1
    ping_inventory_file_r1 = os.path.join(current_path, 'hosts.yml')
    ping_result_r1 = execute_ping_playbook(ping_playbook_r1_file, ping_inventory_file_r1)

    # Save the outcome of the pings on R1 as a dictionary
    ping_result_r1_file = os.path.join(execution_folder, "ping_result_R1.pkl")

    with open(ping_result_r1_file, "wb") as file:
        pickle.dump(ping_result_r1, file)

    # Similarly, repeat the process for R4
    ping_playbook_r4_content = """
           - name: Ping prefixes on R4
             hosts: R4
             gather_facts: false
             tasks:
               - name: Ping prefixes on R4
                 command: ping -c 4 "{{ item }}"
                 with_items:
                   - 192.168.10.1
                   - 192.168.20.1
                   - 192.168.30.1
                   - 192.168.40.1
                   - 192.168.50.1
                   - 192.168.60.1
                   - 192.168.70.1
                   - 192.168.80.1
                   - 172.168.1.17
                   - 192.168.2.1
                   - 192.168.4.1
                   - 192.168.6.1
             """

    ping_playbook_r4_file = os.path.join(execution_folder, "ping_playbook_R4.yml")

    with open(ping_playbook_r4_file, "w") as file:
        file.write(ping_playbook_r4_content)

    # Execute Ansible playbook for pinging prefixes on R4
    ping_inventory_file_r4 = os.path.join(current_path, 'hosts.yml')
    ping_result_r4 = execute_ping_playbook(ping_playbook_r4_file, ping_inventory_file_r4)

    # Save the outcome of the pings on R4 as a dictionary
    ping_result_r4_file = os.path.join(execution_folder, "ping_result_R4.pkl")

    with open(ping_result_r4_file, "wb") as file:
        pickle.dump(ping_result_r4, file)
