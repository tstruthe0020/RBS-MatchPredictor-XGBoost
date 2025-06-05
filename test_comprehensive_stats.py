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

def get_team_performance(team_name="Arsenal"):
    """Get team performance stats"""
    print(f"\n=== Getting Team Performance for {team_name} ===")
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
        
        # Check for required statistics
        required_stats = [
            'xg_per_shot', 'shots_total', 'shots_on_target', 'goals_per_xg', 
            'shot_accuracy', 'conversion_rate', 'penalty_conversion_rate',
            'points', 'goals', 'goals_conceded'
        ]
        
        print("\nHome Stats:")
        for stat in required_stats:
            if stat in home_stats:
                value = home_stats.get(stat, 0)
                print(f"  {stat}: {value}")
                
                if value == 0:
                    print(f"  ❌ {stat} has zero value")
                else:
                    print(f"  ✅ {stat} has non-zero value")
            else:
                print(f"  ❌ {stat} not found in response")
        
        print("\nAway Stats:")
        for stat in required_stats:
            if stat in away_stats:
                value = away_stats.get(stat, 0)
                print(f"  {stat}: {value}")
                
                if value == 0:
                    print(f"  ❌ {stat} has zero value")
                else:
                    print(f"  ✅ {stat} has non-zero value")
            else:
                print(f"  ❌ {stat} not found in response")
        
        return data
    else:
        print(f"Error: {response.status_code}")
        print(response.text)
        return None

if __name__ == "__main__":
    # Step 1: Calculate comprehensive team stats
    test_comprehensive_team_stats()
    
    # Step 2: Get team performance stats for Arsenal
    get_team_performance("Arsenal")