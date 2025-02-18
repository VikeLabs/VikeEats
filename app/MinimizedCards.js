import React from "react";
import "./MinimizedCards.css";
import { useCategory } from "./category-state";
import { stores } from "./minimized-cards-data";

//component for displaying minimized food place cards
const MinimizedCards = () => {
  const cards = stores;
  const [selectedCategories] = useCategory();

  //filteredCards store cards that will be displayed
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
          <img src={store.image} alt="ERROR" className="store_image" />
        </div>
      ))}
    </div>
  );
};

export default MinimizedCards;
