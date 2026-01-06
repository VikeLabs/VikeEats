/**
 * Navbar.js
 * 
 * This component renders the navigation bar for the application.
 * It includes a logo and navigation links for different sections.
 *
 * Features:
 * - Displays the application logo (VikeEats).
 * - Provides navigation links to different sections.
 * - Uses external CSS for styling.
 */

import React from 'react';
import './Navbar.css';
import Link from 'next/link'

/**
 * Navbar Component
 * 
 * Renders a responsive navigation bar for the application.
 * 
 * @component
 * @returns {JSX.Element} The navigation bar.
 */
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