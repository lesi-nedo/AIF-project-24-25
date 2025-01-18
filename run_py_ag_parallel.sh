#!/bin/bash

# Default base port
declare -g BASE_PORT=31415
declare -g PORTS_USED=()
declare -g NUM_EXECUTIONS=0
declare -g CONDA_ENV=""
declare -g PARALLEL_EXECUTIONS=1
declare -g CONDA_FOLDER="$HOME/miniconda3"
declare -g MAIN_FILE=""
declare -g LOGS_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)/logs"
declare -g LOGS_GAME="$LOGS_DIR/game"
declare -g LOGS_EXEC="$LOGS_DIR/agents"
declare -g GAME_SCRIPT="./compile_run_linux.sh"
declare -g GAME_DIR="DareFightingICE_CODE"
declare -g PYTHON=$(command -v python3) || $(command -v python)
declare -g CALLED_CLEANUP=0


set -e
set -o pipefail
set -u

source './common.sh'
mkdir -p "$LOGS_DIR"
mkdir -p "$LOGS_GAME"
mkdir -p "$LOGS_EXEC"
# Function to get next available port
get_available_port() {
    local port=$1
    while ! check_port $port; do
        port=$((port + 1))
    done
    PORTS_USED+=($port)
    echo $port
}

get_random_safe_port() {
    # Avoid well-known ports (0-1023)
    # Avoid common service ports (3306, 5432, 6379, 8080, etc)
    local min_port=10000
    local max_port=60000
    local excluded_ports=(3306 5432 6379 8080 27017 6379 11211)
    
    while true; do
        local random_port=$(( RANDOM % (max_port - min_port + 1) + min_port ))
        local safe=true
        
        # Check if port is in excluded list
        for excluded in "${excluded_ports[@]}"; do
            if [ "$random_port" -eq "$excluded" ]; then
                safe=false
                break
            fi
        done
        
        if [ "$safe" = true ]; then
            echo "$random_port"
            break
        fi
    done
}

display_help(){
  echo "-h, --help: Display help"
  echo "--main-file: Main directory where the Python scripts are located"
  echo "-e, --env: Conda environment name"
  echo "--in-parallel: Number of parallel executions"
  echo "--total: Total number of executions"
  echo "Example: $0 -e my_env --in-parallel 5 --total 10"
  echo "This will launch 5 parallel instances of run_py_ag.sh with the specified conda environment name for a total of 10 executions."
}

check_conda_folders(){
  local all_conda_folders=("$HOME/miniconda3" "$HOME/anaconda3" "$HOME/miniforge3")

  for folder in "${all_conda_folders[@]}"; do
      if [ -d "$folder" ]; then
          CONDA_FOLDER="$folder"
          return 0
      fi
  done
  return 1
}


clean(){

  if [ $CALLED_CLEANUP -eq 1 ]; then
    return
  fi
  sleep $(echo "scale=3; 1 + $RANDOM/12767" | bc)
  for pid in "${PORTS_USED[@]}"; do
    pgrep -f ".*Main.*--pyftg-mode.*--port $pid" | xargs kill -9
  done
  for pid in "${MAIN_PIDS[@]}"; do
    kill -9 "$pid"
  done
  echo "Killed all processes"
  CALLED_CLEANUP=1
}

set +u
while [[ $# -ge 0 ]]; do
  case $1 in
    -h|--help)
      display_help
      exit 0
      ;;
    -e|--env)
      shift
      CONDA_ENV=$1
      ;;
    --in-parallel)
      shift
      PARALLEL_EXECUTIONS=$1
      ;;
    --total)
      shift
      NUM_EXECUTIONS=$1
      ;;
    --main-file)
      shift
      MAIN_FILE=$1
      ;;
    *)
      break
      ;;
  esac
  shift
done
set -u

if [[ ! -f $MAIN_FILE ]]; then
    echo "Error: Main file $MAIN_FILE not found"
    exit 1
fi

# Validate input
if [[ -z $CONDA_ENV ]]; then
    echo "Error: Conda environment name not specified"
    exit 1
