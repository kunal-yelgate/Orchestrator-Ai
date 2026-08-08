import WorkflowGraph from "../components/WorkflowGraph";
import { orchestrate } from "../services/api";
import React, { useEffect, useRef, useState } from "react";

const historyItems = [
  { title: "Product launch plan", time: "10m ago", preview: "Research completed and summarized", tag: "Growth" },
  { title: "Market analysis", time: "1h ago", preview: "Verified with three models", tag: "Strategy" },
  { title: "Customer support flow", time: "Yesterday", preview: "Planner routed the request", tag: "Ops" },
];

const workflowStages = [
  { name: "Planner", detail: "Analyzes the user goal.", icon: "🤖" },
  { name: "Task Splitter", detail: "Breaks the goal into subtasks.", icon: "📋" },
  { name: "Research Agent 1", detail: "Researches the first task.", icon: "🔍" },
  { name: "Research Agent 2", detail: "Researches the second task.", icon: "🔍" },
  { name: "Summarizer", detail: "Combines all research.", icon: "📝" },
  { name: "Verifier", detail: "Validates the final output.", icon: "✅" },
];

const modelPool = [
  { name: "GPT-4.1", role: "Planning" },
  { name: "Gemini 2.5 Pro", role: "Research" },
  { name: "Claude 3.7", role: "Synthesis" },
];

const promptSuggestions = [
  "Compare two product strategies",
  "Draft a research-backed roadmap",
  "Summarize this workflow clearly",
  "Analyze market competitors",
];

