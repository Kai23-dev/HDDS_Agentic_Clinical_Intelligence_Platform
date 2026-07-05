// Central frontend config.
// API base URL comes from the Vite env var VITE_API_URL at build/deploy time
// (e.g. the Azure backend URL), falling back to local dev.
export const API_URL = import.meta.env.VITE_API_URL || 'http://127.0.0.1:8000';
