#!/usr/bin/env bash

# Compile all Java files and include LWJGL libraries in the classpath
javac -d bin -cp "lib/*:lib/lwjgl/*:lib/lwjgl/natives/macos/x64/*" @sources.txt

# Run the program with the LWJGL libraries in the classpath
java -cp "bin:lib/*:lib/lwjgl/*:lib/lwjgl/natives/macos/x64/*" Main --limithp 400 400 --grey-bg --pyftg-mode --headless-mode
