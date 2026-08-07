# 🧠 Orchestrator-Ai

**A multi-agent AI orchestration platform that plans, coordinates, and executes complex tasks by intelligently routing work across multiple AI agents.**

![Status](https://img.shields.io/badge/status-in%20development-yellow)
![Python](https://img.shields.io/badge/backend-Python%20%7C%20FastAPI-3776AB?logo=python&logoColor=white)
![React](https://img.shields.io/badge/frontend-React-61DAFB?logo=react&logoColor=black)
![License](https://img.shields.io/badge/license-MIT-blue)

---

## 📖 Overview

**Orchestrator-Ai** solves a problem that anyone building with multiple AI agents eventually runs into: a single LLM call is rarely enough to complete a real task. Real tasks need planning, delegation, tool use, memory, and verification — and doing that by hand (chaining prompts manually, hardcoding scripts) doesn't scale.

Orchestrator-Ai acts as the **"brain" layer above your AI agents**. Instead of talking to one model directly, you describe a goal, and the orchestrator:

1. Breaks the goal down into smaller sub-tasks
2. Decides which agent (or tool) is best suited for each sub-task
3. Executes those sub-tasks — in sequence or in parallel — while tracking state
4. Passes context/results between agents as needed
5. Reports progress and final output back through the dashboard

Think of it as a **project manager for your AI agents**: it doesn't do the specialized work itself, but it knows who should do what, in what order, and keeps everything moving.

> ⚠️ **Note:** This project is under active development. Architecture, agent interfaces, and UI are evolving — this README documents the current design intent and will be updated as features land.

---

## 💡 Core Concepts

### 1. Orchestrator
The central coordinating engine (backend). It owns the lifecycle of a workflow: receiving a goal, generating/following a plan, assigning tasks to agents, and collecting results. It is the single source of truth for "what is happening right now."

### 2. Agents
Independent, specialized workers that the orchestrator can call on. Each agent is designed to do one thing well — for example, a research agent, a coding agent, a summarization agent, or a data-retrieval agent. Agents are **pluggable**: new agents can be registered without changing the orchestrator's core logic.

### 3. Tasks & Task Graph
A user goal is decomposed into a set of tasks, which may depend on one another (task B needs the output of task A). Internally, this is represented as a **task graph** — the orchestrator walks this graph, executing tasks whose dependencies are satisfied, and can run independent tasks concurrently.

### 4. Workflow
A workflow is a full run — from the initial goal to the final result. It has a status (`pending`, `running`, `completed`, `failed`), a history of steps taken, and the intermediate/final outputs produced by each agent along the way.

### 5. Context / Memory
As agents complete tasks, their outputs are stored and made available as context to downstream tasks — so later agents aren't working blind, and the orchestrator can reason about the whole workflow, not just isolated steps.

### 6. Dashboard (Frontend)
The React frontend is the control room: submit a new goal, watch the task graph execute in real time, inspect what each agent produced, and review past workflow runs.

---

## ⚙️ How It Works (Execution Flow)

```
 User Goal
    │
    ▼
┌─────────────────────┐
│   Orchestrator API   │  ← receives goal via REST endpoint
│      (FastAPI)       │
└─────────┬────────────┘
          │ 1. Plan
          ▼
   ┌───────────────┐
   │  Task Planner  │  → breaks goal into a task graph
   └───────┬────────┘
           │ 2. Dispatch
           ▼
   ┌────────────────────────────┐
   │        Task Router          │  → decides which agent handles which task
   └───────┬───────────┬────────┘
           │           │
           ▼           ▼
     ┌──────────┐ ┌──────────┐
     │ Agent A   │ │ Agent B   │   ... (parallel / sequential execution)
     └────┬─────┘ └────┬─────┘
          │             │
          └──────┬──────┘
                 ▼ 3. Aggregate
         ┌──────────────────┐
         │  Result Collector  │  → merges agent outputs, updates workflow state
         └────────┬──────────┘
                  ▼ 4. Respond
         ┌──────────────────┐
         │   Frontend (React) │  → renders live status + final result
         └──────────────────┘
```

**Step by step:**

1. **Submit a goal** — from the dashboard or directly via the API (e.g. `POST /workflows`).
2. **Planning** — the orchestrator interprets the goal and produces an ordered/graphed list of sub-tasks.
3. **Routing & dispatch** — each task is matched to the agent best equipped to handle it, based on capability tags/metadata registered per agent.
4. **Execution** — agents run their assigned tasks (independent tasks can run in parallel; dependent tasks wait for their inputs).
5. **State tracking** — the orchestrator updates workflow/task status after every step, so progress is visible in real time.
6. **Aggregation** — outputs from all agents are collected and merged into a final result.
7. **Delivery** — the frontend polls/subscribes to workflow status and displays live progress and the final output.

---

## ✨ Abilities & Capabilities

| Capability | Description |
|---|---|
| 🧩 **Task decomposition** | Automatically breaks a high-level goal into smaller, actionable sub-tasks |
| 🔀 **Multi-agent dispatch** | Routes each sub-task to the most suitable registered agent |
| ⚡ **Parallel execution** | Runs independent tasks concurrently to reduce total turnaround time |
| 🔗 **Dependency-aware sequencing** | Ensures tasks that depend on prior results run in the correct order |
| 🧠 **Shared context/memory** | Passes relevant outputs between agents so later steps have full context |
| 🔌 **Pluggable agent registry** | New agents can be added/registered without modifying core orchestrator code |
| 📡 **Real-time status tracking** | Live workflow and task-level status (pending/running/completed/failed) |
| 🖥️ **Visual dashboard** | React UI to submit goals, monitor execution, and inspect agent outputs |
| 🛠️ **REST API access** | Programmatic access to trigger and monitor workflows outside the UI |
| 📜 **Workflow history** | Past runs and their outputs are retrievable for review/debugging |

---

## 🎯 Use Cases

- **Research automation** — assign a research agent to gather information, a summarizer agent to condense it, and a writer agent to produce a final report, all from one submitted goal.
- **Code generation pipelines** — orchestrate a planning agent, a code-generation agent, and a review/testing agent in sequence.
- **Data processing workflows** — coordinate agents that fetch, clean, transform, and analyze data as connected steps.
- **General task automation** — any multi-step process that benefits from being split across specialized AI workers instead of one large prompt.

---

## 🛠️ Tech Stack

| Layer | Technology |
|---|---|
| Backend | Python, FastAPI |
| Frontend | React |
| API Style | REST (JSON) |
| Execution | Async task handling / concurrent agent calls |
| Language | Python 3.x, JavaScript |

---

## 📂 Project Structure

```
Orchestrator-Ai/
├── backend/          # FastAPI service — orchestration engine, task planner, agent router, API
├── frontend/         # React app — dashboard for submitting goals & tracking workflows
├── plan.md           # Project planning notes
└── README.md
```

---

## 🚀 Getting Started

### Prerequisites

- Python 3.9+
- Node.js 18+ and npm/yarn
- pip / virtualenv (recommended)

### 1. Clone the repository

```bash
git clone https://github.com/kunal-yelgate/Orchestrator-Ai.git
cd Orchestrator-Ai
```

### 2. Set up the backend

```bash
cd backend
python -m venv venv
source venv/bin/activate   # On Windows: venv\Scripts\activate
pip install -r requirements.txt
uvicorn main:app --reload
```

Backend runs at `http://localhost:8000` by default. Interactive API docs (Swagger UI) will be available at `http://localhost:8000/docs`.

### 3. Set up the frontend

```bash
cd ../frontend
npm install
npm run dev
```

Frontend runs at `http://localhost:5173` (or your configured Vite/React port).

> 📝 Update the exact run commands and ports above once `backend/` and `frontend/` entrypoints are finalized.

### 4. Try it out

1. Open the dashboard in your browser.
2. Submit a goal (e.g. *"Research topic X and summarize the findings"*).
3. Watch the task graph execute in real time as agents pick up and complete each sub-task.
4. View the final aggregated result once the workflow completes.

---

## 🗺️ Roadmap

- [ ] Define core orchestration engine and task graph model
- [ ] Build agent registry with capability-based routing
- [ ] Implement parallel/sequential task execution engine
- [ ] Connect frontend dashboard to backend API (live status updates)
- [ ] Add workflow history & persistence (database-backed)
- [ ] Add authentication and multi-user support
- [ ] Write full API documentation
- [ ] Add example agents (research, coding, summarization)

---

## 🤝 Contributing

Contributions, ideas, and feedback are welcome!

1. Fork the repo
2. Create a feature branch (`git checkout -b feature/your-feature`)
3. Commit your changes
4. Push and open a PR

---

## 📄 License

This project is licensed under the [MIT License](LICENSE).

---

## 👤 Author
