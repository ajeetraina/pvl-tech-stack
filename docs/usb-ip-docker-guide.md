# USB/IP with Docker: A Practical Guide for EV Testing

## Introduction

This guide provides practical implementation details for setting up USB/IP within a Docker environment for electric vehicle testing with Android devices. This approach is particularly valuable for electric scooter manufacturers who need to test Android app connectivity with their vehicles.

## What is USB/IP?

USB/IP is a protocol that enables sharing USB devices over an IP network. It allows a USB device connected to one machine to be used by software running on another machine, or in our case, within Docker containers.

## Why Use USB/IP with Docker for EV Testing?

1. **Test Isolation**: Isolate your testing environment while maintaining access to physical devices
2. **CI/CD Integration**: Enable automated testing with real devices in your continuous integration pipeline
3. **Remote Testing**: Test with devices that are physically located elsewhere
4. **Parallel Testing**: Connect multiple testing containers to the same device or multiple devices
5. **Reproducibility**: Create consistent testing environments regardless of the host system

## Prerequisites

- Linux host system (USB/IP has better support on Linux)
- Docker and Docker Compose installed
- USB Android device for testing
- Root access on the host system

## Step-by-Step Implementation

### 1. Setting Up the Host System

First, install the necessary packages on your host system:

```bash
# For Ubuntu/Debian
sudo apt-get update
sudo apt-get install linux-tools-generic hwdata usbutils

# For CentOS/RHEL
sudo yum install usbutils usbip
```

Load the required kernel modules:

```bash
sudo modprobe usbip_host
sudo modprobe vhci-hcd
```

To make these modules load at boot time:

```bash
echo "usbip_host" | sudo tee -a /etc/modules
echo "vhci-hcd" | sudo tee -a /etc/modules
```

### 2. Starting the USB/IP Server on the Host

Create a script to start the USB/IP server and bind Android devices:

```bash
#!/bin/bash
# File: start-usbip-server.sh

# Start usbipd daemon
sudo usbipd -D

# List all USB devices
echo "Available USB devices:"
sudo usbip list -l

# Bind all Android devices
for bus_id in $(sudo usbip list -l | grep -i "android" | awk '{print $1}')
do
    echo "Binding $bus_id"
    sudo usbip bind -b "$bus_id"
done

echo "USB/IP server is running. Devices are ready to be shared."
echo "Use 'sudo usbip list -r localhost' from another terminal to see available devices."
```

Make the script executable and run it:

```bash
chmod +x start-usbip-server.sh
./start-usbip-server.sh
```

### 3. Creating a Docker Container for USB/IP Client

Create a `Dockerfile` for the container that will connect to the USB device:

```dockerfile
FROM ubuntu:22.04

# Install USB/IP, ADB and other necessary tools
RUN apt-get update && apt-get install -y \
    linux-tools-generic \
    hwdata \
    usbutils \
    android-tools-adb \
    android-sdk-platform-tools \
    && rm -rf /var/lib/apt/lists/*

# Set up working directory
WORKDIR /app

# Copy the USB/IP connection script
COPY connect-usb.sh /app/
RUN chmod +x /app/connect-usb.sh

# Default command
CMD ["/bin/bash"]
```

Next, create the connection script that will run inside the container:

```bash
#!/bin/bash
# File: connect-usb.sh

# Load necessary modules
modprobe vhci-hcd

# Get host IP
HOST_IP=${HOST_IP:-"host.docker.internal"}

# List devices available on the host
echo "Listing available devices on $HOST_IP"
usbip list -r "$HOST_IP"

# Check if device bus ID was provided
if [ -z "$USB_DEVICE_BUSID" ]; then
    echo "No USB_DEVICE_BUSID specified. Please set this environment variable."
    echo "Example: USB_DEVICE_BUSID=1-1"
    exit 1
fi

# Attach the device
echo "Attaching device $USB_DEVICE_BUSID from $HOST_IP"
usbip attach -r "$HOST_IP" -b "$USB_DEVICE_BUSID"

# Wait a moment for device to be recognized
sleep 2

# List connected USB devices
echo "Connected USB devices:"
lsusb

# Start ADB server
adb start-server

# List Android devices
echo "Connected Android devices:"
adb devices

echo "USB device attached successfully. Ready for testing."

# Keep container running
tail -f /dev/null
```

### 4. Docker Compose Setup

Create a `docker-compose.yml` file for your testing environment:

