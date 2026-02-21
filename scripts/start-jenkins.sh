#!/usr/bin/env bash
set -euo pipefail

# Start Jenkins via systemd if available, otherwise use Docker

if command -v systemctl >/dev/null 2>&1 && systemctl list-units --type=service --all | grep -q jenkins; then
  echo "Starting Jenkins systemd service..."
  sudo systemctl start jenkins
  sudo systemctl status jenkins --no-pager
  exit 0
fi

echo "Systemd Jenkins service not found — starting Jenkins in Docker..."
docker run -d --name jenkins -p 8080:8080 -p 50000:50000 -v jenkins_home:/var/jenkins_home jenkins/jenkins:lts
echo "Jenkins started (Docker). Open http://localhost:8080"
