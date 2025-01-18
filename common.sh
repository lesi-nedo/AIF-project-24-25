#!/bin/bash

# Function to check if port is available
check_port() {
    local port=$1
    (echo >/dev/tcp/127.0.0.1/$port) >/dev/null 2>&1 && return 1 || return 0
}