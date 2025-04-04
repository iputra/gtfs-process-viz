/**
 * Process vehicle data from the WebSocket
 * @param {Array} data - Array of vehicle position data
 * @returns {Array} - Processed vehicle data
 */
export const processVehicleData = (data) => {
  return data.map(vehicle => ({
    id: vehicle.vehicle?.id || vehicle.entity_id,
    latitude: vehicle.position?.latitude,
    longitude: vehicle.position?.longitude,
    speed: vehicle.position?.speed,
    bearing: vehicle.position?.bearing,
    timestamp: vehicle.timestamp || Date.now(),
    // Add any additional processing here
  }));
};

/**
 * Process geofence event data
 * @param {Array} data - Array of geofence event data
 * @returns {Array} - Processed geofence event data
 */
export const processGeofenceEvents = (data) => {
  return data.map(event => ({
    ...event,
    timestamp: event.timestamp || Date.now(),
  }));
};
