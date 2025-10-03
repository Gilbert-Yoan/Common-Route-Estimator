#!/bin/bash

# Check if crontab is available
if ! command -v crontab &> /dev/null; then
    echo "crontab is not installed. Installing cronie..."
    
    # Install cronie package (contains crontab)
    sudo yum install -y cronie

    echo "crontab is now installed. Pushing new cron job..."
    #echo new cron into cron file
    echo "00/10 6-8,16-18 * * 1-5 python3 $( dirname -- "$( readlink -f -- "$0"; )"; )\calculateRouteNow.py" > mycron
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
    echo "00/10 6-8,16-18 * * 1-5 python3 $( dirname -- "$( readlink -f -- "$0"; )"; )\calculateRouteNow.py" > mycron
    #install new cron file
    crontab mycron
    rm mycron
    # Enable and start the cron service
    sudo systemctl enable crond
    sudo systemctl restart crond

    echo "crontab installed and cron service started."
fi