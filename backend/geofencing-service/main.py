import os
import json
import asyncio
import logging
from typing import List, Dict, Any
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from kafka import KafkaConsumer
from dotenv import load_dotenv
import socketio

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

# Kafka configuration
KAFKA_BOOTSTRAP_SERVERS = os.getenv('KAFKA_BOOTSTRAP_SERVERS', 'kafka:29092')
VEHICLE_POSITIONS_TOPIC = os.getenv('VEHICLE_POSITIONS_TOPIC', 'gtfs-vehicle-positions')
GEOFENCE_EVENTS_TOPIC = os.getenv('GEOFENCE_EVENTS_TOPIC', 'geofence-events')

# Create FastAPI app
app = FastAPI(title="Geofencing Service")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Create Socket.IO server
sio = socketio.AsyncServer(
    async_mode='asgi',
    cors_allowed_origins='*'
)
socket_app = socketio.ASGIApp(sio)

# Mount Socket.IO app
app.mount('/socket.io', socket_app)

# In-memory storage for connected clients
connected_clients = set()

# Load geofences
def load_geofences():
    """Load geofence definitions from a JSON file."""
    try:
        geofence_file = os.getenv('GEOFENCE_FILE', '../spark-processor/geofences.json')
        with open(geofence_file, 'r') as f:
            geofences = json.load(f)
        logger.info(f"Loaded {len(geofences)} geofences")
        return geofences
    except Exception as e:
        logger.error(f"Error loading geofences: {e}")
        return []

# Kafka consumer for vehicle positions
async def consume_vehicle_positions():
    """Consume vehicle positions from Kafka and broadcast to connected clients."""
    try:
        consumer = KafkaConsumer(
            VEHICLE_POSITIONS_TOPIC,
            bootstrap_servers=KAFKA_BOOTSTRAP_SERVERS,
            value_deserializer=lambda v: json.loads(v.decode('utf-8')),
            auto_offset_reset='latest',
            group_id='geofencing-service-vehicle-positions'
        )
        
        logger.info(f"Started consuming from {VEHICLE_POSITIONS_TOPIC}")
        
        while True:
            # Non-blocking poll for messages
            messages = consumer.poll(timeout_ms=100, max_records=10)
            
            for topic_partition, records in messages.items():
                for record in records:
                    # Broadcast vehicle position to all connected clients
                    await sio.emit('vehicle_positions', [record.value])
            
            # Sleep to avoid high CPU usage
            await asyncio.sleep(0.1)
            
    except Exception as e:
        logger.error(f"Error consuming vehicle positions: {e}")
        
# Kafka consumer for geofence events
async def consume_geofence_events():
    """Consume geofence events from Kafka and broadcast to connected clients."""
    try:
        consumer = KafkaConsumer(
            GEOFENCE_EVENTS_TOPIC,
            bootstrap_servers=KAFKA_BOOTSTRAP_SERVERS,
            value_deserializer=lambda v: json.loads(v.decode('utf-8')),
            auto_offset_reset='latest',
            group_id='geofencing-service-geofence-events'
        )
        
        logger.info(f"Started consuming from {GEOFENCE_EVENTS_TOPIC}")
        
        while True:
            # Non-blocking poll for messages
            messages = consumer.poll(timeout_ms=100, max_records=10)
            
            for topic_partition, records in messages.items():
                for record in records:
                    # Broadcast geofence event to all connected clients
                    await sio.emit('geofence_events', record.value)
            
            # Sleep to avoid high CPU usage
            await asyncio.sleep(0.1)
            
    except Exception as e:
        logger.error(f"Error consuming geofence events: {e}")

# Socket.IO event handlers
@sio.event
async def connect(sid, environ):
    """Handle client connection."""
    logger.info(f"Client connected: {sid}")
    connected_clients.add(sid)
    
@sio.event
async def disconnect(sid):
    """Handle client disconnection."""
    logger.info(f"Client disconnected: {sid}")
    if sid in connected_clients:
        connected_clients.remove(sid)

# FastAPI routes
@app.get("/")
async def root():
    """Root endpoint."""
    return {"message": "Geofencing Service API"}

@app.get("/geofences")
async def get_geofences():
    """Get all geofences."""
    return load_geofences()

@app.on_event("startup")
async def startup_event():
    """Start background tasks on application startup."""
    # Start Kafka consumers as background tasks
    asyncio.create_task(consume_vehicle_positions())
    asyncio.create_task(consume_geofence_events())
    logger.info("Started Kafka consumers as background tasks")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
