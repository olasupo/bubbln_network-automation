import readline
import os
import time
from utility import PDF, validate_cidr_network, convert_cidr_network, convert_cidr_network_wildcard, animate_message, \
    get_positive_integer_input, save_configuration, load_configuration, print_summary
from prompt_generator import prompt_generator_function

# Function to get router parameters from the user
def parameter_input_function(execution_folder, model_name, elapsed_time, program_start_time):
    while True:
        animate_message("\n\n\t\t\tLet's Begin Setup of Your Network")  # Display welcome message
        print("\n\t\t\t===================================\n\n")
        input_param_start_time = time.time()  # Record start time for input
        interface_configurations = load_configuration()  # Load existing configurations if available
        if interface_configurations is None:  # If no configurations found
            interface_configurations = []
            router_count = get_positive_integer_input("How many routers do you want to configure: ")  # Get number of routers
            for i in range(router_count):
                print(f"\n\nWe will now take the configuration parameters for Router {i + 1} : \n\n")
                router_interface_count = get_positive_integer_input(f"How many interfaces are to be configured?: ")  # Get number of interfaces
                protocol_count = get_positive_integer_input(f"And how many protocols: ")  # Get number of protocols
                interface_configurations.append(
                    get_router_interface_configuration(protocol_count, router_interface_count))  # Get router interface configurations
            save_configuration(interface_configurations)  # Save configurations
        else:  # If existing configurations found
            response = input("\nWe found a previous configuration. Would you like to load it? (y/n): ")
            if response.lower() == "n":
                interface_configurations = []
                router_count = get_positive_integer_input("\nHow many routers do you want to configure: ")
                for i in range(router_count):
                    print(f"\n\nWe will now take the configuration parameters for Router {i + 1} : \n\n")
                    router_interface_count = get_positive_integer_input(f"How many interfaces are to be configured?: ")
                    protocol_count = get_positive_integer_input(f"...And how many protocols?: ")
                    interface_configurations.append(
                        get_router_interface_configuration(protocol_count, router_interface_count))
                save_configuration(interface_configurations)
        os.system('clear')  # Clear screen
        print("\n\n**********Please review and validate your inputs**********")
        if validate_inputs(interface_configurations):  # Validate user inputs
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
            # Call function to generate prompts and save them
            generate_playbooks_duration, elapsed_time = prompt_generator_function(pdf, interface_configurations,
                                                                                  execution_folder, model_name,
                                                                                  generate_playbooks_start_time)
            # Save the PDF document
            pdf.output(os.path.join(execution_folder, "network_configuration_report.pdf"), "F")

            # Print summary
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

# Function to validate user inputs
def validate_inputs(interface_configurations):
    for i, router_config in enumerate(interface_configurations):
        print(f"Router {i + 1}:")
        for protocol_config in router_config:
            if 'protocol' in protocol_config:
                protocol = protocol_config['protocol']
                print(f"\tProtocol: {protocol}")
                if protocol.lower() == 'ospf':
                    area = protocol_config['area']
                    process_id = protocol_config['process_id']
                    num_networks = len(protocol_config['networks'])
                    print(f"\t\tOSPF Area: {area}")
                    print(f"\t\tOSPF Process ID: {process_id}")
                    print(f"\t\tNumber of networks to advertise: {num_networks}")
                    for j, network in enumerate(protocol_config['networks']):
                        print(f"\t\tNetwork {j + 1}: {network}")
                elif protocol.lower() == 'eigrp':
                    as_number = protocol_config['as_number']
                    num_networks = len(protocol_config['networks'])
                    print(f"\t\tEIGRP AS Number: {as_number}")
                    print(f"\t\tNumber of networks to advertise: {num_networks}")
                    for j, network in enumerate(protocol_config['networks']):
                        print(f"\t\tNetwork {j + 1}: {network}")
        for interface_config in router_config:
            if 'interface' in interface_config and 'ip' in interface_config:
                interface_name = interface_config['interface']
                ip_address = interface_config['ip']
                print(f"\tInterface: {interface_name}")
                print(f"\tIP Address: {ip_address}")
        print()

    while True:
        confirm = input("Do you want to proceed with the above inputs? (y/n): ")
        if confirm.lower() == 'y':
            return True
        elif confirm.lower() == 'n':
            while True:
                index_to_correct = input(
                    "\n\nOn which router do you want to make corrections - Enter '1' for Router1 etc: ")
                try:
                    index = int(index_to_correct) - 1
                    if 0 <= index < len(interface_configurations):
                        router_config = interface_configurations[index]
                        protocol_count = len([config for config in router_config if 'protocol' in config])
                        interface_count = len(
                            [config for config in router_config if 'interface' in config and 'ip' in config])
                        print(f"\nCorrecting inputs for Router {index + 1}...\n")
                        interface_configurations[index] = get_router_interface_configuration(protocol_count,
                                                                                             interface_count)
                        os.system('clear')
                        break
                    else:
                        print(
                            f"Invalid input! Please enter a valid router index between 1 and {len(interface_configurations)}.")
                except ValueError:
                    print("Invalid input! Please enter a valid router index number.")
            print("\n\nPlease review and validate your corrected inputs:")
            return validate_inputs(interface_configurations)
        else:
            print("Invalid input! Please enter 'y' or 'n'.")

