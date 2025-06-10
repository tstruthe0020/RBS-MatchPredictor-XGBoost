import requests
import os
import json
import time
import pprint
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Get the backend URL from environment
BACKEND_URL = os.environ.get('REACT_APP_BACKEND_URL', 'http://localhost:8001')
BASE_URL = f"{BACKEND_URL}/api"

# Pretty printer for better output formatting
pp = pprint.PrettyPrinter(indent=2)

def test_prediction_configs_list():
    """Test the GET /api/prediction-configs endpoint to list all prediction configs"""
    print("\n=== Testing Prediction Configs List Endpoint ===")
    response = requests.get(f"{BASE_URL}/prediction-configs")
    
    if response.status_code == 200:
        print(f"Status: {response.status_code} OK")
        data = response.json()
        print(f"Success: {data.get('success', False)}")
        
        # Check configs
        configs = data.get('configs', [])
        print(f"Configs Found: {len(configs)}")
        
        if configs:
            print("\nSample Configs:")
            for config in configs[:3]:  # Show first 3 configs
                print(f"\n  - Name: {config.get('config_name')}")
                print(f"    Created At: {config.get('created_at')}")
                print(f"    Updated At: {config.get('updated_at')}")
            
            if len(configs) > 3:
                print("  ...")
        
        return data
    else:
        print(f"Error: {response.status_code}")
        print(response.text)
        return None

def test_create_prediction_config(config_name="test_config"):
    """Test the POST /api/prediction-config endpoint to create a new prediction config"""
    print(f"\n=== Testing Create Prediction Config Endpoint ({config_name}) ===")
    
    # Create a test config with custom values
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
    
    response = requests.post(f"{BASE_URL}/prediction-config", json=config_data)
    
    if response.status_code == 200:
        print(f"Status: {response.status_code} OK")
        data = response.json()
        print(f"Success: {data.get('success', False)}")
        print(f"Message: {data.get('message', '')}")
        
        # Check if config was created
        config = data.get('config', {})
        if config:
            print(f"\nCreated Config: {config.get('config_name')}")
            print(f"Created At: {config.get('created_at')}")
            print(f"Updated At: {config.get('updated_at')}")
            
            # Verify custom values
            print("\nVerifying custom values:")
            print(f"xG Shot-based Weight: {config.get('xg_shot_based_weight')} (Expected: 0.35)")
            print(f"xG Historical Weight: {config.get('xg_historical_weight')} (Expected: 0.45)")
            print(f"RBS Scaling Factor: {config.get('rbs_scaling_factor')} (Expected: 0.25)")
        
        return data
    else:
        print(f"Error: {response.status_code}")
        print(response.text)
        return None

def test_get_prediction_config(config_name="test_config"):
    """Test the GET /api/prediction-config/{config_name} endpoint to retrieve a specific config"""
    print(f"\n=== Testing Get Prediction Config Endpoint ({config_name}) ===")
    
    response = requests.get(f"{BASE_URL}/prediction-config/{config_name}")
    
    if response.status_code == 200:
        print(f"Status: {response.status_code} OK")
        data = response.json()
        print(f"Success: {data.get('success', False)}")
        
        # Check if config was retrieved
        config = data.get('config', {})
        is_default = data.get('is_default', False)
        
        if config:
            print(f"\nRetrieved Config: {config.get('config_name')}")
            print(f"Is Default: {is_default}")
            
            if not is_default:
                print(f"Created At: {config.get('created_at')}")
                print(f"Updated At: {config.get('updated_at')}")
                
                # Verify values
                print("\nVerifying values:")
                print(f"xG Shot-based Weight: {config.get('xg_shot_based_weight')}")
                print(f"xG Historical Weight: {config.get('xg_historical_weight')}")
                print(f"RBS Scaling Factor: {config.get('rbs_scaling_factor')}")
        
        return data
    else:
        print(f"Error: {response.status_code}")
        print(response.text)
        return None

def test_delete_prediction_config(config_name="test_config"):
    """Test the DELETE /api/prediction-config/{config_name} endpoint to delete a config"""
    print(f"\n=== Testing Delete Prediction Config Endpoint ({config_name}) ===")
    
    response = requests.delete(f"{BASE_URL}/prediction-config/{config_name}")
    
    if response.status_code == 200:
        print(f"Status: {response.status_code} OK")
        data = response.json()
        print(f"Success: {data.get('success', False)}")
        print(f"Message: {data.get('message', '')}")
        return data
    else:
        print(f"Error: {response.status_code}")
        print(response.text)
        return None

