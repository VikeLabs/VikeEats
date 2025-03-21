import React, { useEffect, useState } from "react";

import NavBar from "./Navbar";
import MinimizedCards from "./minimized-cards";
import FilterButtons from "./first-level-filter";
import MapLayer from "./map";
import MarkerLayer from "./marker";
import UserLocationMarker from "./UserLocationMarker";

/**
 * The main application component.
 * Fetches food outlet data from an API and displays the schedule.
 *
 * @component
 * @returns {JSX.Element} The rendered App component.
 */
const App = () => {
  // State to store food outlet data fetched from the API
  const [foodOutletsData, setFoodOutletsData] = useState(null);

  // Fetches food outlet schedule from the backend API on component mount.
  useEffect(() => {
    fetch("http://127.0.0.1:5328/api/food_outlets")
      .then((response) => response.json())
      .then((data) => setFoodOutletsData(data))
      .catch((error) => console.error("Error fetching food_outlets:", error));
  }, []); // Empty dependency array ensures this runs only once when component mounts

  return (
    <div>
      {/* 
      *For test only
      *Displays the data from backend nicely
       */}
{/*        
      <div>
        {foodOutletsData ? (
          <div> */}
            {/* Loop through each day and display food outlets with their schedule */}
            {/* {Object.entries(foodOutletsData).map(([day, outlets]) => (
              <div
                key={day}
                style={{
                  marginBottom: "20px",
                  borderBottom: "1px solid #ccc",
                  paddingBottom: "10px",
                }}
              >
                <h2>{day}</h2>
                <ul> */}
                  {/* Loop through each outlet and display its hours */}
                  {/* {Object.entries(outlets).map(([outlet, hours]) => (
                    <li key={outlet}>
                      <strong>{outlet}:</strong> {hours}
                    </li>
                  ))}
                </ul>
              </div>
            ))}
          </div>
        ) : (
          <p>Loading food outlet schedule...</p>
        )}
      </div>  */}
      
      {/* Uncomment these components to see the app */}
      <MapLayer />
      <MarkerLayer />
      <UserLocationMarker />
      <FilterButtons />
      <NavBar />
      <MinimizedCards />
    </div>
  );
};

export default App;
