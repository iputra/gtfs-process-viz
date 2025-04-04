import os
import time
import json
import requests
import logging
from dotenv import load_dotenv
from kafka import KafkaProducer
from google.transit import gtfs_realtime_pb2
from google.protobuf.json_format import MessageToJson

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

# Kafka configuration
KAFKA_BOOTSTRAP_SERVERS = os.getenv('KAFKA_BOOTSTRAP_SERVERS', 'localhost:9092')
KAFKA_TOPIC = os.getenv('KAFKA_TOPIC', 'gtfs-vehicle-positions')

# GTFS Realtime feed URL
GTFS_REALTIME_URL = os.getenv('GTFS_REALTIME_URL')

def create_kafka_producer():
    """Create and return a Kafka producer instance."""
    try:
        producer = KafkaProducer(
            bootstrap_servers=KAFKA_BOOTSTRAP_SERVERS,
            value_serializer=lambda v: json.dumps(v).encode('utf-8')
        )
        logger.info(f"Kafka producer connected to {KAFKA_BOOTSTRAP_SERVERS}")
        return producer
    except Exception as e:
        logger.error(f"Failed to create Kafka producer: {e}")
        raise

def fetch_gtfs_realtime_data():
    """Fetch GTFS Realtime data from the feed URL."""
    try:
        if not GTFS_REALTIME_URL:
            logger.error("GTFS_REALTIME_URL environment variable not set")
            return None
            
        response = requests.get(GTFS_REALTIME_URL)
        response.raise_for_status()
        
        feed = gtfs_realtime_pb2.FeedMessage()
        feed.ParseFromString(response.content)
        
        logger.info(f"Fetched GTFS Realtime data with {len(feed.entity)} entities")
        return feed
    except requests.exceptions.RequestException as e:
        logger.error(f"Error fetching GTFS Realtime data: {e}")
        return None
    except Exception as e:
        logger.error(f"Error parsing GTFS Realtime data: {e}")
        return None

def process_vehicle_positions(feed, producer):
    """Process vehicle positions from the GTFS Realtime feed and send to Kafka."""
    if not feed:
        return
        
    for entity in feed.entity:
        if entity.HasField('vehicle'):
            try:
                # Convert protobuf message to JSON
                vehicle_json = json.loads(MessageToJson(entity.vehicle))
                
                # Add entity ID
                vehicle_json['entity_id'] = entity.id
                
                # Add timestamp
                vehicle_json['processing_timestamp'] = int(time.time())
                
                # Send to Kafka
                producer.send(KAFKA_TOPIC, vehicle_json)
                logger.debug(f"Sent vehicle position for entity {entity.id} to Kafka")
            except Exception as e:
                logger.error(f"Error processing vehicle position for entity {entity.id}: {e}")

def main():
    """Main function to run the GTFS Realtime consumer."""
    try:
        producer = create_kafka_producer()
        
        logger.info("Starting GTFS Realtime consumer")
        
        while True:
            feed = fetch_gtfs_realtime_data()
            process_vehicle_positions(feed, producer)
            
            # Wait before fetching again
            time.sleep(int(os.getenv('FETCH_INTERVAL_SECONDS', '30')))
            
    except KeyboardInterrupt:
        logger.info("Stopping GTFS Realtime consumer")
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
    finally:
        if 'producer' in locals():
            producer.flush()
            producer.close()
            logger.info("Kafka producer closed")

if __name__ == "__main__":
    main()
