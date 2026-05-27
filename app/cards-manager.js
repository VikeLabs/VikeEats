/**
 *cards-manager.js
 *
 * Manages minimized and maximized cards
 * It ensures minimized cards and maximized cards use the same data
 *
 * Features:
 * - manages the clicked store (controlled from App for map list sync)
 * - retrieve clicks from minimized-cards.js to set the store to be displayed
 * - retrieve clicks from maximized-cards.js to close modal
 * - displays the store stored in selectedStore state
 */

import React from "react";
import MinimizedCards from "./minimized-cards";
import MaximizedCards from "./maximized-cards";

const CardsContainer = ({
  stores,
  selectedStore,
  onSelectedStoreChange,
}) => {
  const handleCardClick = (store) => {
    onSelectedStoreChange(store);
  };

  const closeModal = () => {
    onSelectedStoreChange(null);
  };

  return (
    <div>
      <MinimizedCards stores={stores} onCardClick={handleCardClick} />

      {selectedStore && (
        <MaximizedCards store={selectedStore} onClose={closeModal} />
      )}
    </div>
  );
};

export default CardsContainer;
