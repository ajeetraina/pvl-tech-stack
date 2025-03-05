# Electric Vehicle PVL Tech Stack

This repository contains a comprehensive technology stack for Product Verification Laboratory (PVL) testing for electric vehicles, focusing on two-wheeled electric scooters with Android connectivity via USB/IP.

## 🔋 Overview

The PVL (Product Verification Laboratory) serves as a critical function in EV development, ensuring all aspects of the vehicle meet quality, safety, and performance standards before mass production. This repo provides a containerized, scalable approach to test automation and validation.

## 🚀 Key Features

- **Containerized Testing Environment**: All tools packaged in Docker containers
- **USB/IP for Android Testing**: Connect Android devices to test equipment remotely
- **Automated Test Framework**: Robot Framework and pytest integration
- **Real-time Data Analysis**: InfluxDB, Grafana, and Python data science stack
- **CI/CD Pipeline**: Automated test execution with Jenkins

## 🛠️ Tech Stack Components

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

## 📋 Repository Structure

- [`/docker`](./docker) - Docker configurations for testing tools
- [`/k8s`](./k8s) - Kubernetes deployment files
- [`/tests`](./tests) - Example test suites (Robot Framework, pytest)
- [`/deployment`](./deployment) - Deployment guides
- [`/mermaid-diagrams.md`](./mermaid-diagrams.md) - Architecture diagrams using Mermaid.js

## 🔄 Architecture Diagrams

View our architecture diagrams in the [mermaid-diagrams.md](./mermaid-diagrams.md) file, which includes:

- Complete System Architecture
- Test Data Flow
- CI/CD Pipeline
- USB/IP Android Testing Workflow

## 🏁 Getting Started

### Prerequisites

- Docker and Docker Compose
- Kubernetes cluster (for full deployment)
- Git
- Android device for testing

### Quick Start

1. Clone this repository:
   ```
   git clone https://github.com/ajeetraina/pvl-tech-stack.git
   cd pvl-tech-stack
   ```

2. Start the basic testing environment:
   ```
   docker-compose up -d
   ```

3. Connect an Android device via USB to your host machine

4. Run a sample test:
   ```
   docker-compose exec robot-framework robot /tests/robot-examples/battery_tests.robot
   ```

## 📊 Example Test Results

The test framework will generate:

- HTML test reports
- Performance metrics in Grafana
- Logs in the ELK stack
- Data visualizations for analysis

## 🤝 Contributing

Contributions to improve the PVL tech stack are welcome. Please see [CONTRIBUTING.md](./CONTRIBUTING.md) for details.

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.