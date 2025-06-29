---
layout: post 
title: Playing around with Ansible
category: technicalArticles
---

> From my experience working at [Simpl](https://simpl.com/).

In this article, I write my experience around debugging an issue and getting an opportunity to work with Ansible. Will highlight things at a top level. 
We have a service which powers our Airflow & distributed computing infra. Deployment of the service is a fairly complex process as it involves different steps.
We use concourse to deploy code to the AWS infra. 

Deployment pipeline of service: Concourse containers -> Bastion Servers (Ansible scripts to deploy) -> Airflow & Computing EC2 machines // 2 hop process

We can use fly intercept/set commands to access concourse containers or update pipeline config. 

First issue was related to machines not being able to communicate with each other, which was fixed. 

Second issue, but before that some info around Ansible:

- Ansible playbooks are a fundamental component of Ansible, serving as the primary means to automate tasks across multiple systems. They are written in YAML format. When you execute a playbook using the command ansible-playbook <playbook.yml>, Ansible parses the YAML file and prepares to execute the defined plays. Ansible connects to each host specified in the inventory file and executes the tasks in order. If a task fails on one host, Ansible continues executing tasks on other hosts unless configured otherwise. During execution, Ansible provides real-time feedback on the status of each task, including successes and failures. After completing all tasks, Ansible summarizes the execution results, detailing which tasks succeeded or failed.
- Now, if we view this command which runs in deploying code changes from ansible to machines and dissect it: `ansible-playbook -vv -i inventories/${INSTALL_TO_ENV}/hosts.py airflow.yml  --vault-password-file=~/vault_pass_no_prompt`
  - `ansible-playbook`: This is the command used to run Ansible playbooks. It initiates the execution of the specified playbook file.
  - `-vv`: This option increases the verbosity level of the output. The -v flag can be repeated (up to four times) to provide more detailed logging information during execution. This is useful for debugging and understanding what Ansible is doing behind the scenes.
  - `-i inventories/prod/hosts.py`: This specifies the inventory file that contains the list of hosts on which the playbook will run. In this case, hosts.py is a dynamic inventory script, which means it generates the list of hosts dynamically rather than being a static file.
  - `airflow.yml`: This is the name of the playbook file that will be executed. The playbook contains tasks that define what actions should be performed on the specified hosts.
  - `--vault-password-file=~/vault_pass_no_prompt`: This option specifies a file that contains the password used to decrypt any sensitive data stored in Ansible Vault within the playbook or any included files.
- Ansible Vault is a feature within Ansible that provides a secure mechanism for managing sensitive data, such as passwords, API keys, and other confidential information. It allows users to encrypt values and data structures within Ansible projects, ensuring that sensitive information is not stored in plaintext, which could pose a security risk.
  - Encryption and Decryption: Ansible Vault enables users to encrypt files containing sensitive data. This encryption uses symmetric encryption with the AES256 algorithm, meaning the same password is used for both encryption and decryption. Users can encrypt existing files or create new encrypted files directly.
  - File-Level Granularity: Ansible Vault operates at the file level, meaning that entire files can be encrypted or left unencrypted. This allows for flexibility in managing sensitive information alongside regular configuration data.
  - Integration with Playbooks: Encrypted content can be seamlessly integrated into Ansible playbooks. When executing a playbook, Ansible automatically decrypts any vault-encrypted content at runtime if the correct password is provided.
  - Secure Storage: By using Ansible Vault, users can securely store sensitive data within their playbooks and configuration files, preventing unauthorized access even if someone gains access to the files themselves.
- In above case we provide this flag in command: --vault-password-file=~/vault_pass_no_prompt. The vault password is crucial when working with Ansible Vault because it:
  - Decrypts Encrypted Data: If your playbook or any referenced files (like variables or configuration files) contain encrypted content (e.g., passwords, API keys), Ansible needs to decrypt this data before executing tasks that require it. The --vault-password-file option tells Ansible where to find the password needed for decryption.
  - Automates Password Handling: By using a password file (in this case, ~/vault_pass_no_prompt -> Can view contents using `vi vault_pass_no_prompt`), you can automate the process of providing the vault password without being prompted during execution. This is particularly useful for automated deployments or CI/CD pipelines where manual input would be impractical.

Now coming back, what was the issue?: 

As we know, the playbook uses set of secret credentials which is stored in ansible vault when it deploys the yaml file.
One of the secret credentials had expired.
Hence had to use the vault_pass_no_prompt key to open the ansible vault, decrypt the yaml file inside which the secret keys were kept encrypted (Note that though we say ansible vault, all the files present in the vault are present in machine only, its just that vault is just a layering on top of accessing it), change the key in yaml file, encrypt back the yaml file. 
These were the sequence of steps. Sample path where secret keys are stored encrypted in machine was: `/deploy/ansible/inventories/keys.yml`
Ansible commands for encrypting/decrypting once inside the bastion machine:
```
source ~/.venv/ansible_env/bin/activate ## activating the env with which deployment happens to ensure changes are persisted with our manual intervention
cd /deploy/ansible/inventories ## go in the dir
ansible-vault decrypt keys.yml --vault-password-file=~/vault_pass_no_prompt ## decrypt keys which are used by playbook in running yaml steps defined in files
vi keys.yml ## make changes and save 
ansible-vault encrypt keys.yml --vault-password-file=~/vault_pass_no_prompt ## encrypt back 
```

So the expired key was also fixed. 

----------------
