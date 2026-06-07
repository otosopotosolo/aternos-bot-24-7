#!/bin/bash
# Install common penetration testing tools

echo "=== Installing Penetration Testing Tools ==="

# Update package list
sudo apt update

# Install basic tools
echo "Installing nmap..."
sudo apt install -y nmap

echo "Installing sqlmap..."
sudo apt install -y sqlmap

echo "Installing nikto..."
sudo apt install -y nikto

echo "Installing dirb..."
sudo apt install -y dirb

echo "Installing masscan..."
sudo apt install -y masscan

echo "Installing gobuster..."
sudo apt install -y gobuster

echo "Installing git..."
sudo apt install -y git

echo "Installing Python3 pip..."
sudo apt install -y python3-pip

# Install Python packages
echo "Installing Python packages..."
pip3 install requests bs4 paramiko colorama termcolor

# Install amass (Amass DNS reconnaissance)
if ! command -v amass &> /dev/null; then
    echo "Installing Amass..."
    go install -v github.com/owasp-amass/amass/v3/...@latest 2>/dev/null || \
    sudo apt install -y amass || echo "Amass installation failed"
fi

# Install subfinder
if ! command -v subfinder &> /dev/null; then
    echo "Installing Subfinder..."
    go install -v github.com/projectdiscovery/subfinder/v2/cmd/subfinder@latest 2>/dev/null || echo "Subfinder installation failed"
fi

# Install nuclei
if ! command -v nuclei &> /dev/null; then
    echo "Installing Nuclei..."
    go install -v github.com/projectdiscovery/nuclei/v2/cmd/nuclei@latest 2>/dev/null || echo "Nuclei installation failed"
fi

echo ""
echo "=== Tools Installation Complete ==="
echo ""
echo "Available tools:"
command -v nmap && echo "  [✓] nmap"
command -v sqlmap && echo "  [✓] sqlmap"
command -v nikto && echo "  [✓] nikto"
command -v gobuster && echo "  [✓] gobuster"
command -v amass && echo "  [✓] amass"
command -v subfinder && echo "  [✓] subfinder"
command -v nuclei && echo "  [✓] nuclei"
