#!/bin/bash
INTERFACE="wlan0"
router_ip=$(ip route | awk '/default/ {print $3}')

if ping -c 2 8.8.8.8 > /dev/null 2>&1; then
    echo "$(date): Network connection is ACTIVE."
else
    echo "$(date): No network connection. Attempting to reconnect Wi-Fi..."
    sudo ifconfig $INTERFACE down
    sleep 5
    sudo ifconfig $INTERFACE up

    for i in {1..10}; do
        echo "$(date): Checking LAN connection. Pinging router, attempt $i"
        if ping -c 1 $router_ip > /dev/null 2>&1; then
            break
        fi
        sleep 1
    done
    echo "$(date): Checking internet connection. Pinging Google..."
    if ping -c 2 8.8.8.8 > /dev/null 2>&1; then
        echo "$(date): Successfully reconnected to Wi-Fi."
    else
        echo "$(date): Reconnection attempt FAILED."
    fi
fi
