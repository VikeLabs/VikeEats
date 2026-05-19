// maximized-cards.js
import React, { useEffect, useMemo } from "react";
import "./maximized-cards.css";

/**
 * API returns menu: { sections: [ { title, categories: [ { name, items: [...] } ] } ] }.
 * Legacy flat list: [ { name, description?, price? } ].
 */
function normalizeMenuMenu(menu) {
  if (!menu) {
    return { sections: [] };
  }
  if (Array.isArray(menu)) {
    if (menu.length === 0) {
      return { sections: [] };
    }
    return {
      sections: [
        {
          title: null,
          categories: [{ name: "Menu", items: menu }],
        },
      ],
    };
  }
  if (menu.sections && Array.isArray(menu.sections)) {
    return menu;
  }
  return { sections: [] };
}

function MenuItemRow({ item }) {
  return (
    <li className="menu-item">
      <div className="menu-item-head">
        <span className="item-name">{item.name}</span>
        {item.price ? (
          <span className="item-price">{item.price}</span>
        ) : null}
      </div>
      {item.description ? (
        <p className="item-description">{item.description}</p>
      ) : null}
      {item.allergens ? (
        <p className="item-allergens">
          <span className="item-allergens-label">Contains:</span> {item.allergens}
        </p>
      ) : null}
    </li>
  );
}

const MaximizedCards = ({ store, onClose }) => {
  useEffect(() => {
    const onKey = (e) => {
      if (e.key === "Escape") onClose();
    };
    window.addEventListener("keydown", onKey);
    return () => window.removeEventListener("keydown", onKey);
  }, [onClose]);

  if (!store) return null;

  const isSub = store.location === "The Sub";
  const diets = (store.supportedDiets || []).filter(Boolean);
  const menuData = useMemo(() => normalizeMenuMenu(store.menu), [store.menu]);
  const menuSections = menuData.sections || [];
  const hasMenu = menuSections.some(
    (s) =>
      s.categories &&
      s.categories.some((c) => c.items && c.items.length > 0),
  );
  const closed = store.isClosed === true;

  return (
    <div
      className="modal-overlay"
      role="dialog"
      aria-modal="true"
      aria-labelledby="maximized-store-title"
    >
      <div className="modal-bg" onClick={onClose} aria-hidden="true" />

      <div className="modal-content">
        <button
          type="button"
          className="close-btn"
          onClick={onClose}
          aria-label="Close details"
        >
          <span aria-hidden="true">×</span>
        </button>

        <div className="modal-body">
          <div
            className={
              isSub ? "image-container image-container--logo" : "image-container"
            }
          >
            <img
              src={store.image}
              alt={store.name}
              className={
                isSub ? "image-style image-style--logo" : "image-style"
              }
            />
          </div>

          <div className="details-container">
            <header className="modal-header">
              <h2 id="maximized-store-title" className="store-title">
                {store.name}
              </h2>
              <div className="store-meta">
                {store.location && (
                  <span className="store-location">{store.location}</span>
                )}
                <span
                  className={
                    closed ? "store-status store-status--closed" : "store-status"
                  }
                >
                  {closed ? "Closed today" : "Open"}
                </span>
              </div>
            </header>

            <section className="section section-hours" aria-label="Hours">
              <h3 className="section-title">Today&apos;s hours</h3>
              <p className="hours-value">{store.time}</p>
            </section>

            {diets.length > 0 && (
              <section className="section" aria-label="Dietary options">
                <h3 className="section-title">Dietary options</h3>
                <ul className="diet-list">
                  {diets.map((d) => (
                    <li key={d} className="diet-pill">
                      {d}
                    </li>
                  ))}
                </ul>
              </section>
            )}

            {hasMenu && (
              <section className="section section-menu" aria-label="Menu">
                <h3 className="section-title">Menu</h3>
                <div className="menu-sections">
                  {menuSections.map((section, si) => (
                    <div
                      key={section.title || `section-${si}`}
                      className="menu-section-block"
                    >
                      {section.title && menuSections.length > 1 ? (
                        <h4 className="menu-section-title">{section.title}</h4>
                      ) : null}
                      <div className="menu-category-list">
                        {(section.categories || []).map((cat, ci) => (
                          <details
                            key={`menu-${si}-${ci}-${cat.name}`}
                            className="menu-category"
                          >
                            <summary className="menu-category-summary">
                              <span className="menu-category-name">
                                {cat.name}
                              </span>
                            </summary>
                            <ul className="menu-list menu-list--nested">
                              {(cat.items || []).map((item, index) => (
                                <MenuItemRow
                                  key={`${cat.name}-${item.name}-${index}`}
                                  item={item}
                                />
                              ))}
                            </ul>
                          </details>
                        ))}
                      </div>
                    </div>
                  ))}
                </div>
              </section>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

export default MaximizedCards;
