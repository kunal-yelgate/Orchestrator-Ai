import React, { useState } from "react";

const Home = ({ onAuthenticate, backendStatus }) => {
  const [mode, setMode] = useState("login");
  const [name, setName] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [errors, setErrors] = useState({});
  const [isLoading, setIsLoading] = useState(false);

  const validate = () => {
    const nextErrors = {};
    if (!email.trim()) {
      nextErrors.email = "Email is required.";
    } else if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email)) {
      nextErrors.email = "Enter a valid email.";
    }
    if (!password.trim()) {
      nextErrors.password = "Password is required.";
    } else if (password.length < 6) {
      nextErrors.password = "Must be at least 6 characters.";
    }
    if (mode === "signup" && !name.trim()) {
      nextErrors.name = "Name is required for sign up.";
    }
    setErrors(nextErrors);
    return Object.keys(nextErrors).length === 0;
  };

  const handleSubmit = (event) => {
    event.preventDefault();
    if (!validate()) return;

    setIsLoading(true);
    setTimeout(() => {
      const user = {
        name:
          mode === "signup"
            ? name.trim()
            : email.substring(0, email.indexOf("@")) || email,
        email: email.trim(),
      };
      setIsLoading(false);
      onAuthenticate(user);
    }, 600);
  };

  const features = [
    { icon: "⬡", label: "Multi-model routing", desc: "GPT-4, Gemini, Claude orchestrated in sequence" },
    { icon: "◈", label: "LangGraph pipeline", desc: "4-stage traceable workflow execution" },
    { icon: "⬡", label: "Quality verification", desc: "Automated cross-model consistency checks" },
  ];

  return (
    <div className="landing-shell">
      {/* Floating orbs */}
      <div className="orb orb-1" aria-hidden="true" />
      <div className="orb orb-2" aria-hidden="true" />
      <div className="orb orb-3" aria-hidden="true" />

      <div className="landing-layout">
        {/* Left column — hero copy */}
        <div className="landing-hero">
          <div className="landing-badge" aria-label="Platform type">
            Professional AI orchestration
          </div>
          <h1 className="hero-title">
            The <span className="gradient-text">multi-model</span>
            <br />intelligence platform
          </h1>
          <p className="hero-desc">
            Route complex tasks through a coordinated pipeline of specialized
            AI models — planning, research, synthesis, and verification — with
            full traceability at every step.
          </p>

          <div className="feature-tiles" role="list">
            {features.map((f) => (
              <div key={f.label} className="feature-tile" role="listitem">
                <span className="feature-icon" aria-hidden="true">{f.icon}</span>
                <div>
                  <strong>{f.label}</strong>
                  <span>{f.desc}</span>
                </div>
              </div>
            ))}
          </div>

          <div className="model-strip" aria-label="Supported AI models">
            {["GPT-4.1", "Gemini 2.5 Pro", "Claude 3.7"].map((m) => (
              <span key={m} className="model-badge">{m}</span>
            ))}
          </div>
        </div>

        {/* Right column — auth card */}
        <div className="auth-card" role="main">
          <div className="auth-header">
            <div>
              <div className="landing-badge">
                {mode === "login" ? "Welcome back" : "Get started"}
              </div>
              <h2 className="auth-title">
                {mode === "login" ? (
                  <>Sign in to your <span className="gradient-text">workspace</span></>
                ) : (
                  <>Create your <span className="gradient-text">account</span></>
                )}
              </h2>
              <p>
                {mode === "login"
                  ? "Enter your credentials to access the orchestration dashboard."
                  : "Set up your account to start orchestrating AI workflows."}
              </p>
            </div>

            <div className="auth-switch" role="tablist" aria-label="Auth mode">
              <button
                id="tab-login"
                className={`tab-button ${mode === "login" ? "active" : ""}`}
                type="button"
                role="tab"
                aria-selected={mode === "login"}
                onClick={() => { setMode("login"); setErrors({}); }}
              >
                Sign In
              </button>
              <button
                id="tab-signup"
                className={`tab-button ${mode === "signup" ? "active" : ""}`}
                type="button"
                role="tab"
                aria-selected={mode === "signup"}
                onClick={() => { setMode("signup"); setErrors({}); }}
              >
                Sign Up
              </button>
            </div>
          </div>

          <form className="auth-form" onSubmit={handleSubmit} noValidate aria-label="Authentication form">
            {mode === "signup" && (
              <label className="field-group" htmlFor="auth-name">
                <span>Full name</span>
                <input
                  id="auth-name"
                  type="text"
                  value={name}
                  onChange={(e) => setName(e.target.value)}
                  placeholder="Jane Smith"
                  autoComplete="name"
                />
                {errors.name && <span className="field-error" role="alert">{errors.name}</span>}
              </label>
            )}

            <label className="field-group" htmlFor="auth-email">
              <span>Email address</span>
              <input
                id="auth-email"
                type="email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                placeholder="you@example.com"
                autoComplete="email"
              />
              {errors.email && <span className="field-error" role="alert">{errors.email}</span>}
            </label>

            <label className="field-group" htmlFor="auth-password">
              <span>Password</span>
              <input
                id="auth-password"
                type="password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                placeholder="Minimum 6 characters"
                autoComplete={mode === "login" ? "current-password" : "new-password"}
              />
              {errors.password && <span className="field-error" role="alert">{errors.password}</span>}
            </label>

            <button
              id="auth-submit-btn"
              className="primary-btn auth-submit"
              type="submit"
              disabled={isLoading}
            >
              {isLoading ? (
                <span className="btn-loading">
                  <span className="btn-dot" />
                  <span className="btn-dot" />
                  <span className="btn-dot" />
                </span>
              ) : (
                mode === "login" ? "Access Workspace →" : "Create Account →"
              )}
            </button>
          </form>

          <div className="landing-meta auth-meta" role="status" aria-live="polite">
            <span>{backendStatus}</span>
            <span>4-stage workflow</span>
            <span>3 model pool</span>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Home;
