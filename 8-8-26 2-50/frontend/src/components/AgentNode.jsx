import React from "react";

const AgentNode = ({ label = "Agent" }) => {
  return (
    <div
      style={{
        padding: "0.75rem 1rem",
        borderRadius: "10px",
        background: "#eff6ff",
        border: "1px solid #bfdbfe",
        display: "inline-block",
      }}
    >
      {label}
    </div>
  );
};

export default AgentNode;
