import requests
import os
import json
import time
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Get the backend URL from environment
BACKEND_URL = os.environ.get('REACT_APP_BACKEND_URL', 'http://localhost:8001')
BASE_URL = f"{BACKEND_URL}/api"

def test_predict_match_with_config():
    """Test the POST /api/predict-match endpoint with a custom config"""
    print("\n=== Testing Predict Match with Custom Config ===")
    
    # Create a test config with custom values
    config_name = f"test_pred_config_{int(time.time())}"
    config_data = {
        "config_name": config_name,
        "xg_shot_based_weight": 0.35,
        "xg_historical_weight": 0.45,
        "xg_opponent_defense_weight": 0.2,
        "ppg_adjustment_factor": 0.2,
        "possession_adjustment_per_percent": 0.015,
        "fouls_drawn_factor": 0.025,
        "fouls_drawn_baseline": 9.5,
        "fouls_drawn_min_multiplier": 0.75,
        "fouls_drawn_max_multiplier": 1.25,
        "penalty_xg_value": 0.8,
        "rbs_scaling_factor": 0.25,
        "min_conversion_rate": 0.45,
        "max_conversion_rate": 1.9,
        "min_xg_per_match": 0.15,
        "confidence_matches_multiplier": 5,
        "max_confidence": 95,
        "min_confidence": 25
    }
    
    # Create the config
    print(f"Creating config: {config_name}")
    create_response = requests.post(f"{BASE_URL}/prediction-config", json=config_data)
    
    if create_response.status_code != 200:
        print(f"Failed to create config: {create_response.status_code}")
        print(create_response.text)
        return
    
    create_data = create_response.json()
    print(f"Config created: {create_data.get('success', False)}")
    
    # Create prediction request with custom config
    prediction_data = {
        "home_team": "Arsenal",
        "away_team": "Chelsea",
        "referee_name": "Michael Oliver",
        "match_date": datetime.now().strftime("%Y-%m-%d"),
        "config_name": config_name
    }
    
    # Make prediction request
    print(f"\nMaking prediction with config: {config_name}")
    response = requests.post(f"{BASE_URL}/predict-match", json=prediction_data)
    
    if response.status_code == 200:
        print(f"Status: {response.status_code} OK")
        data = response.json()
        print(f"Success: {data.get('success', False)}")
        
        # Check prediction results
        if data.get('success', False):
            print(f"\nPrediction for {data.get('home_team')} vs {data.get('away_team')}")
            print(f"Referee: {data.get('referee')}")
            print(f"Predicted Home Goals: {data.get('predicted_home_goals')}")
            print(f"Predicted Away Goals: {data.get('predicted_away_goals')}")
            print(f"Home Win Probability: {data.get('home_win_probability')}%")
            print(f"Draw Probability: {data.get('draw_probability')}%")
            print(f"Away Win Probability: {data.get('away_win_probability')}%")
            
            # Check prediction breakdown for config info
            prediction_breakdown = data.get('prediction_breakdown', {})
            print("\nPrediction Breakdown:")
            print(json.dumps(prediction_breakdown, indent=2))
            
            # Check if custom config was used
            config_used = prediction_breakdown.get('config_used', '')
            
            if config_used == config_name:
                print(f"\n✅ Custom config '{config_name}' was used for prediction")
            else:
                print(f"\n❌ Custom config was not used. Config used: '{config_used}'")
        
        # Clean up - delete the test config
        print(f"\nCleaning up - deleting config: {config_name}")
        delete_response = requests.delete(f"{BASE_URL}/prediction-config/{config_name}")
        
        if delete_response.status_code == 200:
            print(f"Config deleted: {delete_response.json().get('success', False)}")
        else:
            print(f"Failed to delete config: {delete_response.status_code}")
            print(delete_response.text)
        
        return data
    else:
        print(f"Error: {response.status_code}")
        print(response.text)
        return None

