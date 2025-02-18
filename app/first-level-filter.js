import React from "react";
import "./first-level-filter.css";
import { useCategory } from "./category-state";

const FilterButtons = () => {
  const [selectedCategories, toggleCategory] = useCategory();

  const categories = [
    "all",
    "filter1",
    "filter2",
    "filter3",
    "filter4",
    "filter5",
  ];

  const handleButtonClick = (category) => {
    toggleCategory(category);
    console.log("Toggled category:", category);
    console.log("Now selected:", selectedCategories);
  };

  return (
    <div>
      <div className="filter-buttons">
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
        <button
          key="clear"
          className="filter-button inactive"
          onClick={() => handleButtonClick(null)}
        >
          clear
        </button>
      </div>
      <div>
        <p>Selected Categories: {selectedCategories.join(", ")}</p>
      </div>
    </div>
  );
};

export default FilterButtons;
