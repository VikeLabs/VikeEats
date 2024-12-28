import { useEffect } from 'react';
import { Feature } from 'ol';
import { Point } from 'ol/geom';
import { fromLonLat } from 'ol/proj';
import VectorLayer from 'ol/layer/Vector';
import VectorSource from 'ol/source/Vector';
import { Style, Circle, Fill, Stroke } from 'ol/style';

//this component doesn't render anything directly
const MarkerLayer = ({ map, activeMarker }) => {
  useEffect(() => {
    //wait for the map to be ready
    if (!map) return;

    const markers = [
      { id: 1, category: "canada", coords: [-123.1216, 49.2827] }, // Vancouver
      { id: 2, category: "america", coords: [-122.3321, 47.6062] }, // Seattle
      { id: 3, category: "america", coords: [-73.9352, 40.7306] },  // New York
      { id: 4, category: "europe", coords: [-0.1276, 51.5074] },   // London
      { id: 5, category: "europe", coords: [2.3522, 48.8566] },    // Paris
    ];

    //convert coordinates to features and assign styles
    const features = markers.map((marker) => {
      const feature = new Feature({
        geometry: new Point(fromLonLat(marker.coords)),
      });

      const isActive = marker.category === activeMarker;
      feature.setStyle(
        new Style({
          image: new Circle({
            radius: 8,
            fill: new Fill({ color: isActive ? 'blue' : 'grey' }),
            stroke: new Stroke({ color: '#000', width: 1 }),
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