# Function to get router interface configuration from user
def get_router_interface_configuration(protocol_count, interface_count):
    router_interface_config = []
    history = []

    def input_with_history(prompt):
        line = input(prompt)
        if line:
            history.append(line)
        return line

    def handle_navigation(current_index):
        if current_index < 0:
            current_index = 0
        elif current_index >= len(history):
            current_index = len(history) - 1
        readline.set_history_length(len(history))
        readline.set_history_item(current_index, history[current_index])
        return history[current_index], current_index

    def navigate_inputs():
        current_index = len(history)
        while True:
            key = input_with_history("")
            if key == "\x1b[A":  # Up arrow key
                current_index -= 1
                line, current_index = handle_navigation(current_index)
                print("\r" + " " * len(line) + "\r" + line)
            elif key == "\x1b[B":  # Down arrow key
                current_index += 1
                line, current_index = handle_navigation(current_index)
                print("\r" + " " * len(line) + "\r" + line)
            else:
                break

    def get_positive_integer_input(prompt):
        while True:
            try:
                value = int(input_with_history(prompt))
                if value > 0:
                    return value
                else:
                    animate_message("Sorry, that's an invalid input! Please enter a positive integer.\n")
            except ValueError:
                animate_message("Sorry, that's an invalid input! Please enter a positive integer.\n")

    # Input router configurations based on protocol and interface count
    for _ in range(protocol_count):
        while True:
            protocol = input_with_history(
                "Please input the network protocol to configure (Choice: OSPF, EIGRP): ").lower()
            if protocol.lower() in ['ospf', 'eigrp']:
                break
            else:
                animate_message("Sorry, that's an invalid input! Please enter either 'OSPF' or 'EIGRP'\n")

        if protocol.lower() == 'ospf':
            area = get_positive_integer_input("Enter the OSPF Area: ")
            process_id = get_positive_integer_input("Enter the OSPF Process ID: ")
            num_networks = get_positive_integer_input("Enter the number of networks to advertise: ")
            networks = []
            print("Please input the networks to advertise using the Format: x.x.x.x/y ")
            for k in range(num_networks):
                while True:
                    network = input_with_history(f"Network {k + 1}: ")
                    if validate_cidr_network(network):
                        break
                    else:
                        animate_message(
                            "That's an invalid input! Please enter a valid CIDR network in the format x.x.x.x/y.")
                network_address = convert_cidr_network_wildcard(network)
                networks.append(network_address)
            router_interface_config.append(
                {'protocol': protocol, 'area': area, 'process_id': process_id, 'networks': networks})
        elif protocol.lower() == 'eigrp':
            as_number = get_positive_integer_input("Enter the AS Number: ")
            num_networks = get_positive_integer_input("Enter the number of networks to advertise: ")
            networks = []
            print("Please input the networks to advertise using the Format: x.x.x.x/y ")
            for k in range(num_networks):
                while True:
                    network = input_with_history(f"Network {k + 1}: ")
                    if validate_cidr_network(network):
                        break
                    else:
                        animate_message(
                            "Sorry, that's an invalid input! Please enter a valid CIDR network in the format "
                            "x.x.x.x/y.\n")
                network_address = convert_cidr_network_wildcard(network)
                networks.append(network_address)

            router_interface_config.append({'protocol': protocol, 'as_number': as_number, 'networks': networks})

    for _ in range(interface_count):
        # Input interface configurations with IP addresses
        interface = input_with_history("Enter the interface name: ").lower()
        while True:
            ip_network = input_with_history("Enter the IP address and network (Format: x.x.x.x/y): ")
            if validate_cidr_network(ip_network):
                break
            else:
                animate_message(
                    "Sorry, that's an invalid input! Please enter a valid CIDR network in the format x.x.x.x/y.\n")
        ip_address = convert_cidr_network(ip_network)
        router_interface_config.append({'interface': interface, 'ip': ip_address})

    navigate_inputs()  # Enable input navigation

    return router_interface_config
