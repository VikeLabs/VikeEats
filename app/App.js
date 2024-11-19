import logo from './logo.svg';
import './App.css';
import React from 'react';
import Button from './filter-button.js'; 
import Dropdown from './filter-button-dropdown.js'; 

const App = () => {
  const handleClick = () => {
    alert('Button clicked!');
  };
  
  const options = [
    { value: 'option1', label: 'Option 1' },
    { value: 'option2', label: 'Option 2' },
    { value: 'option3', label: 'Option 3' },
  ];

  const handleDropdownSelect = (selectedOption) => {
    console.log('Selected Option:', selectedOption);
  };

  return (
    <div>
      <Button 
        label="Filter" 
        onClick={handleClick} 
      />
	  <Dropdown options={options} onSelect={handleDropdownSelect} />
    </div>
  );
};

export default App;