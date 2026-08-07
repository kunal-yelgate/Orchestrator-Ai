import { useEffect, useState } from "react";
import { fetchHealth } from "./services/api";
import Home from "./pages/Home";
import Dashboard from "./pages/Dashboard";
import "./App.css";

function App() {
  const [view, setView] = useState("landing");
  const [backendStatus, setBackendStatus] = useState("Checking...");

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

  return view === "landing" ? (
    <Home
      onEnterDashboard={() => setView("dashboard")}
      backendStatus={backendStatus}
    />
  ) : (
    <Dashboard
      backendStatus={backendStatus}
      onBack={() => setView("landing")}
    />
  );
}

export default App;
