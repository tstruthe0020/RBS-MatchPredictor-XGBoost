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

def test_referee_bias_with_decay(team_name, referee_name, decay_preset=None):
    """Test the referee bias calculation with time decay"""
    print(f"\n=== Testing Referee Bias for {team_name} with {referee_name} ===")
    print(f"Time Decay Preset: {decay_preset or 'None'}")
    
    # Create request data
    request_data = {
        "home_team": team_name,
        "away_team": "Liverpool",  # Dummy away team
        "referee_name": referee_name,
        "use_time_decay": bool(decay_preset),
        "decay_preset": decay_preset or "none"
    }
    
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
    
    # Add starting XI to request
    request_data["home_starting_xi"] = create_test_starting_xi()
    request_data["away_starting_xi"] = create_test_starting_xi()
    
    # Make the request
    response = requests.post(f"{BASE_URL}/predict-match-enhanced", json=request_data)
    
    if response.status_code == 200:
        data = response.json()
        
        if data.get('success'):
            # Extract referee bias info from prediction breakdown
            breakdown = data.get('prediction_breakdown', {})
            referee_bias = {
                'home_referee_bias': breakdown.get('home_referee_bias', 0),
                'away_referee_bias': breakdown.get('away_referee_bias', 0),
                'home_rbs_confidence': breakdown.get('home_rbs_confidence', 0),
                'away_rbs_confidence': breakdown.get('away_rbs_confidence', 0)
            }
            
            print(f"Home Referee Bias: {referee_bias['home_referee_bias']}")
            print(f"Home RBS Confidence: {referee_bias['home_rbs_confidence']}")
            
            # Check for time decay info
            time_decay_info = breakdown.get('time_decay_info', {})
            if time_decay_info:
                print("\nTime Decay Information:")
                for key, value in time_decay_info.items():
                    print(f"  - {key}: {value}")
            
            return referee_bias
        else:
            print(f"Prediction failed: {data.get('error', 'Unknown error')}")
            return None
    else:
        print(f"Error: {response.status_code}")
        print(response.text)
        return None

def test_referee_bias_with_all_presets(team_name, referee_name):
    """Test referee bias with all time decay presets"""
    print(f"\n=== Testing Referee Bias for {team_name} with {referee_name} using all presets ===")
    
    # Get time decay presets
    response = requests.get(f"{BASE_URL}/time-decay/presets")
    if response.status_code != 200:
        print(f"Error getting presets: {response.status_code}")
        return None
    
    presets_data = response.json()
    presets = [preset.get('preset_name') for preset in presets_data.get('presets', [])]
    
    # Add "none" for no time decay
    presets = ["none"] + presets
    
    results = {}
    for preset in presets:
        # Use None for "none" preset to disable time decay
        decay_preset = None if preset == "none" else preset
        result = test_referee_bias_with_decay(team_name, referee_name, decay_preset)
        results[preset] = result
    
    # Compare results
    print("\n=== Comparing Referee Bias Results ===")
    print(f"{'Preset':<15} {'Home Referee Bias':<20} {'Confidence':<15}")
    print("-" * 50)
    
    for preset, result in results.items():
        if result:
            print(f"{preset:<15} {result['home_referee_bias']:<20.4f} {result['home_rbs_confidence']:<15.2f}")
        else:
            print(f"{preset:<15} {'FAILED':<20} {'FAILED':<15}")
    
    # Check if results are different
    different_results = False
    reference_preset = list(results.keys())[0]
    reference_result = results[reference_preset]
    
    if not reference_result:
        print("\nCannot compare results - reference preset failed")
        return results
    
    for preset, result in results.items():
        if preset == reference_preset or not result:
            continue
        
        if abs(result['home_referee_bias'] - reference_result['home_referee_bias']) > 0.01:
            different_results = True
            break
    
    if different_results:
        print("\n✅ Time decay presets produce DIFFERENT referee bias results as expected")
    else:
        print("\n❌ Time decay presets produce SIMILAR referee bias results - may not be working correctly")
    
    return results

def main():
    """Main test function"""
    team_name = "Arsenal"
    referee_name = "Michael Oliver"
    
    # Test referee bias with all presets
    test_referee_bias_with_all_presets(team_name, referee_name)
    
    # Test with Chelsea as well
    test_referee_bias_with_all_presets("Chelsea", referee_name)

if __name__ == "__main__":
    main()
