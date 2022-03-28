#!/bin/bash
sudo usermod -aG docker $USER
sudo systemctl start docker.service