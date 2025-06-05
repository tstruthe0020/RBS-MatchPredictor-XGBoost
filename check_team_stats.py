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

def check_team_stats_data():
    """Check the actual team_stats data in the database"""
    print("\n=== Checking Team Stats Data ===")
    
    # Get all teams
    response = requests.get(f"{API_URL}/teams")
    if response.status_code != 200:
        print(f"❌ Error: Failed to get teams, status code {response.status_code}")
        return False
    
    teams = response.json().get("teams", [])
    if not teams:
        print("❌ Error: No teams found in the database")
        return False
    
    # Get team performance for a few teams
    sample_teams = teams[:5]  # Take first 5 teams
    
    stats_summary = {
        "fouls_drawn_nonzero": 0,
        "penalties_awarded_nonzero": 0,
        "total_teams": len(sample_teams)
    }
    
    for team in sample_teams:
        print(f"\nChecking stats for team: {team}")
        response = requests.get(f"{API_URL}/team-performance/{team}")
        
        if response.status_code != 200:
            print(f"❌ Error: Failed to get team performance for {team}, status code {response.status_code}")
            continue
        
        data = response.json()
        home_stats = data.get("home_stats", {})
        away_stats = data.get("away_stats", {})
        
        # Check fouls_drawn
        home_fouls_drawn = home_stats.get("fouls_drawn", 0)
        away_fouls_drawn = away_stats.get("fouls_drawn", 0)
        
        if home_fouls_drawn > 0 or away_fouls_drawn > 0:
            stats_summary["fouls_drawn_nonzero"] += 1
            print(f"✅ Team {team} has non-zero fouls_drawn: home={home_fouls_drawn}, away={away_fouls_drawn}")
        else:
            print(f"❌ Team {team} has zero fouls_drawn: home={home_fouls_drawn}, away={away_fouls_drawn}")
        
        # Check penalties_awarded
        home_penalties = home_stats.get("penalties_awarded", 0)
        away_penalties = away_stats.get("penalties_awarded", 0)
        
        if home_penalties > 0 or away_penalties > 0:
            stats_summary["penalties_awarded_nonzero"] += 1
            print(f"✅ Team {team} has non-zero penalties_awarded: home={home_penalties}, away={away_penalties}")
        else:
            print(f"❌ Team {team} has zero penalties_awarded: home={home_penalties}, away={away_penalties}")
    
    print("\n=== Team Stats Summary ===")
    print(f"Teams with non-zero fouls_drawn: {stats_summary['fouls_drawn_nonzero']}/{stats_summary['total_teams']}")
    print(f"Teams with non-zero penalties_awarded: {stats_summary['penalties_awarded_nonzero']}/{stats_summary['total_teams']}")
    
    return True

if __name__ == "__main__":
    check_team_stats_data()