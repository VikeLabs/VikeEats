import React, { useRef, useEffect } from "react";
import "./minimized-cards.css";
import { useCategory } from "./category-state";
import { stores } from "./minimized-cards-data";
import { getMapInstance } from "./map-manager";
import { fromLonLat } from "ol/proj";
import { markerData } from "./marker-data";

/**
 * MinimizedCards Component
 * 
 * Renders a list of food outlet cards with an interactive map zoom feature.
 * 
 * Key Features:
 * - Filters cards based on selected categories
 * - Enables smooth map navigation when cards are clicked
 * - Provides a one-time zoom-in effect on the first card click
 * - Resets zoom behavior after double-clicking to zoom out
 * - Maintains a consistent zoomed-in view for subsequent card selections
 * 
 * Interaction Behavior:
 * 1. First card click: Zooms in significantly to the selected location
 * 2. Subsequent card clicks: Centers the map on the selected location
 * 3. Double-click to zoom out resets the zoom state
 * 
 * @component
 * @returns {JSX.Element} Rendered minimized food outlet cards
 */
const MinimizedCards = () => {
  // Retrieve stores and selected categories
  const cards = stores;
  const [selectedCategories] = useCategory();

  // Refs to track zoom state and initial zoom level
  const hasZoomedRef = useRef(false);
  const initialZoomRef = useRef(null);

  // Filter cards based on selected categories
  const filteredCards = selectedCategories.includes("all")
    ? cards
    : cards.filter((card) =>
        card.categories.some((cat) => selectedCategories.includes(cat))
      );

  useEffect(() => {
    const map = getMapInstance();
    if (!map) return;

    // Detect double-click to reset zoom state
    const handleDoubleClick = () => {
      hasZoomedRef.current = false;
      initialZoomRef.current = null;
    };

    map.getViewport().addEventListener('dblclick', handleDoubleClick);

    // Cleanup
    return () => {
      map.getViewport().removeEventListener('dblclick', handleDoubleClick);
    };
  }, []);

  /**
   * Handles card click event to update map view
   * 
   * @param {Object} store - The selected store/card data
   */
  const handleCardClick = (store) => {
    const map = getMapInstance();
    if (!map) return;

    // Find the corresponding marker for the selected store
    const matchingMarker = markerData.find(marker => marker.id === store.id);

    if (matchingMarker) {
      const currentZoom = map.getView().getZoom();
      
      // First-time zoom behavior
      if (!hasZoomedRef.current) {
        // Store the initial zoom level
        initialZoomRef.current = currentZoom;
        
        // Calculate target zoom: 3 levels closer, max 18
        const targetZoom = Math.min(initialZoomRef.current + 3, 18);
        
        // Animate center and zoom in one smooth motion
        map.getView().animate({
          center: fromLonLat(matchingMarker.coords),
          zoom: targetZoom,
          duration: 1000
        });

        hasZoomedRef.current = true;
      } else {
        // Subsequent clicks: just center the map
        map.getView().animate({
          center: fromLonLat(matchingMarker.coords),
          duration: 600
        });
      }
    }
  };

  return (
    <div className="MinimizedCards">
      {filteredCards.map((store, index) => (
        <div 
          key={index} 
          className="store_card" 
          onClick={() => handleCardClick(store)}
          style={{ cursor: 'pointer' }}
        >
          <div className="store_info">
            <h2 className="store_title">{store.name}</h2>
            <p className="store_time">{store.time}</p>
          </div>
          <img src={store.image} alt={store.name} className="store_image" />
        </div>
      ))}
    </div>
  );
};

export default MinimizedCards;