/**
 * map-manager.js
 *
 * This module provides a singleton OpenLayers map instance centered on the University of Victoria.
 * It ensures only one map instance is created and shared across OpenLayers-related components.
 *
 * Features:
 * - Initializes a map with CARTO Positron (light base + labels overlay) for a calmer map while
 *   keeping street and POI names (including many restaurants) from OpenStreetMap-derived tiles.
 * - Centers the map at UVic's coordinates.
 * - Provides a function to retrieve or create the map instance.
 * - Allows updating the target container dynamically.
 */

import { Map, View } from "ol";
import TileLayer from "ol/layer/Tile";
import XYZ from "ol/source/XYZ";
import { fromLonLat } from "ol/proj";
import { UVIC_COORDINATES, MAP_ZOOM_LEVEL } from "./config";

/** @see https://github.com/CartoDB/basemap-styles */
const CARTO_ATTRIBUTION =
  '© <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors © <a href="https://carto.com/attributions">CARTO</a>';

const CARTO_SUBDOMAIN_URL =
  "https://{a-d}.basemaps.cartocdn.com";

function createPositronBaseLayer() {
  return new TileLayer({
    source: new XYZ({
      url: `${CARTO_SUBDOMAIN_URL}/rastertiles/voyager_nolabels/{z}/{x}/{y}.png`,
      attributions: CARTO_ATTRIBUTION,
      maxZoom: 20,
      crossOrigin: "anonymous",
    }),
  });
}

/** Renders text and POI symbols only; stack above base, below vector markers. */
function createPositronLabelsLayer() {
  return new TileLayer({
    source: new XYZ({
      url: `${CARTO_SUBDOMAIN_URL}/rastertiles/voyager_only_labels/{z}/{x}/{y}.png`,
      maxZoom: 20,
      crossOrigin: "anonymous",
    }),
  });
}

//Globals
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
    console.error("getMapInstance cannot be executed in a non-browser environment.");
    return null;
  }

  if (!mapInstance) {
    mapInstance = new Map({
      layers: [createPositronBaseLayer(), createPositronLabelsLayer()],
      view: new View({
        center: fromLonLat(UVIC_COORDINATES),
        zoom: MAP_ZOOM_LEVEL,
      }),
    });
  }

  if (target) {
    mapInstance.setTarget(target);
  }

  return mapInstance;
};
