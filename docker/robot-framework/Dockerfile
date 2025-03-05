FROM python:3.9-slim

RUN apt-get update && apt-get install -y \
    build-essential \
    libusb-1.0-0 \
    && rm -rf /var/lib/apt/lists/*

# Install Robot Framework and dependencies
RUN pip install --no-cache-dir \
    robotframework \
    robotframework-seleniumlibrary \
    robotframework-appiumlibrary \
    pytest \
    requests \
    pyserial \
    python-can

# Set up workspace
WORKDIR /tests

CMD ["robot", "--outputdir", "results", "."]
