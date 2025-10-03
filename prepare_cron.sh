#!/bin/bash

# Check if crontab is available
if ! command -v crontab &> /dev/null; then
    echo "crontab is not installed. Installing cronie..."
    
    # Install cronie package (contains crontab)
    sudo yum install -y cronie

    echo "crontab is now installed. Pushing new cron job..."
    #echo new cron into cron file
    echo "00,10,20,30,40,50 6-8,16-18 * * 1-5 python3 $( dirname -- "$( readlink -f -- "$0"; )"; )/calculateRouteNow.py" > mycron
    #install new cron file
    crontab mycron
    rm mycron

    # Enable and start the cron service
    sudo systemctl enable crond
    sudo systemctl start crond

    echo "crontab installed and cron service started."
else
    echo "crontab is already installed. Only pushing new cron job"
    #echo new cron into cron file
    echo "00,10,20,30,40,50 6-8,16-18 * * 1-5 python3 $( dirname -- "$( readlink -f -- "$0"; )"; )/calculateRouteNow.py" > mycron
    #install new cron file
    crontab mycron
    rm mycron
    # Enable and start the cron service
    sudo systemctl enable crond
    sudo systemctl restart crond

    echo "crontab installed and cron service started."
fi

echo "--Now preparing python env..."

# Check for Python 3
if command -v python3 &> /dev/null; then
    echo "Python 3 is already installed: $(python3 --version)"
else
    echo "Python 3 is not installed."
    sudo yum install -y python3
fi

# Check for pip3
if command -v pip3 &> /dev/null; then
    echo "pip3 is already installed: $(pip3 --version)"
else
    echo "pip3 is not installed. Attempting to install..."
    sudo yum install -y python3-pip
fi

echo "Installing requirements"
pip install -r $( dirname -- "$( readlink -f -- "$0"; )"; )/requirements.txt