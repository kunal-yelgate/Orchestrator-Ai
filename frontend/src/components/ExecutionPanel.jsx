import React from "react";

const ExecutionPanel = () => {
  return (
    <aside
      style={{
        padding: "1rem",
        border: "1px solid #e5e7eb",
        borderRadius: "12px",
        minWidth: "220px",
      }}
    >
      <h3 style={{ marginBottom: "0.5rem" }}>Execution Panel</h3>
      <p style={{ margin: 0, color: "#6b7280" }}>
        Monitor active runs and logs here.
      </p>
    </aside>
  );
};

export default ExecutionPanel;
