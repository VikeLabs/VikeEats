import { Map, View } from "ol";
import TileLayer from "ol/layer/Tile";
import OSM from "ol/source/OSM";
import { fromLonLat } from "ol/proj";

let mapInstance = null;

//creates map instance for UVIC map
//call this function for OL related components
export const getMapInstance = (target) => {
  //prevent execution in non-browser environments
  if (typeof window === "undefined") {
    return null;
  }

  if (!mapInstance) {
    //create the map instance if it doesn't exist
    mapInstance = new Map({
      layers: [
        new TileLayer({
          source: new OSM(),
        }),
      ],
      view: new View({
        center: fromLonLat([-123.31219, 48.46319]),
        zoom: 16,
      }),
    });
  }

  //update the target if provided
  if (target) {
    mapInstance.setTarget(target);
  }

  return mapInstance;
};
