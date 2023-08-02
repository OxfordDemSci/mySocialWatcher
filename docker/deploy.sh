#!/bin/bash
# This script is intended to guide the setup of a new virtual machine.
# It should be run line-by-line rather than executed all at once.

# hostname
sudo hostnamectl set-hostname msw_collectors

# update
sudo apt-get update -y && sudo apt-get upgrade -y && sudo apt-get auto-remove -y && sudo reboot now

sudo crontab -e
# @weekly apt-get update -y && apt-get upgrade -y && apt-get auto-remove -y

#---- docker ----#

# install docker
sudo apt-get install ca-certificates curl gnupg lsb-release

sudo mkdir -p /etc/apt/keyrings
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg

echo \
  "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu \
  $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null

sudo apt-get update && sudo apt-get install -y docker-ce docker-ce-cli containerd.io docker-compose-plugin
sudo apt-get update && sudo apt-get install -y docker-compose

# add user to docker group
sudo usermod -aG docker ubuntu

# crontab to persist read/write access to docker socket
sudo crontab -e
# @reboot chmod a+rw /var/run/docker.sock


#---- github ----#
sudo apt install git

# create GitHub deploy key
cd ~/.ssh
ssh-keygen

#!! Remember to authorize the deploy key on GitHub

# ssh config for github authentication
echo "Host github" >> ~/.ssh/config
echo -e "\tHostName ssh.github.com" >> ~/.ssh/config
echo -e "\tUser git" >> ~/.ssh/config
echo -e "\tIdentityFile ~/.ssh/id_rsa" >> ~/.ssh/config

# clone repository
cd ~
git clone github:OxfordDemSci/mySocialWatcher

# ---- deploy mySocialWatcher ---- #

# python setup (for running scripts in ./config/collections)
sudo apt install python3-pip
cd ~/mySocialWatcher
pip install -r requirements.txt

# copy private config files via ssh (run this command from local machine, not server)
cd ~/git/OxfordDemSci/mySocialWatcher/config
scp -r ./private/ psw_datahub:~/mySocialWatcher/config/private/
