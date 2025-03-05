FROM ubuntu:22.04

RUN apt-get update && apt-get install -y \
    usbip \
    usbutils \
    libusb-1.0-0 \
    adb \
    && rm -rf /var/lib/apt/lists/*

# Set up USB/IP for Android device connectivity
COPY scripts/start-usbip.sh /usr/local/bin/
RUN chmod +x /usr/local/bin/start-usbip.sh

ENTRYPOINT ["/usr/local/bin/start-usbip.sh"]
