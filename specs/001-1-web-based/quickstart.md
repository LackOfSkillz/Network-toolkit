# Quickstart Guide for Network Change Tracking and Auditing Platform

This guide provides a quick overview of how to get started with the application.

## Prerequisites

- Docker and Docker Compose
- A web browser

## Getting Started

1.  **Clone the repository**

    ```bash
    git clone <repository-url>
    cd network-toolkit
    ```

2.  **Start the application**

    ```bash
    docker-compose up -d
    ```

3.  **Access the application**

    Open your web browser and navigate to `http://localhost:3000`.

## Basic Usage

1.  **Login**

    Login with the default admin credentials (admin/admin).

2.  **Upload a configuration**

    Navigate to the "Configurations" page and upload a WatchGuard firewall XML configuration file.

3.  **View the network map**

    Once the configuration is uploaded, a network map will be generated and displayed.

4.  **Run a compliance audit**

    Navigate to the "Compliance" page and run a NERC CIP compliance audit.

5.  **Run a diagnostic test**

    Navigate to the "Diagnostics" page and enter a source IP, destination IP, and port to run a connectivity test.
