import React, { useState, useRef, useEffect, useMemo } from "react";
import "./SearchBar.css";

const SearchBar = ({ stores = [] }) => {
  const [query, setQuery] = useState("");
  const [selectedOutlet, setSelectedOutlet] = useState("");
  const [selectedDiet, setSelectedDiet] = useState("");
  const [results, setResults] = useState({});
  const [isOpen, setIsOpen] = useState(false);
  const searchRef = useRef(null);

  const outletNames = useMemo(() => {
    const names = stores.map((s) => s.name);
    return [...new Set(names)].sort();
  }, [stores]);

  const KNOWN_DIETS = ["vegan", "vegetarian", "gluten free", "dairy free", "halal"];

  const dietOptions = useMemo(() => {
      const diets = stores.flatMap((s) => s.supportedDiets || []);
      return [...new Set(diets)]
        .filter((d) => KNOWN_DIETS.includes(d.toLowerCase()))
        .sort();
  }, [stores]);

  useEffect(() => {
    const handleClickOutside = (e) => {
      if (searchRef.current && !searchRef.current.contains(e.target)) {
        setIsOpen(false);
      }
    };
    document.addEventListener("mousedown", handleClickOutside);
    return () => document.removeEventListener("mousedown", handleClickOutside);
  }, []);

  useEffect(() => {
    const hasQuery = query.length >= 2;
    const hasFilter = selectedOutlet || selectedDiet;

    if (!hasQuery && !hasFilter) {
      setResults({});
      setIsOpen(false);
      return;
    }

    const timer = setTimeout(() => {
      const params = new URLSearchParams();
      if (query.length >= 2) params.set("menu-item", query);
      if (selectedOutlet) params.set("food-outlet", selectedOutlet);
      if (selectedDiet) params.set("restriction", selectedDiet);

      fetch(`/api/search?${params.toString()}`)
        .then((res) => res.json())
        .then((data) => {
          setResults(data);
          setIsOpen(true);
        })
        .catch((err) => console.error("Search error:", err));
    }, 300);

    return () => clearTimeout(timer);
  }, [query, selectedOutlet, selectedDiet]);

  const flatItems = [];
  Object.entries(results).forEach(([outlet, menus]) => {
    Object.entries(menus).forEach(([menu, categoriesOrItems]) => {
      Object.entries(categoriesOrItems).forEach(([key, value]) => {
        if (value.ingredients !== undefined) {
          flatItems.push({ outlet, menu, name: key, ...value });
        } else {
          Object.entries(value).forEach(([itemName, details]) => {
            flatItems.push({ outlet, menu, name: itemName, ...details });
          });
        }
      });
    });
  });

  const hasActiveSearch = query.length >= 2 || selectedOutlet || selectedDiet;

  return (
    <div className="search-container" ref={searchRef}>
      <div className="search-controls">
        <input
          type="text"
          className="search-input"
          placeholder="Search..."
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          onFocus={() => flatItems.length > 0 && setIsOpen(true)}
        />
        <select
          className="search-select"
          value={selectedOutlet}
          onChange={(e) => setSelectedOutlet(e.target.value)}
        >
          <option value="">All outlets</option>
          {outletNames.map((name) => (
            <option key={name} value={name}>{name}</option>
          ))}
        </select>
        <select
          className="search-select"
          value={selectedDiet}
          onChange={(e) => setSelectedDiet(e.target.value)}
        >
          <option value="">Any diet</option>
          {dietOptions.map((diet) => (
            <option key={diet} value={diet}>{diet}</option>
          ))}
        </select>
      </div>

      {isOpen && flatItems.length > 0 && (
        <div className="search-dropdown">
          {flatItems.map((item, i) => (
            <div key={i} className="search-result-item">
              <div className="search-result-name">{item.name}</div>
              <div className="search-result-outlet">{item.outlet} — {item.menu}</div>
              {item["dietary restrictions"]?.length > 0 && (
                <div className="search-result-diets">
                  {item["dietary restrictions"].join(", ")}
                </div>
              )}
            </div>
          ))}
        </div>
      )}

      {isOpen && hasActiveSearch && flatItems.length === 0 && (
        <div className="search-dropdown">
          <div className="search-no-results">No items found</div>
        </div>
      )}
    </div>
  );
};

export default SearchBar;
