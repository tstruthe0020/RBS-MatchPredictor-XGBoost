// Test script - place this in browser console to verify frontend-backend connectivity
const testBackendConnection = async () => {
    console.log('🔍 Testing frontend-backend connection...');
    console.log(`Backend URL configured: ${process.env.REACT_APP_BACKEND_URL || 'http://localhost:8001'}`);
    
    const API_URL = (process.env.REACT_APP_BACKEND_URL || 'http://localhost:8001') + '/api';
    
    const endpoints = [
        '/stats',
        '/teams',
        '/referees',
        '/formations'
    ];
    
    for (const endpoint of endpoints) {
        try {
            const response = await fetch(`${API_URL}${endpoint}`);
            if (response.ok) {
                console.log(`✅ ${endpoint}: ${response.status} OK`);
            } else {
                console.log(`❌ ${endpoint}: ${response.status} ${response.statusText}`);
            }
        } catch (error) {
            console.log(`❌ ${endpoint}: ${error.message}`);
        }
    }
    
    console.log('✅ Connection test complete!');
};

// Auto-run if in browser environment
if (typeof window !== 'undefined') {
    testBackendConnection();
}