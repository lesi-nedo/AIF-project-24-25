#!/bin/bash

ARGS=""
set -e
# Check if the number of arguments is correct
while [[ $# -gt 0 ]]; do
    case $1 in
        --port)
        shift
        if [[ $1 -ge 1024 && $1 -le 49151 ]]; then
            ARGS="$ARGS --port $1"
        else
            echo "Port number must be between 1024 and 49151"
            exit 1
        fi
        ;;
        --headless|--headless-mode)
        ARGS="$ARGS --headless-mode"
        ;;
        *)
        echo "Invalid argument: $1"
        exit 1
        ;;
    esac
    shift
done


if [[ ! $ARGS == "" ]]; then
    echo "Running with args: $ARGS"
fi

# Compile all Java files and include LWJGL libraries in the classpath
javac -d bin -cp "lib/*:lib/lwjgl/*:lib/lwjgl/natives/linux/amd64/*" @sources.txt

# Run the program with the LWJGL libraries in the classpath
java -cp "bin:lib/*:lib/lwjgl/*:lib/lwjgl/natives/linux/amd64/*" Main --limithp 400 400 --grey-bg --pyftg-mode $ARGS
