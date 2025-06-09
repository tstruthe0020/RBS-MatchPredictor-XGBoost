import requests
import os
import sys
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
            print(f"Response: {response.text[:500]}...")
        else:
            print(f"❌ {method} {endpoint} - Status: {response.status_code}")
            print(f"Response: {response.text}")
        
        return status_ok
    except Exception as e:
        print(f"❌ {method} {endpoint} - Error: {e}")
        return False

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python test_individual_endpoints.py <endpoint_number>")
        print("Endpoint numbers:")
        print("1: PDF Export")
        print("2: Enhanced RBS Analysis")
        print("3: Team Performance Analysis")
        print("4: Prediction Configs")
        print("5: RBS Configs")
        print("6: Suggest Prediction Config")
        print("7: Analyze RBS Optimization")
        print("8: Analyze Predictor Optimization")
        print("9: Analyze Comprehensive Regression")
        sys.exit(1)
    
    endpoint_number = int(sys.argv[1])
    
    if endpoint_number == 1:
        # 1. PDF Export
        test_endpoint("export-prediction-pdf", "POST", {
            "home_team": "Arsenal",
            "away_team": "Chelsea",
            "referee_name": "Michael Oliver"
        })
    elif endpoint_number == 2:
        # 2. Enhanced RBS Analysis
        test_endpoint("enhanced-rbs-analysis/Arsenal/Michael Oliver")
    elif endpoint_number == 3:
        # 3. Team Performance Analysis
        test_endpoint("team-performance/Arsenal")
    elif endpoint_number == 4:
        # 4a. Prediction Configs
        test_endpoint("prediction-configs")
    elif endpoint_number == 5:
        # 4b. RBS Configs
        test_endpoint("rbs-configs")
    elif endpoint_number == 6:
        # 5a. Suggest Prediction Config
        test_endpoint("suggest-prediction-config", "POST")
    elif endpoint_number == 7:
        # 5b. Analyze RBS Optimization
        test_endpoint("analyze-rbs-optimization", "POST")
    elif endpoint_number == 8:
        # 5c. Analyze Predictor Optimization
        test_endpoint("analyze-predictor-optimization", "POST")
    elif endpoint_number == 9:
        # 5d. Analyze Comprehensive Regression
        test_endpoint("analyze-comprehensive-regression", "POST")
    else:
        print(f"Invalid endpoint number: {endpoint_number}")
