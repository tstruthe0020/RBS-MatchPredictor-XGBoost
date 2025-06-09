import requests
import os
import json

# Get the backend URL from environment
BACKEND_URL = os.environ.get('REACT_APP_BACKEND_URL', 'http://localhost:8001')
BASE_URL = f"{BACKEND_URL}/api"

def test_endpoint(endpoint, method="GET", data=None, expected_status=200):
    """Test an endpoint and return whether it's accessible"""
    print(f"Testing {method} {endpoint}...")
    
    try:
        if method == "GET":
            response = requests.get(f"{BASE_URL}/{endpoint}")
        elif method == "POST":
            response = requests.post(f"{BASE_URL}/{endpoint}", json=data)
        else:
            print(f"Unsupported method: {method}")
            return False
        
        status_ok = response.status_code == expected_status
        
        if status_ok:
            print(f"✅ {method} {endpoint} - Status: {response.status_code} OK")
        else:
            print(f"❌ {method} {endpoint} - Status: {response.status_code}")
            print(f"Response: {response.text}")
        
        return status_ok
    except Exception as e:
        print(f"❌ {method} {endpoint} - Error: {e}")
        return False

def test_all_endpoints():
    """Test all the required endpoints"""
    print("\n========== TESTING ADVANCED FEATURES ENDPOINTS ==========\n")
    
    # High Priority Features
    print("\n--- High Priority Features ---\n")
    
    # 1. PDF Export
    pdf_export = test_endpoint("export-prediction-pdf", "POST", {
        "home_team": "Arsenal",
        "away_team": "Chelsea",
        "referee_name": "Michael Oliver"
    })
    
    # 2. Enhanced RBS Analysis
    enhanced_rbs = test_endpoint("enhanced-rbs-analysis/Arsenal/Michael Oliver")
    
    # 3. Team Performance Analysis
    team_performance = test_endpoint("team-performance/Arsenal")
    
    # Medium Priority Features
    print("\n--- Medium Priority Features ---\n")
    
    # 4. Configuration Management
    prediction_configs = test_endpoint("prediction-configs")
    rbs_configs = test_endpoint("rbs-configs")
    
    # 5. Advanced AI Optimization
    suggest_prediction = test_endpoint("suggest-prediction-config", "POST")
    rbs_optimization = test_endpoint("analyze-rbs-optimization", "POST")
    predictor_optimization = test_endpoint("analyze-predictor-optimization", "POST")
    comprehensive_regression = test_endpoint("analyze-comprehensive-regression", "POST")
    
    # Print summary
    print("\n========== ENDPOINT TEST SUMMARY ==========\n")
    print("High Priority Features:")
    print(f"1. PDF Export: {'✅ Accessible' if pdf_export else '❌ Not accessible'}")
    print(f"2. Enhanced RBS Analysis: {'✅ Accessible' if enhanced_rbs else '❌ Not accessible'}")
    print(f"3. Team Performance Analysis: {'✅ Accessible' if team_performance else '❌ Not accessible'}")
    
    print("\nMedium Priority Features:")
    print(f"4a. Prediction Configs: {'✅ Accessible' if prediction_configs else '❌ Not accessible'}")
    print(f"4b. RBS Configs: {'✅ Accessible' if rbs_configs else '❌ Not accessible'}")
    print(f"5a. Suggest Prediction Config: {'✅ Accessible' if suggest_prediction else '❌ Not accessible'}")
    print(f"5b. Analyze RBS Optimization: {'✅ Accessible' if rbs_optimization else '❌ Not accessible'}")
    print(f"5c. Analyze Predictor Optimization: {'✅ Accessible' if predictor_optimization else '❌ Not accessible'}")
    print(f"5d. Analyze Comprehensive Regression: {'✅ Accessible' if comprehensive_regression else '❌ Not accessible'}")

if __name__ == "__main__":
    test_all_endpoints()
