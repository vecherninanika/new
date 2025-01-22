#!/bin/bash

# Отмена в случае ошибки
set -e 

echo "Starting setup..."

# Обновление системы
echo "Updating system..."
sudo apt update
sudo apt upgrade -y

# Установка необходимых инструментов
echo "Installing Python and pip..."
sudo apt install python3 python3-pip python3-venv -y
python3 --version
pip3 --version

echo "Installing Docker and Docker Compose..."
sudo apt install docker.io -y
sudo systemctl enable docker
sudo systemctl start docker
sudo apt install docker-compose -y
sudo usermod -aG docker $USER
newgrp docker

echo "Pulling prometheus..."
docker pull prom/prometheus

echo "Installing git..."
sudo apt install git -y

echo "Installing Poetry..."
curl -sSL https://install.python-poetry.org | python3 -
poetry --version


# Установка VSCode (с автоматическим скачиванием и установкой)
echo "Installing VSCode..."
VSCODE_URL=$(
    curl -s https://code.visualstudio.com/sha/download?build=stable&os=linux-deb-x64 | \
    grep -oE 'https://.*\.deb'
)

if [[ -n "$VSCODE_URL" ]]; then
    echo "Downloading VSCode from: $VSCODE_URL"
    wget "$VSCODE_URL" -O vscode.deb
    sudo dpkg -i vscode.deb
    rm vscode.deb
    echo "VSCode installed successfully."
else
    echo "Failed to get the VSCode download URL. Please install VSCode manually."
fi

echo "Setup finished."

# Коммент: нужно сделать ребут для работы докера
# В случае ошибки с докером:
# systemctl status docker
# sudo usermod -aG docker $USER
# newgrp docker
# финал: docker compose up -d --build

# установка poetry (если скрипт не выполнился: poetry install)
