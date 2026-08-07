import React from "react";
import GraphCanvas from "../components/GraphCanvas";
import ExecutionPanel from "../components/ExecutionPanel";

const Workflow = () => {
  return (
    <div style={{ display: "grid", gap: "1rem" }}>
      <h2>Workflow Page</h2>
      <GraphCanvas />
      <ExecutionPanel />
    </div>
  );
};

export default Workflow;
