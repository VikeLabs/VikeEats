import React, { useEffect, useRef } from 'react';
import 'ol/ol.css';
import { Map, View } from 'ol';
import TileLayer from 'ol/layer/Tile';
import OSM from 'ol/source/OSM';

const MapLayer = React.forwardRef((props, ref) => {
  const mapElement = useRef();

  useEffect(() => {
    // Create the map
    const map = new Map({
      target: mapElement.current,
      layers: [
        new TileLayer({
          source: new OSM(),
        }),
      ],
      view: new View({
        center: [0, 0],
        zoom: 2,
      }),
    });

    if (ref) {
      //updates map for parent component
      ref.current = map;
    }

    return () => map.setTarget(null); //cleanup on unmount
  }, []);

  return (
    <div
      ref={mapElement}
      style={{
        width: '100%',
        height: '400px',
        border: '1px solid black',
      }}
    ></div>
  );
});

export default MapLayer;
