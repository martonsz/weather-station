#!/bin/bash

# Script to manage the weather station service
# Usage: ./install-service.sh [OPTION]

# Function to display usage
show_usage() {
    echo "Usage: $0 [OPTION]"
    echo "Options:"
    echo "  -i, --install    Install and enable the service"
    echo "  -u, --uninstall  Disable and remove the service"
    echo "  -s, --start      Start the service"
    echo "  -t, --stop       Stop the service"
    echo "  -r, --restart    Restart the service"
    echo "  -c, --status     Check service status"
    echo "  -h, --help       Display this help message"
}

# Check if script is run as root
if [ "$EUID" -ne 0 ]; then
    echo "Please run as root (use sudo)"
    exit 1
fi

# Handle long options
for arg in "$@"; do
    case "$arg" in
        --install)
            INSTALL=true
            ;;
        --uninstall)
            UNINSTALL=true
            ;;
        --start)
            START=true
            ;;
        --stop)
            STOP=true
            ;;
        --restart)
            RESTART=true
            ;;
        --status)
            STATUS=true
            ;;
        --help)
            show_usage
            exit 0
            ;;
    esac
done

# Handle short options
while getopts "iustrch" opt; do
    case ${opt} in
        i)
            INSTALL=true
            ;;
        u)
            UNINSTALL=true
            ;;
        s)
            START=true
            ;;
        t)
            STOP=true
            ;;
        r)
            RESTART=true
            ;;
        c)
            STATUS=true
            ;;
        h)
            show_usage
            exit 0
            ;;
        \?)
            echo "Invalid option: -$OPTARG" >&2
            show_usage
            exit 1
            ;;
    esac
done

# Execute the requested actions
if [ "$INSTALL" = true ]; then
    echo "Installing weather station service..."
    cp weather-station.service /etc/systemd/system/
    systemctl daemon-reload
    systemctl enable weather-station.service
    systemctl start weather-station.service
    echo "Service installed and started"
fi

if [ "$UNINSTALL" = true ]; then
    echo "Uninstalling weather station service..."
    systemctl stop weather-station.service
    systemctl disable weather-station.service
    rm /etc/systemd/system/weather-station.service
    systemctl daemon-reload
    echo "Service uninstalled"
fi

if [ "$START" = true ]; then
    echo "Starting weather station service..."
    systemctl start weather-station.service
fi

if [ "$STOP" = true ]; then
    echo "Stopping weather station service..."
    systemctl stop weather-station.service
fi

if [ "$RESTART" = true ]; then
    echo "Restarting weather station service..."
    systemctl restart weather-station.service
fi

if [ "$STATUS" = true ]; then
    echo "Weather station service status:"
    systemctl status weather-station.service
fi

# If no options provided, show usage
if [ "$INSTALL" != true ] && [ "$UNINSTALL" != true ] && [ "$START" != true ] && \
   [ "$STOP" != true ] && [ "$RESTART" != true ] && [ "$STATUS" != true ]; then
    show_usage
    exit 1
fi 