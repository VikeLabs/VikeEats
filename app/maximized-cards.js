// maximized-cards.js
import React from "react";
import "./maximized-cards.css";

const MaximizedCards = ({ store, onClose }) => {
  if (!store) return null;

  return (
    <div className="modal-overlay">
      {/* Greyed out background overlay */}
      <div className="modal-bg" onClick={onClose}></div>

      {/* Modal content */}
      <div className="modal-content">
        {/* Close button */}
        <button className="close-btn" onClick={onClose}>
          x
        </button>
        <div className="modal-body">
          {/* Store image */}
          <div className="image-container">
            <img src={store.image} alt={store.name} className="image-style" />
          </div>

          {/* Store details */}
          <div className="details-container">
            <h2 className="store-title">{store.name}</h2>
            <p className="store-info">store-type | store-open-status</p>
            <div className="section">
              <h3 className="section-title">Hours</h3>
              <p>{store.time}</p>
            </div>
            {/* Render each menu section */}
            {store.menu &&
              store.menu.map((item, index) => (
                <div key={index} className="menu-item">
                  <p className="item-name">{item.name}</p>
                  <p className="item-price">{item.price}</p>
                  <p className="item-description">{item.description}</p>
                </div>
              ))}
          </div>
        </div>
      </div>
    </div>
  );
};

export default MaximizedCards;
