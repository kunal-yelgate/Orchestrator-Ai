import WorkflowGraph from "../components/WorkflowGraph";
import { STAGE_TO_AGENT, AGENT_TO_STAGE } from "../lib/workflowStages";
import { orchestrate, uploadFiles, fetchCheckpoints, rollbackWorkflow } from "../services/api";
import { useState, useRef, useEffect } from "react";

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
    name: "Planner",
    detail: "Analyzes the user goal.",
    icon: "🤖",
  },
  {
    name: "Task Splitter",
    detail: "Breaks the goal into subtasks.",
    icon: "📋",
  },
  {
    name: "Research Agent 1",
    detail: "Researches the first task.",
    icon: "🔍",
  },
  {
    name: "Research Agent 2",
    detail: "Researches the second task.",
    icon: "🔍",
  },
  {
    name: "Summarizer",
    detail: "Combines all research.",
    icon: "📝",
  },
  {
    name: "Verifier",
    detail: "Validates the final output.",
    icon: "✅",
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

function formatBytes(bytes) {
  if (bytes < 1024) return `${bytes} B`;
  if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`;
  return `${(bytes / (1024 * 1024)).toFixed(1)} MB`;
}

// Browser speech recognition (Chrome/Edge: webkitSpeechRecognition; some
// browsers expose the unprefixed SpeechRecognition instead).
const SpeechRecognitionAPI =
  typeof window !== "undefined"
    ? window.SpeechRecognition || window.webkitSpeechRecognition
    : null;

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
  const [activeStage, setActiveStage] = useState("Evidence Research");
  const [selectedModel, setSelectedModel] = useState("Auto");
  const messagesEndRef = useRef(null);

  // ── Attachments (upload file + prompt together) ─────────────────
  const [attachedFiles, setAttachedFiles] = useState([]);
  const fileInputRef = useRef(null);

  // ── Voice input ───────────────────────────────────────────────────
  const [isRecording, setIsRecording] = useState(false);
  const [voiceSupported] = useState(!!SpeechRecognitionAPI);
  const recognitionRef = useRef(null);

  // ── Checkpoint revert ────────────────────────────────────────────
  const [currentWorkflowId, setCurrentWorkflowId] = useState(null);
  const [checkpointPanelOpen, setCheckpointPanelOpen] = useState(false);
  const [checkpoints, setCheckpoints] = useState([]);
  const [checkpointsLoading, setCheckpointsLoading] = useState(false);
  const [checkpointsError, setCheckpointsError] = useState("");
  const [revertTargetStage, setRevertTargetStage] = useState(null);
  const [revertingFile, setRevertingFile] = useState(null);

  // Auto-scroll to bottom on new messages
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, isThinking]);

  // Set up speech recognition once
  useEffect(() => {
    if (!SpeechRecognitionAPI) return;

    const recognition = new SpeechRecognitionAPI();
    recognition.continuous = false;
    recognition.interimResults = false;
    recognition.lang = "en-US";

    recognition.onresult = (event) => {
      const transcript = Array.from(event.results)
        .map((r) => r[0].transcript)
        .join(" ");
      setInput((prev) => (prev ? `${prev.trim()} ${transcript}` : transcript));
    };

    recognition.onerror = () => setIsRecording(false);
    recognition.onend = () => setIsRecording(false);

    recognitionRef.current = recognition;

    return () => {
      recognition.onresult = null;
      recognition.onerror = null;
      recognition.onend = null;
    };
  }, []);

  const toggleRecording = () => {
    if (!recognitionRef.current) return;

    if (isRecording) {
      recognitionRef.current.stop();
      setIsRecording(false);
    } else {
      try {
        recognitionRef.current.start();
        setIsRecording(true);
      } catch {
        // start() throws if already started — ignore
      }
    }
  };

  // ── Attachments handlers ───────────────────────────────────────────
  const handleAttachClick = () => fileInputRef.current?.click();

  const handleFilesSelected = (event) => {
    const files = Array.from(event.target.files || []);
    if (files.length) {
      setAttachedFiles((prev) => [...prev, ...files]);
    }
    event.target.value = ""; // allow re-selecting the same file
  };

  const removeAttachedFile = (index) => {
    setAttachedFiles((prev) => prev.filter((_, i) => i !== index));
  };

  const activeStageObj = workflowStages.find((s) => s.name === activeStage);
  const activeIndex = workflowStages.findIndex((s) => s.name === activeStage);

  const handleSubmit = async (event) => {
    event.preventDefault();

    if ((!input.trim() && attachedFiles.length === 0) || isThinking) return;

    const goal = input.trim() || "Analyze the attached file(s).";
    const filesForThisMessage = attachedFiles;

    const userMessage = {
      id: Date.now(),
      role: "user",
      text: goal,
      meta: `Model: ${selectedModel}`,
      attachments: filesForThisMessage.map((f) => ({ name: f.name, size: f.size })),
    };

    setMessages((prev) => [...prev, userMessage]);
    setInput("");
    setAttachedFiles([]);
    setIsThinking(true);

    try {
      // Stage 1
      setActiveStage("Planner");
      await new Promise((resolve) => setTimeout(resolve, 300));

      // Upload any attached files first, then reference them in orchestrate()
      let documents = [];
      if (filesForThisMessage.length > 0) {
        documents = await uploadFiles(filesForThisMessage);
      }

      // Stage 2
      setActiveStage("Task Splitter");
      await new Promise((resolve) => setTimeout(resolve, 300));

      const provider =
        selectedModel === "Auto"
          ? "groq"
          : selectedModel.toLowerCase();

      // ===========================
      // Call FastAPI Backend
      // ===========================
      const result = await orchestrate(goal, provider, documents);

      console.log("Backend Response:", result);

      setCurrentWorkflowId(result.workflow_id || null);

      // Stage 3
      setActiveStage("Research Agent 1");
      await new Promise((resolve) => setTimeout(resolve, 300));

      // Stage 4
      setActiveStage("Research Agent 2");
      await new Promise((resolve) => setTimeout(resolve, 300));

      // Stage 5
      setActiveStage("Summarizer");
      await new Promise((resolve) => setTimeout(resolve, 300));

      // Stage 6
      setActiveStage("Verifier");
      await new Promise((resolve) => setTimeout(resolve, 300));

      // Re-sync to wherever the run actually landed (in case it stopped early)
      if (result.last_agent_name && AGENT_TO_STAGE[result.last_agent_name]) {
        setActiveStage(AGENT_TO_STAGE[result.last_agent_name]);
      }

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
        meta: result.verification?.verified
          ? `Verified ✅ (${Math.round(
              (result.verification.confidence || 0) * 100
            )}%)`
          : "Completed",
      };

      setMessages((prev) => [...prev, assistantMessage]);
    } catch (error) {
      console.error(error);

      setMessages((prev) => [
        ...prev,
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

  // ── Checkpoint revert handlers ──────────────────────────────────────

  const openCheckpointPanel = async (stage) => {
    if (!currentWorkflowId) {
      setMessages((prev) => [
        ...prev,
        {
          id: Date.now(),
          role: "assistant",
          text: "There's no run to revert yet — send a prompt first, then click a graph node to roll back to that step.",
          meta: "Checkpoints",
        },
      ]);
      return;
    }

    setRevertTargetStage(stage);
    setCheckpointPanelOpen(true);
    setCheckpointsLoading(true);
    setCheckpointsError("");

    try {
      const list = await fetchCheckpoints(currentWorkflowId);
      setCheckpoints(list);
    } catch (error) {
      setCheckpointsError(error.message || "Unable to load checkpoints.");
      setCheckpoints([]);
    } finally {
      setCheckpointsLoading(false);
    }
  };

  const closeCheckpointPanel = () => {
    setCheckpointPanelOpen(false);
    setRevertTargetStage(null);
    setCheckpointsError("");
  };

  const handleRevert = async (checkpoint) => {
    if (!currentWorkflowId) return;

    setRevertingFile(checkpoint.file);
    setIsThinking(true);

    setMessages((prev) => [
      ...prev,
      {
        id: Date.now(),
        role: "user",
        text: `↩ Reverted to "${checkpoint.agent_name}" (step ${checkpoint.step_index}) — continuing execution from there.`,
        meta: "Checkpoint revert",
      },
    ]);

    try {
      const result = await rollbackWorkflow(currentWorkflowId, checkpoint.file);

      console.log("Rollback response:", result);

      setCurrentWorkflowId(result.workflow_id || currentWorkflowId);

      if (result.last_agent_name && AGENT_TO_STAGE[result.last_agent_name]) {
        setActiveStage(AGENT_TO_STAGE[result.last_agent_name]);
      }

      let reply = "Workflow resumed and completed successfully.";
      if (result.summary) {
        if (typeof result.summary === "string") {
          reply = result.summary;
        } else if (result.summary.summary) {
          reply = result.summary.summary;
        }
      }

      setMessages((prev) => [
        ...prev,
        {
          id: Date.now() + 1,
          role: "assistant",
          text: reply,
          meta: result.verification?.verified
            ? `Verified ✅ (${Math.round(
                (result.verification.confidence || 0) * 100
              )}%) — resumed run`
            : "Completed — resumed run",
        },
      ]);

      closeCheckpointPanel();
    } catch (error) {
      console.error(error);
      setMessages((prev) => [
        ...prev,
        {
          id: Date.now() + 1,
          role: "assistant",
          text: error.message || "Failed to revert to that checkpoint.",
          meta: "Error",
        },
      ]);
    } finally {
      setRevertingFile(null);
      setIsThinking(false);
    }
  };

  return (
    <div className="app-shell">
      {/* ── Sidebar ─────────────────────────────────────────── */}
      <aside className="sidebar" aria-label="Navigation sidebar">
        <div className="brand-block">
          <div className="brand-icon" aria-hidden="true">
            ✦
          </div>
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
            {workflowStages.map((_, i) => (
              <div
                key={i}
                className={`progress-dot ${
                  i === activeIndex
                    ? "active"
                    : i < activeIndex
                    ? "done"
                    : ""
                }`}
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
            <div
              className="user-badge"
              aria-label={`Signed in as ${
                currentUser?.name || currentUser?.email
              }`}
            >
              {currentUser?.name
                ? currentUser.name
                : currentUser?.email?.split("@")[0]}
            </div>
            <label htmlFor="model-select" className="sr-only">
              Select AI model
            </label>
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
                    {message.attachments && message.attachments.length > 0 && (
                      <div className="message-attachments">
                        {message.attachments.map((a, i) => (
                          <span key={i} className="attachment-chip">
                            📎 {a.name}
                          </span>
                        ))}
                      </div>
                    )}
                  </div>
                </div>
              ))}

              {isThinking && (
                <div
                  className="message-row assistant"
                  aria-label="Orchestrator is thinking"
                >
                  <div className="avatar" aria-hidden="true">
                    AI
                  </div>
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

            <div
              className="prompt-row"
              role="group"
              aria-label="Prompt suggestions"
            >
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

            {attachedFiles.length > 0 && (
              <div className="attachment-row" aria-label="Attached files">
                {attachedFiles.map((file, i) => (
                  <span key={`${file.name}-${i}`} className="attachment-chip removable">
                    📎 {file.name}
                    <small>{formatBytes(file.size)}</small>
                    <button
                      type="button"
                      className="attachment-remove"
                      onClick={() => removeAttachedFile(i)}
                      aria-label={`Remove ${file.name}`}
                    >
                      ×
                    </button>
                  </span>
                ))}
              </div>
            )}

            <form
              className="composer"
              onSubmit={handleSubmit}
              aria-label="Message composer"
            >
              <input
                ref={fileInputRef}
                type="file"
                multiple
                onChange={handleFilesSelected}
                style={{ display: "none" }}
                aria-hidden="true"
              />

              <button
                type="button"
                className="icon-btn"
                onClick={handleAttachClick}
                disabled={isThinking}
                aria-label="Attach a file"
                title="Attach a file"
              >
                📎
              </button>

              {voiceSupported && (
                <button
                  type="button"
                  className={`icon-btn ${isRecording ? "recording" : ""}`}
                  onClick={toggleRecording}
                  disabled={isThinking}
                  aria-label={isRecording ? "Stop voice input" : "Start voice input"}
                  aria-pressed={isRecording}
                  title={isRecording ? "Stop voice input" : "Speak your prompt"}
                >
                  {isRecording ? "⏺" : "🎤"}
                </button>
              )}

              <input
                id="chat-input"
                type="text"
                value={input}
                onChange={(event) => setInput(event.target.value)}
                placeholder={
                  isRecording
                    ? "Listening…"
                    : "Ask the orchestrator to analyze, compare, or synthesize…"
                }
                aria-label="Type your message"
                disabled={isThinking}
                autoComplete="off"
              />
              <button
                id="send-btn"
                type="submit"
                disabled={isThinking || (!input.trim() && attachedFiles.length === 0)}
                aria-label="Send message"
              >
                {isThinking ? "…" : "Send ↗"}
              </button>
            </form>
          </section>

          {/* Insight panel */}
          <aside className="insight-panel" aria-label="Workflow insight panel">
            <div className="info-card">
              <div className="section-title">LangGraph Flow</div>
              <WorkflowGraph
                activeStage={activeStage}
                onNodeClick={openCheckpointPanel}
                revertableStage={revertTargetStage}
              />
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

      {/* ── Checkpoint revert panel ─────────────────────────────── */}
      {checkpointPanelOpen && (
        <div
          className="checkpoint-overlay"
          role="dialog"
          aria-modal="true"
          aria-label="Revert to checkpoint"
          onClick={closeCheckpointPanel}
        >
          <div className="checkpoint-panel" onClick={(e) => e.stopPropagation()}>
            <div className="checkpoint-panel-header">
              <div>
                <div className="section-title">Revert to checkpoint</div>
                <p className="checkpoint-panel-sub">
                  {revertTargetStage
                    ? `Node clicked: ${revertTargetStage}`
                    : "Choose a step to roll back to"}
                </p>
              </div>
              <button
                type="button"
                className="checkpoint-close"
                onClick={closeCheckpointPanel}
                aria-label="Close"
              >
                ×
              </button>
            </div>

            {checkpointsLoading && (
              <div className="checkpoint-loading">Loading checkpoints…</div>
            )}

            {checkpointsError && (
              <div className="global-error" role="alert">
                <span aria-hidden="true">⚠</span> {checkpointsError}
              </div>
            )}

            {!checkpointsLoading && !checkpointsError && checkpoints.length === 0 && (
              <p className="checkpoint-empty">No checkpoints saved yet for this run.</p>
            )}

            <ul className="checkpoint-list">
              {checkpoints.map((cp) => {
                const isTarget =
                  revertTargetStage &&
                  STAGE_TO_AGENT[revertTargetStage] === cp.agent_name;
                const isBusy = revertingFile === cp.file;

                return (
                  <li
                    key={cp.file}
                    className={`checkpoint-item ${isTarget ? "target" : ""}`}
                  >
                    <div className="checkpoint-item-info">
                      <strong>
                        Step {cp.step_index} — {cp.agent_name}
                      </strong>
                      <small>{cp.timestamp}</small>
                      {cp.status && <span className="checkpoint-status">{cp.status}</span>}
                    </div>
                    <button
                      type="button"
                      className="secondary-btn compact"
                      onClick={() => handleRevert(cp)}
                      disabled={isThinking}
                      aria-label={`Revert to ${cp.agent_name} and continue`}
                    >
                      {isBusy ? "Reverting…" : "Revert & continue →"}
                    </button>
                  </li>
                );
              })}
            </ul>
          </div>
        </div>
      )}
    </div>
  );
};

export default Dashboard;
