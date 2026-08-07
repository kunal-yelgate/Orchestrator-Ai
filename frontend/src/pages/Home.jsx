import React, { useState, useEffect, useCallback } from "react";
import { supabase } from "../lib/supabase";

// ── Helpers ──────────────────────────────────────────────────────────

/** Detect email provider from email address for "Open inbox" shortcut */
function getInboxUrl(email) {
  const domain = (email || "").split("@")[1]?.toLowerCase() || "";
  if (domain.includes("gmail")) return "https://mail.google.com";
  if (domain.includes("outlook") || domain.includes("hotmail") || domain.includes("live"))
    return "https://outlook.live.com";
  if (domain.includes("yahoo")) return "https://mail.yahoo.com";
  if (domain.includes("proton")) return "https://mail.proton.me";
  if (domain.includes("icloud") || domain.includes("apple")) return "https://www.icloud.com/mail";
  return null;
}

/** Map raw Supabase error messages to user-friendly strings */
function friendlyAuthError(message = "") {
  if (message.includes("Email not confirmed"))
    return "Your email isn't verified yet. Check your inbox (and spam) for the verification link.";
  if (message.includes("Invalid login credentials") || message.includes("invalid_credentials"))
    return "Incorrect email or password. Double-check and try again.";
  if (message.includes("User already registered"))
    return "An account with this email already exists. Try signing in instead.";
  if (message.includes("rate limit") || message.includes("429") || message.includes("over_email_send_rate_limit"))
    return "Email rate limit hit (Supabase allows ~2 emails/hour on free tier). Wait a moment and try again, or check your spam folder — the email may have already been sent.";
  if (message.includes("Password should be"))
    return message; // pass Supabase's own password policy message through
  if (message.includes("Unable to validate email"))
    return "Please enter a valid email address.";
  return message;
}

// ── Verify Email Screen ───────────────────────────────────────────────
/**
 * Shown right after a successful signUp().
 * Features:
 *  - Countdown timer before allowing resend (60 s)
 *  - "Open inbox" shortcut based on email domain
 *  - "I've verified — continue" button that polls Supabase for an active session
 *  - Rate-limit warning
 */
const VerifyEmailScreen = ({ email, onVerified, onBack }) => {
  const [resendCooldown, setResendCooldown] = useState(60);
  const [resendStatus, setResendStatus] = useState("idle"); // idle | sending | sent | error
  const [checkingSession, setCheckingSession] = useState(false);
  const [checkError, setCheckError] = useState("");

  const inboxUrl = getInboxUrl(email);

  // Count-down timer
  useEffect(() => {
    if (resendCooldown <= 0) return;
    const id = setInterval(() => setResendCooldown((c) => c - 1), 1000);
    return () => clearInterval(id);
  }, [resendCooldown]);

  // Resend verification email
  const handleResend = async () => {
    setResendStatus("sending");
    const { error } = await supabase.auth.resend({ type: "signup", email });
    if (error) {
      setResendStatus("error");
      console.error("[resend]", error.message);
    } else {
      setResendStatus("sent");
      setResendCooldown(60); // restart cooldown
    }
  };

  // "I've verified" — try to get the current session
  const handleCheckVerified = useCallback(async () => {
    setCheckingSession(true);
    setCheckError("");
    // Refresh the session from the server — will succeed if user clicked the link
    const { data: { session }, error } = await supabase.auth.getSession();
    if (error) {
      setCheckError("Couldn't check verification status. Please try again.");
      setCheckingSession(false);
      return;
    }
    if (session?.user) {
      onVerified(session.user);
      return;
    }
    // No session yet — user hasn't clicked the link
    setCheckError("Your email isn't verified yet. Click the link in the email first.");
    setCheckingSession(false);
  }, [onVerified]);

  return (
    <div className="auth-card verify-card" role="main" aria-label="Email verification required">
      <div className="verify-icon" aria-hidden="true">✉️</div>

      <div className="landing-badge">Check your inbox</div>

      <h2 className="auth-title">
        Verify your <span className="gradient-text">email</span>
      </h2>

      <p className="verify-desc">
        We sent a verification link to{" "}
        <strong className="verify-email">{email}</strong>.
        <br />
        Click that link to activate your account, then come back here.
      </p>

      {/* Inbox shortcut */}
      {inboxUrl && (
        <a
          href={inboxUrl}
          target="_blank"
          rel="noopener noreferrer"
          className="primary-btn auth-submit open-inbox-btn"
          id="open-inbox-btn"
          aria-label={`Open inbox for ${email}`}
        >
          Open inbox ↗
        </a>
      )}

      {/* Step tracker */}
      <div className="verify-steps" role="list">
        <div className="verify-step done" role="listitem">
          <span className="vstep-icon">✓</span>
          <span>Account created</span>
        </div>
        <div className="verify-step active" role="listitem">
          <span className="vstep-icon">→</span>
          <span>Click the verification link in your email</span>
        </div>
        <div className="verify-step" role="listitem">
          <span className="vstep-icon">3</span>
          <span>Sign in to your workspace</span>
        </div>
      </div>

      {/* "I've verified" button */}
      <button
        id="check-verified-btn"
        className="primary-btn auth-submit"
        type="button"
        onClick={handleCheckVerified}
        disabled={checkingSession}
        aria-busy={checkingSession}
      >
        {checkingSession ? (
          <span className="btn-loading" aria-label="Checking…">
            <span className="btn-dot" /><span className="btn-dot" /><span className="btn-dot" />
          </span>
        ) : (
          "I've verified my email — continue →"
        )}
      </button>

      {checkError && (
        <div className="global-error" role="alert" aria-live="assertive">
          <span aria-hidden="true">⚠</span> {checkError}
        </div>
      )}

      {/* Resend section */}
      <div className="verify-resend-row">
        <p className="verify-note">
          Didn't receive it?{" "}
          <strong>Check your spam/junk folder first.</strong>
        </p>

        <button
          id="resend-email-btn"
          className="link-btn"
          type="button"
          onClick={handleResend}
          disabled={resendCooldown > 0 || resendStatus === "sending"}
          aria-label={resendCooldown > 0 ? `Resend available in ${resendCooldown}s` : "Resend verification email"}
        >
          {resendStatus === "sending" && "Sending…"}
          {resendStatus === "sent" && "✓ Email resent!"}
          {resendStatus === "error" && "Resend failed — try again"}
          {(resendStatus === "idle" || (resendStatus !== "sending" && resendStatus !== "sent" && resendStatus !== "error")) && (
            resendCooldown > 0
              ? `Resend in ${resendCooldown}s`
              : "Resend verification email"
          )}
        </button>

        {resendCooldown === 0 && resendStatus === "idle" && (
          <p className="verify-note rate-note">
            ⚠️ Supabase free tier allows ~2 emails/hour. If resend fails, wait before retrying.
          </p>
        )}
      </div>

      <button
        id="back-to-login-btn"
        className="link-btn back-link"
        type="button"
        onClick={onBack}
      >
        ← Back to Sign In
      </button>
    </div>
  );
};

