import React from 'react';
import './Navbar.css';

function Navbar() {
    return (
        <nav className="navbar">
            <div className="logo">
                <span className="bold">Vike</span>
                <span>Eats</span>
            </div>
            <div className="nav-links">
                <ul>
                    <li><a href="#">Food Establishments</a></li>
                    <li><a href="#">Amenities</a></li>
                    <li><a href="#">Contact Us</a></li>
                </ul>
            </div>
        </nav>


    );
}

export default Navbar;