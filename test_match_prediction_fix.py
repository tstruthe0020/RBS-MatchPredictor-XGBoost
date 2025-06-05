import requests
import os
import json
import pprint
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Get the backend URL from environment
BACKEND_URL = os.environ.get('REACT_APP_BACKEND_URL', 'http://localhost:8001')
BASE_URL = f"{BACKEND_URL}/api"

# Pretty printer for better output formatting
pp = pprint.PrettyPrinter(indent=2)

def test_chicago_fire_stats():
    """
    Test team performance stats for Chicago Fire to verify xG per shot is now ≤ 1.0
    """
    print("\n=== Testing Chicago Fire Team Performance Stats ===")
    response = requests.get(f"{BASE_URL}/team-performance/Chicago Fire")
    
    if response.status_code == 200:
        print(f"Status: {response.status_code} OK")
        data = response.json()
        print(f"Success: {data['success']}")
        
        if not data.get('success'):
            print(f"Error: {data.get('message', 'Unknown error')}")
            return None
        
        print(f"Team: {data['team_name']}")
        print(f"Total Matches: {data['total_matches']}")
        
        # Check home stats
        home_stats = data.get('home_stats', {})
        away_stats = data.get('away_stats', {})
        
        # Check for bounded statistics
        bounded_stats = ['xg_per_shot', 'shot_accuracy', 'penalty_conversion_rate']
        
        print("\nHome stats for Chicago Fire:")
        for stat in bounded_stats:
            value = home_stats.get(stat, 0)
            print(f"  - {stat}: {value}")
            if value > 1.0:
                print(f"  ❌ {stat} is greater than 1.0 ({value})")
            else:
                print(f"  ✅ {stat} is properly bounded (≤ 1.0)")
        
        print("\nAway stats for Chicago Fire:")
        for stat in bounded_stats:
            value = away_stats.get(stat, 0)
            print(f"  - {stat}: {value}")
            if value > 1.0:
                print(f"  ❌ {stat} is greater than 1.0 ({value})")
            else:
                print(f"  ✅ {stat} is properly bounded (≤ 1.0)")
        
        return data
    else:
        print(f"Error: {response.status_code}")
        print(response.text)
        return None

