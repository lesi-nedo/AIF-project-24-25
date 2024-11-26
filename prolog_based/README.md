# DareFightingICE Prolog-Based Agents 🚀

Welcome to the DareFightingICE Prolog-Based Agents project! This guide will help you set up and run the Prolog-based agents for the DareFightingICE game.

## Prerequisites 📋

Before you begin, ensure you have the following installed:

- Python 3.9 or later
- SWI-Prolog 8.4.2 or later
- 64-bit Intel or ARM processor

> **Important:** Make sure the SWI-Prolog architecture matches the Python architecture. If you are using a 64-bit build of Python, use a 64-bit build of SWI-Prolog, etc.

## Installation Steps 🛠️

### 1. Setting Up Python Environment 🐍

1. **Create a virtual environment:**
    ```sh
    python -m venv venv
    ```
2. **Activate the virtual environment:**
    - On Windows:
        ```sh
        venv\Scripts\activate
        ```
    - On macOS/Linux:
        ```sh
        source venv/bin/activate
        ```

### 2. Installing PySwip 📦

1. **Install PySwip from PyPI:**
    ```sh
    pip install -U pyswip
    ```

2. **Set environment variables for SWI-Prolog:**
    ```sh
    export SWI_HOME_DIR=/path/to/swipl/home
    export LIBSWIPL_PATH=/path/to/libswipl
    ```

    You can find these paths using:
    ```sh
    swipl --dump-runtime-variables
    ```

### 3. Installing SWI-Prolog 🖥️

#### On Linux:
- **Arch Linux / Manjaro Linux / Parabola GNU/Linux-libre:**
    ```sh
    sudo pacman -S swi-prolog
    ```
- **Fedora Workstation:**
    ```sh
    sudo dnf install pl
    ```
- **Debian, Ubuntu, Raspbian:**
    ```sh
    sudo apt install swi-prolog-nox
    ```

#### On Windows:
- **Download and install SWI-Prolog from [SWI-Prolog's website](https://www.swi-prolog.org/Download.html).**

#### On macOS:
- **Using Homebrew:**
    ```sh
    brew install swi-prolog
    ```
- **Official SWI-Prolog App:**
    - Download and install from [SWI-Prolog's website](https://www.swi-prolog.org/Download.html).
    - If you encounter `libgmp.X not found` error, set the environment variable:
        ```sh
        export DYLD_FALLBACK_LIBRARY_PATH=/Applications/SWI-Prolog.app/Contents/Frameworks
        ```

## Running the Agents 🏃‍♂️
1. **Start the DareFightingICE server:**
    By running the appropriate script in the `DareFightingICE-7.0beta` directory.
    E.g. `DareFightingICE-7.0beta\run-linux-amd64.sh` on Linux.

    !IMPORTANT! The server must be running before starting the agents.
    !IMPORTANT! The command inside the script must be run with `--pyftg-mode` flag.

2. **Navigate to the project directory:**
    ```sh
    cd prolog_based/prolog_agent_ole
    ```

3. **Run the Prolog-based agent:**
    ```sh
    python MainPAIvsHuman.py
    ```

## Test Drive 🚗

Run a quick test to ensure everything is set up correctly:

```python
from pyswip import Prolog
Prolog.assertz("father(michael,john)")
print(list(Prolog.query("father(X,Y)")))
Enjoy your AI battles in DareFightingICE! 🎮 ```