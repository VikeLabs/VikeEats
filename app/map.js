import React, { useEffect, useRef } from 'react';
import 'ol/ol.css';
import { getMapInstance } from './map-manager';

const MapLayer = React.forwardRef((props, ref) => {
  const mapElement = useRef();

  useEffect(() => {
    //create the map using function in map-manager.js
    const map = getMapInstance(mapElement.current);

    if (ref) {
      //updates map
      ref.current = map;
    }

    return () => map.setTarget(null); //cleanup on unmount
  }, []);

  return (
    <div
      ref={mapElement}
      style={{
        position: 'absolute',
        top: 0,
        left: 0,
        width: '100%',
        height: '100%',
      }}
    ></div>
  );
});

export default MapLayer;
