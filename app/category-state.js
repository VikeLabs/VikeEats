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
   * If `newCategory` is null, it clears all selections.
   * 
   * @param {string|null} newCategory - The category to toggle, or null to clear selection.
   */
  const toggleCategory = (newCategory) => {
    if (newCategory === null) {
      // Clear all selections
      selectedCategories = [];
      listeners.forEach((listener) => listener([]));
      return;
    }

    // Toggle category selection
    const updated = selectedCategories.includes(newCategory)
      ? selectedCategories.filter((cat) => cat !== newCategory)
      : [...selectedCategories, newCategory];

    // Update global state and notify listeners
    selectedCategories = updated;
    listeners.forEach((listener) => listener(updated));
  };

  return [state, toggleCategory];
};
