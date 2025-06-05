import requests
import os
import json
import pprint
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Get the backend URL from environment
BACKEND_URL = os.environ.get('REACT_APP_BACKEND_URL', 'http://localhost:8001')
BASE_URL = f"{BACKEND_URL}/api"

# Pretty printer for better output formatting
pp = pprint.PrettyPrinter(indent=2)

def test_comprehensive_regression_analysis():
    """Test the comprehensive regression analysis endpoint"""
    print("\n=== Testing Comprehensive Regression Analysis Endpoint ===")
    
    # Get available stats first
    stats_response = requests.get(f"{BASE_URL}/regression-stats")
    if stats_response.status_code != 200:
        print(f"Error getting regression stats: {stats_response.status_code}")
        return None
    
    stats_data = stats_response.json()
    available_stats = stats_data.get('available_stats', [])
    
    if not available_stats:
        print("No available stats found")
        return None
    
    # Use a subset of stats for testing
    test_stats = available_stats[:5]
    print(f"Using stats for testing: {', '.join(test_stats)}")
    
    # Prepare request data
    request_data = {
        "selected_stats": test_stats,
        "target": "points_per_game",
        "test_size": 0.2,
        "random_state": 42
    }
    
    # Make the request
    response = requests.post(f"{BASE_URL}/analyze-comprehensive-regression", json=request_data)
    
    print(f"Status code: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        print("Success!")
        print(f"Analysis type: {data.get('analysis_type')}")
        print(f"Target: {data.get('target')}")
        print(f"Sample size: {data.get('sample_size')}")
        
        # Check results
        results = data.get('results', {})
        print(f"Results sections: {len(results)}")
        for section in results:
            print(f"  - {section}")
        
        # Check recommendations
        recommendations = data.get('recommendations', [])
        print(f"Recommendations: {len(recommendations)}")
        for i, rec in enumerate(recommendations[:3]):
            print(f"  {i+1}. {rec.get('recommendation')} (Priority: {rec.get('priority')})")
        
        return data
    else:
        print(f"Error: {response.status_code}")
        try:
            error_data = response.json()
            print("Error details:")
            pp.pprint(error_data)
        except:
            print(response.text)
        return None

if __name__ == "__main__":
    test_comprehensive_regression_analysis()