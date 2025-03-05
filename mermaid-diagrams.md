# PVL Tech Stack Mermaid Diagrams

This file contains various Mermaid.js diagrams visualizing the PVL testing infrastructure and workflows.

## Complete System Architecture

```mermaid
graph TD
    subgraph "Infrastructure Layer"
        A[Docker Containers] --> B[Kubernetes Orchestration]
        C[Git/GitHub] --> D[CI/CD Pipeline]
        D --> E[Automated Testing]
    end

    subgraph "Hardware Interface Layer"
        F[Electric Scooter] --- G[CAN Bus]
        F --- H[Battery Systems]
        F --- I[Motor Controllers]
        F --- J[Charging Systems]
        K[Android Devices] --- L[USB/IP Connection]
    end

    subgraph "Testing Layer"
        M[Test Management - JIRA/TestRail]
        N[Robot Framework] --> O[Automated Test Execution]
        P[pytest] --> O
        Q[Appium] --> R[Mobile Test Execution]
        L --> R
    end

    subgraph "Data Layer"
        G --> S[Data Collection Services]
        H --> S
        I --> S
        J --> S
        R --> S
        S --> T[InfluxDB]
        S --> U[Kafka Streams]
        S --> V[MinIO Object Storage]
    end

    subgraph "Analysis Layer"
        T --> W[Data Analysis]
        U --> W
        V --> W
        W --> X[Jupyter Notebooks]
        W --> Y[Python Analysis]
        Y --> Z[Machine Learning Models]
    end

    subgraph "Visualization Layer"
        W --> AA[Grafana Dashboards]
        W --> AB[Power BI Reports]
        AA --> AC[Real-time Monitoring]
        AB --> AD[Executive Dashboards]
    end

    subgraph "Operations Layer"
        AE[Prometheus] --> AF[Alerting]
        AG[ELK Stack] --> AH[Log Analysis]
        AE --> AI[System Health]
        AG --> AI
    end

    E --> O
    E --> R
    O --> S
    M --> O
    M --> R
```

## Test Data Flow

```mermaid
flowchart LR
    A[Test Execution] --> B{Data Collection}
    B --> C[Vehicle Telemetry]
    B --> D[Android Metrics]
    B --> E[System Logs]
    
    C --> F[InfluxDB]
    D --> F
    E --> G[Elasticsearch]
    
    F --> H[Data Processing]
    G --> H
    
    H --> I[Visualization]
    H --> J[Anomaly Detection]
    H --> K[Test Reporting]
    
    I --> L[Grafana Dashboards]
    J --> M[Alert System]
    K --> N[TestRail Reports]
```

## CI/CD Pipeline for Test Automation

```mermaid
flowchart TD
    A[Code Changes] --> B[Git Repository]
    B --> C[Jenkins Pipeline]
    
    C --> D[Build Test Containers]
    D --> E[Unit Tests]
    E --> F{Tests Pass?}
    
    F -->|Yes| G[Deploy to Test Environment]
    F -->|No| H[Notify Developers]
    H --> A
    
    G --> I[Integration Tests]
    I --> J{Tests Pass?}
    
    J -->|Yes| K[Deploy to Staging]
    J -->|No| H
    
    K --> L[System Tests]
    L --> M{Tests Pass?}
    
    M -->|Yes| N[Ready for Production]
    M -->|No| H
```

## USB/IP Android Testing Workflow

```mermaid
sequenceDiagram
    participant ET as EV Tester
    participant CI as CI/CD System
    participant DC as Docker Container
    participant AD as Android Device
    participant ES as Electric Scooter
    
    ET->>CI: Initiate Test Run
    CI->>DC: Start Test Container
    DC->>AD: Connect via USB/IP
    DC->>ES: Connect to Vehicle CAN
    
    DC->>AD: Install Test App
    DC->>AD: Launch Test App
    AD->>ES: Send Control Commands
    ES->>DC: Return Telemetry Data
    
    loop Test Execution
        DC->>AD: Execute Test Step
        AD->>ES: Send Command
        ES->>DC: Return Status
        DC->>CI: Log Test Result
    end
    
    DC->>CI: Complete Test Results
    CI->>ET: Report Test Outcome
```
