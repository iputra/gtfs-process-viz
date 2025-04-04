# Real-Time Delivery Tracker

A real-time delivery tracking system that uses GTFS Realtime data, Kafka for real-time data processing, Apache Spark for geofencing, and Kepler.gl for visualization.

## System Architecture

The system consists of the following components:

1. **GTFS Realtime Consumer**: Fetches vehicle position data from a GTFS Realtime feed and publishes it to Kafka.
2. **Kafka**: Message broker for real-time data streaming.
3. **Apache Spark**: Processes the vehicle position data and performs geofencing.
4. **Geofencing Service**: Backend API and WebSocket server that connects Kafka to the frontend.
5. **Frontend**: React application with Kepler.gl for visualization.

## Prerequisites

- Docker with Compose plugin
- A GTFS Realtime feed URL (TransLink SEQ feed is already configured)

## Setup

1. Clone this repository:

```bash
git clone <repository-url>
cd real-time-delivery-tracker
```

2. Create environment files:

```bash
# For GTFS consumer
cp backend/gtfs-consumer/.env.example backend/gtfs-consumer/.env
# For Spark processor
cp backend/spark-processor/.env.example backend/spark-processor/.env
# For Geofencing service
cp backend/geofencing-service/.env.example backend/geofencing-service/.env
```

3. The environment files are already configured with the TransLink SEQ GTFS Realtime feed URL. If you want to use a different feed, edit `backend/gtfs-consumer/.env`.

4. Start the services:

```bash
docker compose up -d
```

Or use the provided script:

```bash
./start.sh
```

## Usage

1. Access the frontend at http://localhost:3000
2. The map will display vehicle positions and geofence zones using OpenStreetMap.
3. The control panel shows statistics and recent geofence events.
4. The system is configured with geofences in Brisbane, Australia to match the TransLink data.

## Customizing Geofences

Geofences are defined in `backend/spark-processor/geofences.json`. Each geofence has the following properties:

- `id`: Unique identifier for the geofence
- `name`: Display name for the geofence
- `description`: Description of the geofence
- `coordinates`: Array of [longitude, latitude] coordinates that define the polygon

To add or modify geofences, edit this file and restart the services.

## Development

### Frontend Development

The frontend is a React application with Vite. To run it in development mode:

```bash
cd frontend
npm install
npm run dev
```

### Backend Development

Each backend service can be run independently for development:

```bash
# GTFS Consumer
cd backend/gtfs-consumer
pip install -r requirements.txt
python gtfs_consumer.py

# Geofencing Service
cd backend/geofencing-service
pip install -r requirements.txt
uvicorn main:app --reload
```

## Troubleshooting

- If the frontend can't connect to the backend, check that the WebSocket server is running.
- If no vehicle data appears, check the GTFS Realtime feed URL and Kafka connection.
- If geofencing doesn't work, check the geofence definitions and Spark processor logs.

## License

This project is licensed under the MIT License - see the LICENSE file for details.
