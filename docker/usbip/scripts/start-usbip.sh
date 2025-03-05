#!/bin/bash

# Start USB/IP service
modprobe usbip-core
modprobe usbip-host
modprobe vhci-hcd

usbipd -D

# List USB devices
echo "Available USB devices:"
lsusb

# Bind Android devices (assuming they are connected)
for device in $(lsusb | grep -i android | awk '{print $2"/"$4}' | sed 's/://'); do
    echo "Binding device: $device"
    usbip bind -b $device
done

echo "USB/IP server started, devices bound."
echo "Use 'usbip list -r localhost' from a client to see available devices."

# Keep the container running
tail -f /dev/null
