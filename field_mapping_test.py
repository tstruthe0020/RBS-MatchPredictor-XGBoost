import requests
import json
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv('/app/backend/.env')

# Get backend URL from frontend .env file
try:
    with open('/app/frontend/.env', 'r') as f:
        for line in f:
            if line.startswith('REACT_APP_BACKEND_URL='):
                BACKEND_URL = line.strip().split('=')[1].strip('"\'')
                break
except Exception as e:
    print(f"Error reading frontend .env file: {e}")
    BACKEND_URL = "http://localhost:8001"  # Fallback

API_URL = f"{BACKEND_URL}/api"
print(f"Using API URL: {API_URL}")

def test_team_performance_endpoint():
    """Test the team performance endpoint for a known team (Arsenal)"""
    team_name = "Arsenal"
    print(f"\n=== Testing Team Performance for {team_name} ===")
    
    response = requests.get(f"{API_URL}/team-performance/{team_name}")
    if response.status_code != 200:
        print(f"❌ Error: Received status code {response.status_code}")
        return False
    
    data = response.json()
    if not data.get("success", False):
        print(f"❌ Error: Response indicates failure")
        return False
    
    print(f"✅ Successfully retrieved team performance data for {team_name}")
    
    # Check home stats
    home_stats = data.get("home_stats", {})
    if not home_stats:
        print("❌ Error: No home stats found in response")
        return False
    
    print("\n=== Home Stats ===")
    # Check fouls fields
    print(f"fouls: {home_stats.get('fouls', 'N/A')}")
    print(f"fouls_committed: {home_stats.get('fouls_committed', 'N/A')}")
    print(f"fouls_drawn: {home_stats.get('fouls_drawn', 'N/A')}")
    
    # Check penalties field
    print(f"penalties_awarded: {home_stats.get('penalties_awarded', 'N/A')}")
    
    # Check possession fields
    print(f"possession_pct: {home_stats.get('possession_pct', 'N/A')}")
    print(f"possession_percentage: {home_stats.get('possession_percentage', 'N/A')}")
    
    # Check xG difference field
    print(f"xg_difference: {home_stats.get('xg_difference', 'N/A')}")
    
    # Verify that the values are not all 0.00
    if home_stats.get("fouls_committed", 0) == 0:
        print("❌ Error: fouls_committed is still 0")
    else:
        print("✅ fouls_committed has non-zero value")
    
    if home_stats.get("fouls_drawn", 0) == 0:
        print("❌ Error: fouls_drawn is still 0")
    else:
        print("✅ fouls_drawn has non-zero value")
    
    if home_stats.get("penalties_awarded", 0) == 0:
        print("⚠️ Warning: penalties_awarded is 0 (may be legitimate)")
    else:
        print("✅ penalties_awarded has non-zero value")
    
    if home_stats.get("possession_percentage", 0) == 0:
        print("❌ Error: possession_percentage is still 0")
    else:
        print("✅ possession_percentage has non-zero value")
    
    if home_stats.get("xg_difference", 0) == 0:
        print("❌ Error: xg_difference is still 0")
    else:
        print("✅ xg_difference has non-zero value")
    
    # Check away stats
    away_stats = data.get("away_stats", {})
    if not away_stats:
        print("❌ Error: No away stats found in response")
        return False
    
    print("\n=== Away Stats ===")
    # Check fouls fields
    print(f"fouls: {away_stats.get('fouls', 'N/A')}")
    print(f"fouls_committed: {away_stats.get('fouls_committed', 'N/A')}")
    print(f"fouls_drawn: {away_stats.get('fouls_drawn', 'N/A')}")
    
    # Check penalties field
    print(f"penalties_awarded: {away_stats.get('penalties_awarded', 'N/A')}")
    
    # Check possession fields
    print(f"possession_pct: {away_stats.get('possession_pct', 'N/A')}")
    print(f"possession_percentage: {away_stats.get('possession_percentage', 'N/A')}")
    
    # Check xG difference field
    print(f"xg_difference: {away_stats.get('xg_difference', 'N/A')}")
    
    # Verify that the values are not all 0.00
    if away_stats.get("fouls_committed", 0) == 0:
        print("❌ Error: fouls_committed is still 0")
    else:
        print("✅ fouls_committed has non-zero value")
    
    if away_stats.get("fouls_drawn", 0) == 0:
        print("❌ Error: fouls_drawn is still 0")
    else:
        print("✅ fouls_drawn has non-zero value")
    
    if away_stats.get("penalties_awarded", 0) == 0:
        print("⚠️ Warning: penalties_awarded is 0 (may be legitimate)")
    else:
        print("✅ penalties_awarded has non-zero value")
    
    if away_stats.get("possession_percentage", 0) == 0:
        print("❌ Error: possession_percentage is still 0")
    else:
        print("✅ possession_percentage has non-zero value")
    
    if away_stats.get("xg_difference", 0) == 0:
        print("❌ Error: xg_difference is still 0")
    else:
        print("✅ xg_difference has non-zero value")
    
    # Check field name consistency
    if home_stats.get("fouls") != home_stats.get("fouls_committed"):
        print("❌ Error: fouls and fouls_committed have different values")
    else:
        print("✅ fouls and fouls_committed have the same value (correct mapping)")
    
    if home_stats.get("possession_pct") != home_stats.get("possession_percentage"):
        print("❌ Error: possession_pct and possession_percentage have different values")
    else:
        print("✅ possession_pct and possession_percentage have the same value (correct mapping)")
    
    return True

