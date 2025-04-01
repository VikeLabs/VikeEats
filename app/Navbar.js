import React from 'react';
import './Navbar.css';
import Link from 'next/link'

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
                    <li><Link href="/contact" legacyBehavior><a>Contact Us</a></Link></li>
                </ul>
            </div>
        </nav>


    );
}

export default Navbar;