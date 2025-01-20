# `monitor_restart.sh` - Script Explanation and Usage Guide

## Overview

The `monitor_restart.sh` script is a Bash utility designed to automate the process of monitoring a directory for file changes and restarting a Python program whenever changes are detected. This is particularly useful during development, allowing for rapid testing and debugging without manual restarts.

## Features

- **Directory Monitoring**: Uses `inotifywait` to watch for file changes in a specified directory.
- **Automatic Restart**: Restarts the specified Python program when changes are detected.
- **Process Management**: Handles the termination of previous instances to prevent multiple instances from running simultaneously.
- **Logging**: Provides timestamped and colored log messages for better readability.
- **Exclusion Patterns**: Ignores changes in specified directories like `__pycache__`, `.git`, etc.
- **Debounce Mechanism**: Prevents rapid restarts by implementing a debounce period.

## Prerequisites

- **Bash Shell**: Ensure the script is run in a Bash shell environment.
- **inotify-tools**: Install `inotifywait` for file system event monitoring.

  Installation commands:

  - **Ubuntu/Debian**: `sudo apt-get install inotify-tools`
  - **Fedora**: `sudo dnf install inotify-tools`

- **Python Virtual Environment**: A Python virtual environment to activate before running the program.
- **gnome-terminal**: The script uses `gnome-terminal` to open new terminals.

## Script Usage

```bash
./monitor_restart.sh <python_venv_name> <directory_to_monitor> [<python_main_file_or_path>]
```

- `<python_venv_name>`: Python virtual environment.
- `<directory_to_monitor>`: Directory where file changes are monitored.
- `<python_main_file_or_path>` (optional): The main Python file to execute. If not provided, the script uses the monitoring directory.

### Examples

1. **Monitor a directory and execute the main Python file within it:**

   ```bash
   ./monitor_restart.sh myenv ./prolog_based/problog_agent_ole/
   ```

2. **Monitor a directory and execute a specific Python file:**

   ```bash
   ./monitor_restart.sh myenv ./prolog_based/problog_agent_ole/ ./prolog_based/problog_agent_ole/main.py
   ```

## How It Works

1. **Initialization**:

   - Validates that `inotifywait` is installed.
   - Parses command-line arguments to determine the virtual environment, directory to monitor, and the Python file to execute.
   - Sets up logging levels and colors for output.

2. **Process Monitoring and Management**:

   - Checks for any running instances of the script or the Python program and terminates them.
   - Defines a `cleanup` function to handle termination signals and clean up processes.

3. **Running the Python Program**:

   - Defines a `run_script` function that activates the virtual environment and runs the Python program in a new `gnome-terminal`.
   - Manages the process ID of the running Python program for later termination.

4. **Directory Watching**:

   - Uses `inotifywait` to monitor the specified directory recursively for events like modification, creation, deletion, and moves.
   - Excludes certain patterns (e.g., `__pycache__`, `.git`) to ignore irrelevant changes.

5. **Restart Logic**:

   - Implements a debounce mechanism to prevent rapid restarts when multiple file changes occur in quick succession.
   - When a change is detected, the script terminates the running Python program and starts a new instance.

## Logging

The script includes a sophisticated logging system with colored output:

- **DEBUG** (Cyan): Detailed debugging information
- **INFO** (Green): General information about script operation
- **WARN** (Yellow): Warning messages that don't stop execution
- **ERROR** (Red): Critical errors that may stop execution

Example log output:
```
[2024-01-20 15:30:45] [INFO] Starting script execution
[2024-01-20 15:30:46] [WARN] Process already running
[2024-01-20 15:30:47] [ERROR] Failed to create log file
```

## Virtual Environment Support

The script now supports multiple Python virtual environment types:

1. **Conda Environments**: Automatically detects and activates Conda environments
2. **Standard venv/virtualenv**: Supports traditional Python virtual environments
3. **pyenv**: Supports pyenv-managed virtual environments

The script will attempt to activate the environment in this order and use the first successful match.

## Terminal Handling

The script now supports multiple terminal emulators:

1. gnome-terminal (default)
2. x-terminal-emulator
3. xterm
4. konsole

The script will try each terminal emulator in sequence until it finds one that's available on the system.

## Exclusion Patterns

The script excludes monitoring certain directories and files using the `EXCLUDE_PATTERN` variable:

```bash
EXCLUDE_PATTERN="(__pycache__|\.git|\.vscode|\.idea|\.pytest_cache|\.mypy_cache)"
```

## Notes

- **Terminal Emulator**: The script uses `gnome-terminal`. If you're using a different terminal emulator, you may need to modify the script accordingly.
- **Permissions**: Ensure the script has execute permissions:

  ```bash
  chmod +x monitor_restart.sh
  ```

- **Debounce Timing**: The debounce period is set using `DEBOUNCE_SECONDS`. Adjust this value if needed.

## Troubleshooting

- **Script Doesn't Start**: Verify that all prerequisites are met and that the correct arguments are provided.
- **Python Program Fails to Run**: Check that the Python virtual environment and the Python file paths are correct.
- **No Reaction to File Changes**: Ensure that you're modifying files within the monitored directory and that they're not excluded by `EXCLUDE_PATTERN`.

## Conclusion

The `monitor_restart.sh` script automates the workflow of monitoring file changes and restarting a Python application, enhancing efficiency during development. By following the usage instructions and ensuring all dependencies are installed, you can integrate this script into your development process for a smoother experience.