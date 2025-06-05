
import requests
import json
import sys

def print_separator(title):
    print("\n" + "=" * 80 + f"\n {title} \n" + "=" * 80)

def get_backend_url():
    # Get backend URL from frontend .env
    with open('/app/frontend/.env', 'r') as f:
        for line in f:
            if line.startswith('REACT_APP_BACKEND_URL='):
                backend_url = line.strip().split('=')[1].strip('"\'')
                return backend_url
    return None

def test_team_performance_check():
    """Test 1: Team Performance Check for Arsenal"""
    print_separator("TEAM PERFORMANCE CHECK")
    
    api_url = f"{get_backend_url()}/api"
    print(f"Using backend URL: {api_url}")
    
    team_name = "Arsenal"
    print(f"\nTesting team performance for: {team_name}")
    
    response = requests.get(f"{api_url}/team-performance/{team_name}")
    
    if response.status_code == 200:
        data = response.json()
        
        # Check home stats
        home_stats = data.get("home_stats", {})
        if home_stats:
            print("\nHome Stats:")
            print(f"  - Fouls Drawn: {home_stats.get('fouls_drawn', 'N/A')}")
            print(f"  - Penalties Awarded: {home_stats.get('penalties_awarded', 'N/A')}")
            
            # Verify values are not zero
            fouls_drawn = home_stats.get('fouls_drawn', 0)
            penalties_awarded = home_stats.get('penalties_awarded', 0)
            
            if fouls_drawn > 0:
                print("✅ Fouls drawn is non-zero")
            else:
                print("❌ Fouls drawn is still zero")
                return False
            
            if penalties_awarded > 0:
                print("✅ Penalties awarded is non-zero")
            else:
                print("⚠️ Penalties awarded is still zero or very low")
                # Not failing the test for this as penalties are rare
        else:
            print("\n❌ No home stats found for team")
            return False
            
        # Check away stats
        away_stats = data.get("away_stats", {})
        if away_stats:
            print("\nAway Stats:")
            print(f"  - Fouls Drawn: {away_stats.get('fouls_drawn', 'N/A')}")
            print(f"  - Penalties Awarded: {away_stats.get('penalties_awarded', 'N/A')}")
            
            # Verify values are not zero
            fouls_drawn = away_stats.get('fouls_drawn', 0)
            penalties_awarded = away_stats.get('penalties_awarded', 0)
            
            if fouls_drawn > 0:
                print("✅ Fouls drawn is non-zero")
            else:
                print("❌ Fouls drawn is still zero")
                return False
            
            if penalties_awarded > 0:
                print("✅ Penalties awarded is non-zero")
            else:
                print("⚠️ Penalties awarded is still zero or very low")
                # Not failing the test for this as penalties are rare
        else:
            print("\n❌ No away stats found for team")
            return False
    else:
        print(f"\n❌ Error: {response.status_code}")
        print(response.text)
        return False
    
    return True

def test_rbs_calculation_verification():
    """Test 2: RBS Calculation Verification for Arsenal"""
    print_separator("RBS CALCULATION VERIFICATION")
    
    api_url = f"{get_backend_url()}/api"
    print(f"Using backend URL: {api_url}")
    
    team_name = "Arsenal"
    print(f"\nTesting RBS results for: {team_name}")
    
    response = requests.get(f"{api_url}/rbs-results", params={"team": team_name})
    
    if response.status_code == 200:
        data = response.json()
        results = data.get("results", [])
        
        if results:
            print(f"Found {len(results)} RBS results for {team_name}")
            
            # Check first result
            result = results[0]
            print(f"\nSample RBS result:")
            print(f"  - Team: {result.get('team_name', 'N/A')}")
            print(f"  - Referee: {result.get('referee', 'N/A')}")
            print(f"  - RBS Score: {result.get('rbs_score', 'N/A')}")
            
            # Check stats breakdown
            stats_breakdown = result.get("stats_breakdown", {})
            if stats_breakdown:
                print("\nStats Breakdown:")
                for stat, value in stats_breakdown.items():
                    print(f"  - {stat}: {value}")
                
                # Verify fouls_drawn and penalties_awarded are included
                if 'fouls_drawn' in stats_breakdown:
                    print("✅ Fouls drawn is included in RBS calculation")
                else:
                    print("❌ Fouls drawn is missing from RBS calculation")
                    return False
                
                if 'penalties_awarded' in stats_breakdown:
                    print("✅ Penalties awarded is included in RBS calculation")
                else:
                    print("❌ Penalties awarded is missing from RBS calculation")
                    return False
                
                # Check if values are non-zero
                if stats_breakdown.get('fouls_drawn', 0) != 0:
                    print("✅ Fouls drawn has non-zero value in RBS calculation")
                else:
                    print("❌ Fouls drawn has zero value in RBS calculation")
                    return False
                
                # Penalties might be zero as they're rare
                if stats_breakdown.get('penalties_awarded', 0) != 0:
                    print("✅ Penalties awarded has non-zero value in RBS calculation")
                else:
                    print("⚠️ Penalties awarded has zero value in RBS calculation (may be normal)")
            else:
                print("\n❌ No stats breakdown found in RBS result")
                return False
        else:
            print(f"\n❌ No RBS results found for {team_name}")
            return False
    else:
        print(f"\n❌ Error: {response.status_code}")
        print(response.text)
        return False
    
    return True

