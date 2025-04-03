/**
 * category-state.js
 * 
 * This module manages the category selection state across multiple components.
 * It provides a global-like state using the `useCategory` hook, allowing components
 * to subscribe to category changes and update selections accordingly.
 *
 * Features:
 * - Uses React state and effect to manage category selection.
 * - Supports toggling categories dynamically.
 * - Notifies all subscribed components when the selection changes.
 */

import { useState, useEffect } from "react";

// Global category state and listeners
let selectedCategories = ["all"];
let listeners = [];

/**
 * Custom hook to manage category selection.
 * 
 * @returns {[string[], function]} The current category state and a function to toggle categories.
 */
export const useCategory = () => {
  const [state, setState] = useState(selectedCategories);

  /**
   * Effect hook to subscribe to category changes and update state.
   * Ensures component re-renders when the category selection updates.
   */
  useEffect(() => {
    const listener = (newCategories) => setState(newCategories);
    listeners.push(listener);
    
    // Cleanup function to remove listener when component unmounts
    return () => {
      listeners = listeners.filter((l) => l !== listener);
    };
  }, []);

  /**
   * Toggles a category selection.
   * Special logic:
   * - When a non-"all" category is selected, the "all" filter is automatically deselected.
   * - When the "all" category is selected, all other filters are deselected.
   * - If toggling a non-"all" category results in no filters being selected, defaults back to "all".
   * 
   * @param {string|null} newCategory - The category to toggle, or null to clear selection.
   */
  const toggleCategory = (newCategory) => {
    if (newCategory === null) {
      // Reset selection to default: "all"
      selectedCategories = ["all"];
      listeners.forEach((listener) => listener(selectedCategories));
      return;
    }

    if (newCategory === "all") {
      // When "all" is selected, deselect all other filters.
      selectedCategories = ["all"];
      listeners.forEach((listener) => listener(selectedCategories));
      return;
    }

    // For non-"all" categories, first remove "all" if it's currently selected.
    let updated = selectedCategories.filter(cat => cat !== "all");

    // Toggle the newCategory
    if (updated.includes(newCategory)) {
      updated = updated.filter(cat => cat !== newCategory);
    } else {
      updated.push(newCategory);
    }

    // If no non-"all" category remains selected, default back to "all"
    if (updated.length === 0) {
      updated = ["all"];
    }

    // Update the global state and notify all listeners.
    selectedCategories = updated;
    listeners.forEach((listener) => listener(updated));
  };

  return [state, toggleCategory];
};
