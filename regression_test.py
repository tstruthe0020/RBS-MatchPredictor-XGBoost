
import requests
import json
import sys

def get_backend_url():
    # Get backend URL from frontend .env
    with open('/app/frontend/.env', 'r') as f:
        for line in f:
            if line.startswith('REACT_APP_BACKEND_URL='):
                backend_url = line.strip().split('=')[1].strip('"\'')
                return backend_url
    return None

def test_regression_analysis():
    """Test regression analysis with different combinations of stats"""
    api_url = f"{get_backend_url()}/api"
    print(f"Using backend URL: {api_url}")
    
    # Test 1: Only fouls_drawn and penalties_awarded
    test1_payload = {
        "selected_stats": ["fouls_drawn", "penalties_awarded"],
        "target": "points_per_game",
        "test_size": 0.2,
        "random_state": 42
    }
    
    print("\nTest 1: Only fouls_drawn and penalties_awarded")
    response = requests.post(f"{api_url}/regression-analysis", json=test1_payload)
    
    if response.status_code == 200:
        data = response.json()
        
        if data.get("success", False):
            print("✅ Regression analysis successful")
            print(f"Sample size: {data.get('sample_size', 'N/A')}")
            print(f"R² score: {data.get('results', {}).get('r2_score', 'N/A')}")
            
            # Print coefficients
            coefficients = data.get("results", {}).get("coefficients", {})
            if coefficients:
                print("\nCoefficients:")
                for stat, coef in coefficients.items():
                    print(f"  - {stat}: {coef}")
        else:
            print(f"\n❌ Error: {data.get('message', 'Unknown error')}")
    else:
        print(f"\n❌ Error: {response.status_code}")
        print(response.text)
    
    # Test 2: fouls_drawn with other stats
    test2_payload = {
        "selected_stats": ["fouls_drawn", "yellow_cards", "red_cards"],
        "target": "points_per_game",
        "test_size": 0.2,
        "random_state": 42
    }
    
    print("\nTest 2: fouls_drawn with other stats")
    response = requests.post(f"{api_url}/regression-analysis", json=test2_payload)
    
    if response.status_code == 200:
        data = response.json()
        
        if data.get("success", False):
            print("✅ Regression analysis successful")
            print(f"Sample size: {data.get('sample_size', 'N/A')}")
            print(f"R² score: {data.get('results', {}).get('r2_score', 'N/A')}")
            
            # Print coefficients
            coefficients = data.get("results", {}).get("coefficients", {})
            if coefficients:
                print("\nCoefficients:")
                for stat, coef in coefficients.items():
                    print(f"  - {stat}: {coef}")
        else:
            print(f"\n❌ Error: {data.get('message', 'Unknown error')}")
    else:
        print(f"\n❌ Error: {response.status_code}")
        print(response.text)
    
    # Test 3: penalties_awarded with other stats
    test3_payload = {
        "selected_stats": ["penalties_awarded", "xg", "shots_on_target"],
        "target": "points_per_game",
        "test_size": 0.2,
        "random_state": 42
    }
    
    print("\nTest 3: penalties_awarded with other stats")
    response = requests.post(f"{api_url}/regression-analysis", json=test3_payload)
    
    if response.status_code == 200:
        data = response.json()
        
        if data.get("success", False):
            print("✅ Regression analysis successful")
            print(f"Sample size: {data.get('sample_size', 'N/A')}")
            print(f"R² score: {data.get('results', {}).get('r2_score', 'N/A')}")
            
            # Print coefficients
            coefficients = data.get("results", {}).get("coefficients", {})
            if coefficients:
                print("\nCoefficients:")
                for stat, coef in coefficients.items():
                    print(f"  - {stat}: {coef}")
        else:
            print(f"\n❌ Error: {data.get('message', 'Unknown error')}")
    else:
        print(f"\n❌ Error: {response.status_code}")
        print(response.text)
    
    # Test 4: Get available stats to see if fouls_drawn and penalties_awarded are included
    print("\nTest 4: Get available regression stats")
    response = requests.get(f"{api_url}/regression-stats")
    
    if response.status_code == 200:
        data = response.json()
        
        if data.get("success", False):
            available_stats = data.get("available_stats", [])
            print(f"Available stats: {len(available_stats)}")
            print(f"Stats: {available_stats}")
            
            if "fouls_drawn" in available_stats:
                print("✅ fouls_drawn is in available stats")
            else:
                print("❌ fouls_drawn is NOT in available stats")
                
            if "penalties_awarded" in available_stats:
                print("✅ penalties_awarded is in available stats")
            else:
                print("❌ penalties_awarded is NOT in available stats")
        else:
            print(f"\n❌ Error: {data.get('message', 'Unknown error')}")
    else:
        print(f"\n❌ Error: {response.status_code}")
        print(response.text)

if __name__ == "__main__":
    test_regression_analysis()
