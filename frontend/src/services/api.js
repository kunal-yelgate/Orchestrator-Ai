const API_BASE_URL = 'http://localhost:5000';

export const fetchHealth = async () => {
  const response = await fetch(`${API_BASE_URL}/health`);
  return response.json();
};
