/**
 * marker.js
 *
 * This module defines a MarkerLayer component that dynamically adds markers to the OpenLayers map.
 * It subscribes to category selection state and updates marker styles based on selected categories.
 *
 * Features:
 * - Pins (circles) stay fixed at geographic coordinates on a non-decluttered layer.
 * - Names render on a separate layer with declutter enabled so labels avoid each other.
 * - Highlights the outlet selected from the list (map–list sync).
 */

import { useEffect } from "react";
import { MapPin as MAP_PIN_SVG } from "lucide-static";
import { Feature } from "ol";
import { Point } from "ol/geom";
import { fromLonLat } from "ol/proj";
import VectorLayer from "ol/layer/Vector";
import VectorSource from "ol/source/Vector";
import { Style, Circle, Fill, Stroke, Text, Icon } from "ol/style";
import { useCategory } from "./category-state";
import { getMapInstance } from "./map-manager";

/** Aligns with tailwind.config.js */
const COLORS = {
  activeFill: "#2f76ff",
  inactiveFill: "#94a3b8",
  activeText: "#002754",
  inactiveText: "#64748b",
  ring: "#ffffff",
  textBg: "rgba(255, 255, 255, 0.94)",
  textBorder: "rgba(0, 39, 84, 0.14)",
  accentYellow: "#F5AA1C",
  selectedGlow: "rgba(245, 170, 28, 0.24)",
  selectedGlowStroke: "rgba(245, 170, 28, 0.5)",
};

const ROLE_PIN = "pin";
const ROLE_LABEL = "label";

const LABEL_MAX_CHARS = 28;

// Lucide's MapPin glyph, drawn in a 24x24 viewBox with the point at the bottom-center
// Anchoring at [0.5, 1] lines the tip up with the actual map coordinate
const PIN_ICON_SIZE = 40; // rendered SVG size in px
console.log("Icon size is", PIN_ICON_SIZE)
const PIN_ANCHOR_FRACTION = [0.5, 1];

// Fallback in case lucide-static's markup shape ever changes and the
// extraction below fails to match — keeps the map from breaking outright.
const FALLBACK_PIN_PATH =
    "M20 10c0 4.993-5.539 10.193-7.399 11.799a1 1 0 0 1-1.202 0C9.539 20.193 4 14.993 4 10a8 8 0 0 1 16 0Z";
const FALLBACK_PIN_HOLE = { cx: "12", cy: "10", r: "3" };

/**
* lucide-static exports each icon as its own named export (PascalCase),
* e.g. `import { MapPin } from "lucide-static"` — the value is a full
* "<svg>...</svg>" markup string (attributes like fill/stroke baked in).
* We only want the raw geometry — the path and the center-hole circle —
* so we can apply our own active/selected coloring. Extracted once at
* module load, not per render.
*/
function extractMapPinGeometry() {
  const svgMarkup = MAP_PIN_SVG;
  if (!svgMarkup) {
    return { path: FALLBACK_PIN_PATH, hole: FALLBACK_PIN_HOLE };
  }

  const pathMatch = svgMarkup.match(/<path[^>]*\sd="([^"]+)"/);
  const circleMatch = svgMarkup.match(
      /<circle[^>]*\scx="([^"]+)"[^>]*\scy="([^"]+)"[^>]*\sr="([^"]+)"/
  );

  return {
    path: pathMatch ? pathMatch[1] : FALLBACK_PIN_PATH,
    hole: circleMatch
        ? { cx: circleMatch[1], cy: circleMatch[2], r: circleMatch[3] }
        : FALLBACK_PIN_HOLE,
  };
}

const { path: LUCIDE_MAP_PIN_PATH, hole: LUCIDE_MAP_PIN_HOLE } = extractMapPinGeometry();


function truncateLabel(name) {
  if (!name) return "Outlet";
  const t = String(name).trim();
  if (t.length <= LABEL_MAX_CHARS) return t;
  return `${t.slice(0, LABEL_MAX_CHARS - 1)}…`;
}

function outletIdsMatch(a, b) {
  if (a === null || a === undefined || b === null || b === undefined) {
    return false;
  }
  return String(a) === String(b);
}

function getPinScale(isSelected) {
  return isSelected ? 1.18 : 1;
}

/**
 * Builds (and caches) an OL style array for a pin: an optional selected
 * glow, a soft ground shadow, and the lucide map-pin icon itself
 * (geometry from lucide-static, recolored and serialized to a data-URI
 * for OL's Icon style).
 */
const PIN_STYLE_CACHE = new Map();

/**
 * Circles only (exact coordinates). Includes selected halo.
 * @returns {import("ol/style/Style").default|import("ol/style/Style").default[]}
 */
