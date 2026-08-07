import React from "react";
import "./WorkflowGraph.css";

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
      <Node
        stage="Planner"
        icon="🤖"
        title="Planner"
        desc="Analyze User Goal"
        active={activeStage === "Planner"}
        completed={
          activeStage !== "Planner"
        }
      />

      <div className="workflow-line"></div>

      {/* Task Splitter */}
      <Node
        stage="Task Splitter"
        icon="📋"
        title="Task Splitter"
        desc="Split into Tasks"
        active={activeStage === "Task Splitter"}
        completed={
          activeStage !== "Planner" &&
          activeStage !== "Task Splitter"
        }
      />

      <div className="workflow-line"></div>

      {/* Dynamic Research Agents */}
      <div className="parallel-wrapper">

        <div className="parallel-row">

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
      <Node
        stage="Summarizer"
        icon="📝"
        title="Summarizer"
        desc="Merge Research Results"
        active={activeStage === "Summarizer"}
        completed={activeStage === "Verifier"}
      />

      <div className="workflow-line"></div>

      {/* Verifier */}
      <Node
        stage="Verifier"
        icon="✅"
        title="Verifier"
        desc="Verify Final Answer"
        active={activeStage === "Verifier"}
        completed={false}
      />

    </div>
  );
};

export default WorkflowGraph;