// ── Main component ────────────────────────────────────────────────────
const Home = ({ onAuthenticate, backendStatus }) => {
  const [mode, setMode] = useState("login");
  const [name, setName] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");
  const [errors, setErrors] = useState({});
  const [globalError, setGlobalError] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [signupEmail, setSignupEmail] = useState(""); // triggers verification screen

  // ── Client-side validation ───────────────────────────────────────
  const validate = () => {
    const e = {};
    if (mode === "signup" && !name.trim()) e.name = "Full name is required.";

    if (!email.trim()) {
      e.email = "Email is required.";
    } else if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email)) {
      e.email = "Enter a valid email address.";
    }

    if (!password) {
      e.password = "Password is required.";
    } else if (password.length < 8) {
      e.password = "Password must be at least 8 characters.";
    } else if (mode === "signup" && !/[A-Z]/.test(password)) {
      e.password = "Include at least one uppercase letter.";
    } else if (mode === "signup" && !/[0-9]/.test(password)) {
      e.password = "Include at least one number.";
    }

    if (mode === "signup" && password && password !== confirmPassword) {
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

  // ── Sign Up ───────────────────────────────────────────────────────
  const handleSignUp = async () => {
    const { data, error } = await supabase.auth.signUp({
      email: email.trim(),
      password,
      options: {
        data: { full_name: name.trim() },
        // Must be whitelisted in Supabase Dashboard → Auth → URL Configuration → Redirect URLs
        emailRedirectTo: `${window.location.origin}/`,
      },
    });

    console.log("[signUp] response:", { data, error });

    if (error) {
      setGlobalError(friendlyAuthError(error.message));
      return;
    }

    // data.user === null means email already existed (Supabase hides this for security)
    if (!data.user) {
      setGlobalError(
        "This email may already be registered. Try signing in, or use a different email."
      );
      return;
    }

    // data.session === null → email confirmation required → show verification screen
    if (!data.session) {
      setSignupEmail(email.trim());
      return;
    }

    // data.session exists → "Confirm email" is disabled in Supabase project → log straight in
    onAuthenticate(data.user);
  };

  // ── Login ─────────────────────────────────────────────────────────
  const handleLogin = async () => {
    const { data, error } = await supabase.auth.signInWithPassword({
      email: email.trim(),
      password,
    });

    console.log("[signIn] response:", { data, error });

    if (error) {
      setGlobalError(friendlyAuthError(error.message));
      return;
    }

    onAuthenticate(data.user);
  };

  const switchMode = (newMode) => {
    setMode(newMode);
    setErrors({});
    setGlobalError("");
  };

  // ── Password strength ─────────────────────────────────────────────
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

  // ── Verification screen ───────────────────────────────────────────
  if (signupEmail) {
    return (
      <div className="landing-shell">
        <div className="orb orb-1" aria-hidden="true" />
        <div className="orb orb-2" aria-hidden="true" />
        <div className="orb orb-3" aria-hidden="true" />
        <div className="landing-layout verify-layout">
          <VerifyEmailScreen
            email={signupEmail}
            onVerified={(user) => {
              setSignupEmail("");
              onAuthenticate(user);
            }}
            onBack={() => {
              setSignupEmail("");
              setMode("login");
            }}
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
                  : "A verification email will be sent to activate your account."}
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

          {globalError && (
            <div className="global-error" role="alert" aria-live="assertive">
              <span aria-hidden="true">⚠</span> {globalError}
            </div>
          )}

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
                  aria-invalid={!!errors.name}
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
                aria-invalid={!!errors.email}
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
                placeholder={mode === "signup" ? "Min 8 chars, 1 uppercase, 1 number" : "Your password"}
                autoComplete={mode === "login" ? "current-password" : "new-password"}
                aria-invalid={!!errors.password}
              />
              {errors.password && <span className="field-error" role="alert">{errors.password}</span>}

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
              aria-busy={isLoading}
            >
              {isLoading ? (
                <span className="btn-loading" aria-label="Loading">
                  <span className="btn-dot" /><span className="btn-dot" /><span className="btn-dot" />
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
