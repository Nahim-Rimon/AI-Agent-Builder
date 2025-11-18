// Use relative path when in production (proxied through nginx)
// Use environment variable or localhost for development
export const API_BASE = process.env.REACT_APP_API_BASE || (process.env.NODE_ENV === 'production' ? '' : 'http://localhost:8000');
