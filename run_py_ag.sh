#!/bin/bash

STARTING_DIR=$(pwd)
GAME_SCRIPT="./run-linux-amd64.sh"

set -e
# Function to check if in a virtual environment
check_virtual_environment() {
  # Check for Python venv
  if [ -n "$VIRTUAL_ENV" ]; then
    echo "In a Python virtual environment (venv)"
    return 0
  fi

  # Check for Conda environment
  if [ -n "$CONDA_PREFIX" ]; then
    echo "In a Conda environment"
    return 0
  fi

  # Check for Anaconda environment
  if [ -n "$ANACONDA_HOME" ]; then
    echo "In an Anaconda environment"
    return 0
  fi

  # Check for Pyenv
  if [ -n "$PYENV_VIRTUAL_ENV" ]; then
    echo "In a Pyenv virtual environment"
    return 0
  fi

  # Alternative method for some virtual environments
  if python -c "import sys; print(sys.prefix)" | grep -q "/env\|/venv\|/conda\|/.venv"; then
    echo "In a virtual environment (detected by Python prefix)"
    return 0
  fi

  echo "Not in a virtual environment"
  return 1
}

# Game Environment Automation Script
# Handles launching game and Python script with robust error management

# Exit on any error
set -e

# Directory for the game environment
GAME_DIR="DareFightingICE-7.0beta"
STARTING_DIR=$(pwd)
FILE="$1"
PREFIX_FILE="${FILE##*.}"

check_virtual_environment

if [ -d "$1" ]; then
  echo "Error: Python script not found"
  echo "Usage: $0 <python_script>"
  exit 1
fi

if [ "$PREFIX_FILE" != "py" ]; then
  echo "Error: Python script not found"
  echo "Usage: $0 <python_script>"
  exit 1
fi

# Function to handle cleanup and error management
cleanup() {
  echo "Cleaning up resources..."

  # Terminate game process if it exists
  if [ ! -z "$GAME_PID" ]; then
    echo "Terminating game process (PID: $GAME_PID)..."
    kill -TERM "$GAME_PID" 2>/dev/null || true
    wait "$GAME_PID" 2>/dev/null || true
  fi

  # Terminate Python process if it exists
  if [ ! -z "$PYTHON_PID" ]; then
    echo "Terminating Python process (PID: $PYTHON_PID)..."
    kill -TERM "$PYTHON_PID" 2>/dev/null || true
    wait "$PYTHON_PID" 2>/dev/null || true
  fi
}

# Trap exit signals to ensure cleanup
trap cleanup EXIT INT TERM ERR

# Validate input
if [ $# -eq 0 ]; then
  echo "Error: Python script not specified"
  echo "Usage: $0 <python_script>"
  exit 1
fi

# Change to game directory
cd "$GAME_DIR" || {
  echo "Error: Cannot change to game directory"
  exit 1
}

# Launch game in new terminal
echo "Launching DareFightingICE..."
# Verify game script exists
if [ ! -x "$GAME_SCRIPT" ]; then
  handle_error "Game startup script not found or not executable: $GAME_SCRIPT"
fi

# Start game in background
$GAME_SCRIPT >/dev/null 2>&1 &

sleep 2

GAME_PID=$(pgrep -f "java.*FightingICE.jar.*Main")
echo "Game PID: $GAME_PID"

# Small delay to ensure game starts
sleep 1

# Validate game process started
if ! kill -0 "$GAME_PID" 2>/dev/null; then
  echo "Error: Game failed to start"
  exit 1
fi

cd "$STARTING_DIR" || {
  echo "Error: Cannot change to starting directory"
  exit 1
}

# Run Python script and capture logs
echo "Running Python script: $1"
python "$1" 2>&1 | tee python_script_log.txt &
PYTHON_PID=$!

# Wait for Python script to complete
wait "$PYTHON_PID"
PYTHON_EXIT_CODE=$?

# Log Python script exit status
if [ $PYTHON_EXIT_CODE -eq 0 ]; then
  echo "Python script completed successfully"
else
  echo "Python script exited with error code: $PYTHON_EXIT_CODE"
fi

set +e

# Script will automatically clean up via trap
exit $PYTHON_EXIT_CODE
