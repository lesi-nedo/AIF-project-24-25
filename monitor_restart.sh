#!/bin/bash


declare -g SCRIPT_NAME='run_py_ag.sh'
declare -g SCRIPT_PATH="$PWD/$SCRIPT_NAME"
declare -g CLEANUP_DONE=0
declare -g last_restart=0
declare -g  active_pid=""
declare -g DEBOUNCE_SECONDS=2
declare -g GAME_PID
declare -g PYTHON_PID
declare -g INOTIFY_PID
declare -g MONITOR_DIR
declare -g PYTHON_FILE
declare -g PYTHON_VENV


# Add at the beginning of the script, after the declarations

# Log levels
declare -r LOG_DEBUG=0
declare -r LOG_INFO=1
declare -r LOG_WARN=2
declare -r LOG_ERROR=3

# Log colors
declare -r COLOR_DEBUG='\033[0;36m'    # Cyan
declare -r COLOR_INFO='\033[0;32m'     # Green
declare -r COLOR_WARN='\033[0;33m'     # Yellow
declare -r COLOR_ERROR='\033[0;31m'    # Red
declare -r COLOR_RESET='\033[0m'       # Reset

log() {
    local level=$1
    local message=$2
    local timestamp=$(date '+%Y-%m-%d %H:%M:%S')
    local color=""
    local level_str=""
    
    case $level in
        "DEBUG")
            color=$COLOR_DEBUG
            level_str="DEBUG"
            ;;
        "INFO")
            color=$COLOR_INFO
            level_str="INFO"
            ;;
        "WARN")
            color=$COLOR_WARN
            level_str="WARN"
            ;;
        "ERROR")
            color=$COLOR_ERROR
            level_str="ERROR"
            ;;
    esac
    
    # Print to console with color
    echo -e "${color}[$timestamp] [$level_str] $message${COLOR_RESET}"

}


# set -e
# set -o pipefail
# set -u
# Check if inotify-tools is installed
if ! command -v inotifywait &> /dev/null; then
    log "ERROR" "Error: inotify-tools is not installed. Please install it first."
    log "INFO" "Ubuntu/Debian: sudo apt-get install inotify-tools"
    log "INFO" "Fedora: sudo dnf install inotify-tools"
    exit 1
fi

echo_usage() {
    echo "Usage: $0 <python_venv_name> <directory_to_monitor> [<python main file or path to it>]" 
    echo "If the second argument is not provided, the first argument will be used as the folder to look for the Main python file"
}

# log number of arguments provided
log "INFO" "Number of arguments: $#"


