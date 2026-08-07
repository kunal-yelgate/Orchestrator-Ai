const API_BASE_URL = "http://127.0.0.1:8000";

// Health Check
export const fetchHealth = async () => {
    const response = await fetch(`${API_BASE_URL}/health`);

    if (!response.ok) {
        throw new Error("Backend is not running");
    }

    return response.json();
};

// Available Providers
export const fetchProviders = async () => {
    const response = await fetch(`${API_BASE_URL}/providers`);

    if (!response.ok) {
        throw new Error("Unable to fetch providers");
    }

    return response.json();
};

// Main Orchestrator API
export const orchestrate = async (goal, provider) => {

    const response = await fetch(`${API_BASE_URL}/orchestrate`, {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
        },
        body: JSON.stringify({
            goal,
            provider,
        }),
    });

    if (!response.ok) {
        throw new Error(await response.text());
    }

    return response.json();
};