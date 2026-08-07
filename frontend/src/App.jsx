import { useEffect, useState } from "react";
import { fetchHealth } from "./services/api";
import Home from "./pages/Home";
import Dashboard from "./pages/Dashboard";
import "./App.css";

function App() {
  const [backendStatus, setBackendStatus] = useState("Checking...");
  const [currentUser, setCurrentUser] = useState(() => {
    const stored = localStorage.getItem("orchestratorCurrentUser");
    return stored ? JSON.parse(stored) : null;
  });
  const [view, setView] = useState(() => {
    const stored = localStorage.getItem("orchestratorCurrentUser");
    return stored ? "dashboard" : "landing";
  });

  useEffect(() => {
    const loadStatus = async () => {
      try {
        const data = await fetchHealth();
        setBackendStatus(
          data?.status === "ok" ? "Backend online" : "Backend offline",
        );
      } catch (error) {
        setBackendStatus("Backend offline");
      }
    };

    loadStatus();
  }, []);

  useEffect(() => {
    if (currentUser) {
      localStorage.setItem(
        "orchestratorCurrentUser",
        JSON.stringify(currentUser),
      );
    } else {
      localStorage.removeItem("orchestratorCurrentUser");
    }
  }, [currentUser]);

  const handleAuthenticate = (user) => {
    setCurrentUser(user);
    setView("dashboard");
  };

  const handleLogout = () => {
    setCurrentUser(null);
    setView("landing");
  };

  return view === "landing" ? (
    <Home onAuthenticate={handleAuthenticate} backendStatus={backendStatus} />
  ) : (
    <Dashboard
      backendStatus={backendStatus}
      currentUser={currentUser}
      onBack={handleLogout}
    />
  );
}

export default App;
