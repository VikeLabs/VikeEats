import React from 'react';
import { Dropdown, Button } from 'react-bootstrap'; // Import necessary components

function BasicDropdownExample() {
  return (
    <Dropdown>
      <Dropdown.Toggle variant="success" id="dropdown-custom-components">
        Dropdown button
      </Dropdown.Toggle>

      <Dropdown.Menu>
        <Dropdown.Item href="#/action-1">Action</Dropdown.Item>
        <Dropdown.Item href="#/action-2">Another action</Dropdown.Item>
        <Dropdown.Item href="#/action-3">Something else</Dropdown.Item>
      </Dropdown.Menu>
    </Dropdown>
  );
}

export default BasicDropdownExample;