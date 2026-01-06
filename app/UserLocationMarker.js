/**
 * UserLocationMarker.js
 * 
 * This component retrieves the user's current location using the browser's geolocation API
 * and displays a marker on the shared OpenLayers map instance.
 *
 * Features:
 * - Requests geolocation permissions from the user.
 * - Creates a new vector layer to render the user location marker.
 * - Uses an OpenLayers Icon style to display the marker.
 * - Animates the map view to center on the user's location.
 */

import { useEffect } from "react";
import { getMapInstance } from "./map-manager";
import Feature from "ol/Feature";
import Point from "ol/geom/Point";
import { fromLonLat } from "ol/proj";
import VectorLayer from "ol/layer/Vector";
import VectorSource from "ol/source/Vector";
import { Style, Circle, Fill } from "ol/style";

/**
 * UserLocationMarker Component
 * 
 * Retrieves the user's geolocation and adds a marker to the map.
 *
 * @component
 * @returns {null} This component does not render any visible DOM elements.
 */
const UserLocationMarker = () => {
  useEffect(() => {
    const map = getMapInstance();
    let vectorLayer = null;

    if (!navigator.geolocation) {
      console.error("Geolocation is not supported by this browser.");
      return;
    }

    // Request the user's geolocation with high accuracy enabled.
    navigator.geolocation.getCurrentPosition(
      (position) => {
        const { latitude, longitude } = position.coords;
        const coordinates = fromLonLat([longitude, latitude]);

        // Create a feature for the user location marker
        const userFeature = new Feature({
          geometry: new Point(coordinates),
        });

        // Set the style for the marker (update the icon path as needed)
        userFeature.setStyle(
          new Style({
            image: new Circle({
                radius: 8,
                fill: new Fill({ color: "black" }),
              }),
          })
        );

        // Create a vector source and layer for the marker
        const vectorSource = new VectorSource({
          features: [userFeature],
        });
        vectorLayer = new VectorLayer({
          source: vectorSource,
        });

        // Add the vector layer (with the user marker) to the map
        map.addLayer(vectorLayer);

        // Animate the map view to center on the user’s location
        map.getView().animate({
          center: coordinates,
          duration: 1000,
        });
      },
      (error) => {
        console.error("Error obtaining geolocation:", error);
      },
      { enableHighAccuracy: true }
    );

    // Cleanup: remove the vector layer when this component unmounts
    return () => {
      if (vectorLayer) {
        map.removeLayer(vectorLayer);
      }
    };
  }, []);

  // This component does not render any DOM elements.
  return null;
};

export default UserLocationMarker;