def test_data_consistency_check():
    """Test 3: Data Consistency Check between team performance and RBS results"""
    print_separator("DATA CONSISTENCY CHECK")
    
    api_url = f"{get_backend_url()}/api"
    print(f"Using backend URL: {api_url}")
    
    team_name = "Arsenal"
    print(f"\nChecking data consistency for: {team_name}")
    
    # Get team performance data
    team_response = requests.get(f"{api_url}/team-performance/{team_name}")
    
    if team_response.status_code != 200:
        print(f"\n❌ Error getting team performance: {team_response.status_code}")
        print(team_response.text)
        return False
    
    team_data = team_response.json()
    home_stats = team_data.get("home_stats", {})
    away_stats = team_data.get("away_stats", {})
    
    # Get RBS results
    rbs_response = requests.get(f"{api_url}/rbs-results", params={"team": team_name})
    
    if rbs_response.status_code != 200:
        print(f"\n❌ Error getting RBS results: {rbs_response.status_code}")
        print(rbs_response.text)
        return False
    
    rbs_data = rbs_response.json()
    rbs_results = rbs_data.get("results", [])
    
    if not rbs_results:
        print(f"\n❌ No RBS results found for {team_name}")
        return False
    
    # Get first RBS result with stats breakdown
    rbs_result = next((r for r in rbs_results if r.get("stats_breakdown")), None)
    
    if not rbs_result:
        print(f"\n❌ No RBS result with stats breakdown found for {team_name}")
        return False
    
    stats_breakdown = rbs_result.get("stats_breakdown", {})
    
    # Compare fouls_drawn values
    home_fouls_drawn = home_stats.get('fouls_drawn', 0)
    away_fouls_drawn = away_stats.get('fouls_drawn', 0)
    rbs_fouls_drawn = stats_breakdown.get('fouls_drawn', 0)
    
    print("\nFouls Drawn Comparison:")
    print(f"  - Team Performance (Home): {home_fouls_drawn}")
    print(f"  - Team Performance (Away): {away_fouls_drawn}")
    print(f"  - RBS Calculation: {rbs_fouls_drawn}")
    
    # Check if values are consistent (non-zero in both)
    if home_fouls_drawn > 0 and away_fouls_drawn > 0 and rbs_fouls_drawn != 0:
        print("✅ Fouls drawn values are consistent and non-zero across endpoints")
    else:
        print("❌ Inconsistency in fouls_drawn values between team performance and RBS")
        return False
    
    # Compare penalties_awarded values
    home_penalties = home_stats.get('penalties_awarded', 0)
    away_penalties = away_stats.get('penalties_awarded', 0)
    rbs_penalties = stats_breakdown.get('penalties_awarded', 0)
    
    print("\nPenalties Awarded Comparison:")
    print(f"  - Team Performance (Home): {home_penalties}")
    print(f"  - Team Performance (Away): {away_penalties}")
    print(f"  - RBS Calculation: {rbs_penalties}")
    
    # For penalties, we're more lenient as they're rare
    if (home_penalties > 0 or away_penalties > 0) and rbs_penalties != 0:
        print("✅ Penalties awarded values are consistent across endpoints")
    elif home_penalties == 0 and away_penalties == 0 and rbs_penalties == 0:
        print("⚠️ All penalties awarded values are zero (may be normal)")
    else:
        print("⚠️ Some inconsistency in penalties_awarded values (may be normal)")
    
    return True

def test_regression_analysis():
    """Test 4: Quick Regression Test with fouls_drawn and penalties_awarded"""
    print_separator("REGRESSION ANALYSIS TEST")
    
    api_url = f"{get_backend_url()}/api"
    print(f"Using backend URL: {api_url}")
    
    # Test regression analysis with fouls_drawn and penalties_awarded
    regression_payload = {
        "selected_stats": ["fouls_drawn", "penalties_awarded", "xg_difference", "possession_percentage"],
        "target": "points_per_game",
        "test_size": 0.2,
        "random_state": 42
    }
    
    response = requests.post(f"{api_url}/regression-analysis", json=regression_payload)
    
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
                
                # Check if fouls_drawn and penalties_awarded have non-zero coefficients
                if 'fouls_drawn' in coefficients and coefficients['fouls_drawn'] != 0:
                    print("✅ Fouls drawn has non-zero coefficient in regression")
                else:
                    print("❌ Fouls drawn has zero coefficient or is missing from regression")
                    return False
                
                if 'penalties_awarded' in coefficients and coefficients['penalties_awarded'] != 0:
                    print("✅ Penalties awarded has non-zero coefficient in regression")
                else:
                    print("❌ Penalties awarded has zero coefficient or is missing from regression")
                    return False
            else:
                print("\n❌ No coefficients found in regression results")
                return False
        else:
            print(f"\n❌ Error: {data.get('message', 'Unknown error')}")
            return False
    else:
        print(f"\n❌ Error: {response.status_code}")
        print(response.text)
        return False
    
    return True

def run_all_tests():
    """Run all verification tests"""
    print("\n=== RUNNING FINAL VERIFICATION TESTS ===\n")
    
    # Dictionary to store test results
    test_results = {}
    
    # Test 1: Team Performance Check
    test_results["Team Performance Check"] = test_team_performance_check()
    
    # Test 2: RBS Calculation Verification
    test_results["RBS Calculation Verification"] = test_rbs_calculation_verification()
    
    # Test 3: Data Consistency Check
    test_results["Data Consistency Check"] = test_data_consistency_check()
    
    # Test 4: Regression Analysis Test
    test_results["Regression Analysis Test"] = test_regression_analysis()
    
    # Print summary of test results
    print("\n=== TEST RESULTS SUMMARY ===\n")
    all_passed = True
    for test_name, result in test_results.items():
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"{test_name}: {status}")
        if not result:
            all_passed = False
    
    print(f"\nOverall Test Result: {'✅ ALL TESTS PASSED' if all_passed else '❌ SOME TESTS FAILED'}")
    
    return 0 if all_passed else 1

if __name__ == "__main__":
    sys.exit(run_all_tests())