fi
check_conda_folders
if [[ $? -ne 0 ]]; then
    echo "Error: Conda not found in default locations"
    exit 1
fi
source "$CONDA_FOLDER/etc/profile.d/conda.sh"

echo "Activating conda environment $CONDA_ENV..."
conda activate "$CONDA_ENV"
if [[ $? -ne 0 ]]; then
    echo "Error: Conda environment $CONDA_ENV not found"
    exit 1
fi
PYTHON=$(command -v python3) || $(command -v python)

# Validate number of parallel executions
if [[ ! $PARALLEL_EXECUTIONS =~ ^[0-9]+$ ]]; then
    echo "Error: Number of parallel executions must be a positive integer"
    exit 1
fi


if [[ ! $NUM_EXECUTIONS =~ ^[0-9]+$ ]]; then
    echo "Error: Number of executions must be a positive integer"
    exit 1
fi

echo "Will launch $PARALLEL_EXECUTIONS parallel instances for a total of $NUM_EXECUTIONS executions."



CURR_DIR=$(pwd)
# Change to game directory
cd "$GAME_DIR" || {
  echo "Error: Cannot change to game directory"
  exit 1
}


# Verify game script exists
if [ ! -x "$GAME_SCRIPT" ]; then
  echo "Game startup script not found or not executable: $GAME_SCRIPT"
  exit 1
fi
# Track running processes
declare -a PIDS=()
MAIN_PART=$(basename "$MAIN_FILE" .py)
echo "Python file to run: $MAIN_PART.py"

declare -g NUMBER_OF_GAMES_LUNCHED=0
declare -a PORTS_USED=()
declare -a GAME_PIDS=()
declare -g BASE_PORT=$(get_random_safe_port)
trap clean EXIT INT TERM ERR HUP QUIT 

for indx in $(seq 1 "$PARALLEL_EXECUTIONS"); do
  PORT=$(get_available_port "$BASE_PORT")
  echo "Launching DareFightingICE using port: $PORT..."
  $GAME_SCRIPT --port $PORT --headless-mode >$LOGS_GAME/$MAIN_PART-game-$indx. 2>&1 &
  if [ $? -ne 0 ]; then
    echo "Error: Failed to start game"
    exit 1
  fi
  GAME_PIDS+=($!)
  sleep $(echo "scale=3; 3 + $RANDOM/12767" | bc)
  NUMBER_OF_GAMES_LUNCHED=$((NUMBER_OF_GAMES_LUNCHED + 1))
  PORTS_USED+=($PORT)
done

cd "$CURR_DIR" || {
  echo "Error: Cannot change to current directory"
  exit 1
}

echo "Lunched $NUMBER_OF_GAMES_LUNCHED games"
echo "Using Python: $PYTHON"

for num_exec in $(seq 1 "$NUM_EXECUTIONS"); do
    
    echo "Starting execution $num_exec python script..."
    # Initialize arrays for each batch
    declare -a MAIN_PIDS=()
  
    # Launch parallel instances
    for i in $(seq 1 "$PARALLEL_EXECUTIONS"); do
        
        PORT=${PORTS_USED[$((i - 1))]}

        echo "Launching $MAIN_PART.py using port: $PORT..."
        "$PYTHON" "$MAIN_FILE" --port $PORT >$LOGS_EXEC/$MAIN_PART-exec-$i. 2>&1 &
        if [ $? -ne 0 ]; then
            echo "Error: Failed to start python script"
            exit 1
        fi
        MAIN_PIDS+=($!)
        
        sleep $(echo "scale=3; 1 + $RANDOM/12767" | bc)
    done

    
    # Wait for all processes and handle errors
    failed=0
    for pid in "${MAIN_PIDS[@]}"; do
        wait "$pid"
        status=$?
        if [ $status -ne 0 ]; then
            echo "Process $pid failed with status $status"
            failed=1
        fi
    done
    echo "All parallel processes finished for execution ${num_exec}"
done


echo "Successfully completed $NUM_EXECUTIONS executions"
