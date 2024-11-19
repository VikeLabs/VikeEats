import React from 'react';
import { Dropdown } from 'react-bootstrap';

const CollectionOfDropdowns = () => {
  // Array of dropdown data
  const dropdowns = [
    { id: 1, label: 'Dropdown 1', items: ['Action 1', 'Action 2', 'Action 3'] },
    { id: 2, label: 'Dropdown 2', items: ['Action A', 'Action B', 'Action C'] },
    { id: 3, label: 'Dropdown 3', items: ['Item 1', 'Item 2', 'Item 3'] }
  ];

  return (
    <div className="d-flex flex-row gap-2">
      {dropdowns.map((dropdown) => (
        <Dropdown key={dropdown.id} className="filter-dropdown">
          <Dropdown.Toggle variant="primary" id={`dropdown-${dropdown.id}`}>
            {dropdown.label}
          </Dropdown.Toggle>

          <Dropdown.Menu>
            {dropdown.items.map((item, index) => (
              <Dropdown.Item key={index} href={`#action-${index + 1}`}>
                {item}
              </Dropdown.Item>
            ))}
          </Dropdown.Menu>
        </Dropdown>
      ))}
    </div>
  );
};

export default CollectionOfDropdowns;