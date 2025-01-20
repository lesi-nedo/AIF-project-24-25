# Logical DareFightingICE AI Agents 🚀

This  part of repository contains multiple AI agents for the DareFightingICE game, including a ProbLog-based agent that uses probabilistic logic programming for decision making.

## Available Agents 🤖

### ProblogAgent
A sophisticated fighting game AI that uses probabilistic logic programming for decision making. Key features include:

- Probabilistic state estimation
- Utility-based action selection
- Real-time opponent modeling
- Adaptive combat strategies
- Performance statistics tracking
- Visual debugging capabilities

The agent uses ProbLog to reason about:
- Opponent state and behavior
- Action effectiveness
- Combat distances
- Energy management
- Health states
- Combat positioning

### PrologAI
A fighting game AI that uses logical programming for decision making. Key features include:
- State-based decision making
- Rule-based action selection
- Real-time opponent modeling
- Predefined combat strategies

The agent uses Prolog to reason about:
- Opponent state and position
- Action selection
- Combat distances
- Health and energy management

## Prerequisites 📋

Before you begin, ensure you have:

- Python 3.9 or later
- ProbLog 2.1 or later
- DareFightingICE 7.0 beta
- SWI-Prolog 8.4.2 or later (for classic Prolog agent)
- 64-bit Intel or ARM processor


## Installation Steps 🛠️

### 1. Setting Up Python Environment 🐍

1. **Create and activate a virtual environment:**
    ```sh
    python -m venv venv
    source venv/bin/activate  # On Linux/macOS
    venv\Scripts\activate     # On Windows
    ```

### 2. Installing Required Packages 📦

1. **Install PySwip:**
    ```sh
    pip install -U pyswip
    ```

### 3. Installing SWI-Prolog 🖥️

Install SWI-Prolog for your operating system:

- **Linux (Ubuntu/Debian):**
    ```sh
    sudo apt install swi-prolog
    ```

- **macOS:**
    ```sh
    brew install swi-prolog
    ```

- **Windows:**
    Download from [SWI-Prolog's website](https://www.swi-prolog.org/Download.html)

    #### Test Drive 🚗

    Run a quick test to ensure everything is set up correctly:

    ```python
    from pyswip import Prolog
    Prolog.assertz("father(michael,john)")
    print(list(Prolog.query("father(X,Y)")))

## Running the Agents 🏃‍♂️

1. **Start DareFightingICE server:**
    ```sh
    ./DareFightingICE-7.0beta/run-{OS}-{arch}.sh[bat]
    ```

2. **Run the Prolog agent:**
    ```sh
    python prolog_based.prolog_agent_simo.MainProlog.py
    ```

3. **Run the ProbLog agent:**
    ```sh
    python prolog_based.problog_agent_ole.MainGameAgentVsMyAgent.py
    ```

Enjoy your AI battles in DareFightingICE! 🎮




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

3. 

Enjoy your AI battles in DareFightingICE! 🎮 ```