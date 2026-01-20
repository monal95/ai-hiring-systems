/**
 * API Configuration
 * Centralizes all API endpoint configuration
 * 
 * For LOCAL development: Uses localhost:5000
 * For TUNNEL/REMOTE access: Uses the dev tunnel URL from .env
 */

// Detect if we're running locally or through a tunnel
const isLocalhost = window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1';

// Use localhost backend for local development, tunnel URL for external access
const API_BASE_URL = isLocalhost 
    ? 'http://localhost:5000' 
    : (process.env.REACT_APP_API_BASE_URL || 'http://localhost:5000');

// Log the API URL being used (helpful for debugging)
console.log('[API Config] Using API_BASE_URL:', API_BASE_URL);
console.log('[API Config] Is localhost:', isLocalhost);

export default API_BASE_URL;

/**
 * Configuration Guide:
 * 
 * 1. For LOCAL development (admin's system):
 *    - Set REACT_APP_API_BASE_URL=http://localhost:5000 in frontend/.env
 *    - Or leave it empty to use the default
 * 
 * 2. For EXTERNAL candidate access via Dev Tunnel:
 *    - Set REACT_APP_API_BASE_URL=https://your-tunnel-url.devtunnels.ms in frontend/.env
 *    - Example: REACT_APP_API_BASE_URL=https://3h16jwxk-5000.inc1.devtunnels.ms
 * 
 * 3. How it works:
 *    - You run the backend on localhost:5000
 *    - You run the frontend on localhost:3000
 *    - VS Code Dev Tunnels forward both ports publicly
 *    - Candidates access via tunnel URLs, which forward to your local server
 *    - Everything runs on YOUR system, candidates just access it remotely
 */
