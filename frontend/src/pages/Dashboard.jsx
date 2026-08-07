import React, { useState } from "react";

const historyItems = [
  {
    title: "Product launch plan",
    time: "10m ago",
    preview: "Research completed and summarized",
    tag: "Growth",
  },
  {
    title: "Market analysis",
    time: "1h ago",
    preview: "Verified with three models",
    tag: "Strategy",
  },
  {
    title: "Customer support flow",
    time: "Yesterday",
    preview: "Planner routed the request",
    tag: "Ops",
  },
];

const workflowStages = [
  {
    name: "Intent Planning",
    detail: "Classifies the request and defines a strategy",
    model: "GPT-4.1",
  },
  {
    name: "Evidence Research",
    detail: "Collects supporting evidence and context",
    model: "Gemini 2.5 Pro",
  },
  {
    name: "Response Synthesis",
    detail: "Combines findings into a structured answer",
    model: "Claude 3.7",
  },
  {
    name: "Quality Verification",
    detail: "Checks consistency, safety, and completeness",
    model: "Hybrid review",
  },
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
];

const Dashboard = ({ backendStatus, currentUser, onBack }) => {
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
  const [activeStage, setActiveStage] = useState("Evidence Research");
  const [selectedModel, setSelectedModel] = useState("Auto");

  const handleSubmit = (event) => {
    event.preventDefault();
    if (!input.trim() || isThinking) return;

    const userMessage = {
      id: Date.now(),
      role: "user",
      text: input.trim(),
      meta: `Requested: ${selectedModel}`,
    };
    setMessages((current) => [...current, userMessage]);
    setInput("");
    setIsThinking(true);

    window.setTimeout(() => {
      const currentStage = workflowStages.find(
        (stage) => stage.name === activeStage,
      );
      const currentIndex = workflowStages.findIndex(
        (stage) => stage.name === activeStage,
      );
      const updatedStage =
        workflowStages[(currentIndex + 1) % workflowStages.length];
      setActiveStage(updatedStage.name);

      const modelUsed =
        selectedModel === "Auto" ? updatedStage.model : selectedModel;
      const assistantMessage = {
        id: Date.now() + 1,
        role: "assistant",
        text: `The orchestrator has advanced to ${updatedStage.name}. ${currentStage?.detail ?? "The workflow is progressing"} and ${modelUsed} is now handling the next phase of execution.`,
        meta: `${updatedStage.name} • ${modelUsed}`,
      };

      setMessages((current) => [...current, assistantMessage]);
      setIsThinking(false);
    }, 900);
  };

  return (
    <div className="app-shell">
      <aside className="sidebar">
        <div className="brand-block">
          <div className="brand-icon">✦</div>
          <div>
            <p className="eyebrow">AI Orchestrator</p>
            <h1>Multi-model workspace</h1>
          </div>
        </div>

        <div className="sidebar-card">
          <div className="section-title">Recent history</div>
          <div className="history-list">
            {historyItems.map((item) => (
              <button key={item.title} className="history-item" type="button">
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
          <div className="section-title">Execution snapshot</div>
          <div className="metric-grid">
            <div className="metric-box">
              <strong>3</strong>
              <span>Models</span>
            </div>
            <div className="metric-box">
              <strong>4</strong>
              <span>Stages</span>
            </div>
            <div className="metric-box">
              <strong>100%</strong>
              <span>Traceable</span>
            </div>
          </div>
        </div>
      </aside>

      <main className="workspace">
        <header className="topbar">
          <div className="topbar-copy">
            <p className="eyebrow">Live orchestrator</p>
            <h2>
              Professional multi-model execution with traceable workflow stages
            </h2>
            <p className="topbar-subtitle">
              Intent planning, evidence research, synthesis, and validation run
              in sequence for accurate results.
            </p>
          </div>
          <div className="topbar-actions">
            <div className="user-badge">
              <span>
                {currentUser?.name
                  ? `Signed in as ${currentUser.name}`
                  : currentUser?.email}
              </span>
            </div>
            <button className="secondary-btn compact" onClick={onBack}>
              Logout
            </button>
            <select
              className="model-select"
              value={selectedModel}
              onChange={(e) => setSelectedModel(e.target.value)}
              aria-label="Select model"
            >
              <option value="Auto">Auto (stage)</option>
              {modelPool.map((m) => (
                <option key={m.name} value={m.name}>
                  {m.name}
                </option>
              ))}
            </select>
            <div
              className={`status-pill ${backendStatus === "Backend offline" ? "offline" : ""}`}
            >
              ● {backendStatus}
            </div>
          </div>
        </header>

        <div className="workspace-grid">
          <section className="chat-panel">
            <div className="message-list">
              {messages.map((message) => (
                <div key={message.id} className={`message-row ${message.role}`}>
                  <div className="avatar">
                    {message.role === "user" ? "U" : "O"}
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
                  <div className="avatar">O</div>
                  <div className="bubble thinking">
                    <p>Orchestrator is reasoning across the model pool…</p>
                  </div>
                </div>
              )}
            </div>

            <div className="prompt-row">
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
                type="text"
                value={input}
                onChange={(event) => setInput(event.target.value)}
                placeholder="Ask the orchestrator to analyze, compare, or synthesize..."
                aria-label="User prompt"
              />
              <button type="submit">Send</button>
            </form>
          </section>

          <aside className="insight-panel">
            <div className="info-card">
              <div className="section-title">LangGraph flow</div>
              <div className="flow-rail">
                {workflowStages.map((stage) => (
                  <div
                    key={stage.name}
                    className={`flow-step ${stage.name === activeStage ? "active" : ""}`}
                  >
                    <span className="step-dot" />
                    <div>
                      <strong>{stage.name}</strong>
                      <p>{stage.detail}</p>
                    </div>
                  </div>
                ))}
              </div>
            </div>

            <div className="info-card">
              <div className="section-title">Model pool</div>
              <div className="model-list">
                {modelPool.map((model) => (
                  <div key={model.name} className="model-pill">
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
