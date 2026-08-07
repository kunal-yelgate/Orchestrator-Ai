import React from "react";

const Home = ({ onEnterDashboard, backendStatus }) => {
  return (
    <div className="landing-shell">
      <div className="landing-card">
        <div className="landing-badge">Professional AI orchestration</div>
        <h1>Black & white orchestration for multi-model intelligence.</h1>
        <p>
          A refined workspace where planning, research, synthesis, and
          verification unfold in a precise, traceable workflow.
        </p>
        <div className="landing-actions">
          <button className="primary-btn" onClick={onEnterDashboard}>
            Enter dashboard
          </button>
          <button
            className="secondary-btn"
            onClick={() => window.location.reload()}
          >
            Refresh status
          </button>
        </div>
        <div className="landing-meta">
          <span>Backend: {backendStatus}</span>
          <span>Workflow: 4 stages</span>
        </div>
        <div className="landing-features">
          <div>
            <strong>Traceable</strong>
            <span>Every stage is visible</span>
          </div>
          <div>
            <strong>Accurate</strong>
            <span>Evidence-led execution</span>
          </div>
          <div>
            <strong>Professional</strong>
            <span>Minimal, sharp, modern</span>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Home;
