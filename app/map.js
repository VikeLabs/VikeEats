/**
 * map.js
 * 
 * This component renders an OpenLayers map using the `getMapInstance` function from `map-manager.js`.
 * It ensures that a single map instance is created and maintained across components.
 *
 * Features:
 * - Uses `useRef` to store a reference to the map container.
 * - Initializes and attaches the OpenLayers map on mount.
 * - Provides a forwarded ref for external manipulation of the map instance.
 * - Cleans up the map target on unmount to prevent memory leaks.
 */

import React, { useEffect, useRef } from 'react';
import 'ol/ol.css';
import { getMapInstance } from './map-manager';

/**
 * MapLayer Component
 * 
 * Renders an OpenLayers map inside a full-screen div. 
 * Uses a forwarded ref to provide access to the map instance.
 * 
 * @component
 * @param {object} props - React component props.
 * @param {React.Ref} ref - Forwarded ref to access the map instance externally.
 * @returns {JSX.Element} The map container element.
 */
const MapLayer = React.forwardRef((props, ref) => {
  const mapElement = useRef();

  useEffect(() => {
    // Create the map using function in map-manager.js
    const map = getMapInstance(mapElement.current);

    if (ref) {
      // Updates ref with the map instance
      ref.current = map;
    }

    // Cleanup function to remove the target reference when component unmounts
    return () => map.setTarget(null);
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
