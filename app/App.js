import React, { useEffect, useState } from "react";

import NavBar from "./Navbar";
import MinimizedCards from "./MinimizedCards";
import FilterButtons from "./first-level-filter";
import MapLayer from "./map";
import MarkerLayer from "./marker";

const App = () => {
  const [foodOutletsData, setFoodOutletsData] = useState(null);

  useEffect(() => {
    fetch("http://127.0.0.1:5328/api/food_outlets")
      .then((response) => response.json())
      .then((data) => setFoodOutletsData(data))
      .catch((error) => console.error("Error fetching food_outlets:", error));
    }, []);

  return (
    <div>
      <div>
        {foodOutletsData ? (
          <div>
            {Object.entries(foodOutletsData).map(([day, outlets]) => (
              <div
                key={day}
                style={{
                  marginBottom: "20px",
                  borderBottom: "1px solid #ccc",
                  paddingBottom: "10px",
                }}
              >
                <h2>{day}</h2>
                <ul>
                  {Object.entries(outlets).map(([outlet, hours]) => (
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
      </div>
      
      {/* <MapLayer />
      <MarkerLayer />
      <FilterButtons />
      <NavBar />
      <MinimizedCards /> */}
    </div>
  );
};

export default App;
