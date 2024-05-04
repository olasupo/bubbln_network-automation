from playbook_executor import execute_playbook
import os
from chatGPT_prompting import chatGPT_prompter
import time


# Function to generate prompts and execute playbooks for each router configuration
def prompt_generator_function(pdf, interface_configurations, execution_folder, model_name,
                              generate_playbooks_start_time):
    # Iterate over each router configuration
    for i, router_config in enumerate(interface_configurations):
        conversation_history = []  # Initialize conversation history for the current router

        # Add a subheading for the current router in the PDF report
        pdf.set_font('Arial', 'B', 12)
        pdf.cell(0, 10, f"Router {i + 1} Configurations", 0, 1, 'L')
        pdf.ln(5)

        # Define the initial prompt for generating the playbook
        prompt = ("Requirements: Strictly adhere to the following explicitly stated requirements; Write a "
                  "simple Ansible playbook with separate tasks for each protocol and interface configurations "
                  "with the following details;")

        prompt += f" hosts: R{i + 1}"  # Add host information to the prompt

        prompt += " Do not worry about the inventory file;"  # Additional requirements
        # Add more requirements to the prompt
        prompt += " Ensure each Task is named;"
        prompt += " Never provide explanations for the generated playbook;"
        prompt += " Do not use variables and templates to generate the playbooks;"
        prompt += ("Ensure all generated playbooks adhere to yaml's rule of always starting a playbook with "
                   "`---` and ending the playbook with a new line containing `...`;")
        prompt += " Always use ios_config module and ensure unsupported parameters are not generated;;"
        prompt += " Use `parents` argument to implement stanzas;"
        prompt += ("when configuring interfaces, ensure you generate codes for only provided interfaces and "
                   "always implement 'No Shutdown' for each interface;")
        prompt += ("when configuring routing protocols, ensure you generate codes for only provided protocols "
                   "and that the protocol is initialized only under the parents argument using the format "
                   "`router protocol-type xx`. Also, DO NOT configure router id;")
        prompt += " set `replace` argument to block. `replace` argument should always be child to `ios_config`;"

        redistribute_required = False  # Flag to track if redistribution is required

        # Iterate over protocol configurations for the current router
        for protocol_config in router_config:
            if 'protocol' in protocol_config:
                protocol = protocol_config['protocol']
                prompt += f" Protocol: {protocol}"  # Add protocol information to the prompt
                if protocol.lower() == 'ospf':
                    # Extract OSPF configuration details
                    area = protocol_config['area']
                    process_id = protocol_config['process_id']
                    num_networks = len(protocol_config['networks'])
                    # Add OSPF configuration details to the prompt
                    prompt += f" OSPF Area: {area}, Process ID: {process_id}, Number of networks to advertise: {num_networks}"
                    # Add network information to the PDF report
                    for j, network in enumerate(protocol_config['networks']):
                        pdf.set_font('Arial', '', 12)
                        pdf.cell(0, 10, f"network: {network}", 0, 1, 'L')
                        pdf.ln(5)
                        prompt += f" network{j + 1}: {network}"
                elif protocol.lower() == 'eigrp':
                    # Extract EIGRP configuration details
                    as_number = protocol_config['as_number']
                    num_networks = len(protocol_config['networks'])
                    # Add EIGRP configuration details to the prompt
                    prompt += f" EIGRP AS Number: {as_number}, Number of networks to advertise: {num_networks}"
                    # Add network information to the PDF report
                    for j, network in enumerate(protocol_config['networks']):
                        pdf.set_font('Arial', '', 12)
                        pdf.cell(0, 10, f"network: {network}", 0, 1, 'L')
                        pdf.ln(5)
                        prompt += f" network{j + 1}: {network}"

                # Check if both EIGRP and OSPF are configured
                if protocol.lower() == 'eigrp':
                    for other_protocol_config in router_config:
                        if 'protocol' in other_protocol_config and other_protocol_config['protocol'].lower() == 'ospf':
                            redistribute_required = True

        # Add redistribution tasks to the prompt if required
        if redistribute_required:
            prompt += (f"; Using dedicated tasks, Please redistribute the routing protocols using "
                       f"'redistribute ospf {process_id} metric 1000 33 255 1 1500' for redistributing OSPF "
                       f"into EIGRP and 'redistribute eigrp {as_number} subnets' for redistributing EIGRP "
                       f"into OSPF;")
            prompt += ("The redistribution tasks, should be generated after the routing protocol configuration "
                       "tasks have been generated;")

        # Add interface configurations to the prompt and PDF report
        for interface_config in router_config:
            if 'interface' in interface_config and 'ip' in interface_config:
                interface_name = interface_config['interface']
                ip_address = interface_config['ip']
                pdf.set_font('Arial', '', 12)
                pdf.cell(0, 10, f"Interface: {interface_name}, IP: {ip_address}", 0, 1, 'L')
                pdf.ln(5)
                prompt += f" Interface: {interface_name}, IP: {ip_address}"

        prompt = prompt.rstrip(";")  # Remove the trailing semicolon

        # Add a chapter for the prompt used to generate each playbook in the PDF report
        pdf.add_page()
        pdf.chapter_title(f"Prompt for Router {i + 1}")
        pdf.chapter_body(prompt)

        # Generate playbook using ChatGPT based on the prompt
        text_before_code, playbook, text_after_code, conversation_history = chatGPT_prompter(prompt, model_name,
                                                                                             conversation_history)
        generate_playbooks_duration = time.time() - generate_playbooks_start_time

        # Add a chapter for the generated playbook in the PDF report
        pdf.add_page()
        pdf.chapter_title(f"Generated Playbook for Router {i + 1}")
        pdf.chapter_body(playbook)

        # Save generated playbook to a file
        playbook_file = os.path.join(execution_folder, f"Router_{i + 1}_Playbook.yml")
        with open(playbook_file, "w") as file:
            file.write(playbook)

        # Execute the generated playbook
        start_time = time.time()
        execute_playbook(playbook_file, model_name, i + 1, text_before_code, text_after_code, conversation_history)

    elapsed_time = time.time() - start_time

    return generate_playbooks_duration, elapsed_time
