import "./WorkflowGraph.css";

const STAGES = [
  "Planner",
  "Task Splitter",
  "Research Agent 1",
  "Research Agent 2",
  "Summarizer",
  "Verifier",
];

// Declared outside WorkflowGraph so it isn't re-created every render.
const Node = ({ stage, icon, title, desc, status, isRevertTarget, onNodeClick }) => (
  <div
    className={`workflow-node ${
      status === "active" ? "active running" : status === "completed" ? "completed" : ""
    } ${isRevertTarget ? "revert-target" : ""}`}
    role="button"
    tabIndex={0}
    title={
      status === "active" || status === "completed"
        ? `Revert to ${title} and continue from here`
        : undefined
    }
    onClick={() => onNodeClick?.(stage)}
    onKeyDown={(e) => {
      if (e.key === "Enter" || e.key === " ") {
        e.preventDefault();
        onNodeClick?.(stage);
      }
    }}
  >
    <div className="workflow-icon">{icon}</div>
    <div className="workflow-title">{title}</div>
    <div className="workflow-desc">{desc}</div>
  </div>
);

const WorkflowGraph = ({ activeStage, onNodeClick, revertableStage }) => {
  const statusFor = (stage) => {
    if (activeStage === stage) return "active";
    if (STAGES.indexOf(stage) < STAGES.indexOf(activeStage)) return "completed";
    return "";
  };

  return (
    <div className="workflow-container">

      <Node
        stage="Planner"
        icon="🤖"
        title="Planner"
        desc="Analyze User Goal"
        status={statusFor("Planner")}
        isRevertTarget={revertableStage === "Planner"}
        onNodeClick={onNodeClick}
      />

      <div className="workflow-line"></div>

      <Node
        stage="Task Splitter"
        icon="📋"
        title="Task Splitter"
        desc="Split into Parallel Tasks"
        status={statusFor("Task Splitter")}
        isRevertTarget={revertableStage === "Task Splitter"}
        onNodeClick={onNodeClick}
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
            status={statusFor("Research Agent 1")}
            isRevertTarget={revertableStage === "Research Agent 1"}
            onNodeClick={onNodeClick}
          />

          <Node
            stage="Research Agent 2"
            icon="🔎"
            title="Research Agent 2"
            desc="Validate Sources"
            status={statusFor("Research Agent 2")}
            isRevertTarget={revertableStage === "Research Agent 2"}
            onNodeClick={onNodeClick}
          />
        </div>
        <div className="workflow-line"></div>
      </div>

      <Node
        stage="Summarizer"
        icon="📝"
        title="Summarizer"
        desc="Merge Research Results"
        status={statusFor("Summarizer")}
        isRevertTarget={revertableStage === "Summarizer"}
        onNodeClick={onNodeClick}
      />

      <div className="workflow-line"></div>

      <Node
        stage="Verifier"
        icon="✅"
        title="Verifier"
        desc="Verify & Finalize Response"
        status={statusFor("Verifier")}
        isRevertTarget={revertableStage === "Verifier"}
        onNodeClick={onNodeClick}
      />

      <p className="workflow-hint">Click any completed node to revert &amp; continue from there</p>

    </div>
  );
};

export default WorkflowGraph;
