|
0 10 * * * /path/to/projects/Strangers\ Calendar\ App/scripts/daily_status_update.sh

# Make the cron job executable
chmod +x projects/Strangers\ Calendar\ App/cron/daily_status_update.sh

# Add the cron job to the crontab
crontab -l | { cat; echo "0 10 * * * /path/to/projects/Strangers\ Calendar\ App/scripts/daily_status_update.sh"; } | crontab -