function createPinStyles(isActive, isSelected) {
  const key = `${isActive ? "a" : "i"}-${isSelected ? "s" : "n"}`;
  if (PIN_STYLE_CACHE.has(key)) {
    return PIN_STYLE_CACHE.get(key);
  }

  const pinFillColor = isActive ? COLORS.activeFill : COLORS.inactiveFill;
  const pinStrokeColor = isSelected ? COLORS.accentYellow : COLORS.ring;
  const pinStrokeWidth = isSelected ? 2.25 : 1.5;
  const pinScale = (PIN_ICON_SIZE / 24) * getPinScale(isSelected);

  const svg =
      `<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" ` +
      `fill="${pinFillColor}" stroke="${pinStrokeColor}" stroke-width="${pinStrokeWidth}" stroke-linecap="round" stroke-linejoin="round">` +
      `<path d="${LUCIDE_MAP_PIN_PATH}" />` +
      `<circle cx="${LUCIDE_MAP_PIN_HOLE.cx}" cy="${LUCIDE_MAP_PIN_HOLE.cy}" r="${LUCIDE_MAP_PIN_HOLE.r}" fill="#ffffff" stroke="none" />` +
      `</svg>`;

  const dataUri = `data:image/svg+xml;base64,${btoa(svg)}`;

  const iconStyle = new Style({
    image: new Icon({
      src: dataUri,
      anchor: PIN_ANCHOR_FRACTION,
      anchorXUnits: "fraction",
      anchorYUnits: "fraction",
      scale: pinScale,
    }),
  });

  const shadowStyle = new Style({
    image: new Circle({
      radius: 3,
      displacement: [0, 1],
      fill: new Fill({ color: "rgba(15, 23, 42, 0.25)" }),
    }),
  });

  const styles = [shadowStyle, iconStyle];

  PIN_STYLE_CACHE.set(key, styles);
  return styles;
}

/**
 * Text-only style for declutter layer (same anchor as pin).
 * @returns {import("ol/style/Style").default}
 */
function createLabelStyle(storeName, isActive, isSelected) {
  const label = truncateLabel(storeName);
  const offsetY = -(PIN_ICON_SIZE * getPinScale(isSelected) + 12);

  const textBorderColor = isSelected
    ? COLORS.accentYellow
    : isActive
      ? COLORS.textBorder
      : "rgba(100, 116, 139, 0.25)";
  const textBorderWidth = isSelected ? 2 : 1;

  return new Style({
    text: new Text({
      text: label,
      font: '600 12px "Figtree", system-ui, -apple-system, sans-serif',
      fill: new Fill({
        color: isActive ? COLORS.activeText : COLORS.inactiveText,
      }),
      backgroundFill: new Fill({
        color: isSelected
          ? "rgba(255, 250, 235, 0.96)"
          : isActive
            ? COLORS.textBg
            : "rgba(248, 250, 252, 0.92)",
      }),
      backgroundStroke: new Stroke({
        color: textBorderColor,
        width: textBorderWidth,
      }),
      padding: [4, 7, 4, 7],
      offsetY,
      textAlign: "center",
      textBaseline: "middle",
    }),
  });
}

function pinLayerStyle(feature) {
  if (feature.get("role") !== ROLE_PIN) {
    return null;
  }
  return createPinStyles(feature.get("isActive"), feature.get("isSelected"));
}

function labelLayerStyle(feature) {
  if (feature.get("role") !== ROLE_LABEL) {
    return null;
  }
  return createLabelStyle(
    feature.get("name"),
    feature.get("isActive"),
    feature.get("isSelected")
  );
}

/** Selected / active labels get drawn first so they win under declutter. */
function labelRenderOrder(a, b) {
  const score = (f) =>
    (f.get("isSelected") ? 2 : 0) + (f.get("isActive") ? 1 : 0);
  return score(b) - score(a);
}

/**
 * MarkerLayer Component
 *
 * @returns {null}
 */
const MarkerLayer = ({ stores, selectedOutletId = null }) => {
  const map = getMapInstance();
  const [selectedCategories] = useCategory();

  useEffect(() => {
    if (!map || !stores || stores.length === 0) return;

    const features = [];

    for (const marker of stores) {
      const coord = fromLonLat(marker.coords);
      const isActive =
        selectedCategories.includes("all") ||
        (marker.categories &&
          marker.categories.some((cat) => selectedCategories.includes(cat)));
      const isSelected = outletIdsMatch(selectedOutletId, marker.id);

      const props = {
        role: ROLE_PIN,
        outletId: marker.id,
        name: marker.name,
        isActive,
        isSelected,
      };

      const pinFeature = new Feature({
        geometry: new Point(coord),
        ...props,
      });

      const labelFeature = new Feature({
        geometry: new Point(coord),
        ...props,
        role: ROLE_LABEL,
      });

      features.push(pinFeature, labelFeature);
    }

    const vectorSource = new VectorSource({ features });

    const pinLayer = new VectorLayer({
      source: vectorSource,
      style: pinLayerStyle,
      zIndex: 100,
    });

    const labelLayer = new VectorLayer({
      source: vectorSource,
      style: labelLayerStyle,
      declutter: true,
      renderOrder: labelRenderOrder,
      zIndex: 101,
    });

    map.addLayer(pinLayer);
    map.addLayer(labelLayer);

    return () => {
      map.removeLayer(pinLayer);
      map.removeLayer(labelLayer);
    };
  }, [map, selectedCategories, stores, selectedOutletId]);

  return null;
};

// Make sure to export as DEFAULT
export default MarkerLayer;