def test_predict_match_enhanced_with_config():
    """Test the POST /api/predict-match-enhanced endpoint with a custom config"""
    print("\n=== Testing Enhanced Predict Match with Custom Config ===")
    
    # Create a test config with custom values
    config_name = f"test_pred_config_{int(time.time())}"
    config_data = {
        "config_name": config_name,
        "xg_shot_based_weight": 0.35,
        "xg_historical_weight": 0.45,
        "xg_opponent_defense_weight": 0.2,
        "ppg_adjustment_factor": 0.2,
        "possession_adjustment_per_percent": 0.015,
        "fouls_drawn_factor": 0.025,
        "fouls_drawn_baseline": 9.5,
        "fouls_drawn_min_multiplier": 0.75,
        "fouls_drawn_max_multiplier": 1.25,
        "penalty_xg_value": 0.8,
        "rbs_scaling_factor": 0.25,
        "min_conversion_rate": 0.45,
        "max_conversion_rate": 1.9,
        "min_xg_per_match": 0.15,
        "confidence_matches_multiplier": 5,
        "max_confidence": 95,
        "min_confidence": 25
    }
    
    # Create the config
    print(f"Creating config: {config_name}")
    create_response = requests.post(f"{BASE_URL}/prediction-config", json=config_data)
    
    if create_response.status_code != 200:
        print(f"Failed to create config: {create_response.status_code}")
        print(create_response.text)
        return
    
    create_data = create_response.json()
    print(f"Config created: {create_data.get('success', False)}")
    
    # Create enhanced prediction request with custom config
    prediction_data = {
        "home_team": "Arsenal",
        "away_team": "Chelsea",
        "referee_name": "Michael Oliver",
        "match_date": datetime.now().strftime("%Y-%m-%d"),
        "config_name": config_name,
        "use_time_decay": True,
        "decay_preset": "moderate"
    }
    
    # Make enhanced prediction request
    print(f"\nMaking enhanced prediction with config: {config_name}")
    response = requests.post(f"{BASE_URL}/predict-match-enhanced", json=prediction_data)
    
    if response.status_code == 200:
        print(f"Status: {response.status_code} OK")
        data = response.json()
        print(f"Success: {data.get('success', False)}")
        
        # Check prediction results
        if data.get('success', False):
            print(f"\nEnhanced Prediction for {data.get('home_team')} vs {data.get('away_team')}")
            print(f"Referee: {data.get('referee')}")
            print(f"Predicted Home Goals: {data.get('predicted_home_goals')}")
            print(f"Predicted Away Goals: {data.get('predicted_away_goals')}")
            print(f"Home Win Probability: {data.get('home_win_probability')}%")
            print(f"Draw Probability: {data.get('draw_probability')}%")
            print(f"Away Win Probability: {data.get('away_win_probability')}%")
            
            # Check prediction breakdown for config info
            prediction_breakdown = data.get('prediction_breakdown', {})
            print("\nPrediction Breakdown:")
            print(json.dumps(prediction_breakdown, indent=2))
            
            # Check if custom config was used
            config_used = prediction_breakdown.get('config_used', '')
            
            if config_used == config_name:
                print(f"\n✅ Custom config '{config_name}' was used for enhanced prediction")
            else:
                print(f"\n❌ Custom config was not used. Config used: '{config_used}'")
            
            # Check if time decay was applied
            time_decay_info = prediction_breakdown.get('time_decay_info', {})
            if time_decay_info:
                print(f"\nTime Decay Preset: {time_decay_info.get('preset_name', 'N/A')}")
                print(f"Decay Type: {time_decay_info.get('decay_type', 'N/A')}")
        else:
            print(f"Error: {data.get('error', 'Unknown error')}")
        
        # Clean up - delete the test config
        print(f"\nCleaning up - deleting config: {config_name}")
        delete_response = requests.delete(f"{BASE_URL}/prediction-config/{config_name}")
        
        if delete_response.status_code == 200:
            print(f"Config deleted: {delete_response.json().get('success', False)}")
        else:
            print(f"Failed to delete config: {delete_response.status_code}")
            print(delete_response.text)
        
        return data
    else:
        print(f"Error: {response.status_code}")
        print(response.text)
        return None

if __name__ == "__main__":
    # Test predict match with custom config
    test_predict_match_with_config()
    
    # Test enhanced predict match with custom config
    test_predict_match_enhanced_with_config()