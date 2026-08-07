import React, { useState } from "react";

const Home = ({ onAuthenticate, backendStatus }) => {
  const [mode, setMode] = useState("login");
  const [name, setName] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [errors, setErrors] = useState({});

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
      nextErrors.password = "Password must be at least 6 characters.";
    }
    if (mode === "signup") {
      if (!name.trim()) {
        nextErrors.name = "Name is required for sign up.";
      }
    }
    setErrors(nextErrors);
    return Object.keys(nextErrors).length === 0;
  };

  const handleSubmit = (event) => {
    event.preventDefault();
    if (!validate()) return;

    const user = {
      name:
        mode === "signup"
          ? name.trim()
          : email.substring(0, email.indexOf("@")) || email,
      email: email.trim(),
    };

    onAuthenticate(user);
  };

  return (
    <div className="landing-shell">
      <div className="landing-card auth-card">
        <div className="auth-header">
          <div>
            <div className="landing-badge">Professional AI orchestration</div>
            <h1>
              {mode === "login"
                ? "Login to the dashboard"
                : "Create your account"}
            </h1>
            <p>
              {mode === "login"
                ? "Enter your email and password to continue."
                : "Sign up with your name, email, and password to start using the dashboard."}
            </p>
          </div>
          <div className="auth-switch">
            <button
              className={`tab-button ${mode === "login" ? "active" : ""}`}
              type="button"
              onClick={() => setMode("login")}
            >
              Login
            </button>
            <button
              className={`tab-button ${mode === "signup" ? "active" : ""}`}
              type="button"
              onClick={() => setMode("signup")}
            >
              Sign Up
            </button>
          </div>
        </div>

        <form className="auth-form" onSubmit={handleSubmit} noValidate>
          {mode === "signup" && (
            <label className="field-group">
              <span>Name</span>
              <input
                type="text"
                value={name}
                onChange={(event) => setName(event.target.value)}
                placeholder="Full name"
              />
              {errors.name && (
                <span className="field-error">{errors.name}</span>
              )}
            </label>
          )}

          <label className="field-group">
            <span>Email</span>
            <input
              type="email"
              value={email}
              onChange={(event) => setEmail(event.target.value)}
              placeholder="you@example.com"
            />
            {errors.email && (
              <span className="field-error">{errors.email}</span>
            )}
          </label>

          <label className="field-group">
            <span>Password</span>
            <input
              type="password"
              value={password}
              onChange={(event) => setPassword(event.target.value)}
              placeholder="Minimum 6 characters"
            />
            {errors.password && (
              <span className="field-error">{errors.password}</span>
            )}
          </label>

          <button className="primary-btn auth-submit" type="submit">
            {mode === "login" ? "Login" : "Create account"}
          </button>
        </form>

        <div className="landing-meta auth-meta">
          <span>Backend: {backendStatus}</span>
          <span>Workflow: 4 stages</span>
        </div>
      </div>
    </div>
  );
};

export default Home;
