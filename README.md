[![published](https://static.production.devnetcloud.com/codeexchange/assets/images/devnet-published.svg)](https://developer.cisco.com/codeexchange/github/repo/olasupo/bubbln_network-automation)           [![Run in Cisco Cloud IDE](https://static.production.devnetcloud.com/codeexchange/assets/images/devnet-runable-icon.svg)](https://developer.cisco.com/codeexchange/devenv/olasupo/bubbln_network-automation/)

# Bubbln: An AI-driven Network Automation

In the world of network engineering, automation has completely transformed the way things work. But, before automation, setting up and managing networks was a tedious job filled with challenges. Engineers had to manually type out configurations, often doing the same tasks repeatedly on different devices. This led to mistakes and wasted time.

Then came automation tools like Ansible, Chef, and Puppet, which changed everything. They made network management much easier and allowed for scalability. But there was still a problem: creating automation scripts required a lot of technical know-how and was prone to errors because it relied on human input.

And that's why we built Bubbln. It's a game-changer in network engineering, integrating AI into Ansible to take automation to the next level. With Bubbln, we can automatically generate and execute playbooks with incredible accuracy, thereby improving automation efficiency and increasing network engineer’s productivity. It was developed using Python programming language and acts as a bridge between ChatGPT and network systems, making interactions seamless and deployments effortless.

## Current Capabilities

**AI-Driven Playbook Generation for OSPF and EIGRP based networks:** Bubbln has been rigorously tested to leverage ChatGPT for generation of playbooks for networks based on OSPF and EIGRP networks, with a very high accuracy rate.

**Auto-creation of Inventory files:** Users do not need to prepare the hosts file. Bubbln will auto-generate this file from input provided by the user.

**Customizable Configurations:** Users can input specific router protocols (OSPF or EIGRP), interface configurations, and other network details to tailor the generated playbooks.

**Documentation:** Bubbln automatically creates a report that contains the network configurations, prompts, and generated playbooks for easy reference in future.

**No expertise required:** By auto-generation of the playbooks and inventory file, Bubbln has been able to eliminate a major hurdle to network automation – need for users to learn the automation tools e.g Ansible, Chef.

**Improved Efficiency:** With AI automation, Bubbln speeds up the deployment of network configurations, reducing the time required for manual playbook creation, thereby increasing the productivity of network engineers.

## Getting Started

There are two main approaches to installing Bubbln on your local machine.

### Docker Container

Bubbln has been packaged using docker containers for easy distribution and usage. The following steps can be followed to deploy the Bubbln container on your local machine.

1. **Ensure docker is installed** on your local machine by entering the below command. This command works for windows and linux OS:

    ```bash
    docker --version
    ```

    The version of docker would be displayed if it is installed. Otherwise, please follow the link below to install docker on your machine:
    
    - Windows: [Docker Desktop for Windows](https://docs.docker.com/desktop/install/)
    - Ubuntu: [Docker Engine for Ubuntu](https://docs.docker.com/engine/install/ubuntu/)
    - CentOS: [Docker Engine for CentOS](https://docs.docker.com/engine/install/centos/)
    - Debian: [Docker Engine for Debian](https://docs.docker.com/engine/install/debian/)
    - Fedora: [Docker Engine for Fedora](https://docs.docker.com/engine/install/fedora/)

2. **Download the docker image**: Create a directory for the project and download Bubbln image using the below command:

    ```bash
    docker pull olasupoo/bubbln:latest
    ```

3. **Run the docker container** using the below command:

    ```bash
    docker run -it --network host --name bubbln-container olasupoo/bubbln
    ```

4. **Update the ssh_ip_addresses.txt file**: Update the ssh_addresses.txt file with the SSH IP addresses of the routers you want to configure. Bubbln will utilize this information along with the login credentials (inputted at runtime) to automatically generate a hosts.yml file required by ansible for network configuration. To do this enter the below command to edit the file:

 ```bash
 nano ssh_ip_addresses.txt
```

5.	**Obtain an OpenAPI API Key**: You may follow this guide to sign up and obtain an API key:

```bash
https://platform.openai.com/docs/quickstart?context=python
```

6.	**Utilizing a Virtualization machine of choice**, setup a network with the following basic configurations:

* Enable SSH on each of the routers.
* Configure IP addresses and enable only interfaces required for connectivity by Bubbln.
* Configure static routes to enable Bubbln reach the routers on the network.
* Ensure all the routers can be reached by ping and SSH from your host machine.

7. **Initialize Bubbln** by entering the below command:

    ```bash
    python3 bubbln.py
    ```

### Github Repository Clone

You can clone Bubbln’s GitHub repository by following the below steps:

1. **Prerequisites**

* Bubbln works well with Python 3.10. You need to ensure python3.10 is installed on your local machine. This can be confirmed by entering the below command:

```bash
python -V
```

* If it is not Installed, then the below command can be utilized to install python 3.10:

```bash
sudo apt update
sudo apt install python3.10
```

2. **Build and Prepare the Project**
* **Clone the Bubbln repository from GitHub**: To clone the repository, first verify you have git installed on your machine by issuing the following commands:

```bash
git --version
```

If git is installed, the version number would be displayed, otherwise, you can issue the following commands to have git installed on your machine:

```bash
sudo apt update
sudo apt install git
```

* **Navigate or create a directory for the project** on your machine and issue the following commands to clone the Bubbln git repository:

```bash
git clone https://github.com/olasupo/bubbln_network-automation.git
```

3. **Create a Virtual Environment for the application**
Firstly, confirm virtualenv is installed on your machine by inputting the following command:

```bash
pip show virtualenv
```

If the output shows something similar to the below, then go to the next step to install virtualenv

``
WARNING: Package(s) not found: env, virtual
``

Issue the below command to install virtualenv:

```bash
pip install virtualenv
```

4. **Create a virtual environment for the project:**

```bash
python3 -m venv chosen_name_of_your_virtual_env
```

5. **Activate the virtual environment**:

```bash
source venv/bin/activate
```

6. **Install the dependencies**

```bash
sudo apt install python3-dev &&
sudo apt install gcc &&
sudo apt install  libssh-dev
```

You can then run the below command to install the necessary packages for the app.

```bash
 pip install -r requirements.txt
```

7. **Update the ssh_ip_addresses.txt file**: Update the ssh_addresses.txt file with the SSH IP addresses of the routers you want to configure. Bubbln will utilize this information along with the login credentials (inputted at runtime) to automatically generate a hosts.yml file required by ansible for network configuration.

8. **Obtain an OpenAPI API Key**: You may follow this guide to sign up and obtain an API key 

    - OpenAI Key: [OpenAI Key](https://platform.openai.com/docs/quickstart?context=python)

9. **Utilizing a Virtualization machine of choice**, setup a network with the following basic configurations:
* Enable SSH on each of the routers.
* Configure IP addresses and enable only interfaces required for connectivity by Bubbln
* Configure static routes to enable Bubbln reach the routers on the network.
* Ensure all the routers can be reached by ping and SSH from your host machine.

10. **Initialize Bubbln**
* **While ensuring that python virtual environment** is activated as stated in step 5, run the below command to initialize Bubbln

```bash
python3 bubbln.py
```

# How Bubbln Works

Bubbln serves as an intermediary between ChatGPT and a network infrastructure, providing logic, control functions, and facilitating network automation. Its operation can be summarized as follows:

![image](https://github.com/olasupo/naijacontest/assets/4561196/1e9a9ca5-e8c5-4ea0-a6c2-c78967457382)
_Figure 1Bubbln architecture and interaction with a network of four routers._

### Initialization:

When Bubbln is initialized, it checks the “user_config.pkl” file to see if Bubbln has ever been initiated. This is indicated by the presence of a welcome message status in the file. If it exists, Bubbln jumps straight to request the user to input the OpenAI key. Otherwise, it displays a welcome message, and updates the user_config.pkl file accordingly. Upon successful input of the API key, the user is prompted for the SSH credentials of the routers. These parameters are then encrypted and saved in the user_config.pkl file. The SSH credential is later decrypted and parsed as input to dynamically generate a hosts.yml file at runtime.

**Responsible Code Section:** bubbln.py:  welcome_message_feature()

![image](https://github.com/olasupo/naijacontest/assets/4561196/74fccfdc-5191-4b47-a02e-dc076ebe0ebb)
_Figure 2 Bubbln's welcome message_.

### Parameter Input & Validation:

In the parameter input stage, Bubbln first checks for the existence of a file called “router_configuration.pkl”. If it exists, the user is prompted to decide whether to load an existing configuration or input a new set of configurations. If the file is empty or non-existent, then users are prompted to input the configuration parameters for each router on the network. These parameters serve as variables that are combined with hardcoded instructions written in natural language to form the prompt sent to ChatGPT. Key parameters include:

**Router Configurations:**
    - OSPF Area
    - OSPF Process ID
    - Number of networks to advertise (OSPF/EIGRP)
    - AS Number (EIGRP)
    - Interface names
    - IP Addresses (in CIDR format)

This module also ensures that parameters are keyed in using the correct data type and format e.g. IP addresses are expected in CIDR format and OSPF Area should be of type integer. Upon completion of parameter input, all parameters are saved into a file called “router_configuration.pkl” upon validation of accuracy by the user.

**Responsible Code Section**: parameter_input.py

![image](https://github.com/olasupo/naijacontest/assets/4561196/03134054-876b-4cfb-b8c3-75f749420b9e)
_Figure 3 Bubbln receiving Network Parameters._

Before generating the prompt, a summary of the inputted parameters is displayed for user validation. This step ensures accuracy and minimizes errors. Users are given the option to make corrections if any discrepancies are found.

**Responsible Code Section**: parameter_input.py: validate_inputs()

![image](https://github.com/olasupo/naijacontest/assets/4561196/8e02f95f-4f82-4cb2-91aa-fd6b4d2d4197)
_Figure 4 Bubbln Awaiting Validation of Inputted Network Parameters._

### Auto-Generation of Prompt:

After validation of inputted parameters, Bubbln composes the prompt by combining the inputted parameters with a set of well-engineered hardcoded instructions written in natural language.
 
**Responsible Code Section**: prompt_generator.py

### ChatGPT Prompting:

The auto-composed prompt is then sent to ChatGPT utilizing gpt-4 chatCompletions model with a temperature parameter of 0.2 and maximum tokens of 1500. The following functions were designed into this process stage
 
**Responsible Code Section**: chatGPT_prompting.py

![image](https://github.com/olasupo/naijacontest/assets/4561196/df8b0096-e99c-4550-99fd-58e2577e8160)
_Figure 5 ChatGPT prompting in progress_

### Playbook Generation & Extraction:

After ChatGPT processes the prompt from Bubbln, it provides a response which usually contains the generated playbook and explanatory notes. Bubbln then extracts the playbook from the explanatory notes by searching for “---” which usually connotes the start of playbooks and saves each generated playbook uniquely using the nomenclature Router_i_Playbook.yml.

**Responsible Code Section**: playbook_extractor.py

![image](https://github.com/olasupo/naijacontest/assets/4561196/ddec4b40-0d2c-4b6c-a2a4-ccbbbd97793b)
_Figure 6 ChatGPT-generated playbook._

### Playbook Execution:
Bubbln loads the saved “Router_i_Playbook.yml” playbook and dynamically generates the hosts.yml file and parses them to the python library ansible_runner for further execution on the configured network. Bubbln generates the hosts.yml file at run time by using the pre-inputted SSH credentials in user_config.pkl file - and decrypts them, as well as IP addresses from the ssh_ip_addresses.txt file, as inputs 

**Responsible Code Section**: playbook_execution.py

![image](https://github.com/olasupo/naijacontest/assets/4561196/e11fef3a-d1d3-49be-8c9d-7458eac55098)
_Figure 7 Playbook execution in progress_

### Sample result of Executed Playbook

Upon successful execution of all playbooks, a query of the routing table on router 4 indicates that router 4 could reach all the prefixes on the network.

![image](https://github.com/olasupo/naijacontest/assets/4561196/7d4b3c55-7e8c-41a7-810b-5054aa3106cb)
_Figure 8 Output of 'sh ip route' executed on R1_

### File Management and Handling

Throughout the execution process, Bubbln manages the creation, saving, and loading of various files to streamline the network automation process.
* **user_config.pkl**: This dictionary file dynamically created at run time is used to store encrypted API keys, SSH credentials and initial welcome message information.
* **router_configuration.pkl**: It is auto created by Bubbln and used to store network configuration parameters for easy loading during subsequent sessions.
* **hosts.yml**: This is a runtime autogenerated file that contains inventory of the network devices. It is auto deleted after the program runs.
* **network_configuration_report.pdf**: This auto-generated report by Bubbln is a documentation of all the routers configured their parameters, generated playbooks, and prompt for each execution of the Bubbln application. It is created after a successful execution of playbooks and network testing and is meant for auditing and documentation purposes.
* **Router_i_Playbook.yml**: After extraction of generated playbooks from ChatGPT’s raw response, Bubbln automatically saves a copy of the generated playbook using unique names for each playbook.

![image](https://github.com/olasupo/naijacontest/assets/4561196/003ca819-e051-4010-801c-71b35996da2f)
_Figure 9 File structure after successful deployment of a four-router network_

### Providing Feedback

We are glad to hear your thoughts and suggestions. Kindly do this through the discussion section of our GitHub - https://github.com/olasupo/bubbln_network-automation/discussions/1#discussion-6487475

We can also be reached on:
Olasupo Okunaiya – [olasupo.o@gmail.com](mailto:olasupo.o@gmail.com)



