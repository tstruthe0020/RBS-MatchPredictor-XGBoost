
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

def test_advanced_regression_analysis():
    """Test regression analysis with advanced stats"""
    api_url = f"{get_backend_url()}/api"
    print(f"Using backend URL: {api_url}")
    
    # Test with advanced stats
    advanced_stats_payload = {
        "selected_stats": ["xg_per_shot", "goals_per_xg", "shot_accuracy", "conversion_rate", "xg_difference"],
        "target": "points_per_game",
        "test_size": 0.2,
        "random_state": 42
    }
    
    print("\nTesting regression analysis with advanced statistics:")
    response = requests.post(f"{api_url}/regression-analysis", json=advanced_stats_payload)
    
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
            
            advanced_r2 = data.get("results", {}).get("r2_score", 0)
        else:
            print(f"\n❌ Error: {data.get('message', 'Unknown error')}")
            advanced_r2 = 0
    else:
        print(f"\n❌ Error: {response.status_code}")
        print(response.text)
        advanced_r2 = 0
    
    # Test with basic stats
    basic_stats_payload = {
        "selected_stats": ["yellow_cards", "red_cards", "fouls_committed", "possession_percentage"],
        "target": "points_per_game",
        "test_size": 0.2,
        "random_state": 42
    }
    
    print("\nTesting regression analysis with basic statistics:")
    response = requests.post(f"{api_url}/regression-analysis", json=basic_stats_payload)
    
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
            
            basic_r2 = data.get("results", {}).get("r2_score", 0)
            
            # Compare R² scores
            print(f"\nBasic stats R² score: {basic_r2}")
            print(f"Advanced stats R² score: {advanced_r2}")
            
            if advanced_r2 > basic_r2:
                print("\n✅ Advanced statistics provide better R² score than basic statistics")
            else:
                print("\n❌ Advanced statistics do not provide better R² score than basic statistics")
        else:
            print(f"\n❌ Error: {data.get('message', 'Unknown error')}")
    else:
        print(f"\n❌ Error: {response.status_code}")
        print(response.text)

if __name__ == "__main__":
    test_advanced_regression_analysis()
