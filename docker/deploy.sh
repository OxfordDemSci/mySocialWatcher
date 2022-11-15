#!/bin/bash
sudo apt-get update -y
sudo apt-get upgrade -y

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


#---- github ----#
sudo apt install git

# create GitHub deploy key
cd ~/.ssh
ssh-keygen

#!! Remember to authorize the key on GitHub

# ssh config for github
echo "Host github" >> ~/.ssh/config
echo -e "\tHostName ssh.github.com" >> ~/.ssh/config
echo -e "\tUser git" >> ~/.ssh/config
echo -e "\tIdentityFile ~/.ssh/id_rsa" >> ~/.ssh/config

# clone repository
cd ~
git clone github:OxfordDemSci/mySocialWatcher

# copy private config files via ssh (run this command from local machine, not server)
cd ~/git/OxfordDemSci/mySocialWatcher/config
scp -r ./private/ psw_datahub:~/mySocialWatcher/config/private/

# python setup (for running scripts in ./config/collections)
sudo apt install python3-pip
cd ~/mySocialWatcher
pip install -r requirements.txt

# setup collections
cd ~/mySocialWatcher
python3 config/collections/dgg_national.py
python3 config/collections/rus_exodus_facebook.py
python3 config/collections/rus_exodus_instagram.py
python3 config/collections/ukraine_countries.py
python3 config/collections/ukraine_europe.py
python3 config/collections/ukraine_language.py
python3 config/collections/ukraine_neighbours1.py
python3 config/collections/ukraine_neighbours2.py
python3 config/collections/ukraine_regions.py
python3 config/collections/venezuelan_exodus1.py
python3 config/collections/venezuelan_exodus2.py

# deploy datahub (for example)
cd ~/mySocialWatcher/docker/datahub
docker-compose up -d --build