def test_rbs_configs_list():
    """Test the GET /api/rbs-configs endpoint to list all RBS configs"""
    print("\n=== Testing RBS Configs List Endpoint ===")
    response = requests.get(f"{BASE_URL}/rbs-configs")
    
    if response.status_code == 200:
        print(f"Status: {response.status_code} OK")
        data = response.json()
        print(f"Success: {data.get('success', False)}")
        
        # Check configs
        configs = data.get('configs', [])
        print(f"RBS Configs Found: {len(configs)}")
        
        if configs:
            print("\nSample RBS Configs:")
            for config in configs[:3]:  # Show first 3 configs
                print(f"\n  - Name: {config.get('config_name')}")
                print(f"    Created At: {config.get('created_at')}")
                print(f"    Updated At: {config.get('updated_at')}")
            
            if len(configs) > 3:
                print("  ...")
        
        return data
    else:
        print(f"Error: {response.status_code}")
        print(response.text)
        return None

def test_create_rbs_config(config_name="test_rbs_config"):
    """Test the POST /api/rbs-config endpoint to create a new RBS config"""
    print(f"\n=== Testing Create RBS Config Endpoint ({config_name}) ===")
    
    # Create a test RBS config with custom values
    config_data = {
        "config_name": config_name,
        "yellow_cards_weight": 0.35,
        "red_cards_weight": 0.55,
        "fouls_committed_weight": 0.15,
        "fouls_drawn_weight": 0.15,
        "penalties_awarded_weight": 0.6,
        "xg_difference_weight": 0.1,
        "possession_percentage_weight": 0.1,
        "confidence_matches_multiplier": 5,
        "max_confidence": 90,
        "min_confidence": 15,
        "confidence_threshold_low": 3,
        "confidence_threshold_medium": 6,
        "confidence_threshold_high": 12
    }
    
    response = requests.post(f"{BASE_URL}/rbs-config", json=config_data)
    
    if response.status_code == 200:
        print(f"Status: {response.status_code} OK")
        data = response.json()
        print(f"Success: {data.get('success', False)}")
        print(f"Message: {data.get('message', '')}")
        
        # Check if config was created
        config = data.get('config', {})
        if config:
            print(f"\nCreated RBS Config: {config.get('config_name')}")
            print(f"Created At: {config.get('created_at')}")
            print(f"Updated At: {config.get('updated_at')}")
            
            # Verify custom values
            print("\nVerifying custom values:")
            print(f"Yellow Cards Weight: {config.get('yellow_cards_weight')} (Expected: 0.35)")
            print(f"Red Cards Weight: {config.get('red_cards_weight')} (Expected: 0.55)")
            print(f"Penalties Awarded Weight: {config.get('penalties_awarded_weight')} (Expected: 0.6)")
        
        return data
    else:
        print(f"Error: {response.status_code}")
        print(response.text)
        return None

def test_get_rbs_config(config_name="test_rbs_config"):
    """Test the GET /api/rbs-config/{config_name} endpoint to retrieve a specific RBS config"""
    print(f"\n=== Testing Get RBS Config Endpoint ({config_name}) ===")
    
    response = requests.get(f"{BASE_URL}/rbs-config/{config_name}")
    
    if response.status_code == 200:
        print(f"Status: {response.status_code} OK")
        data = response.json()
        print(f"Success: {data.get('success', False)}")
        print(f"Message: {data.get('message', '')}")
        
        # Check if config was retrieved
        config = data.get('config', {})
        
        if config:
            print(f"\nRetrieved RBS Config: {config.get('config_name')}")
            print(f"Created At: {config.get('created_at')}")
            print(f"Updated At: {config.get('updated_at')}")
            
            # Verify values
            print("\nVerifying values:")
            print(f"Yellow Cards Weight: {config.get('yellow_cards_weight')}")
            print(f"Red Cards Weight: {config.get('red_cards_weight')}")
            print(f"Penalties Awarded Weight: {config.get('penalties_awarded_weight')}")
        
        return data
    else:
        print(f"Error: {response.status_code}")
        print(response.text)
        return None

def test_delete_rbs_config(config_name="test_rbs_config"):
    """Test the DELETE /api/rbs-config/{config_name} endpoint to delete an RBS config"""
    print(f"\n=== Testing Delete RBS Config Endpoint ({config_name}) ===")
    
    response = requests.delete(f"{BASE_URL}/rbs-config/{config_name}")
    
    if response.status_code == 200:
        print(f"Status: {response.status_code} OK")
        data = response.json()
        print(f"Success: {data.get('success', False)}")
        print(f"Message: {data.get('message', '')}")
        return data
    else:
        print(f"Error: {response.status_code}")
        print(response.text)
        return None

