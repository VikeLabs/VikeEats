/**
 * minimized-cards.js
 *
 * This component renders a minimized card view of available food places.
 * It filters displayed cards based on selected categories from `category-state.js`.
 *
 * Features:
 * - Uses the `useCategory` hook for dynamic category filtering.
 * - Displays food place name, hours, and an image.
 * - Automatically updates when category selections change.
 */

import React, { useEffect, useRef } from "react";
import "./minimized-cards.css";
import { useCategory } from "./category-state";
import { getMapInstance } from "./map-manager";
import { fromLonLat } from "ol/proj";

/**
 * MinimizedCards Component
 *
 * Displays a list of minimized food place cards, filtering them based on selected categories.
 *
 * @component
 * @returns {JSX.Element} The rendered minimized food place cards.
 */
const MinimizedCards = ({ stores = [], onCardClick }) => {
  const [selectedCategories] = useCategory();
  const hasZoomedRef = useRef(false);
  const initialZoomRef = useRef(null);

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
   * Handles card click event to update map view and set the selected store.
   * 
   * @param {Object} store - The selected store/card data
   */
  const handleInternalCardClick = (store) => {
    const map = getMapInstance();
    if (map && store.coords) {
      const currentZoom = map.getView().getZoom();
      
      // First-time zoom behavior
      if (!hasZoomedRef.current) {
        // Store the initial zoom level
        initialZoomRef.current = currentZoom;
        
        // Calculate target zoom: 3 levels closer, max 18
        const targetZoom = Math.min(initialZoomRef.current + 3, 18);
        
        // Animate center and zoom in one smooth motion
        map.getView().animate({
          center: fromLonLat(store.coords),
          zoom: targetZoom,
          duration: 1000
        });

        hasZoomedRef.current = true;
      } else {
        // Subsequent clicks: just center the map
        map.getView().animate({
          center: fromLonLat(store.coords),
          duration: 600
        });
      }
    }
    
    // Call the external onCardClick
    if (onCardClick) {
      onCardClick(store);
    }
  };

  /**
   * Filters cards based on selected categories.
   * If "all" is selected, all cards are displayed.
   * Otherwise, only cards matching selected categories are shown.
   */
  const filteredCards = selectedCategories.includes("all")
    ? stores
    : stores.filter((card) =>
        card.categories && card.categories.some((cat) => selectedCategories.includes(cat))
      );

  return (
    <div className="MinimizedCards">
      {filteredCards.map((store, index) => (
        <div
          key={index}
          className="store_card"
          onClick={() => handleInternalCardClick(store)}
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
