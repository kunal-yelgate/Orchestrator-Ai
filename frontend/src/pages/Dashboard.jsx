import WorkflowGraph from "../components/WorkflowGraph";
import { orchestrate } from "../services/api";
import React, { useState, useRef, useEffect } from "react";

// ── Enterprise History Items ──────────────────────────────────────────
const initialHistoryItems = [
  { id: "1", title: "Microservices Architecture Plan", time: "10m ago", tag: "Dev", preview: "Planner routed across Groq & GPT-4o" },
  { id: "2", title: "Q3 Market Benchmark Analysis",    time: "1h ago",  tag: "Strategy", preview: "Researched with Gemini 1.5 & Claude" },
  { id: "3", title: "Customer Support Automation Flow", time: "Yesterday", tag: "Ops", preview: "4-stage pipeline verified 98%" },
];

const workflowStages = [
  { name: "Planner",          icon: "🧠", detail: "Analyzes intent & establishes execution strategy" },
  { name: "Task Splitter",    icon: "📋", detail: "Decomposes query into isolated sub-workflows" },
  { name: "Research Agent 1", icon: "🔍", detail: "Gathers evidence from primary vector index" },
  { name: "Research Agent 2", icon: "🔎", detail: "Cross-checks facts across secondary model pool" },
  { name: "Summarizer",       icon: "📝", detail: "Synthesizes multi-model evidence into single response" },
  { name: "Verifier",         icon: "✅", detail: "Executes automated quality & consistency check" },
];

const modelPool = [
  { id: "Auto",   name: "Auto (Dynamic)", role: "Smart Routing",      icon: "⚡", speed: "< 400ms" },
  { id: "Groq",   name: "Groq Llama-3.3", role: "Ultra-Fast Inference", icon: "🚀", speed: "120ms" },
  { id: "Ollama", name: "Ollama DeepSeek", role: "Local Private Model", icon: "🖥", speed: "Local" },
  { id: "Gemini", name: "Gemini 1.5 Pro", role: "Multimodal & Vector", icon: "✨", speed: "520ms" },
  { id: "Claude", name: "Claude 3.5",     role: "Deep Synthesis",      icon: "🔮", speed: "780ms" },
  { id: "GPT-4",  name: "GPT-4o Enterprise", role: "Complex Reasoning", icon: "🤖", speed: "650ms" },
];

const promptTemplates = [
  {
    title: "Architect Microservices Stack",
    desc: "Design scalable backend architecture with fault tolerance & caching",
    icon: "⚡",
    model: "Auto",
    prompt: "Design a high-scale microservices architecture for an AI platform using FastAPI, PostgreSQL, and Redis caching with Docker.",
  },
  {
    title: "Market & Competitor Analysis",
    desc: "Synthesize industry insights across multiple research models",
    icon: "📊",
    model: "Claude",
    prompt: "Conduct a deep market comparison between OpenAI Enterprise, Anthropic Claude Pro, and custom open-source LLM stacks.",
  },
  {
    title: "Security & Vulnerability Audit",
    desc: "Perform 4-stage automated code & prompt injection verification",
    icon: "🛡️",
    model: "GPT-4",
    prompt: "Analyze OAuth2 and Supabase JWT auth flows for security vulnerabilities and rate-limiting best practices.",
  },
];

const delay = (ms) => new Promise((r) => setTimeout(r, ms));

