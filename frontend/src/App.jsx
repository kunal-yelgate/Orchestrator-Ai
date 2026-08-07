import { useEffect, useState } from "react";
import { supabase } from "./lib/supabase";
import { fetchHealth } from "./services/api";
import Home from "./pages/Home";
import Dashboard from "./pages/Dashboard";
import "./App.css";

function App() {
  const [backendStatus, setBackendStatus] = useState("Checking...");
  // null = loading, false = no session, object = authenticated user
  const [currentUser, setCurrentUser] = useState(null);
  const [authLoading, setAuthLoading] = useState(true);

  // ── Backend health check ────────────────────────────────────────
  useEffect(() => {
    const loadStatus = async () => {
      try {
        const data = await fetchHealth();
        setBackendStatus(
          data?.status === "ok" ? "Backend online" : "Backend offline",
        );
      } catch {
        setBackendStatus("Backend offline");
      }
    };
    loadStatus();
  }, []);

  // ── Supabase session bootstrap + live listener ──────────────────
  useEffect(() => {
    // 1. Restore any existing session from localStorage on first load
    supabase.auth.getSession().then(({ data: { session } }) => {
      setCurrentUser(session?.user ?? null);
      setAuthLoading(false);
    });

    // 2. Listen for all future auth state changes:
    //    SIGNED_IN, SIGNED_OUT, TOKEN_REFRESHED, USER_UPDATED, etc.
    //    This fires when the user clicks the verification email link too
    //    (Supabase redirects back with #access_token in the URL).
    const {
      data: { subscription },
    } = supabase.auth.onAuthStateChange((_event, session) => {
      setCurrentUser(session?.user ?? null);
    });

    // Cleanup the listener when the component unmounts
    return () => subscription.unsubscribe();
  }, []);

  // ── Handlers ───────────────────────────────────────────────────
  const handleAuthenticate = (user) => setCurrentUser(user);

  const handleLogout = async () => {
    await supabase.auth.signOut();
    // onAuthStateChange fires SIGNED_OUT → sets currentUser to null automatically
  };

  // ── Loading state (prevents flash of login page) ───────────────
  if (authLoading) {
    return (
      <div className="auth-loading-shell" aria-busy="true" aria-label="Loading session">
        <div className="auth-loading-spinner" aria-hidden="true" />
        <p>Restoring your session…</p>
      </div>
    );
  }

  return currentUser ? (
    <Dashboard
      backendStatus={backendStatus}
      currentUser={currentUser}
      onBack={handleLogout}
    />
  ) : (
    <Home
      onAuthenticate={handleAuthenticate}
      backendStatus={backendStatus}
    />
  );
}

export default App;
