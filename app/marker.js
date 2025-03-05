/**
 * marker.js
 * 
 * This module defines a MarkerLayer component that dynamically adds markers to the OpenLayers map.
 * It subscribes to category selection state and updates marker styles based on selected categories.
 *
 * Features:
 * - Uses shared map instance from `map-manager.js`.
 * - Fetches marker data from `marker-data.js`.
 * - Updates marker visibility and style dynamically based on selected categories.
 * - Cleans up by removing the marker layer when unmounted.
 */

import { useEffect } from "react";
import { Feature } from "ol";
import { Point } from "ol/geom";
import { fromLonLat } from "ol/proj";
import VectorLayer from "ol/layer/Vector";
import VectorSource from "ol/source/Vector";
import { Style, Circle, Fill } from "ol/style";
import { markerData } from "./marker-data";
import { useCategory } from "./category-state";
import { getMapInstance } from "./map-manager";

//Globals
let blue = "#2f76ff";

/**
 * MarkerLayer Component
 * 
 * This component manages marker placement on the map.
 * It does not render anything directly but updates the OpenLayers map instance.
 * 
 * @component
 * @returns {null} Does not return JSX since it only interacts with OpenLayers.
 */
const MarkerLayer = () => {
  // Get the shared map instance
  const map = getMapInstance();
  // Get the selected categories from state
  const [selectedCategories] = useCategory();

  useEffect(() => {
    // Wait for the map to be ready
    if (!map) return;

    // Convert marker data to features and apply styles
    const features = markerData.map((marker) => {
      const feature = new Feature({
        geometry: new Point(fromLonLat(marker.coords)),
      });

      // Determine if the marker should be active (blue) or inactive (grey)
      const isActive =
        selectedCategories.includes("all") ||
        (marker.categories &&
          marker.categories.some((cat) => selectedCategories.includes(cat)));

      feature.setStyle(
        new Style({
          image: new Circle({
            radius: 8,
            fill: new Fill({ color: isActive ? blue : "grey" }),
          }),
        })
      );

      return feature;
    });

    // Create a vector source and layer for markers
    const vectorSource = new VectorSource({ features });
    const vectorLayer = new VectorLayer({ source: vectorSource });

    // Add the layer to the map
    map.addLayer(vectorLayer);

    // Cleanup: Remove the marker layer when component unmounts
    return () => map.removeLayer(vectorLayer);
  }, [map, selectedCategories]);

  return null;
};

export default MarkerLayer;
