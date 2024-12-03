# DareFightingICE Python Script Runner

This bash script manages running a Python script with the DareFightingICE game environment. Here's a detailed explanation:

## Purpose
- Launches DareFightingICE game environment
- Runs a Python script that interacts with the game
- Handles cleanup of processes automatically
- Manages virtual environment detection

## Features
- Automatically detects Python virtual environments (venv, conda, anaconda, pyenv)
- Finds main Python files in directories up to 3 levels deep
- Captures Python script output to `python_script_log.txt`
- Handles process cleanup on exit/errors
- Manages game and Python process lifecycles

## Usage

```bash
./run_py_ag.sh <python_script_or_directory>
```

### Examples:
```bash
# Run a specific Python file
./run_py_ag.sh your_script.py

# Run from a directory (will look for main*.py or Main*.py)
./run_py_ag.sh ./your_project_directory/
```

## Requirements
- 

DareFightingICE-7.0beta

 installed in the same directory
- Java runtime for DareFightingICE
- Python environment (virtual environment recommended)

## Process Flow
1. Validates input and environment
2. Changes to game directory
3. Launches DareFightingICE game
4. Returns to original directory
5. Executes Python script
6. Monitors execution
7. Cleans up processes on completion/error

## Error Handling
- Validates file extensions
- Checks for missing files
- Handles multiple main files
- Manages process termination
- Captures exit codes

## Cleanup
Automatically handles:
- Game process termination
- Python process termination
- Resource cleanup on exit/interrupt