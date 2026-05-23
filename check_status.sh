#!/bin/bash
# Check calendar reminder cron job status

echo "=========================================="
echo "Calendar Email Reminder - Status Check"
echo "=========================================="
echo ""

echo "1. Cron Job Configuration:"
echo "------------------------------------------"
crontab -l | grep calendar_email_reminder || echo "❌ No cron job found!"
echo ""

echo "2. Last 10 Cron Runs:"
echo "------------------------------------------"
if [ -f "cron.log" ]; then
    tail -20 cron.log
else
    echo "❌ No cron.log file found yet"
fi
echo ""

echo "3. Sent Notifications:"
echo "------------------------------------------"
if [ -f ".sent_notifications.json" ]; then
    echo "✓ Notification tracking file exists"
    cat .sent_notifications.json
else
    echo "⚠ No notifications sent yet"
fi
echo ""

echo "4. Required Files:"
echo "------------------------------------------"
[ -f ".env" ] && echo "✓ .env exists" || echo "❌ .env missing"
[ -f "credentials.json" ] && echo "✓ credentials.json exists" || echo "❌ credentials.json missing"
[ -f "token.json" ] && echo "✓ token.json exists (authenticated)" || echo "⚠ token.json missing (need to authenticate)"
echo ""

echo "5. Cron Service Status:"
echo "------------------------------------------"
systemctl is-active cron && echo "✓ Cron service is running" || echo "❌ Cron service is not running"
echo ""