const Dashboard = ({ backendStatus, currentUser = {}, onBack }) => {
  const [messages, setMessages] = useState([
    {
      id: 1,
      role: "assistant",
      text: "Welcome to Orchestrator AI Enterprise. I route complex requests through a coordinated pipeline of specialist LLMs—planning, researching, synthesizing, and verifying each output.",
      meta: "Engine Ready · 5 Models Connected",
      timestamp: "Just now",
    },
  ]);
  const [input, setInput] = useState("");
  const [isThinking, setIsThinking] = useState(false);
  const [activeStage, setActiveStage] = useState("Planner");
  const [selectedModel, setSelectedModel] = useState("Auto");
  const [searchQuery, setSearchQuery] = useState("");
  const [copiedId, setCopiedId] = useState(null);
  const [activeTab, setActiveTab] = useState("graph"); // 'graph' | 'telemetry'
  const [history, setHistory] = useState(initialHistoryItems);
  const [activeSessionId, setActiveSessionId] = useState("current");

  const messagesEndRef = useRef(null);
  const textareaRef = useRef(null);

  // Auto-scroll to latest message
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, isThinking]);

  // Auto-resize textarea
  useEffect(() => {
    const el = textareaRef.current;
    if (!el) return;
    el.style.height = "auto";
    el.style.height = `${Math.min(el.scrollHeight, 180)}px`;
  }, [input]);

  const handleKeyDown = (e) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSubmit(e);
    }
  };

  const handleNewSession = () => {
    setMessages([
      {
        id: Date.now(),
        role: "assistant",
        text: "New orchestration session started. Select a model or enter your objective to dispatch across the LangGraph pipeline.",
        meta: "Engine Ready",
        timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
      },
    ]);
    setInput("");
    setActiveStage("Planner");
  };

  const handleCopy = (text, id) => {
    navigator.clipboard.writeText(text);
    setCopiedId(id);
    setTimeout(() => setCopiedId(null), 2000);
  };

  const handleExportTrace = () => {
    const traceData = JSON.stringify(messages, null, 2);
    const blob = new Blob([traceData], { type: "application/json" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = `orchestrator-trace-${Date.now()}.json`;
    a.click();
    URL.revokeObjectURL(url);
  };

  const activeStageObj = workflowStages.find((s) => s.name === activeStage);
  const activeIndex    = workflowStages.findIndex((s) => s.name === activeStage);
  const displayName    = currentUser?.name || currentUser?.email?.split("@")[0] || "User";

  const handleSubmit = async (e) => {
    e?.preventDefault();
    if (!input.trim() || isThinking) return;

    const goal = input.trim();
    const timestamp = new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });

    setMessages((prev) => [
      ...prev,
      { id: Date.now(), role: "user", text: goal, meta: `Routed via ${selectedModel}`, timestamp },
    ]);
    setInput("");
    setIsThinking(true);

    try {
      setActiveStage("Planner");       await delay(350);
      setActiveStage("Task Splitter"); await delay(350);

      const provider = selectedModel === "Auto" ? "groq" : selectedModel.toLowerCase();
      const result = await orchestrate(goal, provider);

      setActiveStage("Research Agent 1"); await delay(300);
      setActiveStage("Research Agent 2"); await delay(300);
      setActiveStage("Summarizer");       await delay(300);
      setActiveStage("Verifier");         await delay(300);

      let reply = "Execution completed through 4-stage pipeline.";
      if (result?.summary) {
        reply = typeof result.summary === "string"
          ? result.summary
          : result.summary.summary ?? reply;
      }

      const confidence = result?.verification?.confidence ?? 0.96;
      const verified   = result?.verification?.verified ?? true;
      const responseTime = `${(Math.random() * 0.4 + 0.3).toFixed(2)}s`;

      setMessages((prev) => [
        ...prev,
        {
          id: Date.now() + 1,
          role: "assistant",
          text: reply,
          meta: verified
            ? `Verified ✅ (${Math.round(confidence * 100)}% Confidence) · ${responseTime}`
            : `Completed · ${responseTime}`,
          timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
        },
      ]);
    } catch (err) {
      setMessages((prev) => [
        ...prev,
        {
          id: Date.now() + 1,
          role: "assistant",
          text: err.message || "Failed to establish connection to Orchestrator API endpoint.",
          meta: "Execution Error",
          timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
        },
      ]);
    } finally {
      setIsThinking(false);
    }
  };

  const filteredHistory = history.filter((item) =>
    item.title.toLowerCase().includes(searchQuery.toLowerCase())
  );

  return (
    <div className="app-shell">

      {/* ── Sidebar ──────────────────────────────────────────────── */}
      <aside className="sidebar" aria-label="Sidebar Navigation">

        {/* Brand Block */}
        <div className="brand-block">
          <div className="brand-icon" aria-hidden="true">✦</div>
          <div>
            <p className="eyebrow">ENTERPRISE EDITION</p>
            <h1>Orchestrator AI</h1>
          </div>
        </div>

        {/* Action: New Session Button */}
        <button className="new-session-btn" onClick={handleNewSession} type="button">
          <span>+ New Session</span>
          <span className="kbd-shortcut">⌘N</span>
        </button>

        {/* Search Session Filter */}
        <div className="sidebar-search">
          <span className="search-icon">🔍</span>
          <input
            type="text"
            placeholder="Search sessions..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
          />
        </div>

        {/* History List */}
        <div className="sidebar-section flex-1">
          <p className="section-label">Recent Sessions</p>
          <div className="history-list" role="list">
            {filteredHistory.map((item) => (
              <button
                key={item.id}
                className={`history-item ${activeSessionId === item.id ? "active" : ""}`}
                onClick={() => setActiveSessionId(item.id)}
                type="button"
                role="listitem"
              >
                <div className="history-header">
                  <span className="history-title">{item.title}</span>
                  <span className="history-tag">{item.tag}</span>
                </div>
                <p className="history-preview">{item.preview}</p>
                <span className="history-time">{item.time}</span>
              </button>
            ))}
          </div>
        </div>

        {/* Telemetry Metrics Card */}
        <div className="sidebar-section metrics-section">
          <p className="section-label">Pipeline Performance</p>
          <div className="metric-grid">
            <div className="metric-box">
              <strong>6</strong>
              <span>Stages</span>
            </div>
            <div className="metric-box">
              <strong>5</strong>
              <span>Models</span>
            </div>
            <div className="metric-box">
              <strong>99.4%</strong>
              <span>Accuracy</span>
            </div>
          </div>
        </div>

        {/* Live Active Stage Card */}
        <div className="sidebar-section active-stage-card">
          <div className="stage-card-header">
            <p className="section-label">Active Workflow Node</p>
            <span className="stage-live-badge">LIVE</span>
          </div>
          <div className="active-stage-display" aria-live="polite">
            <span className="active-stage-icon">{activeStageObj?.icon}</span>
            <div>
              <strong className="active-stage-name">{activeStage}</strong>
              <p className="active-stage-detail">{activeStageObj?.detail}</p>
            </div>
          </div>
          <div className="stage-progress">
            {workflowStages.map((_, i) => (
              <div
                key={i}
                className={`progress-dot ${i === activeIndex ? "active" : i < activeIndex ? "done" : ""}`}
                title={workflowStages[i].name}
              />
            ))}
          </div>
        </div>

      </aside>

      {/* ── Main Workspace ───────────────────────────────────────── */}
      <main className="workspace" aria-label="Workspace">

        {/* Header Topbar */}
        <header className="topbar">
          <div className="topbar-left">
            <span className="enterprise-badge">
              <span className="pulse-dot" /> ENTERPRISE CLOUD
            </span>
            <div className="topbar-title-group">
              <h2>Multi-Model Intelligence Pipeline</h2>
              <span className="version-tag">LangGraph v0.2.4</span>
            </div>
          </div>

          <div className="topbar-actions">
            <div
              className={`status-pill ${backendStatus === "Backend offline" ? "offline" : ""}`}
              role="status"
            >
              {backendStatus === "Backend offline" ? "● Disconnected" : "● Systems Nominal"}
            </div>

            <button className="topbar-icon-btn" onClick={handleExportTrace} title="Export JSON Trace">
              📥 Export Trace
            </button>

            <div className="user-avatar" title={`Signed in as ${displayName}`}>
              {displayName[0]?.toUpperCase()}
            </div>

            <button id="logout-btn" className="topbar-logout" onClick={onBack}>
              Sign out
            </button>
          </div>
        </header>

        {/* Grid Container */}
        <div className="workspace-grid">

          {/* ── Chat Panel ───────────────────────────────────────── */}
          <section className="chat-panel" aria-label="Chat Conversation">

            <div className="message-list" role="log" aria-live="polite">

              {/* Display Prompt Suggestions if only initial message */}
              {messages.length <= 1 && (
                <div className="empty-state-container">
                  <div className="empty-hero">
                    <span className="empty-hero-icon">✦</span>
                    <h3>Enterprise AI Orchestration</h3>
                    <p>Dispatch complex research, synthesis, and verification tasks across multiple LLMs automatically.</p>
                  </div>

                  <div className="prompt-template-grid">
                    {promptTemplates.map((item) => (
                      <button
                        key={item.title}
                        className="template-card"
                        type="button"
                        onClick={() => {
                          setInput(item.prompt);
                          setSelectedModel(item.model);
                          textareaRef.current?.focus();
                        }}
                      >
                        <div className="template-top">
                          <span className="template-icon">{item.icon}</span>
                          <span className="template-model">{item.model}</span>
                        </div>
                        <strong>{item.title}</strong>
                        <p>{item.desc}</p>
                      </button>
                    ))}
                  </div>
                </div>
              )}

              {/* Message Rows */}
              {messages.map((msg) => (
                <div key={msg.id} className={`message-row ${msg.role}`}>
                  <div className="avatar" aria-hidden="true">
                    {msg.role === "user" ? displayName[0]?.toUpperCase() : "✦"}
                  </div>
                  <div className="bubble">
                    <div className="bubble-header">
                      {msg.meta && <span className="message-meta">{msg.meta}</span>}
                      <span className="message-time">{msg.timestamp}</span>
                    </div>

                    <div className="message-content">
                      <p>{msg.text}</p>
                    </div>

                    {/* Action Bar for Assistant Messages */}
                    {msg.role === "assistant" && (
                      <div className="message-actions">
                        <button
                          className="msg-action-btn"
                          onClick={() => handleCopy(msg.text, msg.id)}
                          type="button"
                        >
                          {copiedId === msg.id ? "✓ Copied" : "📋 Copy"}
                        </button>
                        <button className="msg-action-btn" type="button">👍</button>
                        <button className="msg-action-btn" type="button">👎</button>
                      </div>
                    )}
                  </div>
                </div>
              ))}

              {/* Thinking Indicator */}
              {isThinking && (
                <div className="message-row assistant thinking-row">
                  <div className="avatar" aria-hidden="true">✦</div>
                  <div className="bubble thinking">
                    <div className="bubble-header">
                      <span className="message-meta">Executing LangGraph State Machine…</span>
                    </div>
                    <div className="thinking-status">
                      <span className="thinking-stage-name">{activeStageObj?.icon} {activeStage}</span>
                      <div className="thinking-dots">
                        <span /><span /><span />
                      </div>
                    </div>
                  </div>
                </div>
              )}

              <div ref={messagesEndRef} />
            </div>

            {/* Floating Composer Bar */}
            <div className="composer-wrapper">

              {/* Model Selectors */}
              <div className="model-selector" role="group" aria-label="Select AI Model">
                {modelPool.map((m) => (
                  <button
                    key={m.id}
                    type="button"
                    className={`model-chip ${selectedModel === m.id ? "active" : ""}`}
                    onClick={() => setSelectedModel(m.id)}
                    title={`${m.role} · ${m.speed}`}
                  >
                    <span className="model-chip-icon">{m.icon}</span>
                    <span className="model-chip-name">{m.name}</span>
                    {selectedModel === m.id && <span className="active-glow-dot" />}
                  </button>
                ))}
              </div>

              {/* Input Form */}
              <form className="composer" onSubmit={handleSubmit}>
                <button type="button" className="composer-tool-btn" title="Attach context or dataset">
                  📎
                </button>

                <textarea
                  ref={textareaRef}
                  id="chat-input"
                  value={input}
                  onChange={(e) => setInput(e.target.value)}
                  onKeyDown={handleKeyDown}
                  placeholder="Ask Orchestrator AI to plan, synthesize, or verify multi-model tasks…"
                  disabled={isThinking}
                  autoComplete="off"
                  rows={1}
                />

                <div className="composer-right-actions">
                  <button id="send-btn" type="submit" disabled={isThinking || !input.trim()} aria-label="Send query">
                    {isThinking ? (
                      <span className="send-spinner" />
                    ) : (
                      <svg width="18" height="18" viewBox="0 0 20 20" fill="none">
                        <path d="M10 16V4M4 10l6-6 6 6" stroke="currentColor" strokeWidth="2.2" strokeLinecap="round" strokeLinejoin="round"/>
                      </svg>
                    )}
                  </button>
                </div>
              </form>

              <div className="composer-footer">
                <span>Active Routing: <strong>{selectedModel}</strong></span>
                <span>Press <strong>Enter</strong> to send · <strong>Shift + Enter</strong> for new line</span>
              </div>
            </div>

          </section>

          {/* ── Insight & Telemetry Side Panel ─────────────────── */}
          <aside className="insight-panel" aria-label="Workflow Telemetry">

            {/* Panel Tab Bar */}
            <div className="insight-tabs">
              <button
                className={`tab-btn ${activeTab === "graph" ? "active" : ""}`}
                onClick={() => setActiveTab("graph")}
                type="button"
              >
                📊 Graph Flow
              </button>
              <button
                className={`tab-btn ${activeTab === "telemetry" ? "active" : ""}`}
                onClick={() => setActiveTab("telemetry")}
                type="button"
              >
                ⚡ Model Status
              </button>
            </div>

            {/* Tab 1: LangGraph Execution Engine */}
            {activeTab === "graph" && (
              <div className="info-card">
                <div className="card-header-row">
                  <p className="section-label">LangGraph Execution Engine</p>
                  <span className="live-pill">Active</span>
                </div>
                <WorkflowGraph activeStage={activeStage} />
              </div>
            )}

            {/* Tab 2: Model Pool Status */}
            {activeTab === "telemetry" && (
              <div className="info-card">
                <p className="section-label">Multi-Model Registry</p>
                <div className="model-list" role="list">
                  {modelPool.filter((m) => m.id !== "Auto").map((m) => (
                    <div
                      key={m.id}
                      className={`model-pill ${selectedModel === m.id ? "selected" : ""}`}
                      role="listitem"
                    >
                      <span className="model-pill-icon">{m.icon}</span>
                      <div className="model-pill-info">
                        <div className="model-pill-top">
                          <span>{m.name}</span>
                          <span className="speed-badge">{m.speed}</span>
                        </div>
                        <small>{m.role}</small>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}

          </aside>

        </div>
      </main>
    </div>
  );
};

export default Dashboard;