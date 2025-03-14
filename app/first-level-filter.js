/**
 * first-level-filter.js
 * 
 * This component provides a set of filter buttons to allow users to toggle category selections.
 * It utilizes the `useCategory` hook to manage selected categories across multiple components.
 *
 * Features:
 * - Displays a list of predefined category buttons.
 * - Allows toggling of category selection.
 * - Provides a "clear" button to reset selections.
 * - Updates UI based on selected categories.
 */

import React from "react";
import "./first-level-filter.css";
import { useCategory } from "./category-state";

/**
 * FilterButtons Component
 * 
 * Renders a set of filter buttons that allow users to select and toggle categories.
 *
 * @component
 * @returns {JSX.Element} The rendered filter button UI.
 */
const FilterButtons = () => {
  // Retrieve selected categories and function to toggle them
  const [selectedCategories, toggleCategory] = useCategory();

  // List of available category filters
  const categories = [
    "all",
    "filter1",
    "filter2",
    "filter3",
    "filter4",
    "filter5",
  ];

  /**
   * Handles button clicks to toggle category selection.
   * 
   * @param {string|null} category - The category to toggle, or null to clear all selections.
   */
  const handleButtonClick = (category) => {
    toggleCategory(category);
    console.log("Toggled category:", category);
    console.log("Now selected:", selectedCategories);
  };

  return (
    <div>
      <div className="filter-buttons">
        {/* Render category buttons dynamically */}
        {categories.map((category) => (
          <button
            key={category}
            className={`filter-button ${
              selectedCategories.includes(category) ? "active" : "inactive"
            }`}
            onClick={() => handleButtonClick(category)}
          >
            {category}
          </button>
        ))}
        
        {/* Clear selection button */}
        <button
          key="clear"
          className="filter-button inactive"
          onClick={() => handleButtonClick(null)}
        >
          clear
        </button>
      </div>
      
      {/* Display selected categories */}
      <div>
        <p>Selected Categories: {selectedCategories.join(", ")}</p>
      </div>
    </div>
  );
};

export default FilterButtons;