
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

def test_team_performance_data(api_url, team_name="Arsenal"):
    """Test team performance data for xG and possession values"""
    print_separator(f"TEAM PERFORMANCE DATA VERIFICATION: {team_name}")
    
    response = requests.get(f"{api_url}/team-performance/{team_name}")
    
    if response.status_code != 200:
        print(f"❌ Error getting team performance: {response.status_code}")
        print(response.text)
        return False
    
    data = response.json()
    
    # Check home stats
    home_stats = data.get("home_stats", {})
    if home_stats:
        print("\nHome Stats:")
        print(f"  - xG: {home_stats.get('xg', 'N/A')}")
        print(f"  - xG Difference: {home_stats.get('xg_difference', 'N/A')}")
        print(f"  - Possession: {home_stats.get('possession_percentage', 'N/A')}%")
        
        # Verify xG is realistic (not 0.0)
        home_xg = home_stats.get('xg', 0)
        if home_xg > 0.5:
            print("  ✅ xG shows realistic values (not 0.0)")
        else:
            print(f"  ❌ xG value {home_xg} is too low")
            return False
        
        # Verify xG difference is realistic
        home_xg_diff = home_stats.get('xg_difference', 0)
        print(f"  - xG Difference value: {home_xg_diff}")
        
        # Verify possession is realistic (40-60%)
        home_possession = home_stats.get('possession_percentage', 0)
        if 30 <= home_possession <= 70:
            print(f"  ✅ Possession shows realistic values ({home_possession}%)")
        else:
            print(f"  ❌ Possession value {home_possession}% is outside expected range")
            return False
    else:
        print("❌ No home stats found")
        return False
    
    # Check away stats
    away_stats = data.get("away_stats", {})
    if away_stats:
        print("\nAway Stats:")
        print(f"  - xG: {away_stats.get('xg', 'N/A')}")
        print(f"  - xG Difference: {away_stats.get('xg_difference', 'N/A')}")
        print(f"  - Possession: {away_stats.get('possession_percentage', 'N/A')}%")
        
        # Verify xG is realistic (not 0.0)
        away_xg = away_stats.get('xg', 0)
        if away_xg > 0.5:
            print("  ✅ xG shows realistic values (not 0.0)")
        else:
            print(f"  ❌ xG value {away_xg} is too low")
            return False
        
        # Verify xG difference is realistic
        away_xg_diff = away_stats.get('xg_difference', 0)
        print(f"  - xG Difference value: {away_xg_diff}")
        
        # Verify possession is realistic (40-60%)
        away_possession = away_stats.get('possession_percentage', 0)
        if 30 <= away_possession <= 70:
            print(f"  ✅ Possession shows realistic values ({away_possession}%)")
        else:
            print(f"  ❌ Possession value {away_possession}% is outside expected range")
            return False
        
        # Verify xG difference is different for home vs away
        if abs(home_xg_diff - away_xg_diff) > 0.1:
            print("  ✅ xG difference shows different values for home vs away")
        else:
            print("  ❌ xG difference is too similar for home vs away")
            return False
    else:
        print("❌ No away stats found")
        return False
    
    print("\n✅ Team performance data verification passed")
    return True

