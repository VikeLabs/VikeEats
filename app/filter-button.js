import React from 'react';
import './filter-button.css';

const CollectionOfButtons = ({ label, onClick, style }) => {
	
  const buttons = [
    { id: 1, label: 'Dropdown 1' },
    { id: 2, label: 'Dropdown 2' },
    { id: 3, label: 'Dropdown 3' }
  ];

  return (
    <div className="d-flex flex-row gap-2">
      {buttons.map((button) => (
        <button 
		  onClick={onClick} 
		  style={style} 
		  key={buttons.id}
		  className="filter-button"
		>
		  {label}
		</button>
      ))}
    </div>
  );
};

export default CollectionOfButtons;