# ALHS_Backend
Backend software for the **Automated Laboratory Handling System (ALHS)**.  
This project implements a **microservice-based backend architecture** designed for laboratory automation — integrating method parsing, G-code generation, and real-time hardware control through Klipper and Moonraker APIs.

The ALHS Backend provides a unified control layer between user-defined experiment methods and modular laboratory hardware.  
It bridges **NLP-based command parsing**, **G-code compilation**, and **hardware actuation**, enabling reproducible and traceable automated workflows.

📚 Documentation

[FastAPI Documentation](https://fastapi.tiangolo.com/)

[Klipper Firmware](https://github.com/Klipper3d/klipper)

[Moonraker API](https://github.com/Arksine/moonraker)

[ANTLR Parser Generator](https://github.com/antlr/antlr4)

[MariaDB](https://github.com/mariadb)

⚙️ System Architecture

The backend is composed of several independent services :

| Service | Description |
|----------|--------------|
| **FastAPI Gateway** | Main API layer for parsing, user access, and control requests |
| **Parsing Engine** | Converts `.txt` experimental method files into structured representations |
| **G-code Compiler** | Generates and optimizes G-code sequences for execution |
| **Hardware Controller** | Interfaces with Klipper/Moonraker for device control |
| **Database Layer** | Manages experiment logs, telemetry, and user data |

🔧 Key Features

- **FastAPI-based RESTful backend** for laboratory automation
- **NLP + ANTLR parsing engine** to interpret text-based method files
- **Automatic G-code generation** for robotic sample handling
- **Klipper & Moonraker API integration** for real-time control
- **Microservice architecture** with modular scalability
- **Database integration (MariaDB)** for data logging and traceability
