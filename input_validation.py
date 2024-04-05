
import os
import openai

from interface_configuration import get_router_interface_configuration



def validate_openai_key(api_key):
    openai.api_key = api_key
    try:
        openai.Completion.create(model="text-davinci-003", prompt="Test prompt", max_tokens=5)
        return True
    except openai.error.AuthenticationError  as e:
        #print("Invalid API key:", e)
        return False


def validate_inputs(interface_configurations):
    for i, router_config in enumerate(interface_configurations):
        print(f"Router {i+1}:")
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
                        print(f"\t\tNetwork {j+1}: {network}")
                elif protocol.lower() == 'eigrp':
                    as_number = protocol_config['as_number']
                    num_networks = len(protocol_config['networks'])
                    print(f"\t\tEIGRP AS Number: {as_number}")
                    print(f"\t\tNumber of networks to advertise: {num_networks}")
                    for j, network in enumerate(protocol_config['networks']):
                        print(f"\t\tNetwork {j+1}: {network}")
        for interface_config in router_config:
            if 'interface' in interface_config and 'ip' in interface_config:
                interface_name = interface_config['interface']
                ip_address = interface_config['ip']
                print(f"\tInterface: {interface_name}")
                print(f"\tIP Address: {ip_address}")
        print()

    while True:
        confirm = input("Do you want to proceed with the above inputs? (y/n): ")
        #confirm = 'y'
        if confirm.lower() == 'y':
            return True
        elif confirm.lower() == 'n':
            while True:
                index_to_correct = input("\n\nOn which router do you want to make corrections - Enter '1' for Router1 etc: ")
                try:
                    index = int(index_to_correct) - 1
                    if 0 <= index < len(interface_configurations):
                        router_config = interface_configurations[index]
                        protocol_count = len([config for config in router_config if 'protocol' in config])
                        interface_count = len([config for config in router_config if 'interface' in config and 'ip' in config])
                        print(f"\nCorrecting inputs for Router {index + 1}...\n")
                        interface_configurations[index] = get_router_interface_configuration(protocol_count, interface_count)
                        os.system('clear')
                        break
                    else:
                        print(f"Invalid input! Please enter a valid router index between 1 and {len(interface_configurations)}.")
                except ValueError:
                    print("Invalid input! Please enter a valid router index number.")
            print("\n\nPlease review and validate your corrected inputs:")
            return validate_inputs(interface_configurations)
        else:
            print("Invalid input! Please enter 'y' or 'n'.")





