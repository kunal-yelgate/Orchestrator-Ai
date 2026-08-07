import { useEffect, useState } from "react";
import { supabase } from "./lib/supabase";
import { fetchHealth } from "./services/api";
import Home from "./pages/Home";
import Dashboard from "./pages/Dashboard";
import "./App.css";

function App() {
  const [backendStatus, setBackendStatus] = useState("Checking...");

  // ============================
  // Supabase Auth
  // ============================

  const [currentUser, setCurrentUser] = useState(null);
  const [authLoading, setAuthLoading] = useState(true);

  // ============================
  // Backend Health
  // ============================

  useEffect(() => {
    const loadStatus = async () => {
      try {
        await fetchHealth();
        setBackendStatus("Backend online");
      } catch (error) {
        console.error(error);
        setBackendStatus("Backend offline");
      }
    };

    loadStatus();
  }, []);

  // ============================
  // Restore Session
  // ============================

  useEffect(() => {
    supabase.auth.getSession().then(({ data: { session } }) => {
      setCurrentUser(session?.user ?? null);
      setAuthLoading(false);
    });

    const {
      data: { subscription },
    } = supabase.auth.onAuthStateChange((_event, session) => {
      setCurrentUser(session?.user ?? null);
    });

    return () => subscription.unsubscribe();
  }, []);

  // ============================
  // Login
  // ============================

  const handleAuthenticate = (user) => {
    setCurrentUser(user);
  };

  // ============================
  // Logout
  // ============================

  const handleLogout = async () => {
    await supabase.auth.signOut();
  };

  // ============================
  // Loading
  // ============================

  if (authLoading) {
    return (
      <div
        style={{
          display: "grid",
          placeItems: "center",
          height: "100vh",
          fontSize: "20px",
        }}
      >
        Restoring your session...
      </div>
    );
  }

  // ============================
  // Render
  // ============================

  return currentUser ? (
    <Dashboard
      currentUser={currentUser}
      backendStatus={backendStatus}
      onBack={handleLogout}
    />
  ) : (
    <Home onAuthenticate={handleAuthenticate} />
  );
}

export default App;