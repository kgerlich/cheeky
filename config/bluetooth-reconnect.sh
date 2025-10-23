#!/bin/bash
# Bluetooth Auto-Reconnect Script for Cheeky
# Automatically reconnects previously paired Bluetooth speakers on boot

set -e

# Logging
LOG_FILE="/var/log/cheeky-bluetooth-reconnect.log"
echo "[$(date '+%Y-%m-%d %H:%M:%S')] Bluetooth auto-reconnect starting..." >> "$LOG_FILE"

# Wait for Bluetooth service to be ready
sleep 5

# Function to reconnect device
reconnect_device() {
    local mac="$1"
    local device_name="$2"

    echo "[$(date '+%Y-%m-%d %H:%M:%S')] Attempting to connect to $device_name ($mac)" >> "$LOG_FILE"

    bluetoothctl << EOF
connect $mac
quit
EOF

    if [ $? -eq 0 ]; then
        echo "[$(date '+%Y-%m-%d %H:%M:%S')] Successfully connected to $device_name" >> "$LOG_FILE"
    else
        echo "[$(date '+%Y-%m-%d %H:%M:%S')] Failed to connect to $device_name" >> "$LOG_FILE"
    fi
}

# Get list of trusted devices
DEVICES=$(bluetoothctl devices Paired | awk '{print $2, $3, $4, $5}')

if [ -z "$DEVICES" ]; then
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] No paired devices found" >> "$LOG_FILE"
    exit 0
fi

# Try to reconnect each device
while IFS= read -r line; do
    if [ -z "$line" ]; then
        continue
    fi

    # Extract MAC address (first field)
    MAC=$(echo "$line" | awk '{print $1}')
    # Get device name (rest of line)
    NAME=$(echo "$line" | cut -d' ' -f2-)

    reconnect_device "$MAC" "$NAME"
done <<< "$DEVICES"

echo "[$(date '+%Y-%m-%d %H:%M:%S')] Bluetooth auto-reconnect completed" >> "$LOG_FILE"
