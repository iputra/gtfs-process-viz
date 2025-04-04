import React, { useState, useEffect } from "react";
import { useDispatch } from "react-redux";
import { addDataToMap } from "kepler.gl/actions";
import { processCsvData } from "kepler.gl/processors";
import KeplerMap from "./components/KeplerMap";
import ControlPanel from "./components/ControlPanel";
import { connectToSocket } from "./services/socketService";
import { processVehicleData } from "./utils/dataProcessor";

function App() {
  const dispatch = useDispatch();
  const [vehicleData, setVehicleData] = useState([]);
  const [geofenceEvents, setGeofenceEvents] = useState([]);
  const [isConnected, setIsConnected] = useState(false);

  useEffect(() => {
    // Load initial geofence data
    fetch("/api/geofences")
      .then((response) => response.json())
      .then((data) => {
        const geofenceData = {
          fields: [
            { name: "id", format: "", type: "string" },
            { name: "name", format: "", type: "string" },
            { name: "coordinates", format: "", type: "geojson" },
          ],
          rows: data.map((geofence) => [
            geofence.id,
            geofence.name,
            {
              type: "Polygon",
              coordinates: [geofence.coordinates],
            },
          ]),
        };

        // Add geofence data to map
        dispatch(
          addDataToMap({
            datasets: [
              {
                info: {
                  label: "Geofences",
                  id: "geofences",
                },
                data: geofenceData,
              },
            ],
            options: {
              centerMap: true,
            },
          })
        );
      })
      .catch((error) => console.error("Error loading geofences:", error));

    // Connect to WebSocket for real-time updates
    const socket = connectToSocket();

    socket.on("connect", () => {
      console.log("Connected to WebSocket");
      setIsConnected(true);
    });

    socket.on("disconnect", () => {
      console.log("Disconnected from WebSocket");
      setIsConnected(false);
    });

    socket.on("vehicle_positions", (data) => {
      const processedData = processVehicleData(data);
      setVehicleData((prevData) => {
        // Update existing vehicles or add new ones
        const updatedData = [...prevData];
        processedData.forEach((vehicle) => {
          const index = updatedData.findIndex((v) => v.id === vehicle.id);
          if (index >= 0) {
            updatedData[index] = vehicle;
          } else {
            updatedData.push(vehicle);
          }
        });
        return updatedData;
      });

      // Add vehicle data to map
      const vehicleDataset = {
        fields: [
          { name: "id", format: "", type: "string" },
          { name: "latitude", format: "", type: "real" },
          { name: "longitude", format: "", type: "real" },
          { name: "timestamp", format: "", type: "timestamp" },
        ],
        rows: processedData.map((vehicle) => [
          vehicle.id,
          vehicle.latitude,
          vehicle.longitude,
          vehicle.timestamp,
        ]),
      };

      dispatch(
        addDataToMap({
          datasets: [
            {
              info: {
                label: "Vehicles",
                id: "vehicles",
              },
              data: vehicleDataset,
            },
          ],
          options: {
            centerMap: false,
          },
        })
      );
    });

    socket.on("geofence_events", (data) => {
      setGeofenceEvents((prevEvents) => [...prevEvents, ...data]);
    });

    return () => {
      socket.disconnect();
    };
  }, [dispatch]);

  return (
    <div className="app">
      <KeplerMap />
      <ControlPanel
        isConnected={isConnected}
        vehicleCount={vehicleData.length}
        geofenceEvents={geofenceEvents}
      />
    </div>
  );
}

export default App;
