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

// Upload a single file. Returns { path, filename } — `path` is the
// server-side path to pass into orchestrate()'s `documents` array.
export const uploadFile = async (file) => {
    const formData = new FormData();
    formData.append("file", file);

    const response = await fetch(`${API_BASE_URL}/upload`, {
        method: "POST",
        body: formData,
    });

    if (!response.ok) {
        throw new Error(await response.text());
    }

    return response.json();
};

// Upload several files in parallel. Returns the array of server-side
// paths, ready to hand to orchestrate().
export const uploadFiles = async (files) => {
    const results = await Promise.all(files.map((file) => uploadFile(file)));
    return results.map((r) => r.path);
};

// Main Orchestrator API
export const orchestrate = async (goal, provider, documents = []) => {

    const response = await fetch(`${API_BASE_URL}/orchestrate`, {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
        },
        body: JSON.stringify({
            goal,
            provider,
            documents,
        }),
    });

    if (!response.ok) {
        throw new Error(await response.text());
    }

    return response.json();
};

// List saved workflows (for a checkpoint picker)
export const fetchWorkflows = async () => {
    const response = await fetch(`${API_BASE_URL}/workflows`);

    if (!response.ok) {
        throw new Error(await response.text());
    }

    return response.json();
};

// List checkpoints for one workflow — one entry per completed graph node
export const fetchCheckpoints = async (workflowId) => {
    const response = await fetch(`${API_BASE_URL}/workflows/${workflowId}/checkpoints`);

    if (!response.ok) {
        throw new Error(await response.text());
    }

    return response.json();
};

// Roll back to a checkpoint and resume execution from the next node
export const rollbackWorkflow = async (workflowId, checkpointFile) => {
    const response = await fetch(`${API_BASE_URL}/workflows/${workflowId}/rollback`, {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
        },
        body: JSON.stringify({
            checkpoint_file: checkpointFile,
        }),
    });

    if (!response.ok) {
        throw new Error(await response.text());
    }

    return response.json();
};
