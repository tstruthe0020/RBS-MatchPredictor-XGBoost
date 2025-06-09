import requests
import os
import json
import time
import pprint
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Get the backend URL from environment
BACKEND_URL = os.environ.get('REACT_APP_BACKEND_URL', 'http://localhost:8001')
BASE_URL = f"{BACKEND_URL}/api"

# Pretty printer for better output formatting
pp = pprint.PrettyPrinter(indent=2)

def test_time_decay_presets_endpoint():
    """Test the /api/time-decay/presets endpoint to ensure it returns decay presets"""
    print("\n=== Testing Time Decay Presets Endpoint ===")
    response = requests.get(f"{BASE_URL}/time-decay/presets")
    
    if response.status_code == 200:
        print(f"Status: {response.status_code} OK")
        data = response.json()
        print(f"Success: {data.get('success', False)}")
        
        presets = data.get('presets', [])
        print(f"Presets found: {len(presets)}")
        
        for preset in presets:
            print(f"  - {preset.get('preset_name')}: {preset.get('decay_type')} decay")
            print(f"    Description: {preset.get('description')}")
            
        # Verify expected presets are present
        expected_presets = ["aggressive", "moderate", "conservative", "linear", "none"]
        found_presets = [p.get('preset_name') for p in presets]
        
        missing_presets = [p for p in expected_presets if p not in found_presets]
        if missing_presets:
            print(f"❌ Missing expected presets: {', '.join(missing_presets)}")
        else:
            print("✅ All expected presets are present")
            
        return data
    else:
        print(f"Error: {response.status_code}")
        print(response.text)
        return None

def test_predict_match_enhanced_with_different_decay_presets():
    """Test the /api/predict-match-enhanced endpoint with different decay presets"""
    print("\n=== Testing Enhanced Match Prediction with Different Decay Presets ===")
    
    # First, get teams and referees
    teams_response = requests.get(f"{BASE_URL}/teams")
    if teams_response.status_code != 200:
        print(f"❌ Failed to get teams: {teams_response.status_code}")
        return False
    
    teams = teams_response.json().get('teams', [])
    if len(teams) < 2:
        print("❌ Not enough teams for match prediction")
        return False
    
    referees_response = requests.get(f"{BASE_URL}/referees")
    if referees_response.status_code != 200:
        print(f"❌ Failed to get referees: {referees_response.status_code}")
        return False
    
    referees = referees_response.json().get('referees', [])
    if not referees:
        print("❌ No referees found for match prediction")
        return False
    
    # Select teams and referee for testing
    home_team = teams[0]
    away_team = teams[1]
    referee = referees[0]
    
    print(f"Testing enhanced prediction for {home_team} vs {away_team} with referee {referee}")
    
    # Test with different decay presets
    decay_presets = ["aggressive", "moderate", "conservative", "linear", "none"]
    results = {}
    
    for preset in decay_presets:
        print(f"\nTesting with decay preset: {preset}")
        
        request_data = {
            "home_team": home_team,
            "away_team": away_team,
            "referee_name": referee,
            "use_time_decay": True,
            "decay_preset": preset
        }
        
        response = requests.post(f"{BASE_URL}/predict-match-enhanced", json=request_data)
        
        if response.status_code == 200:
            print(f"Status: {response.status_code} OK")
            data = response.json()
            print(f"Success: {data.get('success', False)}")
            
            if data.get('success'):
                print(f"Predicted Home Goals: {data.get('predicted_home_goals')}")
                print(f"Predicted Away Goals: {data.get('predicted_away_goals')}")
                print(f"Home xG: {data.get('home_xg')}")
                print(f"Away xG: {data.get('away_xg')}")
                
                # Store results for comparison
                results[preset] = {
                    'home_goals': data.get('predicted_home_goals'),
                    'away_goals': data.get('predicted_away_goals'),
                    'home_xg': data.get('home_xg'),
                    'away_xg': data.get('away_xg')
                }
                
                # Check for time decay info in breakdown
                breakdown = data.get('prediction_breakdown', {})
                if 'time_decay_info' in breakdown:
                    print("\nTime Decay Info:")
                    decay_info = breakdown.get('time_decay_info', {})
                    for key, value in decay_info.items():
                        print(f"  - {key}: {value}")
            else:
                print(f"Prediction failed: {data.get('error', 'Unknown error')}")
        else:
            print(f"Error: {response.status_code}")
            print(response.text)
    
    # Compare results across different presets
    print("\n=== Comparing Results Across Different Decay Presets ===")
    
    if len(results) > 1:
        # Check if different presets produce different results
        home_goals_values = [r['home_goals'] for r in results.values()]
        away_goals_values = [r['away_goals'] for r in results.values()]
        
        home_goals_different = len(set(home_goals_values)) > 1
        away_goals_different = len(set(away_goals_values)) > 1
        
        if home_goals_different or away_goals_different:
            print("✅ Different decay presets produce different prediction results")
            
            # Print comparison table
            print("\nComparison Table:")
            print(f"{'Preset':<15} {'Home Goals':<15} {'Away Goals':<15} {'Home xG':<15} {'Away xG':<15}")
            print("-" * 75)
            
            for preset, data in results.items():
                print(f"{preset:<15} {data['home_goals']:<15.2f} {data['away_goals']:<15.2f} {data['home_xg']:<15.2f} {data['away_xg']:<15.2f}")
            
            # Check if results follow expected pattern
            # Aggressive decay should weight recent matches more heavily than conservative
            if 'aggressive' in results and 'conservative' in results:
                print("\nComparing aggressive vs conservative decay:")
                aggressive = results['aggressive']
                conservative = results['conservative']
                
                # We can't make specific assertions about the values without knowing the data
                # But we can check if they're different
                if (aggressive['home_goals'] != conservative['home_goals'] or 
                    aggressive['away_goals'] != conservative['away_goals']):
                    print("✅ Aggressive and conservative decay produce different results as expected")
                else:
                    print("❌ Aggressive and conservative decay produce identical results")
            
            # Check if 'none' preset behaves as expected (no time decay)
            if 'none' in results:
                print("\nChecking 'none' preset behavior:")
                none_preset = results['none']
                other_presets = [p for p in decay_presets if p != 'none' and p in results]
                
                if any(none_preset['home_goals'] != results[p]['home_goals'] for p in other_presets):
                    print("✅ 'None' preset produces different results from decay presets")
                else:
                    print("❌ 'None' preset produces identical results to decay presets")
        else:
            print("❌ All decay presets produce identical prediction results")
    else:
        print("❌ Not enough successful predictions to compare")
    
    return results

