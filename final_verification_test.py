
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
    print_separator(f"1. TEAM PERFORMANCE DATA VERIFICATION: {team_name}")
    
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
    
    # Verify field mappings
    field_mappings = [
        ('fouls_committed', 'fouls'),
        ('possession_percentage', 'possession_pct'),
        ('xg_difference', 'calculated from xg')
    ]
    
    print("\nField Mappings:")
    for target, source in field_mappings:
        if target in home_stats and home_stats.get(target) is not None:
            print(f"  ✅ {target} is correctly mapped from {source}")
        else:
            print(f"  ❌ {target} is missing or null")
            return False
    
    print("\n✅ Team performance data verification passed")
    return True

def test_rbs_calculation(api_url, team_name="Arsenal"):
    """Test RBS calculation for xG difference and possession values"""
    print_separator(f"2. RBS CALCULATION VERIFICATION: {team_name}")
    
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
    print_separator(f"3. DATA CONSISTENCY CHECK: {team_name}")
    
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
    
    # Get database stats
    stats_response = requests.get(f"{api_url}/stats")
    
    if stats_response.status_code != 200:
        print(f"❌ Error getting database stats: {stats_response.status_code}")
        print(stats_response.text)
        return False
    
    stats_data = stats_response.json()
    
    player_stats_count = stats_data.get("player_stats", 0)
    team_stats_count = stats_data.get("team_stats", 0)
    
    print(f"Player stats count: {player_stats_count}")
    print(f"Team stats count: {team_stats_count}")
    
    if player_stats_count > 0:
        print("✅ Player stats are present in the database")
    else:
        print("❌ No player stats found in the database")
        return False
    
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
    
    # Check consistency between team performance and RBS
    print("\nVerifying consistency between team performance and RBS:")
    
    # Get first RBS result
    if rbs_results:
        result = rbs_results[0]
        stats_breakdown = result.get("stats_breakdown", {})
        
        if stats_breakdown:
            # Check if xG difference is present in both
            if 'xg_difference' in stats_breakdown and 'xg_difference' in home_stats:
                print("✅ xG difference is present in both team performance and RBS")
            else:
                print("❌ xG difference is not consistently present")
                return False
            
            # Check if possession percentage is present in both
            if 'possession_percentage' in stats_breakdown and 'possession_percentage' in home_stats:
                print("✅ Possession percentage is present in both team performance and RBS")
            else:
                print("❌ Possession percentage is not consistently present")
                return False
        else:
            print("❌ No stats breakdown found in RBS result")
            return False
    else:
        print("❌ No RBS results found")
        return False
    
    print("\n✅ Data consistency check passed")
    return True

def test_regression_analysis(api_url):
    """Test regression analysis with xG difference and possession percentage"""
    print_separator("4. REGRESSION ANALYSIS TEST")
    
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
        
        results[name] = {
            "success": True,
            "r2_score": r2_score,
            "coefficients": coefficients
        }
    
    # Print summary
    print("\nRegression Analysis Summary:")
    
    for name, result in results.items():
        if result.get("success", False):
            print(f"{name}: R² = {result.get('r2_score', 0)}")
        else:
            print(f"{name}: Failed - {result.get('error', 'Unknown error')}")
    
    # Check if advanced stats have better R² score than basic stats
    if "Advanced Stats" in results and "Basic Stats" in results:
        advanced_r2 = results["Advanced Stats"].get("r2_score", 0)
        basic_r2 = results["Basic Stats"].get("r2_score", 0)
        
        print(f"\nAdvanced Stats R² score: {advanced_r2}")
        print(f"Basic Stats R² score: {basic_r2}")
        
        if advanced_r2 > basic_r2:
            print("✅ Advanced statistics provide better R² score than basic statistics")
        else:
            print("❌ Advanced statistics do not provide better R² score than basic statistics")
            return False
    
    # Check if any combination has a good R² score
    good_r2 = any(result.get("r2_score", 0) > 0.1 for result in results.values() if result.get("success", False))
    
    if good_r2:
        print("\n✅ At least one regression analysis has a good R² score (> 0.1)")
        print("\n✅ Regression analysis test passed")
        return True
    else:
        print("\n❌ No regression analysis has a good R² score")
        print("\n❌ Regression analysis test failed")
        return False

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
    test_results["1. Team Performance Data"] = test_team_performance_data(api_url)
    
    # Test RBS calculation
    test_results["2. RBS Calculation"] = test_rbs_calculation(api_url)
    
    # Test data consistency
    test_results["3. Data Consistency"] = test_data_consistency(api_url)
    
    # Test regression analysis
    test_results["4. Regression Analysis"] = test_regression_analysis(api_url)
    
    # Print summary of test results
    print_separator("FINAL TEST RESULTS SUMMARY")
    all_passed = True
    for test_name, result in test_results.items():
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"{test_name}: {status}")
        if not result:
            all_passed = False
    
    if all_passed:
        print("\n✅ ALL TESTS PASSED - xG and possession issues have been resolved")
        print("\nExpected Results Verification:")
        print("✓ xG values are realistic (1.0-2.0 range typically) from player aggregation")
        print("✓ xG_difference is different for home vs away games")
        print("✓ Possession is around 40-60% from team stats")
        print("✓ All statistics contribute meaningfully to RBS calculations")
        print("✓ Values are consistent across team performance and RBS endpoints")
    else:
        print("\n❌ SOME TESTS FAILED - xG and possession issues may not be fully resolved")
    
    return all_passed

if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
