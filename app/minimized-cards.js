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

import React from "react";
import "./minimized-cards.css";
import { useCategory } from "./category-state";
import { stores } from "./minimized-cards-data";

/**
 * MinimizedCards Component
 * 
 * Displays a list of minimized food place cards, filtering them based on selected categories.
 * 
 * @component
 * @returns {JSX.Element} The rendered minimized food place cards.
 */
const MinimizedCards = () => {
  const cards = stores;
  const [selectedCategories] = useCategory();

  /**
   * Filters cards based on selected categories.
   * If "all" is selected, all cards are displayed.
   * Otherwise, only cards matching selected categories are shown.
   */
  const filteredCards = selectedCategories.includes("all")
    ? cards
    : cards.filter((card) =>
        card.categories.some((cat) => selectedCategories.includes(cat))
      );

  return (
    <div className="MinimizedCards">
      {filteredCards.map((store, index) => (
        <div key={index} className="store_card">
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
