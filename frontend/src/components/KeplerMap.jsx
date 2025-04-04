import React, { useEffect } from "react";
import { useDispatch } from "react-redux";
import KeplerGl from "kepler.gl";
import { addDataToMap, updateMap } from "kepler.gl/actions";

function KeplerMap() {
  const dispatch = useDispatch();

  useEffect(() => {
    // Configure Kepler.gl to use OpenStreetMap
    dispatch(
      updateMap({
        mapStyle: {
          styleType: "open-street-map",
        },
      })
    );
  }, [dispatch]);

  return (
    <div style={{ width: "100%", height: "100%" }}>
      <KeplerGl
        id="map"
        width="100%"
        height="100%"
        mapboxApiAccessToken="" // Empty token to force OSM usage
      />
    </div>
  );
}

export default KeplerMap;
