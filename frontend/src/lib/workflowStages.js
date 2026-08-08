// Maps a graph stage label (shown in the UI) to the backend's
// checkpoint agent_name (see backend/graph/runner.py NODE_SEQUENCE).
// Used so clicking a node can look up its checkpoint by agent_name,
// and so a rollback/orchestrate response can re-sync the graph.
export const STAGE_TO_AGENT = {
  "Planner": "Planner",
  "Task Splitter": "TaskSplitter",
  "Research Agent 1": "ResearchAgent1",
  "Research Agent 2": "ResearchAgent2",
  "Summarizer": "Summarizer",
  "Verifier": "Verifier",
};

export const AGENT_TO_STAGE = Object.fromEntries(
  Object.entries(STAGE_TO_AGENT).map(([stage, agent]) => [agent, stage])
);
