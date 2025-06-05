import requests
import os
import json
import pprint
import time
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

def test_team_stats(team_name="Arsenal"):
    """Test team statistics for a specific team"""
    print(f"\n=== Testing Team Stats for {team_name} ===")
    response = requests.get(f"{BASE_URL}/team-stats/{team_name}")
    
    if response.status_code == 200:
        print(f"Status: {response.status_code} OK")
        data = response.json()
        
        # Check for required statistics
        required_stats = [
            'xg_per_shot', 'shots_total', 'shots_on_target', 'goals_per_xg', 
            'shot_accuracy', 'conversion_rate', 'penalty_conversion_rate'
        ]
        
        # Print key stats
        print("\nKey Statistics:")
        for stat in required_stats:
            value = data.get(stat, 0)
            print(f"  {stat}: {value}")
            
            if value == 0:
                print(f"  ❌ {stat} has zero value")
            else:
                print(f"  ✅ {stat} has non-zero value")
        
        return data
    else:
        print(f"Error: {response.status_code}")
        print(response.text)
        return None

def test_rbs_results(team_name="Arsenal"):
    """Test RBS results for a specific team"""
    print(f"\n=== Testing RBS Results for {team_name} ===")
    response = requests.get(f"{BASE_URL}/rbs-results/{team_name}")
    
    if response.status_code == 200:
        print(f"Status: {response.status_code} OK")
        data = response.json()
        
        # Check RBS results
        results = data.get('results', [])
        print(f"Found {len(results)} RBS results")
        
        if results:
            # Check the first result
            first_result = results[0]
            print(f"\nFirst Result:")
            print(f"  Referee: {first_result.get('referee')}")
            print(f"  RBS Score: {first_result.get('rbs_score')}")
            
            # Check stats breakdown
            stats_breakdown = first_result.get('stats_breakdown', {})
            print("\nStats Breakdown:")
            for stat, value in stats_breakdown.items():
                print(f"  {stat}: {value}")
                
                if value == 0:
                    print(f"  ⚠️ {stat} has zero value")
        
        return data
    else:
        print(f"Error: {response.status_code}")
        print(response.text)
        return None

if __name__ == "__main__":
    # Step 1: Calculate comprehensive team stats
    test_comprehensive_team_stats()
    
    # Step 2: Calculate RBS scores
    test_enhanced_rbs_calculation()
    
    # Step 3: Get a list of teams
    teams = get_teams()
    
    if teams:
        team_name = teams[0]
        
        # Step 4: Test team stats
        test_team_stats(team_name)
        
        # Step 5: Test RBS results
        test_rbs_results(team_name)
    else:
        print("No teams found, skipping team-specific tests")