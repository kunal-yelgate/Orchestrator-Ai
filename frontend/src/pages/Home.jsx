import React, { useState } from "react";
import { supabase } from "../lib/supabase";

// ─── Sub-screens ────────────────────────────────────────────────────
/**
 * Shown after a successful signUp() call.
 * Supabase has sent a verification email — user must click the link
 * before they can log in.
 */
const VerifyEmailScreen = ({ email, onBack }) => (
  <div className="auth-card verify-card" role="main">
    <div className="verify-icon" aria-hidden="true">✉️</div>
    <div className="landing-badge">Check your inbox</div>
    <h2 className="auth-title">
      Verify your <span className="gradient-text">email</span>
    </h2>
    <p className="verify-desc">
      We sent a verification link to{" "}
      <strong className="verify-email">{email}</strong>.
      <br />
      Click the link in that email to activate your account, then come
      back here to sign in.
    </p>

    <div className="verify-steps">
      <div className="verify-step done">
        <span className="vstep-icon">✓</span>
        <span>Account created</span>
      </div>
      <div className="verify-step active">
        <span className="vstep-icon">→</span>
        <span>Open verification email</span>
      </div>
      <div className="verify-step">
        <span className="vstep-icon">3</span>
        <span>Sign in to workspace</span>
      </div>
    </div>

    <button
      id="back-to-login-btn"
      className="primary-btn auth-submit"
      type="button"
      onClick={onBack}
    >
      Go to Sign In →
    </button>

    <p className="verify-note">
      Didn't receive it? Check your spam folder, or{" "}
      <button
        className="link-btn"
        type="button"
        onClick={async () => {
          await supabase.auth.resend({ type: "signup", email });
          alert("Verification email resent!");
        }}
      >
        resend the email
      </button>
      .
    </p>
  </div>
);

