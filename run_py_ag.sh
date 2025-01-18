#!/bin/bash

STARTING_DIR=$(pwd)
GAME_SCRIPT="./compile_run_linux.sh"
# Directory for the game environment
GAME_DIR="DareFightingICE_CODE"
STARTING_DIR=$(pwd)
FILE="$1"
PREFIX_FILE="${FILE##*.}"
CLEANUP_DONE=0
JAVA_ARGS=""
PYTHON_ARGS=""
PYTHON_SCRIPT=""

set -e


# Function to handle cleanup and error management
cleanup() {

  if [ $CLEANUP_DONE -eq 1 ]; then
    return
  fi

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

  CLEANUP_DONE=1
}

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


display_help(){
  echo "Usage: $0 <path_to_python_main> or <python_script> [options]"
  echo "Options:"
  echo "  -h, --help  Display this help message"
  echo "--game_script  Specify the game script to use"
  echo "-p, --port Specify the port number for the game server"
  echo "--headless  Run the game in headless mode (no GUI)"
  echo "Example: $0 my_script.py [prolog_based/problog_agent_ole/] -p 4242"
}

# Trap exit signals to ensure cleanup
trap cleanup EXIT INT TERM ERR

check_virtual_environment
# Validate input
if [ $# -eq 0 ]; then
  echo "Error: Python script not specified"
  display_help
  exit 1
fi

source './common.sh'

while [[ $# -gt 0 ]]; do
  case $1 in
    -h|--help)
      display_help
      exit 0
      ;;
    --game_script)
      shift
      GAME_SCRIPT="$1"
      ;;
    -p|--port)
      shift
      PORT="$1"
      JAVA_ARGS="$JAVA_ARGS --port $PORT"
      PYTHON_ARGS="$PYTHON_ARGS --port $PORT"
      ;;
    --headless|--headless-mode)
      JAVA_ARGS="$JAVA_ARGS --headless-mode"
      ;;
    *)
      PYTHON_SCRIPT="$1"
      ;;
  esac
  shift
done


if [[ -d $PYTHON_SCRIPT ]]; then
  MAIN_FILES=$(find $PYTHON_SCRIPT -maxdepth 3 -type f -regex ".*[Mm]ain.*\.py")
  COUNT=$(echo "$MAIN_FILES" | grep -c "^")
  
  if [[ $COUNT -eq 0 ]]; then

    echo "Error: Python script not found in directory"
    display_help
    exit 1
  elif [[ $COUNT -gt 1 ]]; then
    echo "Error: Multiple Python scripts found"
    display_help
    exit 1
  else
    set -- "$MAIN_FILES"
    FILE="$1"
    PREFIX_FILE="${FILE##*.}"

  fi
elif [[ -f $PYTHON_SCRIPT ]]; then
  set -- "$PYTHON_SCRIPT"
  PREFIX_FILE="${PYTHON_SCRIPT##*.}"
else
  echo "Error: Python script not found"
  display_help
  exit 1
fi

if [ "$PREFIX_FILE" != "py" ]; then
  echo "Error: Python script not found"
  display_help
  exit 1
fi



# Change to game directory
cd "$GAME_DIR" || {
  echo "Error: Cannot change to game directory"
  exit 1
}

# Launch game in new terminal
printf "Launching DareFightingICE "
if [[ -n $PORT ]]; then
  if [[ $PORT -lt 1024 || $PORT -gt 49151 ]]; then
    echo "Port number must be between 1024 and 49151"
    exit 1
  fi
  printf "using port: $PORT"
fi
echo "..."

# Verify game script exists
if [ ! -x "$GAME_SCRIPT" ]; then
  echo "Game startup script not found or not executable: $GAME_SCRIPT"
  exit 1
fi

# check if are running
if [[ -n $PORT ]]; then
  if pgrep -f "java.*Main.*--pyftg-mode.*--port $PORT" > /dev/null; then
    echo "Error: Game already running on port $PORT"
    exit 1
  fi
else
  if pgrep -f "java.*Main.*--pyftg-mode" > /dev/null; then
    echo "Error: Game already running"
    exit 1
  fi
fi


"$GAME_SCRIPT" $JAVA_ARGS >/dev/null 2>&1 &
if [ $? -ne 0 ]; then
  echo "Error: Failed to start game"
  exit 1
fi

sleep 3


if [[ -n $PORT ]]; then
  GAME_PID=$(pgrep -f "java.*Main.*--pyftg-mode.*--port $PORT")
  echo "Game PID: $GAME_PID"
else
  GAME_PID=$(pgrep -f "java.*Main.*--pyftg-mode.*")
  echo "Game PID: $GAME_PID"
fi

echo "Game started with PID: $GAME_PID"

# Small delay to ensure game starts
sleep 2

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
python "$1" $PYTHON_ARGS 2>&1  &
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
