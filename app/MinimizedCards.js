<<<<<<< HEAD
import React from "react";
import "./MinimizedCards.css";

const stores = [
  {
    name: "The Cove",
    time: "9am - 5pm",
    image: "https://www.uvic.ca/services/food/assets/images/cove-stairs",
  },
  {
    name: "BiblioCafé",
    time: "9am - 6pm",
    image: "https://www.uvic.ca/services/food/where/bibliocafe/cappweb.jpg",
  },
  {
    name: "Mac's",
    time: "12pm - 3pm",
    image:
      "https://www.uvic.ca/services/food/assets/images/photos/main/sandwichmain.jpg",
  },
  {
    name: "Mystic Market",
    time: "9am - 5pm",
    image: "https://www.uvic.ca/services/food/where/noodlesweb.jpg",
  },
  {
    name: "Nibbles & Bytes Café",
    time: "9am - 6pm",
    image:
      "https://www.uvic.ca/news-management/stories/2018/funding-computer-science-engineering/photos/Engineering%20students%20in%20ECS-960x640.jpg",
  },
  {
    name: "SciCafé",
    time: "12pm - 3pm",
    image:
      "https://www.uvic.ca/info/_assets/images/content-main/buildings-bwc.jpg",
  },
  {
    name: "Arts Place",
    time: "10am - 2pm",
    image: "https://www.uvic.ca/services/food/assets/images/photos/artsplace.jpg"
  },
];

// Component for displaying minimized food place cards
const MinimizedCards = () => {
  return (
    <div className="MinimizedCards">
      {stores.map((store, index) => (
        <div key={index} className="store_card">
          <div className="store_info">
            <h2 className="store_title">{store.name}</h2>
            <p className="store_time">{store.time}</p>
          </div>
          <img src={store.image} alt="ERROR" className="store_image" />
        </div>
      ))}
    </div>
  );
};

export default MinimizedCards;
=======
import React from "react";
import "./MinimizedCards.css";

const stores = [
  {
    name: "The Cove",
    time: "9am - 5pm",
    image: "https://www.uvic.ca/services/food/assets/images/cove-stairs",
  },
  {
    name: "BiblioCafé",
    time: "9am - 6pm",
    image: "https://www.uvic.ca/services/food/where/bibliocafe/cappweb.jpg",
  },
  {
    name: "Mac's",
    time: "12pm - 3pm",
    image:
      "https://www.uvic.ca/services/food/assets/images/photos/main/sandwichmain.jpg",
  },
  {
    name: "Mystic Market",
    time: "9am - 5pm",
    image: "https://www.uvic.ca/services/food/where/noodlesweb.jpg",
  },
  {
    name: "Nibbles & Bytes Café",
    time: "9am - 6pm",
    image:
      "https://www.uvic.ca/news-management/stories/2018/funding-computer-science-engineering/photos/Engineering%20students%20in%20ECS-960x640.jpg",
  },
  {
    name: "SciCafé",
    time: "12pm - 3pm",
    image:
      "https://www.uvic.ca/info/_assets/images/content-main/buildings-bwc.jpg",
  },
  {
    name: "Arts Place",
    time: "10am - 2pm",
    image: "https://www.uvic.ca/services/food/assets/images/photos/artsplace.jpg"
  },
];

// Component for displaying minimized food place cards
const MinimizedCards = () => {
  return (
    <div className="MinimizedCards">
      {stores.map((store, index) => (
        <div key={index} className="store_card">
          <div className="store_info">
            <h2 className="store_title">{store.name}</h2>
            <p className="store_time">{store.time}</p>
          </div>
          <img src={store.image} alt="ERROR" className="store_image" />
        </div>
      ))}
    </div>
  );
};

export default MinimizedCards;
>>>>>>> origin/KenK
