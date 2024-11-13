#!/bin/bash
INTERFACE="wlan0"
router_ip=$(ip route | awk '/default/ {print $3}')

ping -c 2 8.8.8.8 > /dev/null 2>&1

if [[ $? -ne 0 ]]; then
    echo "$(date): No network connection. Attempting to reconnect Wi-Fi..."
    sudo ifconfig $INTERFACE down
    sleep 5
    sudo ifconfig $INTERFACE up
    sleep 10
    echo "$(date): Checking for internet connection..."
    ping -c 2 8.8.8.8 > /dev/null 2>&1
    if [[ $? -eq 0 ]]; then
        echo "$(date): Successfully reconnected to Wi-Fi."
    else
        echo "$(date): Reconnection attempt failed."
    fi
else
    echo "$(date): Network connection is active."
fi
