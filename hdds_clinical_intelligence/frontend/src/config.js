// Central frontend config.
// Since we are now using a single-container deployment (FastAPI serves React),
// we use an empty string so the browser automatically requests from the same domain.
export const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:5001';
