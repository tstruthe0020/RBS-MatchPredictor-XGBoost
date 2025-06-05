import requests
import os
import json
import time
import pprint
from dotenv import load_dotenv

# Load environment variables
load_dotenv('/app/frontend/.env')

# Get the backend URL from environment
BACKEND_URL = os.environ.get('REACT_APP_BACKEND_URL', 'http://localhost:8001')
BASE_URL = f"{BACKEND_URL}/api"

# Pretty printer for better output formatting
pp = pprint.PrettyPrinter(indent=2)

def test_comprehensive_team_stats():
    """Test the /api/calculate-comprehensive-team-stats endpoint"""
    print("\n=== Testing Comprehensive Team Stats Calculation ===")
    response = requests.post(f"{BASE_URL}/calculate-comprehensive-team-stats")
    
    if response.status_code == 200:
        print(f"Status: {response.status_code} OK")
        data = response.json()
        print(f"Success: {data['success']}")
        print(f"Message: {data['message']}")
        print(f"Records Updated: {data['records_updated']}")
        
        # Verify that team stats were updated
        if data['records_updated'] > 0:
            print("✅ Team statistics were successfully updated")
        else:
            print("❌ No team statistics were updated")
        
        return data
    else:
        print(f"Error: {response.status_code}")
        print(response.text)
        return None

def test_enhanced_rbs_calculation():
    """Test the /api/calculate-rbs endpoint"""
    print("\n=== Testing Enhanced RBS Calculation ===")
    response = requests.post(f"{BASE_URL}/calculate-rbs")
    
    if response.status_code == 200:
        print(f"Status: {response.status_code} OK")
        data = response.json()
        print(f"Success: {data['success']}")
        print(f"Message: {data['message']}")
        print(f"Results Count: {data['results_count']}")
        
        # Verify that RBS results were calculated
        if data['results_count'] > 0:
            print("✅ RBS scores were successfully calculated")
        else:
            print("❌ No RBS scores were calculated")
        
        return data
    else:
        print(f"Error: {response.status_code}")
        print(response.text)
        return None

def test_team_performance_stats(team_name="Arsenal"):
    """Test the team performance endpoint to verify statistics"""
    print(f"\n=== Testing Team Performance Stats for {team_name} ===")
    response = requests.get(f"{BASE_URL}/team-performance/{team_name}")
    
    if response.status_code == 200:
        print(f"Status: {response.status_code} OK")
        data = response.json()
        print(f"Success: {data['success']}")
        print(f"Team: {data['team_name']}")
        print(f"Total Matches: {data['total_matches']}")
        print(f"PPG: {data['ppg']}")
        
        # Check home stats
        home_stats = data.get('home_stats', {})
        away_stats = data.get('away_stats', {})
        
        print("\nHome Stats:")
        print(f"  Matches: {home_stats.get('matches_count', 0)}")
        
        # Check for required statistics
        required_stats = [
            'xg_per_shot', 'shots_total', 'shots_on_target', 'goals_per_xg', 
            'shot_accuracy', 'conversion_rate', 'penalty_conversion_rate',
            'points', 'goals', 'goals_conceded'
        ]
        
        missing_home_stats = [stat for stat in required_stats if stat not in home_stats or home_stats[stat] == 0]
        if missing_home_stats:
            print(f"❌ Missing or zero home stats: {', '.join(missing_home_stats)}")
        else:
            print("✅ All required home stats are present and non-zero")
        
        # Print key home stats
        print(f"  xG per shot: {home_stats.get('xg_per_shot', 0)}")
        print(f"  Shots per game: {home_stats.get('shots_total', 0)}")
        print(f"  Shot accuracy: {home_stats.get('shot_accuracy', 0)}")
        print(f"  Conversion rate: {home_stats.get('conversion_rate', 0)}")
        print(f"  Goals per xG: {home_stats.get('goals_per_xg', 0)}")
        
        print("\nAway Stats:")
        print(f"  Matches: {away_stats.get('matches_count', 0)}")
        
        # Check for required statistics in away stats
        missing_away_stats = [stat for stat in required_stats if stat not in away_stats or away_stats[stat] == 0]
        if missing_away_stats:
            print(f"❌ Missing or zero away stats: {', '.join(missing_away_stats)}")
        else:
            print("✅ All required away stats are present and non-zero")
        
        # Print key away stats
        print(f"  xG per shot: {away_stats.get('xg_per_shot', 0)}")
        print(f"  Shots per game: {away_stats.get('shots_total', 0)}")
        print(f"  Shot accuracy: {away_stats.get('shot_accuracy', 0)}")
        print(f"  Conversion rate: {away_stats.get('conversion_rate', 0)}")
        print(f"  Goals per xG: {away_stats.get('goals_per_xg', 0)}")
        
        return data
    else:
        print(f"Error: {response.status_code}")
        print(response.text)
        return None

