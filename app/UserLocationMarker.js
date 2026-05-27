/**
 * UserLocationMarker.js
 *
 * Retrieves the user's current location and draws a distinct “you are here” marker:
 * soft accuracy disk + navy inner dot (not the same grammar as food outlet pins/labels).
 */

import { useEffect } from "react";
import { getMapInstance } from "./map-manager";
import Feature from "ol/Feature";
import Point from "ol/geom/Point";
import { fromLonLat } from "ol/proj";
import VectorLayer from "ol/layer/Vector";
import VectorSource from "ol/source/Vector";
import { Style, Circle, Fill, Stroke } from "ol/style";

/** tailwind: secondary #005493, accent-blue #57B7E7 */
const USER = {
  accuracyFill: "rgba(87, 183, 231, 0.2)",
  accuracyStroke: "rgba(0, 84, 147, 0.35)",
  dotFill: "#005493",
  dotRing: "#ffffff",
};

function createUserLocationStyle() {
  return [
    new Style({
      image: new Circle({
        radius: 24,
        fill: new Fill({ color: USER.accuracyFill }),
        stroke: new Stroke({ color: USER.accuracyStroke, width: 1.5 }),
      }),
    }),
    new Style({
      image: new Circle({
        radius: 8,
        fill: new Fill({ color: USER.dotFill }),
        stroke: new Stroke({ color: USER.dotRing, width: 2.5 }),
      }),
    }),
  ];
}

/**
 * @returns {null}
 */
const UserLocationMarker = () => {
  useEffect(() => {
    const map = getMapInstance();
    let vectorLayer = null;
    let cancelled = false;

    if (!navigator.geolocation) {
      console.error("Geolocation is not supported by this browser.");
      return undefined;
    }

    navigator.geolocation.getCurrentPosition(
      (position) => {
        if (cancelled || !map) return;

        const { latitude, longitude } = position.coords;
        const coordinates = fromLonLat([longitude, latitude]);

        const userFeature = new Feature({
          geometry: new Point(coordinates),
        });
        userFeature.setStyle(createUserLocationStyle());

        const vectorSource = new VectorSource({
          features: [userFeature],
        });
        vectorLayer = new VectorLayer({
          source: vectorSource,
          zIndex: 200,
        });

        map.addLayer(vectorLayer);

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

    return () => {
      cancelled = true;
      if (vectorLayer && map) {
        map.removeLayer(vectorLayer);
      }
    };
  }, []);

  return null;
};

export default UserLocationMarker;
