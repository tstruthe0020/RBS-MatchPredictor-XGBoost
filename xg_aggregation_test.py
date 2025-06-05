
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

def test_xg_aggregation():
    """Test xG aggregation from player stats"""
    api_url = get_backend_url()
    if not api_url:
        print("❌ Error: Could not get backend URL from frontend/.env")
        return False
    
    api_url = f"{api_url}/api"
    print(f"Using backend URL: {api_url}")
    
    print("\n=== XG AGGREGATION FROM PLAYER STATS TEST ===\n")
    
    # Get list of teams
    teams_response = requests.get(f"{api_url}/teams")
    if teams_response.status_code != 200:
        print(f"❌ Error getting teams: {teams_response.status_code}")
        return False
    
    teams = teams_response.json()["teams"]
    if not teams:
        print("❌ No teams found in database")
        return False
    
    # Test with Arsenal and a few other teams
    test_teams = ["Arsenal"]
    if "Arsenal" not in teams:
        test_teams = teams[:3]  # Use first 3 teams if Arsenal not found
    
    all_passed = True
    
    for team in test_teams:
        print(f"\nTesting team: {team}")
        
        # Get team performance data
        team_response = requests.get(f"{api_url}/team-performance/{team}")
        
        if team_response.status_code != 200:
            print(f"❌ Error getting team performance: {team_response.status_code}")
            all_passed = False
            continue
        
        team_data = team_response.json()
        
        # Get home and away stats
        home_stats = team_data.get("home_stats", {})
        away_stats = team_data.get("away_stats", {})
        
        if home_stats:
            home_xg = home_stats.get('xg', 0)
            print(f"Home xG: {home_xg}")
            
            if home_xg > 0.5:
                print("✅ Home xG is realistic (> 0.5)")
            else:
                print(f"❌ Home xG ({home_xg}) is too low")
                all_passed = False
        else:
            print("❌ No home stats found")
            all_passed = False
        
        if away_stats:
            away_xg = away_stats.get('xg', 0)
            print(f"Away xG: {away_xg}")
            
            if away_xg > 0.5:
                print("✅ Away xG is realistic (> 0.5)")
            else:
                print(f"❌ Away xG ({away_xg}) is too low")
                all_passed = False
        else:
            print("❌ No away stats found")
            all_passed = False
        
        # Get RBS results for the team
        rbs_response = requests.get(f"{api_url}/rbs-results", params={"team": team})
        
        if rbs_response.status_code != 200:
            print(f"❌ Error getting RBS results: {rbs_response.status_code}")
            all_passed = False
            continue
        
        rbs_data = rbs_response.json()
        results = rbs_data.get("results", [])
        
        if results:
            print(f"\nFound {len(results)} RBS results")
            
            # Check first result
            result = results[0]
            stats_breakdown = result.get("stats_breakdown", {})
            
            if stats_breakdown and 'xg_difference' in stats_breakdown:
                xg_diff_value = stats_breakdown.get('xg_difference', 0)
                print(f"xG difference in RBS: {xg_diff_value}")
                
                if xg_diff_value != 0:
                    print("✅ xG difference in RBS is non-zero")
                else:
                    print("❌ xG difference in RBS is zero")
                    all_passed = False
            else:
                print("❌ No xG difference found in RBS stats breakdown")
                all_passed = False
        else:
            print("❌ No RBS results found")
            all_passed = False
    
    # Check database stats
    print("\nChecking database stats:")
    stats_response = requests.get(f"{api_url}/stats")
    
    if stats_response.status_code != 200:
        print(f"❌ Error getting database stats: {stats_response.status_code}")
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
        all_passed = False
    
    if all_passed:
        print("\n✅ xG aggregation from player stats test passed")
    else:
        print("\n❌ xG aggregation from player stats test failed")
    
    return all_passed

if __name__ == "__main__":
    success = test_xg_aggregation()
    sys.exit(0 if success else 1)
