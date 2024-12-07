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
declare -g MY_PYTHON_VENV
declare -g CREATED_TERMINAL
declare -g RANDOM_STRING=$(head /dev/urandom | tr -dc A-Za-z0-9 | head -c 13 ; echo '')
declare -g TERMINAL_PID


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
    MY_PYTHON_VENV="$1"
    MONITOR_DIR="$2"
    PYTHON_FILE="$MONITOR_DIR"
    
elif [ $# -eq 3 ]; then
    MY_PYTHON_VENV="$1"
    MONITOR_DIR="$2"
    PYTHON_FILE="$3"
else
    echo_usage
    exit 1
fi

log "INFO" "Python Virtual Environment: $MY_PYTHON_VENV"
log "INFO" "Monitoring Directory: $MONITOR_DIR"
log "INFO" "Python Main File: $PYTHON_FILE"

# Verify directory exists
if [ ! -d "$MONITOR_DIR" ]; then
    log "ERROR" "Error: Directory $MONITOR_DIR does not exist"
    exit 1
fi

# Function to kill processes
cleanup() {
    TERM=9
    # local pid=$1
    # if [ -n "$pid" ] &&  kill -0 "$pid" 2>/dev/null; then
    #     return 0
    # fi

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
    TERMINAL_PID=$(cat /tmp/bash-${RANDOM_STRING}_pid 2>/dev/null)
    if [ ! -z "$TERMINAL_PID" ]; then
        log "INFO" "Terminating terminal process (PID: $TERMINAL_PID)..."
        kill -TERM "$TERMINAL_PID" 2>/dev/null || true
    fi

    rm "/tmp/script-${RANDOM_STRING}.log" 2>/dev/null
    rm "/tmp/script-${RANDOM_STRING}_pid" 2>/dev/null
    rm "/tmp/bash-${RANDOM_STRING}_pid" 2>/dev/null
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

    echo "$RUN_PY_AG_PID" > /tmp/script-${RANDOM_STRING}_pid
    
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


activate_venv() {
    local venv_path="$1"
    local venv_name="$(basename "$venv_path")"
    
    # Check conda environment
    if command -v conda >/dev/null 2>&1; then
        if conda env list | grep -q "^${venv_name}"; then
            echo "Activating conda environment: $venv_name"
            source "$(conda info --base)/etc/profile.d/conda.sh"
            conda activate "$venv_name"
            return 0
        fi
    fi
    
    # Check standard venv/virtualenv
    if [ -f "${venv_path}/bin/activate" ]; then
        echo "Activating venv/virtualenv: $venv_path"
        source "${venv_path}/bin/activate"
        return 0
    fi
    
    # Check pyenv
    if command -v pyenv >/dev/null 2>&1; then
        if pyenv versions | grep -q "$venv_name"; then
            echo "Activating pyenv: $venv_name"
            eval "$(pyenv init -)"
            pyenv shell "$venv_name"
            return 0
        fi
    fi
    
    echo "ERROR" "No virtual environment found at: $venv_path"
    return 1
}


create_terminal_script() {
    # Remove quotes around EOF to allow variable expansion
    cat << EOF
    {
        # Ensure temp directory exists and is writable
        touch /tmp/script-${RANDOM_STRING}.log || {
            echo "ERROR" "Cannot create log file"
            exit 1
        }

        # Store bash PID
        echo \$$ > /tmp/bash-${RANDOM_STRING}_pid || exit 1
        

        # Activate virtual environment
        if ! activate_venv ${MY_PYTHON_VENV} >> /tmp/script-${RANDOM_STRING}.log 2>&1; then
            echo "ERROR" "Failed to activate virtual environment" >> /tmp/script-${RANDOM_STRING}.log
            exit 1
        fi

        # Run main script with logging
        run_script 2>&1 | tee /tmp/script-${RANDOM_STRING}.log &
        
        # Wait and handle exit
        wait \$script_pid
        exec bash
        echo \$$ > /tmp/bash-${RANDOM_STRING}_pid || exit 1
        
    }
EOF
}

# Export function and required variables
export -f run_script
export SCRIPT_PATH PYTHON_FILE
export -f activate_venv
export RANDOM_STRING


restart_program() {
    local current_time=$(date +%s)
    
    # Debounce rapid changes
    if (( current_time - last_restart < DEBOUNCE_SECONDS )); then
        return
    fi

    
    
    
    # Kill existing instance if running
    if [[ -n "$active_pid" ]] && kill -0 "$active_pid" 2>/dev/null; then
        log "INFO" "Terminating previous instance (PID: $active_pid)"
        kill -15 "$active_pid" 2>/dev/null || true
        sleep 1
        kill -9 "$active_pid" 2>/dev/null || true
    fi
    TERMINAL_PID=$(cat /tmp/bash-${RANDOM_STRING}_pid 2>/dev/null)
    # Killing existing terminal if runningz
    if [[ -n "$TERMINAL_PID" ]] && kill -0 "$TERMINAL_PID" 2>/dev/null; then
        log "INFO" "Terminating previous terminal (PID: $TERMINAL_PID)"
        kill -15 "$TERMINAL_PID" 2>/dev/null || true
        sleep 1
        kill -9 "$TERMINAL_PID" 2>/dev/null || true
    fi
    

    for terminal in gnome-terminal x-terminal-emulator xterm konsole; do
        if command -v "$terminal" >/dev/null 2>&1; then
            case "$terminal" in
                gnome-terminal)
                    gnome-terminal -- bash -c "$(create_terminal_script)" & 
                    ;;
                xterm)
                    xterm -e bash -c "$(create_terminal_script)" & 
                    ;;
                *)
                    "$terminal" -e "bash -c '$(create_terminal_script)'" & 
                    ;;
            esac
            while true; do
                if [ -f "/tmp/bash-${RANDOM_STRING}_pid" ]; then
                    break
                fi
                sleep 0.5
            done
            TERMINAL_PID=$(cat /tmp/bash-${RANDOM_STRING}_pid)
            log "INFO" "Started $terminal with PID: $TERMINAL_PID"
            break
        fi
    done

    # Check if any terminal was launched
    if [ -z "$TERMINAL_PID" ]; then
        log "ERROR" "No terminal emulator found"
        exit 1
    fi

    # Wait briefly for PID file
    sleep 1
    active_pid=$(cat /tmp/script-${RANDOM_STRING}_pid)
    last_restart=$current_time
    log "INFO" "Started new instance with PID: $active_pid"
}

