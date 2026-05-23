#!/bin/bash
# Helper script to generate cron job command

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PYTHON_PATH="$SCRIPT_DIR/.venv/bin/python"
MAIN_SCRIPT="$SCRIPT_DIR/main.py"
LOG_FILE="$SCRIPT_DIR/cron.log"

echo "===================================="
echo "Calendar Email Reminder - Cron Setup"
echo "===================================="
echo ""
echo "To run this script every 5 minutes, add this line to your crontab:"
echo ""
echo "*/5 * * * * cd $SCRIPT_DIR && $PYTHON_PATH $MAIN_SCRIPT >> $LOG_FILE 2>&1"
echo ""
echo "To edit your crontab, run:"
echo "  crontab -e"
echo ""
echo "To view cron logs later, run:"
echo "  tail -f $LOG_FILE"
echo ""
