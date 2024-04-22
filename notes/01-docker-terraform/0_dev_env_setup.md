# Development Environment Setup
These notes serve as a guide for setting up a development environment on Google Cloud Platform (GCP) for the Data Engineering Zoomcamp course.

I chose to setup my development environment in GCP so that I would have practice using virtual machines (VMs) in the cloud. This is also best practice for working on projects that require large amounts of compute power or storage (does not fit on local machine). I also wanted to practice using Terraform to manage cloud resources.

I am following this [video tutorial](https://www.youtube.com/watch?v=ae-CV2KfoN0&list=PL3MmuxUbc_hJed7dXYoJw8DoCuVHhGEQb) - it's a bit confusing, so I've documented the steps I took below.

## Prerequisites
- Google Cloud Platform account.
  - Created new GMail account (e.g. `greg.dezc@gmail.com`) to get $300 in free credits when signing up for GCP.
- Visual Studio Code (VSCode) installed.
- Comfortable using the command line.
- Google Cloud SDK installed.

## 1. Create a new GCP project and service account
Go to the [Google Cloud Console](https://console.cloud.google.com/) and create a new project named `data-engineering-zoomcamp`. Make note of the project ID as this will be useful alter (e.g., `data-eng-zoomcamp-420803`).

Go to `IAM > Service Accounts` and create a new service account named `data-eng-zoomcamp-sa` with the following `Basic Viewer` role (we'll update this later as needed). Then, create a new key by click the 3 dots on the right side of the service account row and selecting `Create key`. Save the key as a JSON file to your local machine at `~/.google/credentials` directory.
```bash
# Create the directory to store the GCP service account key
$ mkdir -p ~/.google/credentials
$ mv ~/Downloads/<-downloaded-key-file>.json ~/.google/credentials/google_credentials.json
```

## 2. SSH keys
SSH keys are used to securely connect to virtual machine (VM) instances on GCP.

Create a new SSH key pair (`gcp` and `gcp.pub`) on your local machine using the following command:
```bash
$ cd ~
$ mkdir .ssh
$ cd ~/.ssh
# Create a public and private key pair (gcp and gcp.pub)
$ ssh-keygen \
   -t rsa \     # RSA encryption
   -f gcp \     # Filename for the private key
   -C gclunies  # Username
   -b 2048      # Key length
# No passphrase when prompted
```
We'll use the public key (`gcp.pub`) later to connect to the VM instance.

## 3. Create a VM instance in GCP
Go to `Compute Engine` > `VM instances` > `Create Instance` and create a new VM instance named `data-eng-zoomcamp-vm` using the following settings:
- Region: `us-central1 (Iowa)` (closest to me)
- Instance type: `e2-standard-4 (4vCPU 16 GB memory)`
- Boot disk: `Ubuntu 20.04 LTS`, `Balanced persistent disk`, `30 GB`
- Reserve a static IP address for the VM: `Advanced Options` > `Networking` > `Networking Interfaces` > `External IP` > `Reserved static external IP address`
  - name: `data-eng-zoomcamp-ip`

You can start/stop the VM instance from the `VM instances` page or using from your local machine using the `gcloud` CLI.
```bash
$ gcloud config set project <project-id>
$ gcloud compute instances start <instance-name>
$ gcloud compute instances stop <instance-name>
```

## 4. Connect to the VM instance
### 4.1. Add SSH key to the VM instance
Add the public SSH key (`~/.ssh/gcp.pub`) to the VM instance so you can connect to it securely under `Compute Engine` > `Metadata` > `SSH Keys`.

### 4.2. Connect to the VM instance
Login to the VM instance using the private SSH key (`~/.ssh/gcp`) and the external IP address of the VM.
```bash
$ ssh -i ~/.ssh/gcp gclunies@<external-ip>
```

To make the connection easier, create an SSH config file (`~/.ssh/config`) with the following content:
```bash
Host data-eng-zoomcamp-vm
    HostName <external-ip>
    User gclunies
    IdentityFile ~/.ssh/gcp
```
You can now SSH into the VM instance using the following command.
```bash
# Login to the VM instance
$ ssh de-zoomcamp
gclunies@data-eng-zoomcamp-vm:~$  # Prompt now shows we logged in successfully

# To logout of the VM instance type `Ctrl + D`, `exit` or `logout`
gclunies@data-eng-zoomcamp-vm:~$ exit
```

## 5. Setup VM dev environment
### 5.1. Install `conda`
Install `conda` (Python package manager) via `miniforge`. I use miniforge because:
- It is a minimal installer for conda that only uses the `conda-forge` channel.
- Community maintained, truly open-source, no restrictions on usage (unlike distributions from Anaconda, Inc.).
```bash
# Log into the VM instance
$ ssh de-zoomcamp

# I don't show updated VM prompt here, but you should see something like:
# gclunies@data-eng-zoomcamp-vm:~$

# Download miniforge
$ wget "https://github.com/conda-forge/miniforge/releases/latest/download/Miniforge3-$(uname)-$(uname -m).sh"

# Install miniforge
$ bash Miniforge3-$(uname)-$(uname -m).sh
# Follow the prompts to install miniforge ... yes/enter to all

# Source the .bashrc file to activate conda
$ source ~/.bashrc

# Check that conda was installed version
$ which conda
/home/gclunies/miniforge3/bin/conda

# Add the mamba solver to conda for faster package resolution
$ conda install -n base conda-libmamba-solver
$ conda config --set solver libmamba

# Show all configured conda channels
$ conda config --show channels
$ conda config --set channel_priority strict
```

### 5.2. Install `docker` and `docker-compose`ds
Install `docker` and `docker-compose` on the VM instance.
```bash
# In the VM instance

# Update the package list and install docker
$ sudo apt-get update
$ sudo apt-get install docker.io

# Config docker to run without sudo
$ sudo groupadd docker
$ sudo gpasswd -a $USER docker

# Log out and log back in to apply the changes
$ exit
$ ssh de-zoomcamp

# Test docker installation
$ docker run hello-world

Unable to find image 'hello-world:latest' locally
latest: Pulling from library/hello-world
c1ec31eb5944: Pull complete
Digest: sha256:91bc16c380fe750bcab6a4fd29c55940a7967379663693ec9f4749d3878cd939
Status: Downloaded newer image for hello-world:latest

Hello from Docker!
This message shows that your installation appears to be working correctly.

To generate this message, Docker took the following steps:
 1. The Docker client contacted the Docker daemon.
 2. The Docker daemon pulled the "hello-world" image from the Docker Hub.
    (amd64)
 3. The Docker daemon created a new container from that image which runs the
    executable that produces the output you are currently reading.
 4. The Docker daemon streamed that output to the Docker client, which sent it
    to your terminal.

To try something more ambitious, you can run an Ubuntu container with:
 $ docker run -it ubuntu bash

Share images, automate workflows, and more with a free Docker ID:
 https://hub.docker.com/

For more examples and ideas, visit:
 https://docs.docker.com/get-started/

# Install docker-compose from https://github.com/docker/compose/releases (use latest release)
$ mkdir bin  # Create a bin directory to store executables
$ wget https://github.com/docker/compose/releases/download/v2.26.1/docker-compose-linux-x86_64 -O ~/bin/docker-compose

# Make the file executable
$ chmod +x ~/bin/docker-compose

# Test docker-compose installation
$ ~/bin/docker-compose --version
Docker Compose version v2.26.1

# Add the bin directory to the PATH
$ echo 'export PATH=$HOME/bin:$PATH' >> ~/.bashrc
$ source ~/.bashrc

# Test docker-compose installation
$ docker-compose --version
Docker Compose version v2.26.1
```

### 5.3. Install docker images for `pgadmin` and `postgres`
The course repo contains a `docker-compose.yml` file that define container images for a `pgadmin` and `postgres` service. We will use this to run a PostgreSQL database and a pgAdmin web interface in docker containers.
```bash
# In the VM instance

# Clone the course repo
$ git clone https://github.com/DataTalksClub/data-engineering-zoomcamp.git
# Change to the directory with the docker-compose file
$ cd ~/data-engineering-zoomcamp/01-docker-terraform/2_docker_sql/

# Build the docker images for pgadmin and postgres
$ docker-compose up -d

# Check that the containers are running
$ docker ps
```

### 5.4 Install `pgcli`
```bash
# In the VM instance
$ conda install pgcli

# Test pgcli installation
$ pgcli --version
Version: 4.0.1

# Connect to the PostgreSQL database (Docker containers must be running on the VM!)
$ pgcli -h localhost -U root -d ny_taxi
Password for root:  # Enter the password 'root' when prompted

Server: PostgreSQL 13.14 (Debian 13.14-1.pgdg120+2)
Version: 4.0.1
Home: http://pgcli.com
root@localhost:ny_taxi> \dt  # List tables in the database
+--------+------+------+-------+
| Schema | Name | Type | Owner |
|--------+------+------+-------|
+--------+------+------+-------+
SELECT 0
Time: 0.013s
$ root@localhost:ny_taxi> \q  # Quit pgcli
Goodbye!
```

### 5.5 SSH Port Forwarding
Remember that `postgres` and `pgadmin` are running in a docker container on the VM instance.

To simplify the development workflow, we can forward the port(s) running on the VM instance to our local machine. This way we can access the `postgres` database and  `pgadmin` web interface locally.

```bash
# In the VM instance
# Forward port 8080 on the VM to port 8080 on your local machine
$ ssh -L 8080:localhost:8080 gclunies@<external-ip>
```
Now you can access the pgAdmin web interface by going to `http://localhost:8080` in your browser.
![alt text](./images/image.png).

Alternatively, you can connect to the host VM via VSCode and use the `Remote - SSH` extension to forward the port(s) to your local machine. See the [video tutorial](https://www.youtube.com/watch?v=ae-CV2KfoN0&list=PL3MmuxUbc_hJed7dXYoJw8DoCuVHhGEQb&index=16&t=32m17s) for a demo.

## 6. Install Terraform
Terraform is an open-source infrastructure as code tool that provides a consistent CLI workflow to manage hundreds of cloud services.

```bash
$ ssh data-eng-zoomcamp-vm

# In the VM instance
$ cd bin
$ wget https://releases.hashicorp.com/terraform/1.8.1/terraform_1.8.1_linux_amd64.zip
$ sudo apt-get install unzip
$ unzip terraform_1.8.1_linux_amd64.zipds
$ rm terraform_1.8.1_linux_amd64.zip
```
To use Terraform on the VM, we need the GCP service account key (previously saved to our machine) on the VM instance. We can use `sftp` to transfer the file to the VM instance.
```bash
# On local machine
$ cd ~/.google/credentials
$ sftp data-eng-zoomcamp-vm
Connected to data-eng-zoomcamp-vm.
$ sftp> .mkdir .google
$ sftp> cd .google
$ sftp> mkdir credentials
$ sftp> cd credentials
$ sftp> ls -lah
drwxrwxr-x    ? 1001     1002         4.0K Apr 20 16:15 .
drwxr-xr-x    ? 1001     1002         4.0K Apr 20 16:15 ..
$ sftp> put google_credentials.json
Uploading google_credentials.json to /home/gclunies/.google/credentials/google_credentials.json
google_credentials.json                                                                          100% 2406    47.2KB/s   00:00
$ sftp> ls -lah
drwxrwxr-x    ? 1001     1002         4.0K Apr 20 16:15 .
drwxr-xr-x    ? 1001     1002         4.0K Apr 20 16:15 ..
-rw-rw-r--    ? 1001     1002         2.4K Apr 20 16:15 google_credentials.json
```

Now, on the VM instance, we can set a `GOOGLE_APPLICATION_CREDENTIALS` environment variable to the path of the service account key file.
```bash
$ ssh data-eng-zoomcamp-vm

# On the VM instance
# Set the GOOGLE_APPLICATION_CREDENTIALS environment variable
$ export GOOGLE_APPLICATION_CREDENTIALS=~/.google/credentials/google_credentials.json
# Authenticate the service account using the key file environment variable
$ gcloud auth activate-service-account --key-file=$GOOGLE_APPLICATION_CREDENTIALS
Activated service account credentials for: [data-eng-zoomcamp-sa@data-eng-zoomcamp-420803.iam.gserviceaccount.com]
```