const Dashboard = ({ backendStatus, currentUser = {}, onBack }) => {
  const [messages, setMessages] = useState([
    {
      id: 1,
      role: "assistant",
      text: "Hello! I can help you plan, research, and verify any request. Ask me anything and I will orchestrate the response through multiple specialist models.",
      meta: "Orchestrator ready",
    },
  ]);

  const [input, setInput] = useState("");
  const [isThinking, setIsThinking] = useState(false);
  const [activeStage, setActiveStage] = useState("Planner");
  const [selectedModel, setSelectedModel] = useState("Auto");
  const [workflow, setWorkflow] = useState(null);

  const [metrics, setMetrics] = useState({
    execution_time: 0,
    total_tokens: 0,
    prompt_tokens: 0,
    completion_tokens: 0,
    estimated_cost: 0,
    provider: "",
    model: "",
  });

  const messagesEndRef = useRef(null);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, isThinking]);

  const activeStageObj = workflowStages.find(
    (stage) => stage.name === activeStage
  );

  const activeIndex = workflowStages.findIndex(
    (stage) => stage.name === activeStage
  );

  const handleSubmit = async (event) => {
    event.preventDefault();

    if (!input.trim() || isThinking) return;

    const goal = input.trim();

    setMessages((previousMessages) => [
      ...previousMessages,
      {
        id: Date.now(),
        role: "user",
        text: goal,
        meta: `Model: ${selectedModel}`,
      },
    ]);

    setInput("");
    setIsThinking(true);

    try {
      setActiveStage("Planner");
      await new Promise((resolve) => setTimeout(resolve, 300));

      setActiveStage("Task Splitter");
      await new Promise((resolve) => setTimeout(resolve, 300));

      const provider =
        selectedModel === "Auto" ? "groq" : selectedModel.toLowerCase();

      const result = await orchestrate(goal, provider);

      console.log("Backend Response:", result);

      setWorkflow(result);

      setMetrics({
        execution_time: result.execution_time ?? 0,
        total_tokens: result.total_tokens ?? 0,
        prompt_tokens: result.prompt_tokens ?? 0,
        completion_tokens: result.completion_tokens ?? 0,
        estimated_cost: result.estimated_cost ?? 0,
        provider: result.provider ?? "",
        model: result.model ?? "",
      });

      const workflowTasks = result.tasks || [];

      for (let index = 0; index < workflowTasks.length; index += 1) {
        setActiveStage(`Research Agent ${index + 1}`);
        await new Promise((resolve) => setTimeout(resolve, 400));
      }

      setActiveStage("Summarizer");
      await new Promise((resolve) => setTimeout(resolve, 400));

      setActiveStage("Verifier");
      await new Promise((resolve) => setTimeout(resolve, 400));

      let reply = "Workflow completed successfully.";

      if (typeof result.summary === "string") {
        reply = result.summary;
      } else if (result.summary?.summary) {
        reply = result.summary.summary;
      }

      setMessages((previousMessages) => [
        ...previousMessages,
        {
          id: Date.now() + 1,
          role: "assistant",
          text: reply,
          meta: result.verification?.verified
            ? `Verified ✅ (${Math.round(
                (result.verification.confidence || 0) * 100
              )}%)`
            : "Completed",
        },
      ]);
    } catch (error) {
      console.error(error);

      setMessages((previousMessages) => [
        ...previousMessages,
        {
          id: Date.now() + 1,
          role: "assistant",
          text: error.message || "Failed to connect to backend.",
          meta: "Error",
        },
      ]);
    } finally {
      setIsThinking(false);
    }
  };

  return (
    <div className="app-shell">
      <aside className="sidebar" aria-label="Navigation sidebar">
        <div className="brand-block">
          <div className="brand-icon" aria-hidden="true">✦</div>
          <div>
            <p className="eyebrow">Orchestrator AI</p>
            <h1>Multi-model workspace</h1>
          </div>
        </div>

        <div className="sidebar-card">
          <div className="section-title">Recent history</div>

          <div className="history-list" role="list">
            {historyItems.map((item) => (
              <button
                key={item.title}
                className="history-item"
                type="button"
                role="listitem"
                aria-label={`Open ${item.title}`}
              >
                <div className="history-top">
                  <span>{item.title}</span>
                  <span className="history-tag">{item.tag}</span>
                </div>
                <small>{item.time}</small>
                <p>{item.preview}</p>
              </button>
            ))}
          </div>
        </div>

        <div className="sidebar-card metrics-card">
          <div className="section-title">Live metrics</div>

          <div className="metric-grid">
            <div className="metric-box">
              <strong>{metrics.execution_time.toFixed(2)}s</strong>
              <span>Execution</span>
            </div>

            <div className="metric-box">
              <strong>{metrics.total_tokens}</strong>
              <span>Tokens</span>
            </div>

            <div className="metric-box">
              <strong>${metrics.estimated_cost}</strong>
              <span>Cost</span>
            </div>

            <div className="metric-box">
              <strong>{metrics.provider || "-"}</strong>
              <span>Provider</span>
            </div>

            <div className="metric-box">
              <strong>{metrics.model || "-"}</strong>
              <span>Model</span>
            </div>
          </div>
        </div>

        <div className="sidebar-card active-stage-card">
          <div className="section-title">Active stage</div>

          <div
            className="active-stage-display"
            aria-live="polite"
            aria-label={`Active stage: ${activeStage}`}
          >
            <div className="active-stage-icon" aria-hidden="true">
              {activeStageObj?.icon}
            </div>

            <div>
              <strong className="active-stage-name">{activeStage}</strong>
              <p className="active-stage-detail">{activeStageObj?.detail}</p>
            </div>
          </div>

          <div
            className="stage-progress"
            aria-label={`Stage ${activeIndex + 1} of ${workflowStages.length}`}
          >
            {workflowStages.map((_, index) => (
              <div
                key={index}
                className={`progress-dot ${
                  index === activeIndex
                    ? "active"
                    : index < activeIndex
                    ? "done"
                    : ""
                }`}
                aria-hidden="true"
              />
            ))}
          </div>
        </div>
      </aside>

      <main className="workspace" aria-label="AI orchestration workspace">
        <header className="topbar">
          <div className="topbar-copy">
            <p className="eyebrow">Live orchestrator</p>
            <h2>Professional multi-model execution</h2>
            <p className="topbar-subtitle">
              Intent planning → research → synthesis → verification
            </p>
          </div>

          <div className="topbar-actions">
            <div
              className="user-badge"
              aria-label={`Signed in as ${
                currentUser?.name || currentUser?.email
              }`}
            >
              {currentUser?.name || currentUser?.email?.split("@")[0]}
            </div>

            <label htmlFor="model-select" className="sr-only">
              Select AI model
            </label>

            <select
              id="model-select"
              className="model-select"
              value={selectedModel}
              onChange={(event) => setSelectedModel(event.target.value)}
            >
              <option value="Auto">⚡ Auto (stage)</option>
              {modelPool.map((model) => (
                <option key={model.name} value={model.name}>
                  {model.name}
                </option>
              ))}
            </select>

            <div
              className={`status-pill ${
                backendStatus === "Backend offline" ? "offline" : ""
              }`}
              role="status"
              aria-label={backendStatus}
            >
              {backendStatus}
            </div>

            <button
              id="logout-btn"
              className="secondary-btn compact"
              onClick={onBack}
              aria-label="Logout"
            >
              Logout
            </button>
          </div>
        </header>

        <div className="workspace-grid">
          <section className="chat-panel" aria-label="Chat conversation">
            <div
              className="message-list"
              role="log"
              aria-live="polite"
              aria-label="Conversation messages"
            >
              {messages.map((message) => (
                <div
                  key={message.id}
                  className={`message-row ${message.role}`}
                  aria-label={`${
                    message.role === "user" ? "You" : "Orchestrator"
                  }: ${message.text}`}
                >
                  <div className="avatar" aria-hidden="true">
                    {message.role === "user" ? "U" : "AI"}
                  </div>

                  <div className="bubble">
                    {message.meta && (
                      <div className="message-meta">{message.meta}</div>
                    )}
                    <p>{message.text}</p>
                  </div>
                </div>
              ))}

              {isThinking && (
                <div className="message-row assistant">
                  <div className="avatar" aria-hidden="true">AI</div>

                  <div className="bubble thinking">
                    <div className="message-meta">
                      Routing across model pool…
                    </div>

                    <div className="thinking-dots" aria-hidden="true">
                      <span />
                      <span />
                      <span />
                    </div>
                  </div>
                </div>
              )}

              <div ref={messagesEndRef} />
            </div>

            <div className="prompt-row" role="group" aria-label="Prompt suggestions">
              {promptSuggestions.map((suggestion) => (
                <button
                  key={suggestion}
                  type="button"
                  className="prompt-chip"
                  onClick={() => setInput(suggestion)}
                >
                  {suggestion}
                </button>
              ))}
            </div>

            <form className="composer" onSubmit={handleSubmit}>
              <input
                id="chat-input"
                type="text"
                value={input}
                onChange={(event) => setInput(event.target.value)}
                placeholder="Ask the orchestrator to analyze, compare, or synthesize…"
                aria-label="Type your message"
                disabled={isThinking}
                autoComplete="off"
              />

              <button
                id="send-btn"
                type="submit"
                disabled={isThinking || !input.trim()}
              >
                {isThinking ? "…" : "Send ↗"}
              </button>
            </form>
          </section>

          <aside className="insight-panel" aria-label="Workflow insight panel">
            <div className="info-card">
              <div className="section-title">LangGraph Flow</div>
              <WorkflowGraph
                activeStage={activeStage}
                tasks={workflow?.tasks || []}
              />
            </div>

            <div className="metric-card">
              <h4>Retries</h4>
              <p>{workflow?.retry_count || 0}</p>
            </div>

            <div className="metric-card">
              <h4>Budget</h4>

              <p>
                {workflow?.budget?.used_tokens || 0}
                {" / "}
                {workflow?.budget?.max_tokens || 0}
              </p>

              <div className="budget-bar">
                <div
                  className="budget-fill"
                  style={{
                    width: `${workflow?.budget?.utilization || 0}%`,
                    width: `${Math.min(workflow?.budget?.utilization || 0, 100)}%`,
                  }}
                />
              </div>
            </div>

            <div className="info-card">
              <div className="section-title">Model Pool</div>

              <div className="model-list" role="list">
                {modelPool.map((model) => (
                  <div
                    key={model.name}
                    className="model-pill"
                    role="listitem"
                    aria-label={`${model.name} — ${model.role}`}
                  >
                    <span>{model.name}</span>
                    <small>{model.role}</small>
                  </div>
                ))}
              </div>
            </div>
          </aside>
        </div>
      </main>
    </div>
  );
};

export default Dashboard;