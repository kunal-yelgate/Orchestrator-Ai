import React from "react";

const Navbar = () => {
  return (
    <nav
      style={{
        display: "flex",
        justifyContent: "space-between",
        alignItems: "center",
        padding: "1rem 1.5rem",
        borderBottom: "1px solid #e5e7eb",
      }}
    >
      <strong>Orchestrator AI</strong>
      <div style={{ display: "flex", gap: "1rem" }}>
        <span>Home</span>
        <span>Workflow</span>
        <span>Dashboard</span>
      </div>
    </nav>
  );
};

export default Navbar;