def test_rbs_calculation(api_url, team_name="Arsenal"):
    """Test RBS calculation for xG difference and possession values"""
    print_separator(f"RBS CALCULATION VERIFICATION: {team_name}")
    
    # Get RBS results for the team
    response = requests.get(f"{api_url}/rbs-results", params={"team": team_name})
    
    if response.status_code != 200:
        print(f"❌ Error getting RBS results: {response.status_code}")
        print(response.text)
        return False
    
    data = response.json()
    results = data.get("results", [])
    
    if not results:
        print(f"❌ No RBS results found for {team_name}")
        return False
    
    print(f"Found {len(results)} RBS results for {team_name}")
    
    # Check first 3 results
    all_passed = True
    for i, result in enumerate(results[:3]):
        print(f"\nRBS Result {i+1}:")
        print(f"  - Team: {result.get('team_name', 'N/A')}")
        print(f"  - Referee: {result.get('referee', 'N/A')}")
        print(f"  - RBS Score: {result.get('rbs_score', 'N/A')}")
        
        # Check stats breakdown
        stats_breakdown = result.get("stats_breakdown", {})
        if stats_breakdown:
            print("\n  Stats Breakdown:")
            for stat, value in stats_breakdown.items():
                print(f"    - {stat}: {value}")
            
            # Verify xG difference is included with non-zero values
            if 'xg_difference' in stats_breakdown:
                xg_diff_value = stats_breakdown.get('xg_difference', 0)
                if xg_diff_value != 0:
                    print("    ✅ xG difference is included with non-zero value")
                else:
                    print("    ❌ xG difference is zero")
                    all_passed = False
            else:
                print("    ❌ xG difference is missing from stats breakdown")
                all_passed = False
            
            # Verify possession percentage is included with meaningful values
            if 'possession_percentage' in stats_breakdown:
                possession_value = stats_breakdown.get('possession_percentage', 0)
                print(f"    - Possession percentage contribution: {possession_value}")
            else:
                print("    ❌ Possession percentage is missing from stats breakdown")
                all_passed = False
            
            # Verify all 7 statistics are included
            expected_stats = [
                'yellow_cards', 'red_cards', 'fouls_committed', 
                'fouls_drawn', 'penalties_awarded', 'xg_difference', 
                'possession_percentage'
            ]
            
            missing_stats = [stat for stat in expected_stats if stat not in stats_breakdown]
            if not missing_stats:
                print("    ✅ All 7 statistics are included in stats breakdown")
            else:
                print(f"    ❌ Missing statistics: {', '.join(missing_stats)}")
                all_passed = False
        else:
            print("  ❌ No stats breakdown found")
            all_passed = False
    
    if all_passed:
        print("\n✅ RBS calculation verification passed")
    else:
        print("\n❌ RBS calculation verification failed")
    
    return all_passed

def test_data_consistency(api_url, team_name="Arsenal"):
    """Test data consistency between team performance and RBS calculation"""
    print_separator(f"DATA CONSISTENCY CHECK: {team_name}")
    
    # Get team performance data
    team_response = requests.get(f"{api_url}/team-performance/{team_name}")
    
    if team_response.status_code != 200:
        print(f"❌ Error getting team performance: {team_response.status_code}")
        print(team_response.text)
        return False
    
    team_data = team_response.json()
    
    # Get RBS results for the team
    rbs_response = requests.get(f"{api_url}/rbs-results", params={"team": team_name})
    
    if rbs_response.status_code != 200:
        print(f"❌ Error getting RBS results: {rbs_response.status_code}")
        print(rbs_response.text)
        return False
    
    rbs_data = rbs_response.json()
    rbs_results = rbs_data.get("results", [])
    
    if not rbs_results:
        print(f"❌ No RBS results found for {team_name}")
        return False
    
    # Check if xG values are properly aggregated from player stats
    print("\nVerifying xG aggregation from player stats:")
    
    # Get sample match data to verify player stats aggregation
    stats_response = requests.get(f"{api_url}/debug/team-stats-sample")
    
    if stats_response.status_code != 200:
        print(f"❌ Error getting team stats sample: {stats_response.status_code}")
        print(stats_response.text)
        return False
    
    stats_data = stats_response.json()
    sample_stats = stats_data.get("sample_stats", [])
    
    if sample_stats:
        print(f"Found {len(sample_stats)} sample team stats")
        
        # Check if xG is present in team stats
        for i, stat in enumerate(sample_stats):
            print(f"\nSample Team Stat {i+1}:")
            print(f"  - Match ID: {stat.get('match_id', 'N/A')}")
            print(f"  - Team: {stat.get('team_name', 'N/A')}")
            print(f"  - xG: {stat.get('xg', 'N/A')}")
            
            if stat.get('xg', 0) > 0:
                print("  ✅ xG value is present and non-zero")
            else:
                print("  ⚠️ xG value is zero (may be valid for some matches)")
    else:
        print("❌ No sample team stats found")
    
    # Verify xG difference calculation
    print("\nVerifying xG difference calculation:")
    home_stats = team_data.get("home_stats", {})
    away_stats = team_data.get("away_stats", {})
    
    if home_stats and away_stats:
        home_xg = home_stats.get('xg', 0)
        home_xg_conceded = home_stats.get('xg_conceded', 0)
        home_xg_diff = home_stats.get('xg_difference', 0)
        
        away_xg = away_stats.get('xg', 0)
        away_xg_conceded = away_stats.get('xg_conceded', 0)
        away_xg_diff = away_stats.get('xg_difference', 0)
        
        print(f"Home xG: {home_xg}, Home xG Conceded: {home_xg_conceded}, Home xG Diff: {home_xg_diff}")
        print(f"Away xG: {away_xg}, Away xG Conceded: {away_xg_conceded}, Away xG Diff: {away_xg_diff}")
        
        # Check if xG difference is calculated correctly
        calculated_home_diff = round(home_xg - home_xg_conceded, 3)
        calculated_away_diff = round(away_xg - away_xg_conceded, 3)
        
        if abs(calculated_home_diff - home_xg_diff) < 0.01:
            print("✅ Home xG difference is calculated correctly")
        else:
            print(f"❌ Home xG difference calculation is incorrect: {calculated_home_diff} vs {home_xg_diff}")
            return False
        
        if abs(calculated_away_diff - away_xg_diff) < 0.01:
            print("✅ Away xG difference is calculated correctly")
        else:
            print(f"❌ Away xG difference calculation is incorrect: {calculated_away_diff} vs {away_xg_diff}")
            return False
    else:
        print("❌ Missing home or away stats")
        return False
    
    # Verify possession values come from team_stats possession_pct column
    print("\nVerifying possession values:")
    
    if home_stats and away_stats:
        home_possession = home_stats.get('possession_percentage', 0)
        away_possession = away_stats.get('possession_percentage', 0)
        
        print(f"Home possession: {home_possession}%")
        print(f"Away possession: {away_possession}%")
        
        if 30 <= home_possession <= 70 and 30 <= away_possession <= 70:
            print("✅ Possession values are in realistic range (30-70%)")
        else:
            print("❌ Possession values are outside realistic range")
            return False
    else:
        print("❌ Missing home or away stats")
        return False
    
    print("\n✅ Data consistency check passed")
    return True

