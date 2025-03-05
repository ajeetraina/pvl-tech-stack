FROM appium/appium:latest

# Install Android tools
RUN apt-get update && apt-get install -y \
    android-tools-adb \
    usbutils \
    usbip \
    && rm -rf /var/lib/apt/lists/*

# Install USB/IP client tools
RUN npm install -g appium-usbmuxd

# Set up workspace
WORKDIR /mobile-tests

# Start Appium server with USB support
CMD ["appium", "--allow-insecure=chromedriver_autodownload"]
