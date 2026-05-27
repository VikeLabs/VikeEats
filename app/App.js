import React, { useEffect, useState } from "react";
import NavBar from "./Navbar";
import FilterButtons from "./first-level-filter";
import MapLayer from "./map";
import MarkerLayer from "./marker";
import UserLocationMarker from "./UserLocationMarker";
import CardsContainer from "./cards-manager";

/**
 * The main application component.
 * Fetches food outlet data from the API and coordinates core UI components.
 */
const App = () => {
  const [storesData, setStoresData] = useState([]);
  const [selectedStore, setSelectedStore] = useState(null);

  useEffect(() => {
    fetch(`/api/ui/stores`)
      .then((response) => response.json())
      .then((data) => setStoresData(data))
      .catch((error) => console.error("Error fetching ui/stores:", error));
  }, []);

  const selectedOutletId = selectedStore?.id ?? null;

  return (
    <div className="relative min-h-screen">
      <MapLayer />
      <MarkerLayer stores={storesData} selectedOutletId={selectedOutletId} />
      <UserLocationMarker />
      <FilterButtons />
      <NavBar stores={storesData} />
      <CardsContainer
        stores={storesData}
        selectedStore={selectedStore}
        onSelectedStoreChange={setSelectedStore}
      />
    </div>
  );
}

export default App;
