#!/bin/bash
sudo useradd -m dev 2>/dev/null
sudo usermod -aG wheel dev
echo 'dev ALL=(ALL) NOPASSWD:ALL' | sudo tee /etc/sudoers.d/dev >/dev/null
sudo cp -n /etc/yum.repos.d/CentOS-Base.repo /etc/yum.repos.d/CentOS-Base.repo.bak
sudo yum --disablerepo=* --enablerepo=local-cdrom makecache 2>&1 | tail -1
