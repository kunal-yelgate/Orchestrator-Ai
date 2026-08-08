import "./WorkflowGraph.css";

<<<<<<< HEAD
const WorkflowGraph = ({ activeStage, tasks = [] }) => {

  const isResearchStage = (stage) =>
    stage.startsWith("Research");

  const Node = ({ stage, icon, title, desc, active, completed }) => (
    <div
      className={`workflow-node ${
        active
          ? "active running"
          : completed
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
  );  return (
    <div className="workflow-container">

      {/* Planner */}
=======
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

>>>>>>> e94346cfcadddf8d394baf03670753eda76980c0
      <Node
        stage="Planner"
        icon="🤖"
        title="Planner"
        desc="Analyze User Goal"
<<<<<<< HEAD
        active={activeStage === "Planner"}
        completed={
          activeStage !== "Planner"
        }
=======
        status={statusFor("Planner")}
        isRevertTarget={revertableStage === "Planner"}
        onNodeClick={onNodeClick}
>>>>>>> e94346cfcadddf8d394baf03670753eda76980c0
      />

      <div className="workflow-line"></div>

<<<<<<< HEAD
      {/* Task Splitter */}
=======
>>>>>>> e94346cfcadddf8d394baf03670753eda76980c0
      <Node
        stage="Task Splitter"
        icon="📋"
        title="Task Splitter"
<<<<<<< HEAD
        desc="Split into Tasks"
        active={activeStage === "Task Splitter"}
        completed={
          activeStage !== "Planner" &&
          activeStage !== "Task Splitter"
        }
=======
        desc="Split into Parallel Tasks"
        status={statusFor("Task Splitter")}
        isRevertTarget={revertableStage === "Task Splitter"}
        onNodeClick={onNodeClick}
>>>>>>> e94346cfcadddf8d394baf03670753eda76980c0
      />

      <div className="workflow-line"></div>

<<<<<<< HEAD
      {/* Dynamic Research Agents */}
=======
      {/* Parallel Research */}
>>>>>>> e94346cfcadddf8d394baf03670753eda76980c0
      <div className="parallel-wrapper">
        <div className="parallel-row">
<<<<<<< HEAD

          {tasks.length > 0 ? (

            tasks.map((task, index) => (

              <Node
                key={task.id || index}
                stage={`Research Agent ${index + 1}`}
                icon="🔍"
                title={task.title}
                desc={task.specialization || "Research"}
                active={
                  activeStage === `Research Agent ${index + 1}`
                }
                completed={
                  isResearchStage(activeStage) &&
                  activeStage !== `Research Agent ${index + 1}`
                }
              />

            ))

          ) : (

            <Node
              stage="Research"
              icon="🔍"
              title="Waiting..."
              desc="No Tasks Generated"
              active={false}
              completed={false}
            />

          )}

        </div>

      </div>

      <div className="workflow-line"></div>

      {/* Summarizer */}
=======
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

>>>>>>> e94346cfcadddf8d394baf03670753eda76980c0
      <Node
        stage="Summarizer"
        icon="📝"
        title="Summarizer"
        desc="Merge Research Results"
<<<<<<< HEAD
        active={activeStage === "Summarizer"}
        completed={activeStage === "Verifier"}
=======
        status={statusFor("Summarizer")}
        isRevertTarget={revertableStage === "Summarizer"}
        onNodeClick={onNodeClick}
>>>>>>> e94346cfcadddf8d394baf03670753eda76980c0
      />

      <div className="workflow-line"></div>

<<<<<<< HEAD
      {/* Verifier */}
=======
>>>>>>> e94346cfcadddf8d394baf03670753eda76980c0
      <Node
        stage="Verifier"
        icon="✅"
        title="Verifier"
<<<<<<< HEAD
        desc="Verify Final Answer"
        active={activeStage === "Verifier"}
        completed={false}
=======
        desc="Verify & Finalize Response"
        status={statusFor("Verifier")}
        isRevertTarget={revertableStage === "Verifier"}
        onNodeClick={onNodeClick}
>>>>>>> e94346cfcadddf8d394baf03670753eda76980c0
      />

      <p className="workflow-hint">Click any completed node to revert &amp; continue from there</p>

    </div>
  );
};

export default WorkflowGraph;
