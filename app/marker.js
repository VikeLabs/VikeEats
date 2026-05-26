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
import { Feature } from "ol";
import { Point } from "ol/geom";
import { fromLonLat } from "ol/proj";
import VectorLayer from "ol/layer/Vector";
import VectorSource from "ol/source/Vector";
import { Style, Circle, Fill, Stroke, Text } from "ol/style";
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

function pinRadii(isActive, isSelected) {
  const baseRadius = isActive ? 12 : 9;
  const radius = isSelected ? baseRadius + 2 : baseRadius;
  return { baseRadius, radius };
}

/**
 * Circles only (exact coordinates). Includes selected halo.
 * @returns {import("ol/style/Style").default|import("ol/style/Style").default[]}
 */
function createPinStyles(isActive, isSelected) {
  const { radius } = pinRadii(isActive, isSelected);
  const pinStrokeColor = isSelected ? COLORS.accentYellow : COLORS.ring;
  const pinStrokeWidth = isSelected ? 3.5 : 2.5;

  const pinOnly = new Style({
    image: new Circle({
      radius,
      fill: new Fill({
        color: isActive ? COLORS.activeFill : COLORS.inactiveFill,
      }),
      stroke: new Stroke({ color: pinStrokeColor, width: pinStrokeWidth }),
    }),
  });

  if (!isSelected) {
    return pinOnly;
  }

  const haloStyle = new Style({
    image: new Circle({
      radius: radius + 12,
      fill: new Fill({ color: COLORS.selectedGlow }),
      stroke: new Stroke({
        color: COLORS.selectedGlowStroke,
        width: 1,
      }),
    }),
  });

  return [haloStyle, pinOnly];
}

/**
 * Text-only style for declutter layer (same anchor as pin).
 * @returns {import("ol/style/Style").default}
 */
function createLabelStyle(storeName, isActive, isSelected) {
  const label = truncateLabel(storeName);
  const { radius } = pinRadii(isActive, isSelected);
  const offsetY = -(radius + 10);

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

export default MarkerLayer;