// ─── Main component ─────────────────────────────────────────────────
const Home = ({ onAuthenticate, backendStatus }) => {
  const [mode, setMode] = useState("login");
  const [name, setName] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");
  const [errors, setErrors] = useState({});
  const [globalError, setGlobalError] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [signupEmail, setSignupEmail] = useState(""); // email used for verification screen

  // ── Client-side field validation ─────────────────────────────────
  const validate = () => {
    const e = {};

    if (mode === "signup" && !name.trim()) {
      e.name = "Full name is required.";
    }

    if (!email.trim()) {
      e.email = "Email is required.";
    } else if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email)) {
      e.email = "Enter a valid email address.";
    }

    if (!password) {
      e.password = "Password is required.";
    } else if (password.length < 8) {
      e.password = "Password must be at least 8 characters.";
    } else if (!/[A-Z]/.test(password)) {
      e.password = "Include at least one uppercase letter.";
    } else if (!/[0-9]/.test(password)) {
      e.password = "Include at least one number.";
    }

    if (mode === "signup" && password !== confirmPassword) {
      e.confirmPassword = "Passwords do not match.";
    }

    setErrors(e);
    return Object.keys(e).length === 0;
  };

  // ── Submit ────────────────────────────────────────────────────────
  const handleSubmit = async (event) => {
    event.preventDefault();
    setGlobalError("");
    if (!validate()) return;

    setIsLoading(true);
    try {
      if (mode === "signup") {
        await handleSignUp();
      } else {
        await handleLogin();
      }
    } finally {
      setIsLoading(false);
    }
  };

  // ── Sign Up via Supabase ─────────────────────────────────────────
  const handleSignUp = async () => {
    const { data, error } = await supabase.auth.signUp({
      email: email.trim(),
      password,
      options: {
        data: { full_name: name.trim() },           // saved in user_metadata
        emailRedirectTo: window.location.origin,     // redirect back here after verification
      },
    });

    if (error) {
      setGlobalError(error.message);
      return;
    }

    if (data.user && !data.session) {
      // Supabase returns a user but no session → email NOT yet confirmed
      // → show the "check your inbox" screen
      setSignupEmail(email.trim());
      return;
    }

    // Edge case: email confirmation disabled in Supabase project settings
    if (data.session) {
      onAuthenticate(data.user);
    }
  };

  // ── Login via Supabase ───────────────────────────────────────────
  const handleLogin = async () => {
    const { data, error } = await supabase.auth.signInWithPassword({
      email: email.trim(),
      password,
    });

    if (error) {
      // Friendly error messages for common Supabase errors
      if (error.message.includes("Email not confirmed")) {
        setGlobalError(
          "Your email is not verified yet. Please check your inbox and click the verification link."
        );
      } else if (
        error.message.includes("Invalid login credentials") ||
        error.message.includes("invalid_credentials")
      ) {
        setGlobalError("Incorrect email or password. Please try again.");
      } else {
        setGlobalError(error.message);
      }
      return;
    }

    // Session is now active — App.jsx's onAuthStateChange will pick this up
    // and set currentUser, but we also call onAuthenticate for immediate UI update
    onAuthenticate(data.user);
  };

  const switchMode = (newMode) => {
    setMode(newMode);
    setErrors({});
    setGlobalError("");
  };

  // ── Password strength indicator ──────────────────────────────────
  const getPasswordStrength = (pw) => {
    if (!pw) return { score: 0, label: "", color: "" };
    let score = 0;
    if (pw.length >= 8) score++;
    if (/[A-Z]/.test(pw)) score++;
    if (/[0-9]/.test(pw)) score++;
    if (/[^A-Za-z0-9]/.test(pw)) score++;
    const labels = ["", "Weak", "Fair", "Good", "Strong"];
    const colors = ["", "#ef4444", "#f59e0b", "#10b981", "#06b6d4"];
    return { score, label: labels[score] || "Weak", color: colors[score] || "#ef4444" };
  };

  const strength = mode === "signup" ? getPasswordStrength(password) : null;

  const features = [
    { icon: "⬡", label: "Multi-model routing", desc: "GPT-4, Gemini, Claude orchestrated in sequence" },
    { icon: "◈", label: "LangGraph pipeline", desc: "4-stage traceable workflow execution" },
    { icon: "✦", label: "Quality verification", desc: "Automated cross-model consistency checks" },
  ];

  // ── If signup was successful → show verification screen ──────────
  if (signupEmail) {
    return (
      <div className="landing-shell">
        <div className="orb orb-1" aria-hidden="true" />
        <div className="orb orb-2" aria-hidden="true" />
        <div className="orb orb-3" aria-hidden="true" />
        <div className="landing-layout verify-layout">
          <VerifyEmailScreen
            email={signupEmail}
            onBack={() => { setSignupEmail(""); setMode("login"); }}
          />
        </div>
      </div>
    );
  }

  // ── Main auth page ────────────────────────────────────────────────
  return (
    <div className="landing-shell">
      <div className="orb orb-1" aria-hidden="true" />
      <div className="orb orb-2" aria-hidden="true" />
      <div className="orb orb-3" aria-hidden="true" />

      <div className="landing-layout">
        {/* Left — hero */}
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

        {/* Right — auth card */}
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
                  : "Set up your account. A verification email will be sent."}
              </p>
            </div>

            <div className="auth-switch" role="tablist" aria-label="Auth mode">
              <button
                id="tab-login"
                className={`tab-button ${mode === "login" ? "active" : ""}`}
                type="button"
                role="tab"
                aria-selected={mode === "login"}
                onClick={() => switchMode("login")}
              >
                Sign In
              </button>
              <button
                id="tab-signup"
                className={`tab-button ${mode === "signup" ? "active" : ""}`}
                type="button"
                role="tab"
                aria-selected={mode === "signup"}
                onClick={() => switchMode("signup")}
              >
                Sign Up
              </button>
            </div>
          </div>

          {/* Global API error */}
          {globalError && (
            <div className="global-error" role="alert" aria-live="assertive">
              <span aria-hidden="true">⚠</span> {globalError}
            </div>
          )}

          <form className="auth-form" onSubmit={handleSubmit} noValidate aria-label="Authentication form">
            {/* Name — signup only */}
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
                  aria-invalid={!!errors.name}
                />
                {errors.name && (
                  <span className="field-error" role="alert">{errors.name}</span>
                )}
              </label>
            )}

            {/* Email */}
            <label className="field-group" htmlFor="auth-email">
              <span>Email address</span>
              <input
                id="auth-email"
                type="email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                placeholder="you@example.com"
                autoComplete="email"
                aria-invalid={!!errors.email}
              />
              {errors.email && (
                <span className="field-error" role="alert">{errors.email}</span>
              )}
            </label>

            {/* Password */}
            <label className="field-group" htmlFor="auth-password">
              <span>Password</span>
              <input
                id="auth-password"
                type="password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                placeholder={mode === "signup" ? "Min 8 chars, 1 uppercase, 1 number" : "Your password"}
                autoComplete={mode === "login" ? "current-password" : "new-password"}
                aria-invalid={!!errors.password}
              />
              {errors.password && (
                <span className="field-error" role="alert">{errors.password}</span>
              )}

              {/* Password strength meter — signup only */}
              {mode === "signup" && password && (
                <div className="strength-meter" aria-label={`Password strength: ${strength.label}`}>
                  <div className="strength-bar">
                    {[1, 2, 3, 4].map((n) => (
                      <div
                        key={n}
                        className="strength-segment"
                        style={{
                          background: n <= strength.score ? strength.color : undefined,
                          opacity: n <= strength.score ? 1 : 0.2,
                        }}
                      />
                    ))}
                  </div>
                  <span style={{ color: strength.color }}>{strength.label}</span>
                </div>
              )}
            </label>

            {/* Confirm password — signup only */}
            {mode === "signup" && (
              <label className="field-group" htmlFor="auth-confirm-password">
                <span>Confirm password</span>
                <input
                  id="auth-confirm-password"
                  type="password"
                  value={confirmPassword}
                  onChange={(e) => setConfirmPassword(e.target.value)}
                  placeholder="Re-enter your password"
                  autoComplete="new-password"
                  aria-invalid={!!errors.confirmPassword}
                />
                {errors.confirmPassword && (
                  <span className="field-error" role="alert">{errors.confirmPassword}</span>
                )}
              </label>
            )}

            <button
              id="auth-submit-btn"
              className="primary-btn auth-submit"
              type="submit"
              disabled={isLoading}
            >
              {isLoading ? (
                <span className="btn-loading" aria-label="Loading">
                  <span className="btn-dot" />
                  <span className="btn-dot" />
                  <span className="btn-dot" />
                </span>
              ) : (
                mode === "login" ? "Access Workspace →" : "Create Account & Verify →"
              )}
            </button>
          </form>

          <div className="landing-meta auth-meta" role="status" aria-live="polite">
            <span>{backendStatus}</span>
            <span>4-stage workflow</span>
            <span>Email verified auth</span>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Home;
