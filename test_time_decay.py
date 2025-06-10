import requests
import json
import pprint
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Get the backend URL from environment
BACKEND_URL = os.environ.get('REACT_APP_BACKEND_URL', 'http://localhost:8001')
BASE_URL = f"{BACKEND_URL}/api"

# Pretty printer for better output formatting
pp = pprint.PrettyPrinter(indent=2)

def test_time_decay_presets():
    """Test the time decay presets endpoint to verify available presets"""
    print("\n=== Testing Time Decay Presets ===")
    response = requests.get(f"{BASE_URL}/time-decay/presets")
    
    if response.status_code == 200:
        data = response.json()
        print(f"Success: {data.get('success', False)}")
        
        presets = data.get('presets', [])
        print(f"Found {len(presets)} presets:")
        
        for preset in presets:
            print(f"  - {preset.get('preset_name')}: {preset.get('decay_type')} decay")
            print(f"    Description: {preset.get('description')}")
            if preset.get('decay_type') == 'exponential':
                print(f"    Half-life: {preset.get('half_life_months')} months")
            elif preset.get('decay_type') == 'linear':
                print(f"    Decay rate: {preset.get('decay_rate_per_month')} per month")
        
        return presets
    else:
        print(f"Error: {response.status_code}")
        print(response.text)
        return None

def test_enhanced_prediction_with_time_decay(home_team, away_team, referee, decay_preset):
    """Test the enhanced prediction endpoint with a specific time decay preset"""
    print(f"\n=== Testing Enhanced Prediction with {decay_preset} Time Decay ===")
    
    # Create a simple starting XI for testing
    def create_test_starting_xi(formation="4-4-2"):
        positions = []
        for i in range(11):
            position_type = "GK" if i == 0 else "DEF" if i < 5 else "MID" if i < 9 else "FWD"
            position_id = f"{position_type}{i+1}"
            player = {
                "player_name": f"Test Player {i+1}",
                "position": position_type,
                "minutes_played": 900,
                "matches_played": 10
            }
            positions.append({
                "position_id": position_id,
                "position_type": position_type,
                "player": player
            })
        return {
            "formation": formation,
            "positions": positions
        }
    
    # Create test starting XIs
    home_xi = create_test_starting_xi()
    away_xi = create_test_starting_xi()
    
    request_data = {
        "home_team": home_team,
        "away_team": away_team,
        "referee_name": referee,
        "use_time_decay": True,
        "decay_preset": decay_preset,
        "home_starting_xi": home_xi,
        "away_starting_xi": away_xi
    }
    
    response = requests.post(f"{BASE_URL}/predict-match-enhanced", json=request_data)
    
    if response.status_code == 200:
        data = response.json()
        print(f"Success: {data.get('success', False)}")
        
        if data.get('success'):
            print(f"Home Team: {data.get('home_team')}")
            print(f"Away Team: {data.get('away_team')}")
            print(f"Referee: {data.get('referee')}")
            print(f"Predicted Home Goals: {data.get('predicted_home_goals')}")
            print(f"Predicted Away Goals: {data.get('predicted_away_goals')}")
            print(f"Home Win Probability: {data.get('home_win_probability')}%")
            print(f"Draw Probability: {data.get('draw_probability')}%")
            print(f"Away Win Probability: {data.get('away_win_probability')}%")
            
            # Check for time decay info in the prediction breakdown
            breakdown = data.get('prediction_breakdown', {})
            time_decay_info = breakdown.get('time_decay_info', {})
            
            if time_decay_info:
                print("\nTime Decay Information:")
                for key, value in time_decay_info.items():
                    print(f"  - {key}: {value}")
            else:
                print("\nNo time decay information found in prediction breakdown")
            
            return data
        else:
            print(f"Prediction failed: {data.get('error', 'Unknown error')}")
            return data
    else:
        print(f"Error: {response.status_code}")
        print(response.text)
        return None

def compare_time_decay_results(results):
    """Compare the results of predictions with different time decay settings"""
    print("\n=== Comparing Time Decay Results ===")
    
    if len(results) < 2:
        print("Not enough results to compare")
        return
    
    # Extract key metrics for comparison
    comparison = {}
    for preset, result in results.items():
        if not result or not result.get('success'):
            comparison[preset] = "Failed"
            continue
        
        comparison[preset] = {
            "home_goals": result.get('predicted_home_goals'),
            "away_goals": result.get('predicted_away_goals'),
            "home_win_prob": result.get('home_win_probability'),
            "draw_prob": result.get('draw_probability'),
            "away_win_prob": result.get('away_win_probability')
        }
    
    # Print comparison table
    print("\nPrediction Comparison:")
    print("-" * 80)
    print(f"{'Preset':<15} {'Home Goals':<15} {'Away Goals':<15} {'Home Win %':<15} {'Draw %':<15} {'Away Win %':<15}")
    print("-" * 80)
    
    for preset, metrics in comparison.items():
        if metrics == "Failed":
            print(f"{preset:<15} {'FAILED':<15} {'FAILED':<15} {'FAILED':<15} {'FAILED':<15} {'FAILED':<15}")
        else:
            print(f"{preset:<15} {metrics['home_goals']:<15.2f} {metrics['away_goals']:<15.2f} "
                  f"{metrics['home_win_prob']:<15.2f} {metrics['draw_prob']:<15.2f} {metrics['away_win_prob']:<15.2f}")
    
    print("-" * 80)
    
    # Check if results are different
    different_results = False
    reference_preset = list(comparison.keys())[0]
    reference_metrics = comparison[reference_preset]
    
    if reference_metrics == "Failed":
        print("Cannot compare results - reference preset failed")
        return
    
    for preset, metrics in comparison.items():
        if preset == reference_preset or metrics == "Failed":
            continue
        
        if (abs(metrics['home_goals'] - reference_metrics['home_goals']) > 0.01 or
            abs(metrics['away_goals'] - reference_metrics['away_goals']) > 0.01 or
            abs(metrics['home_win_prob'] - reference_metrics['home_win_prob']) > 0.1):
            different_results = True
            break
    
    if different_results:
        print("\n✅ Time decay presets produce DIFFERENT prediction results as expected")
    else:
        print("\n❌ Time decay presets produce SIMILAR prediction results - may not be working correctly")

def main():
    """Main test function"""
    # Step 1: Test time decay presets
    presets = test_time_decay_presets()
    if not presets:
        print("❌ Failed to get time decay presets")
        return
    
    # Step 2: Test enhanced prediction with different time decay settings
    home_team = "Arsenal"
    away_team = "Chelsea"
    referee = "Michael Oliver"
    
    print(f"\nTesting predictions for {home_team} vs {away_team} with referee {referee}")
    
    # Test with different presets
    preset_names = [preset.get('preset_name') for preset in presets]
    results = {}
    
    for preset in preset_names:
        result = test_enhanced_prediction_with_time_decay(home_team, away_team, referee, preset)
        results[preset] = result
    
    # Step 3: Compare results with different time decay settings
    compare_time_decay_results(results)

if __name__ == "__main__":
    main()
