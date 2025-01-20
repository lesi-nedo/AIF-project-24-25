# `run_py_ag_parallel.sh` - Parallel Python Agent Runner

## Overview

The `run_py_ag_parallel.sh` script enables parallel execution of Python agents for the DareFightingICE game environment. It manages multiple game instances and their corresponding Python agents, automatically handling port allocation and process management.

## Features

- Multiple game instance management
- Automatic port allocation and validation
- Conda environment support
- Parallel execution control
- Comprehensive logging system
- Process cleanup and management
- Random safe port selection

## Prerequisites

- Conda (Miniconda3, Anaconda3, or Miniforge3)
- Bash shell environment
- DareFightingICE game environment
- Python 3.x

## Usage

```bash
./run_py_ag_parallel.sh -e <conda_env> --main-file <python_file> --in-parallel <num> --total <total_executions>
```

### Parameters

- `-e, --env`: Conda environment name (required)
- `--main-file`: Path to the main Python script (required)
- `--in-parallel`: Number of parallel game instances (default: 1)
- `--total`: Total number of execution rounds
- `-h, --help`: Display help information

### Example

```bash
./run_py_ag_parallel.sh -e fighting_ice --main-file ./agents/main.py --in-parallel 5 --total 10
```

This command will:
1. Activate the "fighting_ice" conda environment
2. Launch 5 parallel game instances
3. Run the specified Python agent 10 times in total
4. Manage all processes and cleanup automatically

## Directory Structure

```
project/
├── run_py_ag_parallel.sh
├── DareFightingICE_CODE/
│   └── compile_run_linux.sh
└── logs/
    ├── game/
    └── agents/
```

## Logging

The script creates two types of log directories:

1. `logs/game/`: Game instance logs
2. `logs/agents/`: Python agent execution logs

Log files are named using the pattern:
- Game logs: `<main_script>-game-<instance_number>`
- Agent logs: `<main_script>-exec-<instance_number>`

## Port Management

- Base port: 31415 (default)
- Automatically finds available ports
- Avoids common service ports
- Uses random safe port selection

## Process Management

The script handles:
- Game instance processes
- Python agent processes
- Cleanup on exit/interruption
- Process synchronization

## Error Handling

- Validates conda environment
- Checks script dependencies
- Verifies port availability
- Manages process failures
- Provides cleanup on errors

## Best Practices

1. Ensure sufficient system resources for parallel execution
2. Monitor log files for debugging
3. Use appropriate parallel count based on system capacity
4. Keep conda environment updated
5. Check port availability before running

## Troubleshooting

### Common Issues

1. **Port Conflicts**
   ```bash
   Error: Port already in use
   ```
   Solution: Wait for ports to clear or specify different base port

2. **Conda Environment**
   ```bash
   Error: Conda environment not found
   ```
   Solution: Verify environment name and installation

3. **Process Cleanup**
   ```bash
   Error: Processes still running
   ```
   Solution: Manually terminate using provided PIDs

## Notes

- The script requires execution permissions (`chmod +x run_py_ag_parallel.sh`)
- Ensure DareFightingICE is properly configured
- Monitor system resources during parallel execution
- Keep logs for debugging purposes
