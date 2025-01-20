# DareFightingICE Python Script Runner

This bash script manages running a Python script with the DareFightingICE game environment.

## Purpose
- Launches DareFightingICE game environment
- Runs a Python script that interacts with the game
- Handles cleanup of processes automatically
- Manages virtual environment detection and validation

## Features
- Automatically detects Python virtual environments (venv, conda, anaconda, pyenv)
- Recursively finds main Python files in directories up to 3 levels deep
- Port management for game server connections
- Headless mode support for running without GUI
- Process isolation and cleanup
- Virtual environment validation
- Flexible command-line options

## Usage

```bash
./run_py_ag.sh <python_script_or_directory> [options]
```

### Command Line Options
```
-h, --help          Display help message
--game_script       Specify custom game script to use
-p, --port          Specify port number for game server
--headless          Run game in headless mode (no GUI)
```

### Examples:
```bash
# Run a specific Python file
./run_py_ag.sh your_script.py

# Run with custom port
./run_py_ag.sh your_script.py -p 31415

# Run in headless mode
./run_py_ag.sh your_script.py --headless

# Run from directory (auto-finds main*.py)
./run_py_ag.sh ./your_project_directory/
```

## Requirements
- DareFightingICE-7.0beta installed in the same directory
- Java runtime for DareFightingICE
- Active Python virtual environment (venv, conda, pyenv, or anaconda)

## Process Flow
1. Validates virtual environment
2. Parses command-line arguments
3. Locates Python script (direct or in directory)
4. Changes to game directory
5. Launches DareFightingICE with specified options
6. Returns to original directory
7. Executes Python script
8. Monitors execution
9. Performs cleanup on completion/error

## Error Handling
- Validates virtual environment setup
- Checks port availability and range (1024-49151)
- Handles multiple main file scenarios
- Validates file extensions and existence
- Manages process conflicts
- Captures and reports exit codes

## Cleanup
Automatically handles:
- Game process termination
- Python process termination
- Port release
- Resource cleanup on exit/interrupt