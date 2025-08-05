#!/bin/bash
# Script to clean ANSI escape codes from monitor output

./monitor_agents.sh 2>&1 | sed 's/\x1b\[[0-9;]*m//g'