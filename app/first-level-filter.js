import React, { useState } from "react";
import "./first-level-filter.css";
import { useCategory } from "./category-state";

//temporary filter buttons for markers
//sets the selected category into activeMarker state for MarkerLayer to display
const FilterButtons = () => {
  //stores id of the selected filter button
  //used for styling of the buttons
  const [idSelected, setIdSelected] = useState(null);

  //stores category selected
  const [selectedCategory, setSelectedCategory] = useCategory();

  //filter buttons
  const categories = [
    "all",
    "filter1",
    "filter2",
    "filter3",
    "filter4",
    "filter5",
  ];

  //set selected id and category to its respective states
  const handleButtonClick = (id, category) => {
    setIdSelected(id);
    setSelectedCategory(category);
    console.log({ category });
    console.log({ selectedCategory });
  };

  return (
    <div>
      <div className="filter-buttons">
        {/* map out filter buttons from categories array from above */}
        {categories.map((category, index) => (
          <button
            className={`filter-button ${
              idSelected === index ? "active" : "inactive"
            }`}
            key={category}
            id={index}
            onClick={() => handleButtonClick(index, category)}
          >
            {category}
          </button>
        ))}

        {/* greys all markers and hides all cards */}
        <button
          key={"clear"}
          id={-1}
          onClick={() => handleButtonClick(-1, null)}
          className={"filter-button inactive"}
        >
          clear
        </button>
      </div>
    </div>
  );
};

export default FilterButtons;