if [ $# -lt 2 ]; then
    echo_usage
    exit 1
elif [ $# -eq 2 ]; then
    PYTHON_VENV="$1"
    MONITOR_DIR="$2"
    PYTHON_FILE="$MONITOR_DIR"
    
elif [ $# -eq 3 ]; then
    PYTHON_VENV="$1"
    MONITOR_DIR="$2"
    PYTHON_FILE="$3"
else
    echo_usage
    exit 1
fi

log "INFO" "Python Virtual Environment: $PYTHON_VENV"
log "INFO" "Monitoring Directory: $MONITOR_DIR"
log "INFO" "Python Main File: $PYTHON_FILE"

# Verify directory exists
if [ ! -d "$MONITOR_DIR" ]; then
    log "ERROR" "Error: Directory $MONITOR_DIR does not exist"
    exit 1
fi

# Function to kill processes
cleanup() {
    if [ $CLEANUP_DONE -eq 1 ]; then
        return
    fi
    log "INFO" "Cleaning up..."
    # Kill game process if exists
    if [ ! -z "$GAME_PID" ]; then
        log "INFO" "Terminating game process (PID: $GAME_PID)..."
        kill -TERM "$GAME_PID" 2>/dev/null || true
    fi
    # Kill Python process if exists
    if [ ! -z "$PYTHON_PID" ]; then
        log "INFO" "Terminating Python process (PID: $PYTHON_PID)..."
        kill -TERM "$PYTHON_PID" 2>/dev/null || true
    fi
    # Kill the inotifywait process
    if [ ! -z "$INOTIFY_PID" ]; then
        kill $INOTIFY_PID 2>/dev/null || true
    fi
    
    if [ ! -z "$active_pid" ]; then
        log "INFO" "Terminating active process (PID: $active_pid)..."
        kill -TERM "$active_pid" 2>/dev/null || true
    fi
    rm "/tmp/script-${RANDOM_STRING}.log" 2>/dev/null
    rm "/tmp/script-${RANDOM_STRING}_pid" 2>/dev/null
    CLEANUP_DONE=1
    exit 0
}



RUNNING_PIDS=$(pgrep -f ".*$SCRIPT_NAME $PYTHON_FILE")

if [ -z "$RUNNING_PIDS" ]; then
    log "INFO" "$SCRIPT_NAME processes is not running"
    log "INFO" "Starting $SCRIPT_NAME in new terminal"
    
else
    log "INFO" "$SCRIPT_NAME processes is running with PIDs: $RUNNING_PIDS"
    log "INFO" "Killing $SCRIPT_NAME processes"
    kill $RUNNING_PIDS 2>/dev/null
    sleep 1
fi

run_script() {
    echo "INFO" "Starting script: $SCRIPT_PATH with input: $PYTHON_FILE"
    

    # Run in background and capture PID
    "$SCRIPT_PATH" "$PYTHON_FILE" &
    RUN_PY_AG_PID=$!
    
    # Wait for process and capture exit status
    wait $RUN_PY_AG_PID
    local status=$?
    
    if [ $status -ne 0 ]; then
        echo "ERROR" "Error: Script failed with status $status"
        # Optional: add cleanup code here
        return $status
    fi
    
    echo "INFO" "Script completed successfully"
    return 0
}

# Export function and required variables
export -f run_script
export SCRIPT_PATH PYTHON_FILE


RANDOM_STRING=$(head /dev/urandom | tr -dc A-Za-z0-9 | head -c 13 ; echo '')

restart_program() {
    local current_time=$(date +%s)
    
    # Debounce rapid changes
    if (( current_time - last_restart < DEBOUNCE_SECONDS )); then
        return
    fi
    
    log "INFO" "Change detected - Restarting program"
    
    # Kill existing instance if running
    if [[ -n "$active_pid" ]] && kill -0 "$active_pid" 2>/dev/null; then
        log "INFO" "Terminating previous instance (PID: $active_pid)"
        kill "$active_pid" 2>/dev/null || true
        sleep 1
        kill -9 "$active_pid" 2>/dev/null || true
    fi
    
    # Start new instance
    gnome-terminal -- bash -c "
        source ${PYTHON_VENV}/bin/activate
        # Redirect stderr to stdout and save both to log file
        run_script > >(tee /tmp/script-${RANDOM_STRING}.log) 2>&1 &
        script_pid=\$!
        echo \$script_pid > /tmp/script-${RANDOM_STRING}_pid
        wait \$script_pid
        exit_status=\$?
        if [ \$exit_status -ne 0 ]; then
            exit \$exit_status
        fi
        exec bash
    " &
    
    # Wait briefly for PID file
    sleep 1
    active_pid=$(cat /tmp/script-${RANDOM_STRING}_pid 2>/dev/null)
    last_restart=$current_time
    log "INFO" "Started new instance with PID: $active_pid"
}

# Trap signals
trap cleanup SIGINT SIGTERM
restart_program
sleep 1

# Check if active_pid is still running
if [ -z "$active_pid" ] || ! kill -0 "$active_pid" 2>/dev/null; then
    log "INFO" "Error: Failed to start program"
    log "INFO" "Reason:"
    cat /tmp/script-${RANDOM_STRING}.log
    exit 1
fi


EXCLUDE_PATTERN="(__pycache__|\.git|\.vscode|\.idea|\.pytest_cache|\.mypy_cache)"

# Get process IDs from environment variables if they exist
GAME_PID=${GAME_PID:-$(pgrep -f "java.*FightingICE.jar.*Main")}
PYTHON_PID=${PYTHON_PID:-$(pgrep -f "python .*[Mm]ain.*\.py")}


log "INFO" "Monitoring directory: $MONITOR_DIR"
log "INFO" "Press Ctrl+C to stop monitoring"

# Keep script running and handle file changes
while true; do
    read -r EVENT FILE
    # Add a small delay to coalesce multiple events
    sleep 0.1
    # Clear any pending events in the pipe
    while read -t 0.1 -r NEXT_EVENT NEXT_FILE; do
        EVENT=$NEXT_EVENT
        FILE=$NEXT_FILE
    done
    log "INFO" "Change detected: $EVENT on $FILE"
    restart_program
done < <(inotifywait -m -r \
    --exclude "$EXCLUDE_PATTERN" \
    -e modify,create,delete,move \
    "$MONITOR_DIR" \
    --format "%e %w%f" 2>/dev/null)