import React, { useEffect } from "react";
import { useDispatch } from "react-redux";
import { KeplerGl } from "kepler.gl";
import { addDataToMap } from "kepler.gl/actions";

function KeplerMap() {
  const dispatch = useDispatch();

  useEffect(() => {
    // Configure Kepler.gl with initial state
    dispatch(
      addDataToMap({
        options: {
          readOnly: false,
          centerMap: true,
          mapStyle: {
            styleType: "dark",
          },
        },
      })
    );
  }, [dispatch]);

  return (
    <div style={{ width: "100%", height: "100%" }}>
      <KeplerGl id="map" width="100%" height="100%" />
    </div>
  );
}

export default KeplerMap;
