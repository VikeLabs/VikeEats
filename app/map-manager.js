/**
 * map-manager.js
 * 
 * This module provides a singleton OpenLayers map instance centered on the University of Victoria.
 * It ensures only one map instance is created and shared across OpenLayers-related components.
 *
 * Features:
 * - Initializes a map with OpenStreetMap (OSM) as the base layer.
 * - Centers the map at UVic's coordinates.
 * - Provides a function to retrieve or create the map instance.
 * - Allows updating the target container dynamically.
 */

import { Map, View } from "ol";
import TileLayer from "ol/layer/Tile";
import OSM from "ol/source/OSM";
import { fromLonLat } from "ol/proj";

// Singleton map instance
let mapInstance = null;

/**
 * Retrieves or creates a singleton OpenLayers map instance.
 * This function should be used by all OpenLayers-related components to ensure a single map instance.
 *
 * @param {string|HTMLElement|null} target - The DOM element ID or reference where the map should be rendered.
 * @returns {Map|null} The OpenLayers map instance, or null if executed in a non-browser environment.
 */
export const getMapInstance = (target) => {
  // Prevent execution in non-browser environments
  if (typeof window === "undefined") {
    return null;
  }

  if (!mapInstance) {
    // Create the map instance if it doesn't exist
    mapInstance = new Map({
      layers: [
        new TileLayer({
          source: new OSM(),
        }),
      ],
      view: new View({
        center: fromLonLat([-123.31219, 48.46319]), // UVic coordinates
        zoom: 16,
      }),
    });
  }

  // Update the target if provided
  if (target) {
    mapInstance.setTarget(target);
  }

  return mapInstance;
};