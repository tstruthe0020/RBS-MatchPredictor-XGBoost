// Test script to verify frontend can connect to backend locally
const API_URL = 'http://localhost:8001/api';

console.log('Testing local frontend-backend connection...');
console.log(`Frontend should connect to: ${API_URL}`);

// Test basic endpoints
const testEndpoints = [
    '/stats',
    '/teams', 
    '/referees',
    '/formations',
    '/time-decay/presets'
];

async function testConnection() {
    console.log('\n=== Testing Backend Connectivity ===');
    
    for (const endpoint of testEndpoints) {
        try {
            const response = await fetch(`${API_URL}${endpoint}`);
            const status = response.status;
            console.log(`✅ ${endpoint}: ${status} ${response.ok ? 'OK' : 'ERROR'}`);
        } catch (error) {
            console.log(`❌ ${endpoint}: Connection failed - ${error.message}`);
        }
    }
}

// Run if in Node.js environment
if (typeof window === 'undefined') {
    // Node.js environment
    const fetch = require('node-fetch');
    testConnection();
} else {
    // Browser environment
    console.log('Run this in browser console to test frontend connectivity:');
    console.log('testConnection()');
    window.testConnection = testConnection;
}