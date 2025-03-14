import { Map, View } from "ol";
import TileLayer from "ol/layer/Tile";
import OSM from "ol/source/OSM";
import { fromLonLat } from "ol/proj";
import { defaults as defaultInteractions } from 'ol/interaction';
import DoubleClickZoom from 'ol/interaction/DoubleClickZoom';
import { UVIC_COORDINATES, MAP_ZOOM_LEVEL } from './config';

// Globals
let mapInstance = null;

/**
 * Retrieves or creates a singleton OpenLayers map instance.
 * Disables default double-click zoom but adds custom double-click handler for zooming out.
 *
 * @param {string|HTMLElement|null} target - The DOM element ID or reference where the map should be rendered.
 * @returns {Map|null} The OpenLayers map instance, or null if executed in a non-browser environment.
 */
export const getMapInstance = (target) => {
  if (typeof window === "undefined") {
    console.error("getMapInstance cannot be executed in a non-browser environment.");
    return null;
  }

  if (!mapInstance) {
    // Get default interactions but exclude double-click zoom
    const interactions = defaultInteractions({
      doubleClickZoom: false // Disable the default double-click zoom
    });

    // Create the map instance if it doesn't exist
    mapInstance = new Map({
      layers: [
        new TileLayer({
          source: new OSM(),
        }),
      ],
      view: new View({
        center: fromLonLat(UVIC_COORDINATES),
        zoom: MAP_ZOOM_LEVEL,
      }),
      interactions: interactions
    });
    
    // Add custom double-click handler to zoom out
    mapInstance.on('dblclick', (event) => {
      event.preventDefault();
      
      const view = mapInstance.getView();
      const currentZoom = view.getZoom();
      const currentCenter = view.getCenter();
      
      // For zooming: MAP_ZOOM_LEVEL is the minimum zoom level. 
      // currentZoom - 2 = zoom out 2 levels
      // Overall, the zoom will be the highest between the minimum or the currentZoom zoomed out by 2
      const targetZoom = Math.max(MAP_ZOOM_LEVEL, currentZoom - 2);
      
      // Animate zoom out effect
      view.animate({
        center: currentCenter,
        zoom: targetZoom,
        duration: 1000 // Smooth animation - happens over 1 second (1000ms)
      });
    });
  }

  // Update the target if provided
  if (target) {
    mapInstance.setTarget(target);
  }

  return mapInstance;
};