def test_regression_analysis(api_url):
    """Test regression analysis with xG difference and possession percentage"""
    print_separator("REGRESSION ANALYSIS TEST")
    
    # Test regression analysis with xG difference and possession percentage
    payload = {
        "selected_stats": ["xg_difference", "possession_percentage"],
        "target": "points_per_game",
        "test_size": 0.2,
        "random_state": 42
    }
    
    response = requests.post(f"{api_url}/regression-analysis", json=payload)
    
    if response.status_code != 200:
        print(f"❌ Error performing regression analysis: {response.status_code}")
        print(response.text)
        return False
    
    data = response.json()
    
    if not data.get("success", False):
        print(f"❌ Regression analysis failed: {data.get('message', 'Unknown error')}")
        return False
    
    print("Regression analysis successful")
    
    # Check coefficients
    results = data.get("results", {})
    coefficients = results.get("coefficients", {})
    
    if not coefficients:
        print("❌ No coefficients found in regression results")
        return False
    
    print("\nCoefficients:")
    for stat, coef in coefficients.items():
        print(f"  - {stat}: {coef}")
    
    # Verify xG difference and possession percentage have meaningful coefficients
    xg_diff_coef = coefficients.get("xg_difference", 0)
    possession_coef = coefficients.get("possession_percentage", 0)
    
    if abs(xg_diff_coef) > 0.01:
        print("✅ xG difference has a meaningful coefficient")
    else:
        print(f"❌ xG difference coefficient ({xg_diff_coef}) is too small")
        return False
    
    if abs(possession_coef) > 0.001:
        print("✅ Possession percentage has a meaningful coefficient")
    else:
        print(f"❌ Possession percentage coefficient ({possession_coef}) is too small")
        return False
    
    # Check R² score
    r2_score = results.get("r2_score", 0)
    print(f"\nR² score: {r2_score}")
    
    if r2_score > 0.05:
        print("✅ R² score is meaningful (> 0.05)")
    else:
        print(f"❌ R² score ({r2_score}) is too low")
        return False
    
    print("\n✅ Regression analysis test passed")
    return True

def run_all_tests():
    """Run all tests for xG and possession issues"""
    api_url = get_backend_url()
    if not api_url:
        print("❌ Error: Could not get backend URL from frontend/.env")
        return False
    
    api_url = f"{api_url}/api"
    print(f"Using backend URL: {api_url}")
    
    # Dictionary to store test results
    test_results = {}
    
    # Test team performance data
    test_results["Team Performance Data"] = test_team_performance_data(api_url)
    
    # Test RBS calculation
    test_results["RBS Calculation"] = test_rbs_calculation(api_url)
    
    # Test data consistency
    test_results["Data Consistency"] = test_data_consistency(api_url)
    
    # Test regression analysis
    test_results["Regression Analysis"] = test_regression_analysis(api_url)
    
    # Print summary of test results
    print_separator("TEST RESULTS SUMMARY")
    all_passed = True
    for test_name, result in test_results.items():
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"{test_name}: {status}")
        if not result:
            all_passed = False
    
    print(f"\nOverall Test Result: {'✅ ALL TESTS PASSED' if all_passed else '❌ SOME TESTS FAILED'}")
    
    return all_passed

if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