def test_match_prediction_with_chicago_fire():
    """
    Test match prediction with Chicago Fire to verify xG per shot is now ≤ 1.0
    """
    print("\n=== Testing Match Prediction with Chicago Fire ===")
    
    # Get a list of teams to find an opponent
    teams_response = requests.get(f"{BASE_URL}/teams")
    if teams_response.status_code != 200:
        print(f"Error getting teams: {teams_response.status_code}")
        return None
    
    teams = teams_response.json().get('teams', [])
    if not teams:
        print("No teams found")
        return None
    
    # Find Chicago Fire and an opponent
    chicago_fire = None
    opponent = None
    
    for team in teams:
        if "Chicago Fire" in team:
            chicago_fire = team
        elif "Chicago Fire" not in team and opponent is None:
            opponent = team
    
    if not chicago_fire:
        print("Chicago Fire not found in teams list")
        return None
    
    if not opponent:
        print("No opponent found for Chicago Fire")
        return None
    
    # Get a referee
    referees_response = requests.get(f"{BASE_URL}/referees")
    if referees_response.status_code != 200:
        print(f"Error getting referees: {referees_response.status_code}")
        return None
    
    referees = referees_response.json().get('referees', [])
    if not referees:
        print("No referees found")
        return None
    
    referee = referees[0]
    
    # Test Chicago Fire as home team
    print(f"\nTesting Chicago Fire (home) vs {opponent} with referee {referee}")
    
    request_data = {
        "home_team": chicago_fire,
        "away_team": opponent,
        "referee_name": referee
    }
    
    response = requests.post(f"{BASE_URL}/predict-match", json=request_data)
    
    if response.status_code != 200:
        print(f"Error: {response.status_code}")
        print(response.text)
        return None
    
    prediction_data = response.json()
    
    if not prediction_data.get('success'):
        error_message = prediction_data.get('prediction_breakdown', {}).get('error', 'Unknown error')
        print(f"Prediction failed: {error_message}")
        return None
    
    print("Match prediction successful!")
    print(f"Predicted Home Goals: {prediction_data['predicted_home_goals']}")
    print(f"Predicted Away Goals: {prediction_data['predicted_away_goals']}")
    print(f"Home xG: {prediction_data['home_xg']}")
    print(f"Away xG: {prediction_data['away_xg']}")
    
    # Check prediction breakdown for bounded values
    breakdown = prediction_data.get('prediction_breakdown', {})
    
    # Check xG per shot values
    home_xg_per_shot = breakdown.get('home_xg_per_shot', 0)
    away_xg_per_shot = breakdown.get('away_xg_per_shot', 0)
    
    print(f"Chicago Fire xG per shot: {home_xg_per_shot}")
    print(f"{opponent} xG per shot: {away_xg_per_shot}")
    
    if home_xg_per_shot > 1.0:
        print(f"❌ Chicago Fire xG per shot is greater than 1.0 ({home_xg_per_shot})")
    else:
        print(f"✅ Chicago Fire xG per shot is properly bounded (≤ 1.0)")
    
    # Test Chicago Fire as away team
    print(f"\nTesting {opponent} (home) vs Chicago Fire (away) with referee {referee}")
    
    request_data = {
        "home_team": opponent,
        "away_team": chicago_fire,
        "referee_name": referee
    }
    
    response = requests.post(f"{BASE_URL}/predict-match", json=request_data)
    
    if response.status_code != 200:
        print(f"Error: {response.status_code}")
        print(response.text)
        return None
    
    prediction_data = response.json()
    
    if not prediction_data.get('success'):
        error_message = prediction_data.get('prediction_breakdown', {}).get('error', 'Unknown error')
        print(f"Prediction failed: {error_message}")
        return None
    
    print("Match prediction successful!")
    print(f"Predicted Home Goals: {prediction_data['predicted_home_goals']}")
    print(f"Predicted Away Goals: {prediction_data['predicted_away_goals']}")
    print(f"Home xG: {prediction_data['home_xg']}")
    print(f"Away xG: {prediction_data['away_xg']}")
    
    # Check prediction breakdown for bounded values
    breakdown = prediction_data.get('prediction_breakdown', {})
    
    # Check xG per shot values
    home_xg_per_shot = breakdown.get('home_xg_per_shot', 0)
    away_xg_per_shot = breakdown.get('away_xg_per_shot', 0)
    
    print(f"{opponent} xG per shot: {home_xg_per_shot}")
    print(f"Chicago Fire xG per shot: {away_xg_per_shot}")
    
    if away_xg_per_shot > 1.0:
        print(f"❌ Chicago Fire xG per shot is greater than 1.0 ({away_xg_per_shot})")
    else:
        print(f"✅ Chicago Fire xG per shot is properly bounded (≤ 1.0)")
    
    return prediction_data

def test_multiple_teams_stats():
    """
    Test team performance stats for multiple teams to verify all derived statistics are properly bounded
    """
    print("\n=== Testing Multiple Teams Performance Stats ===")
    
    # Get a list of teams
    teams_response = requests.get(f"{BASE_URL}/teams")
    if teams_response.status_code != 200:
        print(f"Error getting teams: {teams_response.status_code}")
        return None
    
    teams = teams_response.json().get('teams', [])
    if not teams:
        print("No teams found")
        return None
    
    # Select a sample of teams to test (up to 5)
    test_teams = teams[:min(5, len(teams))]
    print(f"Testing {len(test_teams)} teams: {', '.join(test_teams)}")
    
    results = {}
    all_bounded = True
    
    for team in test_teams:
        print(f"\nTesting team: {team}")
        response = requests.get(f"{BASE_URL}/team-performance/{team}")
        
        if response.status_code != 200:
            print(f"Error: {response.status_code}")
            print(response.text)
            continue
        
        data = response.json()
        
        if not data.get('success'):
            print(f"Error: {data.get('message', 'Unknown error')}")
            continue
        
        home_stats = data.get('home_stats', {})
        away_stats = data.get('away_stats', {})
        
        # Check for bounded statistics
        bounded_stats = ['xg_per_shot', 'shot_accuracy', 'penalty_conversion_rate']
        team_bounded = True
        
        print(f"Home stats for {team}:")
        for stat in bounded_stats:
            value = home_stats.get(stat, 0)
            print(f"  - {stat}: {value}")
            if value > 1.0:
                print(f"  ❌ {stat} is greater than 1.0 ({value})")
                team_bounded = False
                all_bounded = False
            else:
                print(f"  ✅ {stat} is properly bounded (≤ 1.0)")
        
        print(f"Away stats for {team}:")
        for stat in bounded_stats:
            value = away_stats.get(stat, 0)
            print(f"  - {stat}: {value}")
            if value > 1.0:
                print(f"  ❌ {stat} is greater than 1.0 ({value})")
                team_bounded = False
                all_bounded = False
            else:
                print(f"  ✅ {stat} is properly bounded (≤ 1.0)")
        
        results[team] = {
            'home_stats': {stat: home_stats.get(stat, 0) for stat in bounded_stats},
            'away_stats': {stat: away_stats.get(stat, 0) for stat in bounded_stats},
            'bounded': team_bounded
        }
    
    print("\n=== Multiple Teams Performance Stats Summary ===")
    for team, result in results.items():
        if result['bounded']:
            print(f"✅ {team}: All stats properly bounded (≤ 1.0)")
        else:
            print(f"❌ {team}: Some stats exceed bounds")
    
    if all_bounded:
        print("\n✅ All teams have properly bounded statistics")
    else:
        print("\n❌ Some teams have statistics that exceed bounds")
    
    return results

