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

// Globals
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
    if (!map) return;

    // Convert marker data to features and apply styles
    const features = markerData.map((marker) => {
      const feature = new Feature({
        geometry: new Point(fromLonLat(marker.coords)), // Convert coords once here
        markerData: marker, // Store marker data for reference
      });

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

    // Create vector source and layer
    const vectorSource = new VectorSource({ features });
    const vectorLayer = new VectorLayer({ 
      source: vectorSource,
      zIndex: 10 // Ensure markers are on top
    });

    // Add the layer to the map
    map.addLayer(vectorLayer);

    // Define click handler function that will prevent default behavior
    const handleMarkerClick = (event) => {
      let markerClicked = false;
      
      map.forEachFeatureAtPixel(event.pixel, (feature) => {
        const marker = feature.get("markerData");
        if (marker) {
          // Prevent the event from propagating to the map
          event.preventDefault();
          event.stopPropagation();
          markerClicked = true;
          
          // Get current zoom level
          const currentZoom = map.getView().getZoom();
          
          // Calculate target zoom level - ensure it's higher than current zoom
          // Target zoom 16 for a good detail level, or current zoom + 2 if already zoomed in
          const targetZoom = Math.max(16, currentZoom + 2);
          
          // First center on the marker without changing zoom
          map.getView().animate({
            center: fromLonLat(marker.coords),
            duration: 600, // Smooth centering
          });
          
          // Then zoom in after a short delay to ensure smooth transition
          setTimeout(() => {
            map.getView().animate({
              zoom: targetZoom,
              duration: 1000, // Longer duration for smoother zoom
            });
          }, 100);
          
          return true; // Stop iterating through features
        }
        return false;
      });
      
      if (markerClicked) {
        // Return false to prevent default map click behavior
        return false;
      }
    };

    // Add click event listener for markers 
    // Use the 'singleclick' event to better differentiate from double-clicks
    map.on("singleclick", handleMarkerClick);

    // Cleanup: Remove layer and event listener on unmount
    return () => {
      map.removeLayer(vectorLayer);
      map.un("singleclick", handleMarkerClick); // Remove specific listener
    };
  }, [map, selectedCategories]);

  return null;
};

// Make sure to export as DEFAULT
export default MarkerLayer;