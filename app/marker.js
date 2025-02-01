import { useEffect } from "react";
import { Feature } from "ol";
import { Point } from "ol/geom";
import { fromLonLat } from "ol/proj";
import VectorLayer from "ol/layer/Vector";
import VectorSource from "ol/source/Vector";
import { Style, Circle, Fill, Stroke } from "ol/style";
import { markerData } from "./marker-data";
import { useCategory } from "./category-state";
import { getMapInstance } from "./map-manager";

//Globals
let blue = "#2f76ff"

//this component doesn't render anything directly
const MarkerLayer = () => {
  //get the shared map instance
  const map = getMapInstance();
  //get the shared state for markers
  const [activeMarker] = useCategory();

  useEffect(() => {
    //wait for the map to be ready
    if (!map) return;

    //convert coordinates to features and assign styles
    const features = markerData.map((marker) => {
      const feature = new Feature({
        geometry: new Point(fromLonLat(marker.coords)),
      });

      //decides which marker is blue
      const isActive = 
        activeMarker === "All" || 
        (marker.categories && marker.categories.includes(activeMarker));

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

    //add markers to a vector source and layer
    const vectorSource = new VectorSource({ features });
    const vectorLayer = new VectorLayer({ source: vectorSource });

    //add the layer to the map
    map.addLayer(vectorLayer);

    //cleanup on component unmount
    return () => map.removeLayer(vectorLayer);
  }, [map, activeMarker]);

  return null;
};

export default MarkerLayer;