def test_predict_match_with_config(config_name="test_config"):
    """Test the POST /api/predict-match endpoint with a custom config"""
    print(f"\n=== Testing Predict Match with Custom Config ({config_name}) ===")
    
    # Create prediction request with custom config
    prediction_data = {
        "home_team": "Arsenal",
        "away_team": "Chelsea",
        "referee_name": "Michael Oliver",
        "match_date": datetime.now().strftime("%Y-%m-%d"),
        "config_name": config_name
    }
    
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
            
            # Check if custom config was used
            prediction_breakdown = data.get('prediction_breakdown', {})
            config_used = prediction_breakdown.get('config_used', '')
            
            if config_used == config_name:
                print(f"\n✅ Custom config '{config_name}' was used for prediction")
            else:
                print(f"\n❌ Custom config was not used. Config used: '{config_used}'")
        
        return data
    else:
        print(f"Error: {response.status_code}")
        print(response.text)
        return None

def test_predict_match_enhanced_with_config(config_name="test_config"):
    """Test the POST /api/predict-match-enhanced endpoint with a custom config"""
    print(f"\n=== Testing Enhanced Predict Match with Custom Config ({config_name}) ===")
    
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
            
            # Check if custom config was used
            prediction_breakdown = data.get('prediction_breakdown', {})
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
        
        return data
    else:
        print(f"Error: {response.status_code}")
        print(response.text)
        return None

def test_config_persistence():
    """Test that configs persist in MongoDB database"""
    print("\n=== Testing Config Persistence in Database ===")
    
    # Create unique config names with timestamp
    timestamp = int(time.time())
    pred_config_name = f"test_pred_config_{timestamp}"
    rbs_config_name = f"test_rbs_config_{timestamp}"
    
    # Step 1: Create configs
    print("\nStep 1: Creating test configs")
    pred_config = test_create_prediction_config(pred_config_name)
    rbs_config = test_create_rbs_config(rbs_config_name)
    
    if not pred_config or not rbs_config:
        print("❌ Failed to create test configs")
        return False
    
    # Step 2: Verify configs exist in database
    print("\nStep 2: Verifying configs exist in database")
    pred_config_get = test_get_prediction_config(pred_config_name)
    rbs_config_get = test_get_rbs_config(rbs_config_name)
    
    if not pred_config_get or not rbs_config_get:
        print("❌ Failed to retrieve test configs")
        return False
    
    # Step 3: Verify timestamps
    print("\nStep 3: Verifying timestamps")
    pred_created_at = pred_config_get.get('config', {}).get('created_at')
    pred_updated_at = pred_config_get.get('config', {}).get('updated_at')
    rbs_created_at = rbs_config_get.get('config', {}).get('created_at')
    rbs_updated_at = rbs_config_get.get('config', {}).get('updated_at')
    
    if pred_created_at and pred_updated_at:
        print(f"Prediction Config - Created At: {pred_created_at}")
        print(f"Prediction Config - Updated At: {pred_updated_at}")
        print("✅ Prediction config has proper timestamps")
    else:
        print("❌ Prediction config missing timestamps")
    
    if rbs_created_at and rbs_updated_at:
        print(f"RBS Config - Created At: {rbs_created_at}")
        print(f"RBS Config - Updated At: {rbs_updated_at}")
        print("✅ RBS config has proper timestamps")
    else:
        print("❌ RBS config missing timestamps")
    
    # Step 4: Use configs in predictions
    print("\nStep 4: Using configs in predictions")
    pred_result = test_predict_match_with_config(pred_config_name)
    enhanced_result = test_predict_match_enhanced_with_config(pred_config_name)
    
    if not pred_result or not enhanced_result:
        print("❌ Failed to use configs in predictions")
    
    # Step 5: Clean up - delete test configs
    print("\nStep 5: Cleaning up - deleting test configs")
    test_delete_prediction_config(pred_config_name)
    test_delete_rbs_config(rbs_config_name)
    
    # Final verification
    print("\nFinal verification - configs should be deleted")
    pred_config_after = test_get_prediction_config(pred_config_name)
    rbs_config_after = test_get_rbs_config(rbs_config_name)
    
    if pred_config_after and pred_config_after.get('is_default', False):
        print("✅ Prediction config was properly deleted (default returned)")
    else:
        print("❌ Prediction config was not properly deleted")
    
    if rbs_config_after and "not found" in rbs_config_after.get('message', ''):
        print("✅ RBS config was properly deleted (not found message)")
    else:
        print("❌ RBS config was not properly deleted")
    
    return True

