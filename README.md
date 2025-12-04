# ALHS_Backend
Backend software for the **Automated Laboratory Handling System (ALHS)**.  
This backend adopts a **3D printer–derived control architecture** to enable modular and reproducible laboratory automation.  
It integrates **FastAPI**, **Klipper**, **Moonraker**, and **GPT-based parsing** to automate experimental workflows end-to-end.

The **ALHS Backend** provides a unified interface between user-defined experimental methods and modular laboratory hardware.  
Inspired by the **3D printer motion control architecture**, this system applies the same principles of G-code–based actuation and firmware modularity to laboratory devices such as dispensers, mixers, and samplers.

The backend serves as a bridge between:
- **Human-readable experiment instructions** and  
- **Machine-executable commands (G-code)**  

📚 Documentation

[FastAPI Documentation](https://fastapi.tiangolo.com/)

[Klipper Firmware](https://github.com/Klipper3d/klipper)

[Moonraker API](https://github.com/Arksine/moonraker)

[ANTLR Parser Generator](https://github.com/antlr/antlr4)

[MariaDB](https://github.com/mariadb)

⚙️ System Architecture

The backend is composed of several independent services 

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