def test_prediction_probabilities():
    """
    Test that match prediction probabilities are calculated correctly and sum to 100%
    """
    print("\n=== Testing Match Prediction Probabilities ===")
    
    # Get a list of teams
    teams_response = requests.get(f"{BASE_URL}/teams")
    if teams_response.status_code != 200:
        print(f"Error getting teams: {teams_response.status_code}")
        return None
    
    teams = teams_response.json().get('teams', [])
    if len(teams) < 2:
        print("Not enough teams for match prediction")
        return None
    
    # Get a referee
    referees_response = requests.get(f"{BASE_URL}/referees")
    if referees_response.status_code != 200:
        print(f"Error getting referees: {referees_response.status_code}")
        return None
    
    referees = referees_response.json().get('referees', [])
    if not referees:
        print("No referees found")
        return None
    
    referee = referees[0]
    
    # Test with 3 different team combinations
    test_combinations = []
    if len(teams) >= 6:
        test_combinations = [
            (teams[0], teams[1]),
            (teams[2], teams[3]),
            (teams[4], teams[5])
        ]
    elif len(teams) >= 4:
        test_combinations = [
            (teams[0], teams[1]),
            (teams[2], teams[3]),
            (teams[0], teams[2])
        ]
    elif len(teams) >= 2:
        test_combinations = [
            (teams[0], teams[1]),
            (teams[1], teams[0]),
            (teams[0], teams[1])  # Repeat with same teams
        ]
    
    results = []
    all_valid = True
    
    for i, (home_team, away_team) in enumerate(test_combinations):
        print(f"\nTest {i+1}: {home_team} vs {away_team} with referee {referee}")
        
        request_data = {
            "home_team": home_team,
            "away_team": away_team,
            "referee_name": referee
        }
        
        response = requests.post(f"{BASE_URL}/predict-match", json=request_data)
        
        if response.status_code != 200:
            print(f"Error: {response.status_code}")
            print(response.text)
            continue
        
        prediction_data = response.json()
        
        if not prediction_data.get('success'):
            error_message = prediction_data.get('prediction_breakdown', {}).get('error', 'Unknown error')
            print(f"Prediction failed: {error_message}")
            continue
        
        # Check for probability fields
        if 'home_win_probability' not in prediction_data or 'draw_probability' not in prediction_data or 'away_win_probability' not in prediction_data:
            print("❌ Probability fields are missing from the response!")
            all_valid = False
            continue
        
        home_win_prob = prediction_data['home_win_probability']
        draw_prob = prediction_data['draw_probability']
        away_win_prob = prediction_data['away_win_probability']
        
        print(f"Home Win Probability: {home_win_prob}%")
        print(f"Draw Probability: {draw_prob}%")
        print(f"Away Win Probability: {away_win_prob}%")
        
        # Verify probabilities are reasonable (0-100%)
        if not (0 <= home_win_prob <= 100 and 0 <= draw_prob <= 100 and 0 <= away_win_prob <= 100):
            print("❌ Probabilities are not within the valid range (0-100%)!")
            all_valid = False
            continue
        
        # Verify probabilities sum to approximately 100%
        total_prob = home_win_prob + draw_prob + away_win_prob
        if not (99.5 <= total_prob <= 100.5):  # Allow for small rounding errors
            print(f"❌ Probabilities do not sum to 100%! Total: {total_prob}%")
            all_valid = False
            continue
        
        print(f"✅ Probabilities are valid and sum to {total_prob}%")
        
        results.append({
            'home_team': home_team,
            'away_team': away_team,
            'home_win_probability': home_win_prob,
            'draw_probability': draw_prob,
            'away_win_probability': away_win_prob,
            'total': total_prob
        })
    
    print("\n=== Match Prediction Probabilities Summary ===")
    for i, result in enumerate(results):
        print(f"Test {i+1}: {result['home_team']} vs {result['away_team']}")
        print(f"  Home Win: {result['home_win_probability']}%, Draw: {result['draw_probability']}%, Away Win: {result['away_win_probability']}%")
        print(f"  Total: {result['total']}%")
    
    if all_valid and results:
        print("\n✅ All match prediction probabilities are valid and sum to 100%")
    else:
        print("\n❌ Some match prediction probabilities are invalid or don't sum to 100%")
    
    return results

