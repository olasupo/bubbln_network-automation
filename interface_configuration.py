import re
import ipaddress
import readline
import time


# This function animates outputs information
def animate_message(message):
    for char in message:
        print(char, end='', flush=True)
        time.sleep(0.05)
    # print()


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

    def validate_cidr_network(cidr_network):
        # Validate if the CIDR network format is correct
        network_parts = cidr_network.split("/")
        if len(network_parts) != 2:
            return False

        ip_address = network_parts[0]
        subnet_mask = network_parts[1]
        if not re.match(r"\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$", ip_address):
            return False

        try:
            ipaddress.IPv4Network(cidr_network, strict=False)
            return True
        except (ipaddress.AddressValueError, ipaddress.NetmaskValueError, ValueError):
            return False

    def convert_cidr_network(cidr_network):
        # Convert CIDR network to network address
        ip, subnet = cidr_network.split("/")
        subnet_mask = (0xFFFFFFFF << (32 - int(subnet))) & 0xFFFFFFFF
        subnet_mask = [(subnet_mask >> i) & 0xFF for i in [24, 16, 8, 0]]
        ip_parts = ip.split(".")
        network_address = ".".join(ip_parts[:4]) + " " + ".".join(str(part) for part in subnet_mask)
        return network_address

    def convert_cidr_network_wildcard(cidr_network):
        # Convert CIDR network to network address with wildcard mask
        ip, subnet = cidr_network.split("/")
        subnet_mask = (0xFFFFFFFF << (32 - int(subnet))) & 0xFFFFFFFF
        subnet_mask = [(subnet_mask >> i) & 0xFF for i in [24, 16, 8, 0]]
        wildcard_mask = [(255 - subnet_mask[i]) for i in range(4)]
        ip_parts = ip.split(".")
        network_address = ".".join(ip_parts[:4]) + " " + ".".join(str(part) for part in wildcard_mask)
        return network_address

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

    navigate_inputs()

    return router_interface_config
