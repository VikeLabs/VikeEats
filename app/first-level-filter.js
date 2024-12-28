import React, { useState } from "react";
import "./first-level-filter.css";

//temporary filter buttons for markers
//sets the selected category into activeMarker state for MarkerLayer to display
const FilterButtons = ({ activeMarker, setActiveMarker }) => {
  //stores id of the selected filter button
  //used for styling of the buttons
  const [idSelected, setIdSelected] = useState(null);

  //set selected id and category to its respective states
  const handleButtonClick = (id, category) => {
    setIdSelected(id);
    setActiveMarker(category);
  };

  return (
    <div>
      <div className="filter-buttons">
        <button
          id="1"
          category="canada"
          className={`filter-button ${
            idSelected === 1 ? "active" : "inactive" //this is for filter button styling
          }`}
          onClick={() => handleButtonClick(1, "canada")}
        >
          Filter 1
        </button>

        <button
          id="2"
          category="america"
          className={`filter-button ${
            idSelected === 2 ? "active" : "inactive"
          }`}
          onClick={() => handleButtonClick(2, "america")}
        >
          Filter 2
        </button>

        <button
          id="3"
          category="america"
          className={`filter-button ${
            idSelected === 3 ? "active" : "inactive"
          }`}
          onClick={() => handleButtonClick(3, "america")}
        >
          Filter 3
        </button>

        <button
          id="4"
          category="europe"
          className={`filter-button ${
            idSelected === 4 ? "active" : "inactive"
          }`}
          onClick={() => handleButtonClick(4, "europe")}
        >
          Filter 4
        </button>
        
        <button
          id="5"
          category="europe"
          className={`filter-button ${
            idSelected === 5 ? "active" : "inactive"
          }`}
          onClick={() => handleButtonClick(5, "europe")}
        >
          Filter 5
        </button>
      </div>

      {/* for testing purposes */}
      {/* <div className="selected-filter">
        {activeMarker ? (
          <p>Selected Filter: {activeMarker}<br />Selected Id: {idSelected}</p>
        ) : (
          <p>No filter selected.</p>
        )}
      </div> */}
    </div>
  );
};

export default FilterButtons;
