FROM bitnami/spark:latest

USER root

# Install system dependencies including GEOS for Shapely
RUN apt-get update && \
    apt-get install -y python3-pip libgeos-dev binutils libproj-dev gdal-bin && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .

# Install dependencies with additional flags to help with Shapely
RUN pip3 install --no-cache-dir --prefer-binary -r requirements.txt || \
    pip3 install --no-cache-dir --no-binary=:all: shapely==1.8.5 && \
    pip3 install --no-cache-dir -r requirements.txt

COPY . .

CMD ["spark-submit", "--master", "spark://spark-master:7077", "--packages", "org.apache.spark:spark-sql-kafka-0-10_2.12:3.4.1", "geofencing_processor.py"]