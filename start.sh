#!/bin/bash

# Start the services
echo "Starting services..."
docker compose up -d

# Wait for services to start
echo "Waiting for services to start..."
sleep 10

# Check if services are running
echo "Checking services..."
docker compose ps

echo ""
echo "Real-Time Delivery Tracker is now running!"
echo "Access the frontend at: http://localhost:3000"
echo ""
echo "To stop the services, run: docker compose down"
