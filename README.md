# Electric Vehicle PVL Tech Stack

This repository contains the comprehensive technology stack for Product Verification Laboratory (PVL) testing for electric vehicles, with a focus on two-wheeled electric scooters.

## Overview

The PVL (Product Verification Laboratory) serves as a critical function in EV development, ensuring all aspects of the vehicle meet quality, safety, and performance standards before mass production.

## Tech Stack Components

### Core Infrastructure

- **Containerization**: Docker, Docker Compose
- **Orchestration**: Kubernetes, Helm
- **Version Control**: Git, GitHub
- **CI/CD**: Jenkins, GitHub Actions
- **Artifact Management**: Artifactory, Docker Registry

### Testing Framework

- **Test Management**: JIRA, TestRail
- **Automation**: Robot Framework, pytest, Selenium
- **Mobile Testing**: Appium, Android Debug Bridge (ADB)
- **USB/IP Testing**: Containerized USB/IP protocol stack
- **Data Collection**: InfluxDB, Kafka, MinIO

### Hardware Integration

- **CAN Bus Analysis**: Vector CANalyzer (containerized)
- **Diagnostic Systems**: Customized diagnostic containers
- **Battery Testing**: BMS diagnostic tools 
- **Motor Controller Testing**: Specialized testing containers

### Data Analysis & Reporting

- **Analytics**: Jupyter notebooks, Python data stack (NumPy, Pandas)
- **Visualization**: Grafana, Power BI
- **Logging**: ELK Stack (Elasticsearch, Logstash, Kibana)
- **Monitoring**: Prometheus, Alertmanager

### Android Integration for Testing

- **Connectivity**: USB/IP protocol for Android phone connection
- **Testing**: Appium, Espresso
- **Analysis**: Perfetto, Android SDK tools (containerized)

## Implementation Architecture

See the [architecture diagram](architecture.md) for a visual representation of how these components interact.

## Deployment Guide

Deployment instructions and configuration examples are available in the [deployment](deployment/) directory.

## Contributing

Contributions to improve the PVL tech stack are welcome. Please see [CONTRIBUTING.md](CONTRIBUTING.md) for details.
