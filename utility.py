import shutil
import pickle
from pygments import highlight
from pygments.lexers import get_lexer_by_name
from pygments.formatters import TerminalFormatter
import re
import ipaddress
import os
from fpdf import FPDF

# Get the current directory path
current_path = os.path.dirname(os.path.abspath(__file__))

# Load or create user configuration
def load_user_config():
    existing_config_file = os.path.join(current_path, "user_config.pkl")
    if os.path.exists(existing_config_file):
        with open(existing_config_file, "rb") as file:
            return pickle.load(file)
    else:
        return {}

def save_user_config(config):
    existing_config_file = os.path.join(current_path, "user_config.pkl")
    with open(existing_config_file, "wb") as file:
        pickle.dump(config, file)

# Encrypt or load OpenAI key
def encrypt_key(key, cipher_suite):
    return cipher_suite.encrypt(key.encode())

def decrypt_key(encrypted_key, cipher_suite):
    return cipher_suite.decrypt(encrypted_key).decode()

def animate_message(message):
    # Animate the message to be printed one character at a time
    for char in message:
        print(char, end='', flush=True)

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
    print("=" * width)

# Function to get a positive integer input from the user
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

# Function to save router configurations
def save_configuration(configurations):
    config_file = os.path.join(current_path, "router_configurations.pkl")
    with open(config_file, "wb") as file:
        pickle.dump(configurations, file)

# Function to load router configurations
def load_configuration():
    config_file = os.path.join(current_path, "router_configurations.pkl")
    if os.path.exists(config_file):
        with open(config_file, "rb") as file:
            return pickle.load(file)
    else:
        return None

# Function to print text in blue color
def print_blue(text):
    animate_message("\033[94m{}\033[0m".format(text))

# Function to format and print colored code
def print_colored_code(code):
    lexer = get_lexer_by_name("yaml")  # Set the appropriate lexer for the code language
    formatter = TerminalFormatter()
    colored_code = highlight(code, lexer, formatter)
    print(colored_code)

# Function to print a summary of execution times
def print_summary(input_router_duration, generate_playbooks_duration, execute_playbooks_duration, summary_duration):
    print_blue("\n\n********** Below is a Summary of How Long It Took Us To Setup Your Network **********")
    print_blue("\n1. We spent {:.2f} seconds to input the various router parameters.".format(input_router_duration))
    print_blue("\n2. The process for generating all the playbooks took {:.2f} seconds.".format(generate_playbooks_duration))
    print_blue("\n3. We spent {:.2f} seconds to execute all the generated playbooks".format(execute_playbooks_duration))
    print_blue("\n4. In Total, it has taken {:.2f} seconds to automate your network from start to finish".format(summary_duration))

# Function to validate CIDR network format
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

# Function to convert CIDR network to network address
def convert_cidr_network(cidr_network):
    ip, subnet = cidr_network.split("/")
    subnet_mask = (0xFFFFFFFF << (32 - int(subnet))) & 0xFFFFFFFF
    subnet_mask = [(subnet_mask >> i) & 0xFF for i in [24, 16, 8, 0]]
    ip_parts = ip.split(".")
    network_address = ".".join(ip_parts[:4]) + " " + ".".join(str(part) for part in subnet_mask)
    return network_address

# Function to convert CIDR network to network address with wildcard mask
def convert_cidr_network_wildcard(cidr_network):
    ip, subnet = cidr_network.split("/")
    subnet_mask = (0xFFFFFFFF << (32 - int(subnet))) & 0xFFFFFFFF
    subnet_mask = [(subnet_mask >> i) & 0xFF for i in [24, 16, 8, 0]]
    wildcard_mask = [(255 - subnet_mask[i]) for i in range(4)]
    ip_parts = ip.split(".")
    network_address = ".".join(ip_parts[:4]) + " " + ".".join(str(part) for part in wildcard_mask)
    return network_address

# Class to format the PDF report
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
