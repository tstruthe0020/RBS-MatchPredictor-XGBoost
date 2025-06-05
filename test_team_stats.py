import requests
import os
import json
import pprint
from dotenv import load_dotenv

# Load environment variables
load_dotenv('/app/frontend/.env')

# Get the backend URL from environment
BACKEND_URL = os.environ.get('REACT_APP_BACKEND_URL', 'http://localhost:8001')
BASE_URL = f"{BACKEND_URL}/api"

# Pretty printer for better output formatting
pp = pprint.PrettyPrinter(indent=2)

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
    print("\n=== Getting Teams ===")
    response = requests.get(f"{BASE_URL}/teams")
    if response.status_code == 200:
        teams = response.json().get('teams', [])
        print(f"Found {len(teams)} teams")
        if teams:
            print(f"First 5 teams: {', '.join(teams[:5])}")
        return teams
    else:
        print(f"Error: {response.status_code}")
        print(response.text)
        return []

if __name__ == "__main__":
    teams = get_teams()
    if teams:
        test_team_performance_stats(teams[0])
    else:
        print("No teams found, using default team")
        test_team_performance_stats()