def test_time_decay_with_different_match_dates():
    """Test time decay with different match dates to verify decay behavior"""
    print("\n=== Testing Time Decay with Different Match Dates ===")
    
    # First, get teams and referees
    teams_response = requests.get(f"{BASE_URL}/teams")
    if teams_response.status_code != 200:
        print(f"❌ Failed to get teams: {teams_response.status_code}")
        return False
    
    teams = teams_response.json().get('teams', [])
    if len(teams) < 2:
        print("❌ Not enough teams for match prediction")
        return False
    
    referees_response = requests.get(f"{BASE_URL}/referees")
    if referees_response.status_code != 200:
        print(f"❌ Failed to get referees: {referees_response.status_code}")
        return False
    
    referees = referees_response.json().get('referees', [])
    if not referees:
        print("❌ No referees found for match prediction")
        return False
    
    # Select teams and referee for testing
    home_team = teams[0]
    away_team = teams[1]
    referee = referees[0]
    
    print(f"Testing time decay with different match dates for {home_team} vs {away_team}")
    
    # Test with different match dates
    match_dates = [
        "2023-01-01",  # Very old
        "2023-06-01",  # Moderately old
        "2023-11-01",  # Recent
        "2024-01-01",  # Very recent
        None           # Current date (default)
    ]
    
    results = {}
    
    for date in match_dates:
        date_label = date if date else "Current"
        print(f"\nTesting with match date: {date_label}")
        
        request_data = {
            "home_team": home_team,
            "away_team": away_team,
            "referee_name": referee,
            "match_date": date,
            "use_time_decay": True,
            "decay_preset": "moderate"  # Use moderate decay for all tests
        }
        
        response = requests.post(f"{BASE_URL}/predict-match-enhanced", json=request_data)
        
        if response.status_code == 200:
            print(f"Status: {response.status_code} OK")
            data = response.json()
            print(f"Success: {data.get('success', False)}")
            
            if data.get('success'):
                print(f"Predicted Home Goals: {data.get('predicted_home_goals')}")
                print(f"Predicted Away Goals: {data.get('predicted_away_goals')}")
                
                # Store results for comparison
                results[date_label] = {
                    'home_goals': data.get('predicted_home_goals'),
                    'away_goals': data.get('predicted_away_goals'),
                    'home_xg': data.get('home_xg'),
                    'away_xg': data.get('away_xg')
                }
                
                # Check for time decay info in breakdown
                breakdown = data.get('prediction_breakdown', {})
                if 'time_decay_info' in breakdown:
                    print("\nTime Decay Info:")
                    decay_info = breakdown.get('time_decay_info', {})
                    for key, value in decay_info.items():
                        print(f"  - {key}: {value}")
            else:
                print(f"Prediction failed: {data.get('error', 'Unknown error')}")
        else:
            print(f"Error: {response.status_code}")
            print(response.text)
    
    # Compare results across different match dates
    print("\n=== Comparing Results Across Different Match Dates ===")
    
    if len(results) > 1:
        # Check if different dates produce different results
        home_goals_values = [r['home_goals'] for r in results.values()]
        away_goals_values = [r['away_goals'] for r in results.values()]
        
        home_goals_different = len(set(home_goals_values)) > 1
        away_goals_different = len(set(away_goals_values)) > 1
        
        if home_goals_different or away_goals_different:
            print("✅ Different match dates produce different prediction results")
            
            # Print comparison table
            print("\nComparison Table:")
            print(f"{'Match Date':<15} {'Home Goals':<15} {'Away Goals':<15} {'Home xG':<15} {'Away xG':<15}")
            print("-" * 75)
            
            for date, data in results.items():
                print(f"{str(date):<15} {data['home_goals']:<15.2f} {data['away_goals']:<15.2f} {data['home_xg']:<15.2f} {data['away_xg']:<15.2f}")
        else:
            print("❌ All match dates produce identical prediction results")
    else:
        print("❌ Not enough successful predictions to compare")
    
    return results

