import React from "react";

const Sidebar = () => {
  return (
    <aside
      style={{
        width: "220px",
        padding: "1rem",
        borderRight: "1px solid #e5e7eb",
        minHeight: "100vh",
      }}
    >
      <h4 style={{ marginBottom: "1rem" }}>Menu</h4>
      <ul
        style={{
          listStyle: "none",
          padding: 0,
          margin: 0,
          display: "grid",
          gap: "0.5rem",
        }}
      >
        <li>Overview</li>
        <li>Agents</li>
        <li>Workflows</li>
        <li>Settings</li>
      </ul>
    </aside>
  );
};

export default Sidebar;
