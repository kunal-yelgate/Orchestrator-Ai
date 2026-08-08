# 🧠 Orchestrator-AI

**A multi-agent AI orchestration platform that plans, coordinates, and executes complex tasks by intelligently routing work across multiple AI agents.**

<p align="center">
  <img src="https://img.shields.io/badge/status-in%20development-yellow" alt="Status" />
  <img src="https://img.shields.io/badge/backend-Python%20%7C%20FastAPI-3776AB?logo=python&logoColor=white" alt="Python" />
  <img src="https://img.shields.io/badge/frontend-React%20%7C%20Vite-61DAFB?logo=react&logoColor=black" alt="React" />
  <img src="https://img.shields.io/badge/pipeline-LangGraph-1C3C3C" alt="LangGraph" />
  <img src="https://img.shields.io/badge/auth-Supabase-3ECF8E?logo=supabase&logoColor=white" alt="Supabase" />
  <img src="https://img.shields.io/badge/license-MIT-blue" alt="License" />
</p>

<p align="center">
  <img width="1280" height="853" alt="Orchestrator-AI dashboard preview" src="https://github.com/user-attachments/assets/ddb7d816-5c98-41f7-b29d-5b9800574a67" />
</p>

> ⚠️ **Note:** This project is under active development. Architecture, agent interfaces, and UI are evolving — this README documents the current design intent and will be updated as features land.

---

## 📑 Table of Contents