```yaml
version: '3.8'

services:
  # USB/IP client container
  android-testing:
    build:
      context: ./docker/android-testing
    privileged: true  # Required for USB/IP
    environment:
      - HOST_IP=172.17.0.1  # Default Docker bridge network gateway
      - USB_DEVICE_BUSID=1-1  # Replace with your device's bus ID
    volumes:
      - ./tests:/app/tests
    command: ["/app/connect-usb.sh"]
    extra_hosts:
      - "host.docker.internal:host-gateway"

  # Test execution container
  test-runner:
    build:
      context: ./docker/test-runner
    depends_on:
      - android-testing
    volumes:
      - ./tests:/app/tests
      - ./results:/app/results
```

### 5. Running Tests with the Connected Device

Now you can execute tests that interact with the Android device. Here's an example using Python and Appium:

```python
# File: tests/test_android_connection.py
from appium import webdriver
import unittest
import time

class AndroidConnectionTest(unittest.TestCase):
    def setUp(self):
        # Appium desired capabilities
        desired_caps = {
            'platformName': 'Android',
            'deviceName': 'Android Device',  # Uses any available device
            'automationName': 'UiAutomator2',
            'appPackage': 'com.example.evcontrol',  # Your app package
            'appActivity': '.MainActivity',  # Your app's main activity
            'noReset': True
        }
        
        # Connect to Appium server
        self.driver = webdriver.Remote('http://android-testing:4723/wd/hub', desired_caps)
        time.sleep(2)  # Wait for app to launch

    def tearDown(self):
        if self.driver:
            self.driver.quit()

    def test_connect_to_scooter(self):
        # Click connect button
        connect_btn = self.driver.find_element_by_id('com.example.evcontrol:id/connectButton')
        connect_btn.click()
        
        # Wait for connection
        time.sleep(3)
        
        # Verify connection status text
        status_text = self.driver.find_element_by_id('com.example.evcontrol:id/statusText')
        self.assertEqual('Connected to scooter', status_text.text)
        
        # Test some basic functionality
        battery_btn = self.driver.find_element_by_id('com.example.evcontrol:id/batteryStatusButton')
        battery_btn.click()
        
        time.sleep(1)
        
        # Verify battery status is displayed
        battery_level = self.driver.find_element_by_id('com.example.evcontrol:id/batteryLevelText')
        self.assertIn('%', battery_level.text)

if __name__ == '__main__':
    unittest.main()
```

## Integration with CI/CD Pipeline

To integrate this setup with a CI/CD pipeline, you'll need to:

1. Set up a dedicated testing machine with the USB device connected
2. Run the USB/IP server script on this machine
3. Configure your CI/CD pipeline to use this machine as a runner
4. Use Docker containers for test execution

Here's an example GitHub Actions workflow configuration:

```yaml
name: Android Device Testing

on:
  push:
    branches: [ main ]
  pull_request:
    branches: [ main ]

jobs:
  android-tests:
    runs-on: [self-hosted, android-testing]  # Custom runner tags
    steps:
    - uses: actions/checkout@v2
    
    - name: Start USB/IP server
      run: ./scripts/start-usbip-server.sh
      
    - name: Run tests in Docker
      run: |
        docker-compose build
        docker-compose up --abort-on-container-exit
        
    - name: Upload test results
      uses: actions/upload-artifact@v2
      with:
        name: test-results
        path: ./results
```

## Troubleshooting Common Issues

### Device Not Detected

If the Android device isn't detected in the container:

1. Check that the USB device is properly connected to the host
2. Verify that the USB/IP server is running on the host
3. Confirm the device is properly bound with `sudo usbip list -l`
4. Ensure the correct bus ID is provided in the environment variable
5. Check that the container is running in privileged mode

### ADB Connection Issues

If ADB can't connect to the device:

1. Ensure USB debugging is enabled on the Android device
2. Try restarting the ADB server inside the container: `adb kill-server && adb start-server`
3. Verify the device appears in `lsusb` output inside the container
4. Check for USB permission issues with `adb devices -l`

### Network Connectivity

If the container can't connect to the host:

1. Verify the correct host IP is provided
2. Check that the host firewall allows connections to the USB/IP port (3240)
3. Try using the Docker gateway IP instead of host.docker.internal

## Best Practices

1. **Script Everything**: Automate all setup steps to ensure reproducibility
2. **Use Device Serials**: When testing with multiple devices, identify them by serial number
3. **Resource Cleanup**: Ensure devices are properly detached when tests complete
4. **Health Checks**: Add health check scripts to verify device connectivity
5. **Fallback Mechanisms**: Implement reconnection logic in case of temporary disconnections

## Conclusion

Implementing USB/IP with Docker provides a powerful, flexible approach for testing Android applications that interact with electric vehicles. This setup enables automated testing with real hardware while maintaining the benefits of containerization, such as isolation and reproducibility.

By following this guide, electric scooter manufacturers can create a robust testing infrastructure that supports efficient development and quality assurance processes.