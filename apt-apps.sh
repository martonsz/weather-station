#!/bin/bash

sudo apt update 
sudo apt install --no-install-recommends \
    build-essential \
    git \
    python3.11-dev \
    vim
sudo apt install python3-tk

sudo apt install python3-pil
sudo apt install vim
sudo apt install --no-install-recommends xserver-xorg xinit x11-xserver-utils chromium-browser matchbox-window-manager unclutter
history |grep apt