- [Overview](#-overview)
- [Why Orchestrator-AI?](#-why-orchestrator-ai)
- [Core Concepts](#-core-concepts)
- [How It Works](#️-how-it-works-execution-flow)
- [Abilities & Capabilities](#-abilities--capabilities)
- [Use Cases](#-use-cases)
- [Tech Stack](#️-tech-stack)
- [Project Structure & Architecture](#-project-structure--architecture)
- [Getting Started](#-getting-started--setup-instructions)
- [API Reference](#-api-reference-preview)
- [Adding a New Agent](#-adding-a-new-agent)
- [Configuration Reference](#️-configuration-reference)
- [Roadmap](#️-roadmap)
- [FAQ](#-faq)
- [Contributing](#-contributing)
- [License](#-license)
- [Author](#-author)

---

## 📖 Overview

**Orchestrator-AI** solves a problem that anyone building with multiple AI agents eventually runs into: a single LLM call is rarely enough to complete a real task. Real tasks need planning, delegation, tool use, memory, and verification — and doing that by hand (chaining prompts manually, hardcoding scripts) doesn't scale.

Orchestrator-AI acts as the **"brain" layer above your AI agents**. Instead of talking to one model directly, you describe a goal, and the orchestrator:

1. Breaks the goal down into smaller sub-tasks
2. Decides which agent (or tool) is best suited for each sub-task
3. Executes those sub-tasks — in sequence or in parallel — while tracking state
4. Passes context/results between agents as needed
5. Reports progress and final output back through the dashboard

Think of it as a **project manager for your AI agents**: it doesn't do the specialized work itself, but it knows who should do what, in what order, and keeps everything moving.

---

## 🤔 Why Orchestrator-AI?

Most "multi-agent" demos are really just a single prompt with extra steps. Orchestrator-AI is built around a few opinionated ideas:

- **Explicit task graphs over implicit chains** — dependencies between sub-tasks are modeled, not hidden inside a giant prompt, so execution order is predictable and debuggable.
- **Agents are pluggable, not hardcoded** — the orchestrator core never needs to change when a new agent is added; agents register their own capabilities.
- **State is a first-class citizen** — every workflow, task, and agent output is tracked and queryable, not just streamed and discarded.
- **Model-agnostic by design** — the LLM layer is a swappable interface, so a workflow isn't locked into one provider.
- **Observability from the start** — the dashboard exists so you can *see* the plan the orchestrator made, not just the final answer.

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
2. **Planning** — the orchestrator interprets the goal and produces an ordered/graphed list of sub-tasks, typically via a LangGraph node that calls an LLM with a planning prompt.
3. **Routing & dispatch** — each task is matched to the agent best equipped to handle it, based on capability tags/metadata registered per agent.
4. **Execution** — agents run their assigned tasks (independent tasks can run in parallel via `asyncio`; dependent tasks wait for their inputs to resolve).
5. **State tracking** — the orchestrator updates workflow/task status after every step (`pending → running → completed/failed`), so progress is visible in real time.
6. **Aggregation** — outputs from all agents are collected and merged into a final result, with intermediate outputs preserved for inspection.
7. **Delivery** — the frontend polls/subscribes to workflow status and displays live progress and the final output, including a visual task graph.

---

## ✨ Abilities & Capabilities

| Capability | Description |
|---|---|
| 🧩 **Task decomposition** | Automatically breaks a high-level goal into smaller, actionable sub-tasks |
| 🔀 **Multi-agent dispatch** | Routes each sub-task to the most suitable registered agent based on capability matching |
| ⚡ **Parallel execution** | Runs independent tasks concurrently to reduce total turnaround time |
| 🔗 **Dependency-aware sequencing** | Ensures tasks that depend on prior results run in the correct order |
| 🧠 **Shared context/memory** | Passes relevant outputs between agents so later steps have full context |
| 🔌 **Pluggable agent registry** | New agents can be added/registered without modifying core orchestrator code |
| 📡 **Real-time status tracking** | Live workflow and task-level status (pending/running/completed/failed) |
| 🖥️ **Visual dashboard** | React UI to submit goals, monitor execution, and inspect agent outputs |
| 🛠️ **REST API access** | Programmatic access to trigger and monitor workflows outside the UI |
| 📜 **Workflow history** | Past runs and their outputs are retrievable for review/debugging |
| 🔐 **Authenticated access** | Supabase-backed auth gates workflow submission and history per user |
| 🌐 **Multi-model support** | Swap between Groq, Ollama, GPT-4, Gemini, or Claude per agent |

---

## 🎯 Use Cases

- **Research automation** — assign a research agent to gather information, a summarizer agent to condense it, and a writer agent to produce a final report, all from one submitted goal.
- **Code generation pipelines** — orchestrate a planning agent, a code-generation agent, and a review/testing agent in sequence.
- **Data processing workflows** — coordinate agents that fetch, clean, transform, and analyze data as connected steps.
- **Customer-facing assistants** — route a user request across intent-classification, retrieval, and response-generation agents.
- **General task automation** — any multi-step process that benefits from being split across specialized AI workers instead of one large prompt.

---

## 🛠️ Tech Stack

| Layer | Technology |
|---|---|
| Backend | Python, FastAPI |
| Orchestration Pipeline | LangGraph |
| Frontend | React, Vite |
| Database | Vector DB (for context/memory retrieval) |
| Authentication | Supabase Auth |
| LLM Models | Groq, Ollama, GPT-4, Gemini, Claude |
| API Style | REST (JSON) |
| Execution | Async task handling / concurrent agent calls (`asyncio`) |
| Language | Python 3.x, JavaScript |

---

## 📂 Project Structure & Architecture

Orchestrator-AI is split into a decoupled **React frontend** and a **FastAPI backend**. Below is a detailed map of the folder structure and what each component is responsible for.

### 🐍 Backend (`/backend`)
The backend is a Python FastAPI application that runs the core orchestration logic, connects to the LLMs, and manages the LangGraph execution pipeline.

```text
backend/
├── main.py                 # 🚀 Application entry point. Initializes FastAPI, configures CORS, and wires up all routes.
├── requirements.txt        # 📦 Python dependencies (FastAPI, LangChain, Supabase, etc).
├── .env                    # 🔑 Environment variables (API keys, Supabase credentials).
│
├── api/                    # 🌐 REST API Controllers
│   └── routes/             # Defines the HTTP endpoints exposed to the frontend (e.g., /workflows, /health).
│
├── agents/                 # 🤖 Specialized AI Workers
│   └── ...                 # Individual agent implementations (e.g., Researcher, Summarizer) that the orchestrator routes tasks to.
│
├── graph/                  # 🕸️ LangGraph Pipeline
│   └── ...                 # Defines the nodes, edges, and state of the orchestration workflow. This is where the step-by-step logic lives.
│
├── llm/                    # 🧠 LLM Integration Layer
│   └── ...                 # Wrappers and configuration for different AI models (GPT-4, Gemini, Claude).
│
├── models/                 # 📝 Data Models (Pydantic)
│   └── ...                 # Type definitions and schemas for API requests, responses, and internal state.
│
├── prompts/                # 💬 Prompt Engineering
│   └── ...                 # Stored prompt templates used by the orchestrator and individual agents.
│
├── database/               # 💾 Persistence Layer
│   └── ...                 # Database connection logic (e.g., Supabase DB clients) for saving workflow history.
│
└── utils/                  # 🛠️ Helper Functions
    └── ...                 # Shared utilities, logging configuration, and generic helper methods.
```

### ⚛️ Frontend (`/frontend`)
The frontend is a modern React application built with Vite, utilizing Supabase for authentication and a sleek dark-mode UI for monitoring workflows.

```text
frontend/
├── index.html              # 📄 HTML entry point.
├── package.json            # 📦 Node dependencies and npm scripts.
├── vite.config.js          # ⚡ Vite bundler configuration.
├── proxy/                  # 🛡️ Custom Proxy Server
│   └── server.js           # Express server that intercepts requests, validates Supabase auth tokens, and forwards to the backend.
│
└── src/                    # 💻 React Source Code
    ├── main.jsx            # React root injection point.
    ├── App.jsx             # Top-level routing, session management, and auth state listener.
    ├── App.css             # Main application styles, including the dark-mode design system.
    ├── index.css           # Global CSS variables and resets.
    │
    ├── pages/              # 🖥️ Full-page components
    │   ├── Home.jsx        # The landing page with hero text and the unified Sign Up / Log In auth card.
    │   └── Dashboard.jsx   # The main protected view where users submit goals and monitor live execution.
    │
    ├── components/         # 🧩 Reusable UI Components
    │   ├── AgentNode.jsx   # UI representation of an agent/task in the execution graph.
    │   └── ...             # Other shared UI elements (buttons, modals, loaders).
    │
    ├── lib/                # 🔧 Libraries & Config
    │   └── supabase.js     # Singleton Supabase client configuration for client-side authentication.
    │
    └── services/           # 🔌 API Integration
        └── api.js          # Functions for making HTTP requests to the backend/proxy.
```

---

## 🚀 Getting Started & Setup Instructions

Follow these step-by-step instructions to get the project running on your local machine.

### Prerequisites
- **Python 3.9+** (for the backend)
- **Node.js 18+** and npm (for the frontend)
- API Keys for the AI models you intend to use (e.g., Gemini, OpenAI, Groq)
- A [Supabase](https://supabase.com/) project (for authentication)

### 1. Clone the repository

```bash
git clone https://github.com/kunal-yelgate/Orchestrator-Ai.git
cd Orchestrator-Ai
```

### 2. Set up the Backend (FastAPI)

Open a terminal and navigate to the `backend` directory:

```bash
cd backend
```

**Create and activate a virtual environment:**
```bash
# On macOS/Linux:
python -m venv venv
source venv/bin/activate

# On Windows:
python -m venv venv
venv\Scripts\activate
```

**Install dependencies:**
```bash
pip install -r requirements.txt
```

**Configure Environment Variables:**
Create a `.env` file in the `backend` directory and add your required keys:
```env
GEMINI_API_KEY=your_gemini_api_key
MODEL_NAME=gemini-2.0-flash
SUPABASE_URL=your_supabase_project_url
SUPABASE_SERVICE_KEY=your_supabase_service_role_key
# Add other keys as required by your agents (GROQ_API_KEY, OPENAI_API_KEY, etc.)
```

**Start the FastAPI server:**
```bash
uvicorn main:app --reload --port 5000
```
> The backend API will now be running at `http://localhost:5000`. You can view the interactive API documentation (Swagger UI) at `http://localhost:5000/docs`.

### 3. Set up the Frontend (React + Vite)

Open a **new** terminal window and navigate to the `frontend` directory:

```bash
cd frontend
```

**Install dependencies:**
```bash
npm install
```

**Configure Environment Variables:**
Create a `.env` file in the `frontend` directory for Supabase authentication:
```env
# Required for the proxy server and client
NEXT_PUBLIC_SUPABASE_URL=your_supabase_project_url
NEXT_PUBLIC_SUPABASE_ANON_KEY=your_supabase_anon_key
VITE_SUPABASE_URL=your_supabase_project_url
VITE_SUPABASE_ANON_KEY=your_supabase_anon_key
```

**Start the Development Servers:**
The frontend uses a Vite dev server alongside a custom Express proxy (to handle secure Auth routing). Start them both in separate terminals:

```bash
# Terminal 1 (Frontend Proxy):
node proxy/server.js
# Runs on http://localhost:3001

# Terminal 2 (Vite App):
npm run dev
# Runs on http://localhost:5173
```

### 4. How to Use the App

1. Open your browser and navigate to **`http://localhost:5173`**.
2. **Sign Up / Log In**: Create a new account. The app uses Supabase for authentication. *(Note: You may need to verify your email, or disable email confirmations in your Supabase dashboard for quick local testing).*
3. **Submit a Goal**: Once on the Dashboard, enter a complex goal (e.g., *"Research market trends for AI orchestrators and write a summary report"*).
4. **Monitor Execution**: Watch the UI as the Orchestrator breaks the goal into tasks, assigns them to agents, and streams the results back to the dashboard in real time.
5. **Review History**: Revisit past workflow runs from the dashboard to inspect what each agent produced.

---

## 📡 API Reference (Preview)

> Full interactive docs are auto-generated by FastAPI at `/docs` once the backend is running. Below is a preview of the core endpoints.

| Method | Endpoint | Description |
|---|---|---|
| `POST` | `/workflows` | Submit a new goal; returns a `workflow_id` and initial status |
| `GET` | `/workflows/{workflow_id}` | Get current status, task graph, and outputs for a workflow |
| `GET` | `/workflows` | List past workflow runs for the authenticated user |
| `GET` | `/agents` | List all registered agents and their declared capabilities |
| `GET` | `/health` | Health check for the API service |

**Example — submitting a goal:**
```bash
curl -X POST http://localhost:5000/workflows \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <supabase_access_token>" \
  -d '{
        "goal": "Research market trends for AI orchestrators and write a summary report"
      }'
```

**Example response:**
```json
{
  "workflow_id": "b3f1a2e4-...",
  "status": "running",
  "created_at": "2026-08-08T10:15:00Z"
}
```

---

## 🧩 Adding a New Agent

Because agents are pluggable, adding one typically follows this pattern:

1. Create a new module under `backend/agents/`, implementing the agent's `run(task)` logic.
2. Declare the agent's **capability tags** (e.g. `["research", "web-search"]`) so the Task Router can match it to relevant sub-tasks.
3. Register the agent in the agent registry — no changes to the core orchestrator or graph logic required.
4. (Optional) Add a dedicated prompt template under `backend/prompts/` if the agent needs custom instructions.

```python
# backend/agents/researcher_agent.py
class ResearcherAgent:
    name = "researcher"
    capabilities = ["research", "web-search", "information-gathering"]

    async def run(self, task: dict, context: dict) -> dict:
        # 1. Read task.description and any relevant context
        # 2. Call the LLM / external tools as needed
        # 3. Return structured output for downstream agents
        ...
```

---

## ⚙️ Configuration Reference

| Variable | Location | Description |
|---|---|---|
| `GEMINI_API_KEY` | `backend/.env` | API key for Gemini-based agents |
| `MODEL_NAME` | `backend/.env` | Default model used by the orchestrator's planning step |
| `SUPABASE_URL` | `backend/.env`, `frontend/.env` | Your Supabase project URL |
| `SUPABASE_SERVICE_KEY` | `backend/.env` | Service-role key used server-side for privileged DB access |
| `VITE_SUPABASE_ANON_KEY` | `frontend/.env` | Public anon key used by the client-side Supabase SDK |

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
- [ ] Add retry/error-recovery logic for failed tasks
- [ ] Support streaming agent outputs to the dashboard
- [ ] Add workflow templates for common multi-agent patterns

---

## ❓ FAQ

**Does Orchestrator-AI run agents itself, or just coordinate them?**
It only coordinates — planning, routing, and tracking state. Each agent is responsible for its own execution logic.

**Can I use a local model instead of a hosted API?**
Yes — Ollama is supported in the LLM integration layer, so agents can run against local models.

**What happens if one agent in a workflow fails?**
The workflow's status is updated to reflect the failure at the task level; other independent tasks can still complete. Retry/error-recovery is on the roadmap.

**Is this tied to LangChain specifically?**
The orchestration pipeline uses LangGraph for the node/edge execution model, but the LLM integration layer is designed to be swappable across providers.

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