def test_rbs_calculation():
    """Test RBS calculation using the RBS results endpoint"""
    print("\n=== Testing RBS Calculation ===")
    
    # Get RBS results
    response = requests.get(f"{API_URL}/rbs-results")
    if response.status_code != 200:
        print(f"❌ Error: Failed to get RBS results, status code {response.status_code}")
        return False
    
    data = response.json()
    if not data.get("success", False):
        print(f"❌ Error: Response indicates failure")
        return False
    
    results = data.get("results", [])
    if not results:
        print("❌ Error: No RBS results found")
        return False
    
    print(f"Found {len(results)} RBS results")
    
    # Get a sample result
    sample_result = results[0]
    team_name = sample_result.get("team_name", "Unknown")
    referee = sample_result.get("referee", "Unknown")
    
    print(f"\nSample RBS for team '{team_name}' with referee '{referee}':")
    print(f"RBS Score: {sample_result.get('rbs_score', 'N/A')}")
    print(f"Confidence: {sample_result.get('confidence_level', 'N/A')}")
    
    # Check stats breakdown
    stats_breakdown = sample_result.get("stats_breakdown", {})
    print("\n=== Stats Breakdown ===")
    for stat, value in stats_breakdown.items():
        print(f"{stat}: {value}")
    
    # Verify that the breakdown includes all the required fields
    required_fields = ["fouls_committed", "fouls_drawn", "penalties_awarded", "xg_difference", "possession_percentage"]
    missing_fields = [field for field in required_fields if field not in stats_breakdown]
    
    if missing_fields:
        print(f"❌ Error: Missing fields in stats breakdown: {', '.join(missing_fields)}")
        return False
    else:
        print("✅ All required fields present in stats breakdown")
    
    return True