check_process() {
    local pid=$1
    if [ -n "$pid" ] && ! kill -0 $pid > /dev/null; then
        return 1
    fi
    log "INFO" "Process $pid is running"
    return 0
}

# Trap signals
trap cleanup EXIT

restart_program
sleep 4

# Check if active_pid is still running
if [ -z "$active_pid" ] || ! kill -0 "$active_pid" 2>/dev/null; then
    log "INFO" "Error: Failed to start program"
    log "INFO" "Reason:"
    cat /tmp/script-${RANDOM_STRING}.log    
    exit 1
fi


EXCLUDE_PATTERN="(__pycache__|\.git|\.vscode|\.idea|\.pytest_cache|\.mypy_cache)"

sleep 3
# Get process IDs from environment variables if they exist
GAME_PID=$(pgrep -f "java.*FightingICE.jar.*Main")
PYTHON_PID=$(pgrep -f "python .*[Mm]ain.*\.py")


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
    log "INFO" "Restarting program..."
    restart_program
    
    sleep 4
    # Check if active_pid is still running
    if [ -z "$active_pid" ] || ! kill -0 "$active_pid" 2>/dev/null; then
        log "INFO" "Error: Failed to start program"
        log "INFO" "Reason:"
        cat /tmp/script-${RANDOM_STRING}.log
    fi
done < <(inotifywait -m -r \
    --exclude "$EXCLUDE_PATTERN" \
    -e modify,create,delete,move \
    "$MONITOR_DIR" \
    --format "%e %w%f" 2>/dev/null)