def run_tests():
    """Run all tests for the corrected match prediction algorithm"""
    print("\n========== TESTING CORRECTED MATCH PREDICTION ALGORITHM ==========\n")
    
    # Test 1: Chicago Fire team stats
    chicago_fire_stats = test_chicago_fire_stats()
    
    # Test 2: Match prediction with Chicago Fire
    chicago_fire_prediction = test_match_prediction_with_chicago_fire()
    
    # Test 3: Multiple teams stats
    multiple_teams_stats = test_multiple_teams_stats()
    
    # Test 4: Prediction probabilities
    prediction_probabilities = test_prediction_probabilities()
    
    # Print summary
    print("\n========== CORRECTED MATCH PREDICTION ALGORITHM TEST SUMMARY ==========\n")
    
    # Check Chicago Fire stats
    if chicago_fire_stats:
        home_xg_per_shot = chicago_fire_stats.get('home_stats', {}).get('xg_per_shot', 0)
        away_xg_per_shot = chicago_fire_stats.get('away_stats', {}).get('xg_per_shot', 0)
        
        if home_xg_per_shot <= 1.0 and away_xg_per_shot <= 1.0:
            print("✅ Chicago Fire xG per shot is properly bounded (≤ 1.0)")
            print(f"   Home: {home_xg_per_shot}, Away: {away_xg_per_shot}")
        else:
            print("❌ Chicago Fire xG per shot exceeds bounds")
            if home_xg_per_shot > 1.0:
                print(f"   Home: {home_xg_per_shot} (exceeds 1.0)")
            if away_xg_per_shot > 1.0:
                print(f"   Away: {away_xg_per_shot} (exceeds 1.0)")
    else:
        print("❌ Failed to get Chicago Fire stats")
    
    # Check match prediction with Chicago Fire
    if chicago_fire_prediction and chicago_fire_prediction.get('success'):
        print("✅ Match prediction with Chicago Fire is working correctly")
    else:
        print("❌ Match prediction with Chicago Fire failed")
    
    # Check multiple teams stats
    if multiple_teams_stats:
        all_bounded = all(result['bounded'] for result in multiple_teams_stats.values())
        if all_bounded:
            print("✅ All teams have properly bounded statistics")
        else:
            print("❌ Some teams have statistics that exceed bounds")
    else:
        print("❌ Failed to get multiple teams stats")
    
    # Check prediction probabilities
    if prediction_probabilities:
        all_valid = all(99.5 <= result['total'] <= 100.5 for result in prediction_probabilities)
        if all_valid:
            print("✅ All match prediction probabilities are valid and sum to 100%")
        else:
            print("❌ Some match prediction probabilities are invalid or don't sum to 100%")
    else:
        print("❌ Failed to test prediction probabilities")
    
    # Overall assessment
    if (chicago_fire_stats and 
        chicago_fire_prediction and chicago_fire_prediction.get('success') and
        multiple_teams_stats and all(result['bounded'] for result in multiple_teams_stats.values()) and
        prediction_probabilities and all(99.5 <= result['total'] <= 100.5 for result in prediction_probabilities)):
        print("\n✅ OVERALL RESULT: The corrected match prediction algorithm is working properly!")
        print("✅ All derived statistics are within reasonable bounds:")
        print("  - xG per shot ≤ 1.0")
        print("  - Shot accuracy ≤ 1.0 (100%)")
        print("  - Penalty conversion rate ≤ 1.0 (100%)")
        print("✅ Prediction probabilities are calculated correctly and sum to 100%")
    else:
        print("\n❌ OVERALL RESULT: The corrected match prediction algorithm still has issues")

if __name__ == "__main__":
    run_tests()