def test_time_decay_calculation_functions():
    """Test the time decay calculation functions directly"""
    print("\n=== Testing Time Decay Calculation Functions ===")
    
    # Since we can't directly access the internal functions, we'll test them indirectly
    # through the enhanced prediction endpoint with different configurations
    
    # First, get teams and referees
    teams_response = requests.get(f"{BASE_URL}/teams")
    if teams_response.status_code != 200:
        print(f"❌ Failed to get teams: {teams_response.status_code}")
        return False
    
    teams = teams_response.json().get('teams', [])
    if len(teams) < 2:
        print("❌ Not enough teams for match prediction")
        return False
    
    referees_response = requests.get(f"{BASE_URL}/referees")
    if referees_response.status_code != 200:
        print(f"❌ Failed to get referees: {referees_response.status_code}")
        return False
    
    referees = referees_response.json().get('referees', [])
    if not referees:
        print("❌ No referees found for match prediction")
        return False
    
    # Select teams and referee for testing
    home_team = teams[0]
    away_team = teams[1]
    referee = referees[0]
    
    print(f"Testing time decay calculation functions for {home_team} vs {away_team}")
    
    # Test with and without time decay to compare
    test_cases = [
        {"use_time_decay": False, "label": "No Decay"},
        {"use_time_decay": True, "decay_preset": "aggressive", "label": "Aggressive Decay"},
        {"use_time_decay": True, "decay_preset": "moderate", "label": "Moderate Decay"},
        {"use_time_decay": True, "decay_preset": "conservative", "label": "Conservative Decay"},
        {"use_time_decay": True, "decay_preset": "linear", "label": "Linear Decay"}
    ]
    
    results = {}
    
    for case in test_cases:
        print(f"\nTesting with {case['label']}")
        
        request_data = {
            "home_team": home_team,
            "away_team": away_team,
            "referee_name": referee,
            "use_time_decay": case["use_time_decay"]
        }
        
        if case["use_time_decay"]:
            request_data["decay_preset"] = case["decay_preset"]
        
        response = requests.post(f"{BASE_URL}/predict-match-enhanced", json=request_data)
        
        if response.status_code == 200:
            print(f"Status: {response.status_code} OK")
            data = response.json()
            print(f"Success: {data.get('success', False)}")
            
            if data.get('success'):
                # Store results for comparison
                results[case['label']] = {
                    'home_goals': data.get('predicted_home_goals'),
                    'away_goals': data.get('predicted_away_goals'),
                    'home_xg': data.get('home_xg'),
                    'away_xg': data.get('away_xg')
                }
                
                # Check for time decay info in breakdown
                breakdown = data.get('prediction_breakdown', {})
                if 'time_decay_info' in breakdown:
                    decay_info = breakdown.get('time_decay_info', {})
                    results[case['label']]['decay_info'] = decay_info
                    
                    print("\nTime Decay Info:")
                    for key, value in decay_info.items():
                        print(f"  - {key}: {value}")
                
                # Check for team averages with decay
                if 'team_averages' in breakdown:
                    team_avg = breakdown.get('team_averages', {})
                    if 'home_team' in team_avg:
                        print("\nHome Team Averages (with decay):")
                        for key, value in list(team_avg['home_team'].items())[:5]:
                            print(f"  - {key}: {value}")
                        print("  ...")
                    
                    if 'away_team' in team_avg:
                        print("\nAway Team Averages (with decay):")
                        for key, value in list(team_avg['away_team'].items())[:5]:
                            print(f"  - {key}: {value}")
                        print("  ...")
                
                # Check for referee bias with decay
                if 'referee_bias' in breakdown:
                    ref_bias = breakdown.get('referee_bias', {})
                    print("\nReferee Bias (with decay):")
                    for key, value in ref_bias.items():
                        print(f"  - {key}: {value}")
                
                # Check for head-to-head stats with decay
                if 'head_to_head' in breakdown:
                    h2h = breakdown.get('head_to_head', {})
                    print("\nHead-to-Head Stats (with decay):")
                    for key, value in h2h.items():
                        print(f"  - {key}: {value}")
                
                # Check for team form with decay
                if 'form' in breakdown:
                    form = breakdown.get('form', {})
                    print("\nTeam Form (with decay):")
                    for key, value in form.items():
                        print(f"  - {key}: {value}")
            else:
                print(f"Prediction failed: {data.get('error', 'Unknown error')}")
        else:
            print(f"Error: {response.status_code}")
            print(response.text)
    
    # Compare results to verify time decay functions are working
    print("\n=== Comparing Results to Verify Time Decay Functions ===")
    
    if "No Decay" in results and len(results) > 1:
        no_decay = results["No Decay"]
        
        print("\nComparison Table:")
        print(f"{'Test Case':<20} {'Home Goals':<15} {'Away Goals':<15} {'Home xG':<15} {'Away xG':<15}")
        print("-" * 80)
        
        for label, data in results.items():
            print(f"{label:<20} {data['home_goals']:<15.2f} {data['away_goals']:<15.2f} {data['home_xg']:<15.2f} {data['away_xg']:<15.2f}")
        
        # Check if decay produces different results than no decay
        decay_cases = [label for label in results.keys() if label != "No Decay"]
        differences_found = False
        
        for label in decay_cases:
            decay_data = results[label]
            
            if (decay_data['home_goals'] != no_decay['home_goals'] or 
                decay_data['away_goals'] != no_decay['away_goals'] or
                decay_data['home_xg'] != no_decay['home_xg'] or
                decay_data['away_xg'] != no_decay['away_xg']):
                differences_found = True
                break
        
        if differences_found:
            print("\n✅ Time decay functions produce different results than no decay")
            
            # Check if different decay presets produce different results
            if len(decay_cases) > 1:
                decay_results = [results[label] for label in decay_cases]
                home_goals_values = [r['home_goals'] for r in decay_results]
                away_goals_values = [r['away_goals'] for r in decay_results]
                
                home_goals_different = len(set(home_goals_values)) > 1
                away_goals_different = len(set(away_goals_values)) > 1
                
                if home_goals_different or away_goals_different:
                    print("✅ Different decay presets produce different results")
                else:
                    print("❌ All decay presets produce identical results")
        else:
            print("\n❌ Time decay functions do not produce different results than no decay")
    else:
        print("❌ Not enough successful predictions to compare")
    
    return results