def get_teams():
    """Get list of teams"""
    response = requests.get(f"{BASE_URL}/teams")
    if response.status_code == 200:
        return response.json().get('teams', [])
    return []

def test_rbs_results(team_name="Arsenal"):
    """Test the RBS results endpoint to verify statistics"""
    print(f"\n=== Testing RBS Results for {team_name} ===")
    response = requests.get(f"{BASE_URL}/rbs-results/{team_name}")
    
    if response.status_code == 200:
        print(f"Status: {response.status_code} OK")
        data = response.json()
        print(f"Success: {data['success']}")
        print(f"Team: {data['team_name']}")
        print(f"Results Count: {len(data.get('results', []))}")
        
        # Check RBS results
        results = data.get('results', [])
        if not results:
            print("❌ No RBS results found")
            return data
        
        # Check the first result
        first_result = results[0]
        print(f"\nRBS Score: {first_result.get('rbs_score')}")
        print(f"Referee: {first_result.get('referee')}")
        print(f"Confidence: {first_result.get('confidence_level')}")
        
        # Check stats breakdown
        stats_breakdown = first_result.get('stats_breakdown', {})
        print("\nStats Breakdown:")
        for stat, value in stats_breakdown.items():
            print(f"  {stat}: {value}")
        
        # Verify all required stats are in the breakdown
        required_stats = [
            'yellow_cards', 'red_cards', 'fouls_committed', 'fouls_drawn',
            'penalties_awarded', 'xg_difference', 'possession_percentage'
        ]
        
        missing_stats = [stat for stat in required_stats if stat not in stats_breakdown]
        if missing_stats:
            print(f"❌ Missing stats in breakdown: {', '.join(missing_stats)}")
        else:
            print("✅ All required stats are present in the breakdown")
        
        # Check for non-zero values in key stats
        zero_stats = [stat for stat in required_stats if stat in stats_breakdown and stats_breakdown[stat] == 0]
        if zero_stats:
            print(f"⚠️ Zero values in stats: {', '.join(zero_stats)}")
        else:
            print("✅ All stats have non-zero values")
        
        return data
    else:
        print(f"Error: {response.status_code}")
        print(response.text)
        return None

def run_tests():
    """Run all tests"""
    print("\n\n========== TESTING ENHANCED RBS CALCULATION FUNCTIONALITY ==========\n")
    
    # Step 1: Test comprehensive team stats calculation
    comprehensive_stats_data = test_comprehensive_team_stats()
    
    # Step 2: Test enhanced RBS calculation
    rbs_calculation_data = test_enhanced_rbs_calculation()
    
    # Step 3: Get a list of teams
    teams = get_teams()
    if teams:
        team_name = teams[0]
        print(f"\nUsing team {team_name} for further tests")
        
        # Step 4: Test team performance stats to verify derived statistics
        team_performance_data = test_team_performance_stats(team_name)
        
        # Step 5: Test RBS results to verify statistics
        rbs_results_data = test_rbs_results(team_name)
    else:
        print("No teams found, skipping team-specific tests")
    
    # Print summary of tests
    print("\n\n========== ENHANCED RBS CALCULATION TESTS SUMMARY ==========\n")
    
    if comprehensive_stats_data and comprehensive_stats_data.get('success'):
        print(f"✅ Comprehensive Team Stats Calculation: {comprehensive_stats_data.get('records_updated')} records updated")
    else:
        print("❌ Comprehensive Team Stats Calculation: Failed")
    
    if rbs_calculation_data and rbs_calculation_data.get('success'):
        print(f"✅ Enhanced RBS Calculation: {rbs_calculation_data.get('results_count')} results calculated")
    else:
        print("❌ Enhanced RBS Calculation: Failed")
    
    if 'team_performance_data' in locals() and team_performance_data and team_performance_data.get('success'):
        home_stats = team_performance_data.get('home_stats', {})
        away_stats = team_performance_data.get('away_stats', {})
        
        # Check for non-zero values in key stats
        key_stats = ['xg_per_shot', 'shots_total']
        all_stats_ok = all(home_stats.get(stat, 0) > 0 or away_stats.get(stat, 0) > 0 for stat in key_stats)
        
        if all_stats_ok:
            print("✅ Team Performance Stats: All key statistics have non-zero values")
        else:
            print("❌ Team Performance Stats: Some key statistics have zero values")
    else:
        print("❌ Team Performance Stats: Failed")
    
    if 'rbs_results_data' in locals() and rbs_results_data and rbs_results_data.get('success'):
        results = rbs_results_data.get('results', [])
        if results:
            print(f"✅ RBS Results Stats: {len(results)} results verified")
        else:
            print("❌ RBS Results Stats: No results found")
    else:
        print("❌ RBS Results Stats: Failed")

if __name__ == "__main__":
    run_tests()