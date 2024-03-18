#/ bin/bash

echo "############ Install docker #############"
# Add Docker's official GPG key:
sudo apt-get update
sudo apt-get install ca-certificates curl -y
sudo install -m 0755 -d /etc/apt/keyrings
sudo curl -fsSL https://download.docker.com/linux/ubuntu/gpg -o /etc/apt/keyrings/docker.asc
sudo chmod a+r /etc/apt/keyrings/docker.asc

# Add the repository to Apt sources:
echo \
  "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.asc] https://download.docker.com/linux/ubuntu \
  $(. /etc/os-release && echo "$VERSION_CODENAME") stable" | \
  sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
sudo apt-get update
sudo apt-get install docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin -y

sudo groupadd docker

sudo usermod -aG docker $USER

newgrp docker

echo "############ End Install docker #############"


echo "############ Install kubectl #############"

sudo snap install kubectl --classic

sudo apt-get install bash-completion -y

kubectl completion bash | sudo tee /etc/bash_completion.d/kubectl > /dev/null

echo 'alias k=kubectl' >>~/.bashrc

source ~/.bashrc

echo "############ End Install kubectl #############"


echo "############ Install minikube #############"
curl -Lo minikube https://storage.googleapis.com/minikube/releases/latest/minikube-linux-amd64 \
  && chmod +x minikube
sudo mkdir -p /usr/local/bin/
sudo install minikube /usr/local/bin/
minikube start

echo "############ End Install minikube #############"


