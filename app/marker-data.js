/**
 * marker-data.js
 * 
 * This module exports a dataset of marker locations for the UVic map.
 * Each marker represents a specific location with categories that can be used for filtering.
 *
 * Features:
 * - Provides predefined marker locations with longitude and latitude coordinates.
 * - Assigns each marker to one or more filterable categories.
 * - Can be used in mapping components to display markers dynamically.
 */

export const markerData = [
  { id: 1, categories: ["all", "filter1", "filter2", "filter3", "filter4", "filter5"], coords: [-123.30727, 48.46423] }, // Cove
  { id: 2, categories: ["all", "filter1"], coords: [-123.30987, 48.46351] }, // Biblio
  { id: 3, categories: ["all", "filter2"], coords: [-123.31338, 48.46275] }, // Macs
  { id: 4, categories: ["all", "filter3"], coords: [-123.31174, 48.46483] }, // Mystic
  { id: 5, categories: ["all", "filter4"], coords: [-123.31051, 48.46117] }, // Nibbles and Bytes
  { id: 6, categories: ["all", "filter5"], coords: [-123.30892, 48.46203] }, // Sci Cafe
  { id: 7, categories: ["all", "filter1", "filter3", "filter5"], coords: [-123.31668, 48.46196] }, // Arts Place
];