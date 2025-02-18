import { useState, useEffect } from "react";

let selectedCategories = ["all"];
let listeners = [];

export const useCategory = () => {
  const [state, setState] = useState(selectedCategories);

  useEffect(() => {
    const listener = (newCategories) => setState(newCategories);
    listeners.push(listener);
    return () => {
      listeners = listeners.filter((l) => l !== listener);
    };
  }, []);

  const toggleCategory = (newCategory) => {
    if (newCategory === null) {
      // Clear all selections
      selectedCategories = [];
      listeners.forEach((listener) => listener([]));
      return;
    }
    const updated = selectedCategories.includes(newCategory)
      ? selectedCategories.filter((cat) => cat !== newCategory)
      : [...selectedCategories, newCategory];

    selectedCategories = updated;
    listeners.forEach((listener) => listener(updated));
  };

  return [state, toggleCategory];
};
