#!/bin/bash
# Wait for Jenkins to be fully up
timeout=600  # 10 minutes
elapsed=0
until curl -s -f http://localhost:8080/login > /dev/null || [ $elapsed -ge $timeout ]; do
    echo "Waiting for Jenkins... ($elapsed seconds elapsed)"
    sleep 10
    elapsed=$((elapsed + 10))
done
if [ $elapsed -ge $timeout ]; then
    echo "Error: Jenkins did not start within 10 minutes."
    exit 1
fi
echo "Jenkins is configured and ready."