#!/bin/bash

# Get the directory of this script (resolved to absolute path)
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PROJECT_DIR="$( dirname "$SCRIPT_DIR" )"

cd "$PROJECT_DIR" || exit 1

# Activate virtual environment
if [ -d ".venv" ]; then
    source .venv/bin/activate
fi

# Run the Django db_backup command (keeping the last 10 backups by default)
python manage.py db_backup --keep 10 >> backups/backup.log 2>&1