def test_regression_analysis():
    """Test regression analysis to verify advanced stats show proper values"""
    print("\n=== Testing Regression Analysis ===")
    
    # Define a set of stats to analyze
    stats = [
        "fouls_committed", "fouls_drawn", "penalties_awarded", 
        "xg_difference", "possession_percentage"
    ]
    
    # Run regression analysis
    payload = {
        "selected_stats": stats,
        "target": "points_per_game",
        "test_size": 0.2,
        "random_state": 42
    }
    
    response = requests.post(f"{API_URL}/regression-analysis", json=payload)
    if response.status_code != 200:
        print(f"❌ Error: Failed to run regression analysis, status code {response.status_code}")
        return False
    
    data = response.json()
    print(f"Success: {data.get('success', False)}")
    print(f"Sample Size: {data.get('sample_size', 0)}")
    
    results = data.get("results", {})
    coefficients = results.get("coefficients", {})
    
    print("\n=== Coefficients ===")
    for stat, coef in coefficients.items():
        print(f"{stat}: {coef}")
    
    # Verify that the coefficients exist for our fields of interest
    missing_coefficients = [stat for stat in stats if stat not in coefficients]
    
    if missing_coefficients:
        print(f"❌ Error: Missing coefficients for stats: {', '.join(missing_coefficients)}")
        return False
    else:
        print("✅ All required stats have coefficients in the regression results")
    
    return True

def test_sample_team_stats_document():
    """Query a sample team_stats document to check field names and values"""
    print("\n=== Testing Sample Team Stats Document ===")
    
    # Get a sample team stats document for Arsenal
    team_name = "Arsenal"
    response = requests.get(f"{API_URL}/team-performance/{team_name}")
    if response.status_code != 200:
        print(f"❌ Error: Failed to get team performance, status code {response.status_code}")
        return False
    
    data = response.json()
    home_stats = data.get("home_stats", {})
    away_stats = data.get("away_stats", {})
    
    print("\n=== Sample Team Stats Document Fields ===")
    all_fields = set(list(home_stats.keys()) + list(away_stats.keys()))
    for field in sorted(all_fields):
        home_value = home_stats.get(field, "N/A")
        away_value = away_stats.get(field, "N/A")
        print(f"{field}: home={home_value}, away={away_value}")
    
    # Check for field name consistency
    if "fouls" not in home_stats:
        print("❌ Error: fouls field is missing")
        return False
    
    if "fouls_committed" not in home_stats:
        print("❌ Error: fouls_committed field is missing")
        return False
    
    if home_stats.get("fouls") != home_stats.get("fouls_committed"):
        print("❌ Error: fouls and fouls_committed have different values")
    else:
        print("✅ fouls and fouls_committed have the same value (correct mapping)")
    
    if "possession_pct" not in home_stats:
        print("❌ Error: possession_pct field is missing")
        return False
    
    if "possession_percentage" not in home_stats:
        print("❌ Error: possession_percentage field is missing")
        return False
    
    if home_stats.get("possession_pct") != home_stats.get("possession_percentage"):
        print("❌ Error: possession_pct and possession_percentage have different values")
    else:
        print("✅ possession_pct and possession_percentage have the same value (correct mapping)")
    
    return True

def main():
    print("=== Field Mapping Issues Verification ===")
    
    # Test 1: Team Performance Data Verification
    team_performance_success = test_team_performance_endpoint()
    
    # Test 2: Sample Team Stats Inspection
    team_stats_success = test_sample_team_stats_document()
    
    # Test 3: RBS Calculation Verification
    rbs_calculation_success = test_rbs_calculation()
    
    # Test 4: Regression Analysis Data Check
    regression_analysis_success = test_regression_analysis()
    
    # Print summary
    print("\n=== Summary ===")
    print(f"Team Performance Data Verification: {'✅ PASSED' if team_performance_success else '❌ FAILED'}")
    print(f"Sample Team Stats Inspection: {'✅ PASSED' if team_stats_success else '❌ FAILED'}")
    print(f"RBS Calculation Verification: {'✅ PASSED' if rbs_calculation_success else '❌ FAILED'}")
    print(f"Regression Analysis Data Check: {'✅ PASSED' if regression_analysis_success else '❌ FAILED'}")
    
    overall_success = team_performance_success and team_stats_success and rbs_calculation_success and regression_analysis_success
    
    print(f"\nOverall Result: {'✅ PASSED' if overall_success else '❌ FAILED'}")
    print("Field mapping issues have been resolved." if overall_success else "Some field mapping issues still exist.")
    
    return 0 if overall_success else 1

if __name__ == "__main__":
    sys.exit(main())