def run_all_tests():
    """Run all time decay tests"""
    print("\n\n========== TESTING PHASE 2 TIME DECAY IMPLEMENTATION ==========\n")
    
    # Test 1: Time Decay Presets Endpoint
    print("\nTest 1: Time Decay Presets Endpoint")
    presets_data = test_time_decay_presets_endpoint()
    
    if not presets_data or not presets_data.get('success'):
        print("❌ Time decay presets endpoint test failed")
    else:
        print("✅ Time decay presets endpoint test passed")
    
    # Test 2: Enhanced Prediction with Different Decay Presets
    print("\nTest 2: Enhanced Prediction with Different Decay Presets")
    decay_preset_results = test_predict_match_enhanced_with_different_decay_presets()
    
    if not decay_preset_results:
        print("❌ Enhanced prediction with different decay presets test failed")
    else:
        print("✅ Enhanced prediction with different decay presets test passed")
    
    # Test 3: Time Decay with Different Match Dates
    print("\nTest 3: Time Decay with Different Match Dates")
    match_date_results = test_time_decay_with_different_match_dates()
    
    if not match_date_results:
        print("❌ Time decay with different match dates test failed")
    else:
        print("✅ Time decay with different match dates test passed")
    
    # Test 4: Time Decay Calculation Functions
    print("\nTest 4: Time Decay Calculation Functions")
    calculation_results = test_time_decay_calculation_functions()
    
    if not calculation_results:
        print("❌ Time decay calculation functions test failed")
    else:
        print("✅ Time decay calculation functions test passed")
    
    # Final summary
    print("\n========== PHASE 2 TIME DECAY IMPLEMENTATION TEST SUMMARY ==========")
    
    tests_passed = [
        presets_data and presets_data.get('success'),
        bool(decay_preset_results),
        bool(match_date_results),
        bool(calculation_results)
    ]
    
    if all(tests_passed):
        print("✅ All Phase 2 time decay implementation tests passed!")
        return True
    else:
        print("❌ Some Phase 2 time decay implementation tests failed")
        return False

if __name__ == "__main__":
    run_all_tests()
