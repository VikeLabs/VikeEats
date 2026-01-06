/**
 *cards-manager.js
 * 
 * Manages minimized and maximized cards
 * It ensures minimized cards and maximized cards use the same data
 * 
 * Features:
 * - manages the state of the clicked store
 * - retrieve clicks from minimized-cards.js to set the store to be displayed
 * - retieve clicks from maximized-cards.js to close modal
 * - displays the store stored in selectedStore state
 *  */ 

import React, { useState } from 'react';
import MinimizedCards from './minimized-cards';
import MaximizedCards from './maximized-cards';
import { stores } from './cards-data';

const CardsContainer = () => {
  const [selectedStore, setSelectedStore] = useState(null);

  // displays minimized card as maximized card
  const handleCardClick = (store) => {
    setSelectedStore(store);
  };

  // Closes maximized card
  const closeModal = () => {
    setSelectedStore(null);
  };

  return (
    <div>
      {/* Render minimized cards, passing stores and click handler */}
      <MinimizedCards stores={stores} onCardClick={handleCardClick} />

      {/* Conditionally render the maximized card modal */}
      {selectedStore && (
        <MaximizedCards store={selectedStore} onClose={closeModal} />
      )}
    </div>
  );
};

export default CardsContainer;
