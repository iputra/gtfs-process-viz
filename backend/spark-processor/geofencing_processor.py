import os
import json
import logging
from dotenv import load_dotenv
from pyspark.sql import SparkSession
from pyspark.sql.functions import from_json, col, udf, struct, to_json
from pyspark.sql.types import StructType, StructField, StringType, DoubleType, IntegerType, BooleanType
from shapely.geometry import Point, Polygon

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
INPUT_TOPIC = os.getenv('INPUT_TOPIC', 'gtfs-vehicle-positions')
OUTPUT_TOPIC = os.getenv('OUTPUT_TOPIC', 'geofence-events')

# Define the schema for the vehicle position data
vehicle_schema = StructType([
    StructField("entity_id", StringType(), True),
    StructField("processing_timestamp", IntegerType(), True),
    StructField("position", StructType([
        StructField("latitude", DoubleType(), True),
        StructField("longitude", DoubleType(), True),
        StructField("bearing", DoubleType(), True),
        StructField("speed", DoubleType(), True)
    ]), True),
    StructField("vehicle", StructType([
        StructField("id", StringType(), True)
    ]), True),
    StructField("timestamp", StringType(), True)
])

# Load geofence definitions
def load_geofences():
    """Load geofence definitions from a JSON file."""
    try:
        geofence_file = os.getenv('GEOFENCE_FILE', 'geofences.json')
        with open(geofence_file, 'r') as f:
            geofences = json.load(f)
        
        # Convert coordinates to Shapely polygons
        for geofence in geofences:
            coordinates = geofence['coordinates']
            geofence['polygon'] = Polygon(coordinates)
            
        logger.info(f"Loaded {len(geofences)} geofences")
        return geofences
    except Exception as e:
        logger.error(f"Error loading geofences: {e}")
        # Return a default empty list if file not found
        return []

# Define UDF for geofence checking
def check_geofences(geofences):
    """Create a UDF to check if a point is inside any geofence."""
    def is_in_geofence(lat, lon, vehicle_id):
        if lat is None or lon is None:
            return []
            
        point = Point(lon, lat)
        results = []
        
        for geofence in geofences:
            is_inside = geofence['polygon'].contains(point)
            results.append({
                "geofence_id": geofence['id'],
                "geofence_name": geofence['name'],
                "vehicle_id": vehicle_id,
                "latitude": lat,
                "longitude": lon,
                "is_inside": is_inside
            })
            
        return json.dumps(results)
    
    return udf(is_in_geofence, StringType())

def create_spark_session():
    """Create and return a Spark session."""
    return (SparkSession.builder
            .appName("GTFS Geofencing Processor")
            .config("spark.streaming.stopGracefullyOnShutdown", "true")
            .getOrCreate())

def process_vehicle_positions(spark):
    """Process vehicle positions and detect geofence events."""
    # Load geofences
    geofences = load_geofences()
    geofence_checker = check_geofences(geofences)
    
    # Read from Kafka
    df = (spark
          .readStream
          .format("kafka")
          .option("kafka.bootstrap.servers", KAFKA_BOOTSTRAP_SERVERS)
          .option("subscribe", INPUT_TOPIC)
          .option("startingOffsets", "latest")
          .load())
    
    # Parse JSON data
    parsed_df = df.selectExpr("CAST(value AS STRING) as json_data")
    vehicle_df = parsed_df.select(from_json(col("json_data"), vehicle_schema).alias("data")).select("data.*")
    
    # Extract position data
    position_df = vehicle_df.select(
        col("entity_id"),
        col("vehicle.id").alias("vehicle_id"),
        col("position.latitude").alias("latitude"),
        col("position.longitude").alias("longitude"),
        col("processing_timestamp")
    )
    
    # Apply geofencing
    geofenced_df = position_df.withColumn(
        "geofence_results",
        geofence_checker(col("latitude"), col("longitude"), col("vehicle_id"))
    )
    
    # Prepare output
    output_df = geofenced_df.select(
        col("entity_id"),
        col("vehicle_id"),
        col("latitude"),
        col("longitude"),
        col("processing_timestamp"),
        col("geofence_results")
    )
    
    # Write to Kafka
    query = (output_df
             .selectExpr("CAST(vehicle_id AS STRING) AS key", "CAST(geofence_results AS STRING) AS value")
             .writeStream
             .format("kafka")
             .option("kafka.bootstrap.servers", KAFKA_BOOTSTRAP_SERVERS)
             .option("topic", OUTPUT_TOPIC)
             .option("checkpointLocation", "/tmp/checkpoint")
             .outputMode("update")
             .start())
    
    return query

def main():
    """Main function to run the geofencing processor."""
    try:
        spark = create_spark_session()
        logger.info("Starting Geofencing Processor")
        
        query = process_vehicle_positions(spark)
        query.awaitTermination()
        
    except KeyboardInterrupt:
        logger.info("Stopping Geofencing Processor")
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
    finally:
        if 'spark' in locals():
            spark.stop()
            logger.info("Spark session stopped")

if __name__ == "__main__":
    main()
