import { orchestrate } from "../services/api";
import React, { useState, useRef, useEffect } from "react";

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
    icon: "◈",
  },
  {
    name: "Evidence Research",
    detail: "Collects supporting evidence and context",
    model: "Gemini 2.5 Pro",
    icon: "⬡",
  },
  {
    name: "Response Synthesis",
    detail: "Combines findings into a structured answer",
    model: "Claude 3.7",
    icon: "◆",
  },
  {
    name: "Quality Verification",
    detail: "Checks consistency, safety, and completeness",
    model: "Hybrid review",
    icon: "✦",
  },
];

const modelPool = [
  { name: "GPT-4.1", role: "Planning", color: "#10b981" },
  { name: "Gemini 2.5 Pro", role: "Research", color: "#818cf8" },
  { name: "Claude 3.7", role: "Synthesis", color: "#f59e0b" },
];

const promptSuggestions = [
  "Compare two product strategies",
  "Draft a research-backed roadmap",
  "Summarize this workflow clearly",
  "Analyze market competitors",
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
  const messagesEndRef = useRef(null);

  // Auto-scroll to bottom on new messages
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, isThinking]);

  
  const activeStageObj = workflowStages.find((s) => s.name === activeStage);
  const activeIndex = workflowStages.findIndex((s) => s.name === activeStage);
  
  const handleSubmit = async (event) => {
  event.preventDefault();

  if (!input.trim() || isThinking) return;

  const goal = input.trim();

  const userMessage = {
    id: Date.now(),
    role: "user",
    text: goal,
    meta: `Model: ${selectedModel}`,
  };

  setMessages((prev) => [...prev, userMessage]);
  setInput("");
  setIsThinking(true);

  try {
    // Stage 1
    setActiveStage("Intent Planning");

    const provider =
      selectedModel === "Auto"
        ? "groq"
        : selectedModel.toLowerCase();

    // ===========================
    // Call FastAPI Backend
    // ===========================
    const result = await orchestrate(
      goal,
      provider
    );

    console.log("Backend Response:", result);

    // Stage 2
    setActiveStage("Evidence Research");
    await new Promise((resolve) => setTimeout(resolve, 300));

    // Stage 3
    setActiveStage("Response Synthesis");
    await new Promise((resolve) => setTimeout(resolve, 300));

    // Stage 4
    setActiveStage("Quality Verification");

    let reply = "Workflow completed successfully.";

    if (result.summary) {
      if (typeof result.summary === "string") {
        reply = result.summary;
      } else if (result.summary.summary) {
        reply = result.summary.summary;
      }
    }

    const assistantMessage = {
      id: Date.now() + 1,
      role: "assistant",
      text: reply,
      meta:
        result.verification?.verified
          ? `Verified ✅ (${Math.round(
              (result.verification.confidence || 0) * 100
            )}%)`
          : "Completed",
    };

    setMessages((prev) => [
      ...prev,
      assistantMessage,
    ]);

  } catch (error) {
    console.error(error);

    setMessages((prev) => [
      ...prev,
      {
        id: Date.now() + 1,
        role: "assistant",
        text:
          error.message ||
          "Failed to connect to backend.",
        meta: "Error",
      },
    ]);
  } finally {
    setIsThinking(false);
  }
};



  return (
    <div className="app-shell">
      {/* ── Sidebar ─────────────────────────────────────────── */}
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
              <strong>3</strong>
              <span>Models</span>
            </div>
            <div className="metric-box">
              <strong>4</strong>
              <span>Stages</span>
            </div>
            <div className="metric-box">
              <strong>100%</strong>
              <span>Traced</span>
            </div>
          </div>
        </div>

        {/* Active stage indicator */}
        <div className="sidebar-card active-stage-card">
          <div className="section-title">Active stage</div>
          <div className="active-stage-display" aria-live="polite" aria-label={`Active stage: ${activeStage}`}>
            <div className="active-stage-icon" aria-hidden="true">{activeStageObj?.icon}</div>
            <div>
              <strong className="active-stage-name">{activeStage}</strong>
              <p className="active-stage-detail">{activeStageObj?.detail}</p>
            </div>
          </div>
          <div className="stage-progress" aria-label={`Stage ${activeIndex + 1} of ${workflowStages.length}`}>
            {workflowStages.map((_, i) => (
              <div
                key={i}
                className={`progress-dot ${i === activeIndex ? "active" : i < activeIndex ? "done" : ""}`}
                aria-hidden="true"
              />
            ))}
          </div>
        </div>
      </aside>

      {/* ── Main workspace ───────────────────────────────────── */}
      <main className="workspace" aria-label="AI orchestration workspace">
        {/* Top bar */}
        <header className="topbar">
          <div className="topbar-copy">
            <p className="eyebrow">Live orchestrator</p>
            <h2>Professional multi-model execution</h2>
            <p className="topbar-subtitle">
              Intent planning → research → synthesis → verification
            </p>
          </div>
          <div className="topbar-actions">
            <div className="user-badge" aria-label={`Signed in as ${currentUser?.name || currentUser?.email}`}>
              {currentUser?.name
                ? currentUser.name
                : currentUser?.email?.split("@")[0]}
            </div>
            <label htmlFor="model-select" className="sr-only">Select AI model</label>
            <select
              id="model-select"
              className="model-select"
              value={selectedModel}
              onChange={(e) => setSelectedModel(e.target.value)}
            >
              <option value="Auto">⚡ Auto (stage)</option>
              {modelPool.map((m) => (
                <option key={m.name} value={m.name}>
                  {m.name}
                </option>
              ))}
            </select>
            <div
              className={`status-pill ${backendStatus === "Backend offline" ? "offline" : ""}`}
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

        {/* Grid: chat + insight */}
        <div className="workspace-grid">
          {/* Chat panel */}
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
                  aria-label={`${message.role === "user" ? "You" : "Orchestrator"}: ${message.text}`}
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
                <div className="message-row assistant" aria-label="Orchestrator is thinking">
                  <div className="avatar" aria-hidden="true">AI</div>
                  <div className="bubble thinking">
                    <div className="message-meta">Routing across model pool…</div>
                    <div className="thinking-dots" aria-hidden="true">
                      <span /><span /><span />
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
                  aria-label={`Use prompt: ${suggestion}`}
                >
                  {suggestion}
                </button>
              ))}
            </div>

            <form
              className="composer"
              onSubmit={handleSubmit}
              aria-label="Message composer"
            >
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
                aria-label="Send message"
              >
                {isThinking ? "…" : "Send ↗"}
              </button>
            </form>
          </section>

          {/* Insight panel */}
          <aside className="insight-panel" aria-label="Workflow insight panel">
            <div className="info-card">
              <div className="section-title">LangGraph flow</div>
              <div className="flow-rail" role="list">
                {workflowStages.map((stage) => (
                  <div
                    key={stage.name}
                    className={`flow-step ${stage.name === activeStage ? "active" : ""}`}
                    role="listitem"
                    aria-current={stage.name === activeStage ? "step" : undefined}
                  >
                    <span className="step-dot" aria-hidden="true" />
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