def test_config_system_functionality():
    """Test the complete configuration system functionality"""
    print("\n\n========== TESTING CONFIGURATION SYSTEM FUNCTIONALITY ==========\n")
    
    # Step 1: Test listing existing configs
    print("\nStep 1: Testing listing existing configs")
    pred_configs = test_prediction_configs_list()
    rbs_configs = test_rbs_configs_list()
    
    if not pred_configs or not rbs_configs:
        print("❌ Failed to list existing configs")
    else:
        print("✅ Successfully listed existing configs")
    
    # Step 2: Test config CRUD operations
    print("\nStep 2: Testing config CRUD operations")
    timestamp = int(time.time())
    pred_config_name = f"test_pred_config_{timestamp}"
    rbs_config_name = f"test_rbs_config_{timestamp}"
    
    # Create
    pred_create = test_create_prediction_config(pred_config_name)
    rbs_create = test_create_rbs_config(rbs_config_name)
    
    if not pred_create or not rbs_create:
        print("❌ Failed to create configs")
    else:
        print("✅ Successfully created configs")
    
    # Read
    pred_get = test_get_prediction_config(pred_config_name)
    rbs_get = test_get_rbs_config(rbs_config_name)
    
    if not pred_get or not rbs_get:
        print("❌ Failed to retrieve configs")
    else:
        print("✅ Successfully retrieved configs")
    
    # Delete
    pred_delete = test_delete_prediction_config(pred_config_name)
    rbs_delete = test_delete_rbs_config(rbs_config_name)
    
    if not pred_delete or not rbs_delete:
        print("❌ Failed to delete configs")
    else:
        print("✅ Successfully deleted configs")
    
    # Step 3: Test config persistence
    print("\nStep 3: Testing config persistence")
    persistence_result = test_config_persistence()
    
    if persistence_result:
        print("✅ Config persistence test passed")
    else:
        print("❌ Config persistence test failed")
    
    # Step 4: Test config usage in predictions
    print("\nStep 4: Testing config usage in predictions")
    
    # Create a new config for testing predictions
    pred_config_name = f"test_pred_config_{int(time.time())}"
    pred_create = test_create_prediction_config(pred_config_name)
    
    if not pred_create:
        print("❌ Failed to create config for prediction testing")
    else:
        # Test standard prediction with custom config
        standard_pred = test_predict_match_with_config(pred_config_name)
        
        if not standard_pred or not standard_pred.get('success', False):
            print("❌ Failed to use custom config in standard prediction")
        else:
            print("✅ Successfully used custom config in standard prediction")
        
        # Test enhanced prediction with custom config
        enhanced_pred = test_predict_match_enhanced_with_config(pred_config_name)
        
        if not enhanced_pred or not enhanced_pred.get('success', False):
            print("❌ Failed to use custom config in enhanced prediction")
        else:
            print("✅ Successfully used custom config in enhanced prediction")
        
        # Clean up
        test_delete_prediction_config(pred_config_name)
    
    # Final summary
    print("\n========== CONFIGURATION SYSTEM FUNCTIONALITY TEST SUMMARY ==========")
    
    # Check if all endpoints exist and work properly
    endpoint_check_results = []
    
    # Check prediction config endpoints
    pred_list_response = requests.get(f"{BASE_URL}/prediction-configs")
    endpoint_check_results.append(pred_list_response.status_code == 200)
    
    pred_get_response = requests.get(f"{BASE_URL}/prediction-config/default")
    endpoint_check_results.append(pred_get_response.status_code == 200)
    
    # Check RBS config endpoints
    rbs_list_response = requests.get(f"{BASE_URL}/rbs-configs")
    endpoint_check_results.append(rbs_list_response.status_code == 200)
    
    rbs_get_response = requests.get(f"{BASE_URL}/rbs-config/default")
    endpoint_check_results.append(rbs_get_response.status_code == 200)
    
    if all(endpoint_check_results):
        print("✅ All configuration system endpoints exist and are accessible!")
        return True
    else:
        print("❌ Some configuration system endpoints failed the existence check")
        return False

if __name__ == "__main__":
    # Test the complete configuration system functionality
    test_config_system_functionality()