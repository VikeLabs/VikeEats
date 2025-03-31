/**
 * minimized-cards-data.js
 *
 * This module exports a dataset representing food outlets (stores) at UVic.
 * Each store has associated dietary options, category filters, and an image.
 *
 * Features:
 * - Provides predefined store details including name, hours, and dietary accommodations.
 * - Supports category-based filtering for UI components.
 * - Includes image URLs for display in components.
 *
 * Data Structure:
 * Each store object in the "stores" array contains the following keys:
 *
 * - id: {number} Unique identifier for the store.
 * - supportedDiets: {string[]} Array of strings representing the dietary options supported by the store.
 * - categories: {string[]} Array of category labels for filtering.
 * - name: {string} The name of the store.
 * - time: {string} Operating hours for the store (e.g., "9am - 5pm").
 * - image: {string} URL string linking to an image representing the store.
 * - menu: {dict{}} Contains each item description
 * -  name: {string} Contains item name
 * -  price: {string} Contains price of item
 * -  description: {string} Contains ingredients of item
 */

export const stores = [
  {
    id: 1,
    supportedDiets: [
      "vegan",
      "gluten-free",
      "halal",
      "vegetarian",
      "dairy-free",
    ],
    categories: ["all", "filter1", "filter2", "filter3", "filter4", "filter5"],
    name: "The Cove",
    time: "9am - 5pm",
    image: "https://www.uvic.ca/services/food/assets/images/cove-stairs",
    menu: [
      {
        name: "Buffalo Wings",
        price: "$2.00",
        description: "Chicken, parsley, etc.",
      },
      {
        name: "A",
        price: "$2.00",
        description: "Chicken, parsley, etc.",
      },
    ],
  },
  {
    id: 2,
    supportedDiets: [
      "vegan",
      "gluten-free",
      "halal",
      "vegetarian",
      "dairy-free",
    ],
    categories: ["all", "filter1"],
    name: "BiblioCafé",
    time: "9am - 6pm",
    image: "https://www.uvic.ca/services/food/where/bibliocafe/cappweb.jpg",
  },
  {
    id: 3,
    supportedDiets: [
      "vegan",
      "gluten-free",
      "halal",
      "vegetarian",
      "dairy-free",
    ],
    categories: ["all", "filter2"],
    name: "Mac's",
    time: "12pm - 3pm",
    image:
      "https://www.uvic.ca/services/food/assets/images/photos/main/sandwichmain.jpg",
  },
  {
    id: 4,
    supportedDiets: [
      "vegan",
      "gluten-free",
      "halal",
      "vegetarian",
      "dairy-free",
    ],
    categories: ["all", "filter3"],
    name: "Mystic Market",
    time: "9am - 5pm",
    image: "https://www.uvic.ca/services/food/where/noodlesweb.jpg",
  },
  {
    id: 5,
    supportedDiets: [
      "vegan",
      "gluten-free",
      "halal",
      "vegetarian",
      "dairy-free",
    ],
    categories: ["all", "filter4"],
    name: "Nibbles & Bytes Café",
    time: "9am - 6pm",
    image:
      "https://www.uvic.ca/news-management/stories/2018/funding-computer-science-engineering/photos/Engineering%20students%20in%20ECS-960x640.jpg",
  },
  {
    id: 6,
    supportedDiets: [
      "vegan",
      "gluten-free",
      "halal",
      "vegetarian",
      "dairy-free",
    ],
    categories: ["all", "filter5"],
    name: "SciCafé",
    time: "12pm - 3pm",
    image:
      "https://www.uvic.ca/info/_assets/images/content-main/buildings-bwc.jpg",
  },
  {
    id: 7,
    supportedDiets: [
      "vegan",
      "gluten-free",
      "halal",
      "vegetarian",
      "dairy-free",
    ],
    categories: ["all", "filter1", "filter3", "filter5"],
    name: "Arts Place",
    time: "10am - 2pm",
    image:
      "https://www.uvic.ca/services/food/assets/images/photos/artsplace.jpg",
  },
];
