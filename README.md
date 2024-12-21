# BrowTopPro - Web-Based System Monitoring Application

## Overview
**BrowTopPro** is a web-based system monitoring application designed to provide real-time server statistics and insights. Built with Python and Docker, the application is easy to deploy and provides a simple, user-friendly interface for monitoring server metrics such as CPU usage, memory, disk space, logged-in users, system logs, and more.

This project was developed as part of the **CS-395 2024 Fall Project** and extends the base functionality of BrowTop.

---

## Features

- **Password-Protected Interface:** Secure access to the web application.
- **Real-Time System Statistics:**
  - CPU Usage
  - Memory Usage
  - Disk Usage
  - System Uptime
- **Process Monitoring:**
  - List of running processes.
  - Dynamic sorting by CPU, memory, or PID.
  - Summary of process counts and states.
- **User Information:**
  - Current logged-in users.
  - Last 10 users who logged in.
- **System Logs:** Displays the last 50 lines of the system logs.
- **Dockerized Deployment:** The application runs as a Docker container for easy setup and portability.

---

## Getting Started

### Prerequisites

- **Docker:** Ensure Docker is installed on your system. [Install Docker](https://docs.docker.com/get-docker/)
- **Docker Compose:** Install Docker Compose if it is not included with your Docker installation. [Install Docker Compose](https://docs.docker.com/compose/install/)
- **Linux User ID:** Run `id -u` to find your Linux user ID, which will be used as the exposed port number.

---

### Installation and Deployment

1. **Clone the Repository**
   ```bash
   git clone https://github.com/your-repository/BrowTopPro.git
   cd BrowTopPro
   ```

2. **Ensure Required Files Exist**
   Make sure the `cert` folder contains the necessary SSL certificate files:
   - `cert/localhost.crt`
   - `cert/localhost.key`

   If these files are missing, create or copy them into the `cert` directory.

3. **Build and Run the Docker Container**
   ```bash
   docker-compose up --build
   ```

4. **Access the Application**
   Open your browser and navigate to:
   ```
   https://cs395.org/<your-linux-user-id>/monitor
   ```

   Replace `<your-linux-user-id>` with the output of `id -u`.

5. **WebSocket Endpoint**
   The WebSocket endpoint is available at:
   ```
   https://cs395.org/<your-linux-user-id>/ws
   ```

---

## Project Structure

```
BrowTopPro/
├── cert/                # SSL certificate files (localhost.crt, localhost.key)
├── src/                 # Source code for the backend service
│   ├── server.py        # Python backend server
├── docker-compose.yml   # Docker Compose configuration file
├── Dockerfile           # Docker build configuration file
├── requirements.txt     # Python dependencies
└── README.md            # Project documentation
```

---

## Usage

1. **Login:**
   - Username: `admin`
   - Password: `password`

2. **Monitoring Metrics:**
   - View real-time CPU, memory, and disk usage.
   - Analyze running processes and sort them dynamically.
   - Check system uptime and logged-in users.
   - Inspect the last 50 lines of system logs.

3. **Customization:**
   - Adjust the sorting preferences for processes using the dropdown menu on the web interface.

---

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

---

## Troubleshooting

### Common Issues:

1. **SSL Certificate Not Found:**
   - Ensure the `localhost.crt` and `localhost.key` files exist in the `cert` directory.
   - Check the volume mapping in the `docker-compose.yml` file.

2. **Port Already in Use:**
   - Stop any process using the same port:
     ```bash
     sudo lsof -i:<port-number>
     ```
   - Kill the process if necessary:
     ```bash
     sudo kill <process-id>
     ```

3. **Docker Build Errors:**
   - Clean up previous builds and try again:
     ```bash
     docker-compose down
     docker-compose up --build
     ```

For additional support, please contact your team lead or the instructor.

---

## Contributors

- Muzaffer Canan - **Frontend Development**
- Alp Küçük- **Backend Development**
- Muzaffer Canan and Alp Küçük- **Deployment & Documentation**

---

## Acknowledgments

This project was inspired by:
- [Glances](https://github.com/nicolargo/glances): A cross-platform system monitoring tool.
- [HTop](https://htop.dev/): An interactive process viewer for Unix systems.

---

Happy Monitoring! 🎉
