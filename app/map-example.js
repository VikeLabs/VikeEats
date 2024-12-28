import React, { useRef, useState } from "react";
import MarkerLayer from "./marker";
import FilterButtons from "./first-level-filter";
import MapLayer from "./map";

//bundles all the map related components
//just an example used as a parent component to pass some variables
const MapExample = () => {
  //reference to map object for ol
  //used for base map layer and markers layer
  const mapRef = useRef(null);

  //state for the active markers
  //contains a string of the category selected in the FilterButtons component
  //Ex. "canada" or "america" or "europe"
  const [activeMarker, setActiveMarker] = useState(null);

  return (
    <div>
      <FilterButtons
        activeMarker={activeMarker}
        setActiveMarker={setActiveMarker}
      />
      <MapLayer ref={mapRef} />
      <MarkerLayer map={mapRef.current} activeMarker={activeMarker} />
    </div>
  );
};

export default MapExample;
