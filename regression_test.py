
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

def test_regression_analysis_comprehensive():
    """Test regression analysis with various combinations of statistics"""
    api_url = get_backend_url()
    if not api_url:
        print("❌ Error: Could not get backend URL from frontend/.env")
        return False
    
    api_url = f"{api_url}/api"
    print(f"Using backend URL: {api_url}")
    
    print("\n=== COMPREHENSIVE REGRESSION ANALYSIS TEST ===\n")
    
    # Get available stats
    response = requests.get(f"{api_url}/regression-stats")
    
    if response.status_code != 200:
        print(f"❌ Error getting regression stats: {response.status_code}")
        print(response.text)
        return False
    
    data = response.json()
    available_stats = data.get("available_stats", [])
    
    if not available_stats:
        print("❌ No available stats found")
        return False
    
    print(f"Found {len(available_stats)} available stats")
    
    # Test combinations
    test_combinations = [
        {
            "name": "Basic Stats",
            "stats": ["yellow_cards", "red_cards", "fouls_committed", "possession_percentage"]
        },
        {
            "name": "Advanced Stats",
            "stats": ["xg_per_shot", "goals_per_xg", "shot_accuracy", "conversion_rate"]
        },
        {
            "name": "xG and Possession",
            "stats": ["xg", "xg_difference", "possession_percentage"]
        },
        {
            "name": "Mixed Stats",
            "stats": ["xg", "xg_difference", "possession_percentage", "goals_per_xg", "shot_accuracy"]
        },
        {
            "name": "All Stats",
            "stats": available_stats
        }
    ]
    
    results = {}
    
    for combo in test_combinations:
        name = combo["name"]
        stats = [s for s in combo["stats"] if s in available_stats]
        
        if len(stats) < 2:
            print(f"⚠️ Skipping {name} - not enough valid stats")
            continue
        
        print(f"\nTesting {name} ({len(stats)} stats):")
        print(f"Stats: {', '.join(stats)}")
        
        payload = {
            "selected_stats": stats,
            "target": "points_per_game",
            "test_size": 0.2,
            "random_state": 42
        }
        
        response = requests.post(f"{api_url}/regression-analysis", json=payload)
        
        if response.status_code != 200:
            print(f"❌ Error performing regression analysis: {response.status_code}")
            print(response.text)
            results[name] = {"success": False, "error": f"HTTP {response.status_code}"}
            continue
        
        data = response.json()
        
        if not data.get("success", False):
            print(f"❌ Regression analysis failed: {data.get('message', 'Unknown error')}")
            results[name] = {"success": False, "error": data.get('message', 'Unknown error')}
            continue
        
        # Check results
        r2_score = data.get("results", {}).get("r2_score", 0)
        coefficients = data.get("results", {}).get("coefficients", {})
        
        print(f"R² score: {r2_score}")
        print("Coefficients:")
        for stat, coef in coefficients.items():
            print(f"  - {stat}: {coef}")
        
        # Check if xG difference and possession have meaningful coefficients
        if "xg_difference" in stats:
            xg_diff_coef = coefficients.get("xg_difference", 0)
            print(f"xG difference coefficient: {xg_diff_coef}")
        
        if "possession_percentage" in stats:
            possession_coef = coefficients.get("possession_percentage", 0)
            print(f"Possession percentage coefficient: {possession_coef}")
        
        results[name] = {
            "success": True,
            "r2_score": r2_score,
            "coefficients": coefficients
        }
    
    # Print summary
    print("\n=== REGRESSION ANALYSIS SUMMARY ===\n")
    
    for name, result in results.items():
        if result.get("success", False):
            print(f"{name}: R² = {result.get('r2_score', 0)}")
        else:
            print(f"{name}: Failed - {result.get('error', 'Unknown error')}")
    
    # Check if any combination has a good R² score
    good_r2 = any(result.get("r2_score", 0) > 0.1 for result in results.values() if result.get("success", False))
    
    if good_r2:
        print("\n✅ At least one regression analysis has a good R² score (> 0.1)")
        return True
    else:
        print("\n❌ No regression analysis has a good R² score")
        return False

if __name__ == "__main__":
    success = test_regression_analysis_comprehensive()
    sys.exit(0 if success else 1)
