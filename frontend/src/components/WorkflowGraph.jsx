import React from "react";
import "./WorkflowGraph.css";

const WorkflowGraph = ({ activeStage }) => {
  const stages = [
    "Planner",
    "Task Splitter",
    "Research Agent 1",
    "Research Agent 2",
    "Summarizer",
    "Verifier",
  ];

  const isActive = (stage) => activeStage === stage;

  const isCompleted = (stage) =>
    stages.indexOf(stage) < stages.indexOf(activeStage);

  const Node = ({ stage, icon, title, desc }) => (
    <div
      className={`workflow-node ${
        isActive(stage)
          ? "active running"
          : isCompleted(stage)
          ? "completed"
          : ""
      }`}
    >
      <div className="workflow-icon">
        {icon}
      </div>

      <div className="workflow-title">
        {title}
      </div>

      <div className="workflow-desc">
        {desc}
      </div>
    </div>
  );

  return (
    <div className="workflow-container">

      {/* Planner */}

      <Node
        stage="Planner"
        icon="🤖"
        title="Planner"
        desc="Analyze User Goal"
      />

      <div className="workflow-line"></div>

      {/* Task Splitter */}

      <Node
        stage="Task Splitter"
        icon="📋"
        title="Task Splitter"
        desc="Split into Parallel Tasks"
      />

      <div className="workflow-line"></div>

      {/* Parallel Research */}

      <div className="parallel-wrapper">

        <div className="parallel-row">

          <Node
            stage="Research Agent 1"
            icon="🔍"
            title="Research Agent 1"
            desc="Collect Information"
          />

          <Node
            stage="Research Agent 2"
            icon="🔎"
            title="Research Agent 2"
            desc="Validate Sources"
          />

        </div>
                <div className="workflow-line"></div>

      </div>

      {/* Summarizer */}

      <Node
        stage="Summarizer"
        icon="📝"
        title="Summarizer"
        desc="Merge Research Results"
      />

      <div className="workflow-line"></div>

      {/* Verifier */}

      <Node
        stage="Verifier"
        icon="✅"
        title="Verifier"
        desc="Verify & Finalize Response"
      />

    </div>
  );
};

export default WorkflowGraph;