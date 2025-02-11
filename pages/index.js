import NavBar from "../app/Navbar";
import MinimizedCards from "../app/MinimizedCards";
import FilterButtons from "../app/first-level-filter";
import MapLayer from "../app/map";
import MarkerLayer from "../app/marker";

export default function Home() {
  return (
    <div>
      
      <MapLayer />
      <MarkerLayer />
      <FilterButtons />
      <NavBar />
      <MinimizedCards />
    </div>
  );
}
