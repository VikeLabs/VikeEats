import { useState, useEffect } from "react";

//default set to all to show all store cards
let selectedCategory = "All";
let listeners = [];

//sets up useState for selectedCategory and setSelectedCategory
export const useCategory = () => {
  const [state, setState] = useState(selectedCategory);

  useEffect(() => {
    const listener = (newCategory) => setState(newCategory);
    listeners.push(listener);

    return () => {
      listeners = listeners.filter((l) => l !== listener);
    };
  }, []);

  const setCategory = (newCategory) => {
    selectedCategory = newCategory;
    listeners.forEach((listener) => listener(newCategory));
  };

  return [state, setCategory];
};
