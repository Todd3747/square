#!/bin/bash

# Wrapper script to run updated_sales.py with virtual environment

# Check if a date argument was provided
if [ $# -eq 0 ]; then
    echo ""
    echo -e "\tUSAGE: $0 <query_date ie. 2025-10-13>"
    echo ""
    exit 1
fi

# Get the directory where this script is located
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

# Activate the virtual environment
source "$SCRIPT_DIR/../../venv/all/bin/activate"

# Run the Python script with all passed arguments
python "$SCRIPT_DIR/updated_sales.py" "$@"

# Store the exit code
EXIT_CODE=$?

# Deactivate the virtual environment
deactivate

# Exit with the same code as the Python script
exit $EXIT_CODE
