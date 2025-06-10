import requests
import os
import json
import time
from datetime import datetime
from dotenv import load_dotenv
import pprint

# Load environment variables
load_dotenv()

# Get the backend URL from environment
BACKEND_URL = os.environ.get('REACT_APP_BACKEND_URL', 'http://localhost:8001')
BASE_URL = f"{BACKEND_URL}/api"

# Pretty printer for better output formatting
pp = pprint.PrettyPrinter(indent=2)

def test_prediction_config_crud():
    """Test CRUD operations for prediction configs"""
    print("\n=== Testing Prediction Config CRUD Operations ===")
    
    # Step 1: Get all prediction configs (before creating new one)
    print("\nStep 1: Get all prediction configs (before)")
    response = requests.get(f"{BASE_URL}/prediction-configs")
    
    if response.status_code == 200:
        data = response.json()
        print(f"Status: {response.status_code} OK")
        print(f"Success: {data.get('success', False)}")
        
        configs_before = data.get('configs', [])
        print(f"Found {len(configs_before)} prediction configs:")
        for config in configs_before:
            print(f"  - {config.get('config_name')}")
        
        # Check for required configs
        required_configs = ["test_config", "default", "frontend_fixed_test"]
        found_configs = [config.get('config_name') for config in configs_before]
        
        for req_config in required_configs:
            if req_config in found_configs:
                print(f"✅ Required config '{req_config}' exists")
            else:
                print(f"❌ Required config '{req_config}' not found")
    else:
        print(f"Error: {response.status_code}")
        print(response.text)
        configs_before = []
    
    # Step 2: Create a new prediction config
    print("\nStep 2: Create a new prediction config")
    
    # Generate a unique config name with timestamp
    timestamp = int(time.time())
    new_config_name = f"test_config_{timestamp}"
    
    new_config = {
        "config_name": new_config_name,
        "xg_shot_based_weight": 0.45,
        "xg_historical_weight": 0.35,
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
        "max_conversion_rate": 2.1,
        "min_xg_per_match": 0.15,
        "confidence_matches_multiplier": 5,
        "max_confidence": 95,
        "min_confidence": 25
    }
    
    response = requests.post(f"{BASE_URL}/prediction-config", json=new_config)
    
    if response.status_code == 200:
        data = response.json()
        print(f"Status: {response.status_code} OK")
        print(f"Success: {data.get('success', False)}")
        print(f"Message: {data.get('message', '')}")
        
        # Check if config was created with correct values
        created_config = data.get('config', {})
        if created_config:
            print(f"Created config: {created_config.get('config_name')}")
            
            # Verify a few key fields
            print("\nVerifying key fields:")
            print(f"  xg_shot_based_weight: {created_config.get('xg_shot_based_weight')} (expected: 0.45)")
            print(f"  xg_historical_weight: {created_config.get('xg_historical_weight')} (expected: 0.35)")
            print(f"  ppg_adjustment_factor: {created_config.get('ppg_adjustment_factor')} (expected: 0.2)")
            
            # Check timestamps
            created_at = created_config.get('created_at')
            updated_at = created_config.get('updated_at')
            
            print(f"\nCreated at: {created_at}")
            print(f"Updated at: {updated_at}")
            
            if created_at and updated_at:
                print("✅ Timestamps are present")
            else:
                print("❌ Timestamps are missing")
    else:
        print(f"Error: {response.status_code}")
        print(response.text)
        new_config_name = None
    
    # Step 3: Get the newly created config
    if new_config_name:
        print(f"\nStep 3: Get the newly created config '{new_config_name}'")
        
        response = requests.get(f"{BASE_URL}/prediction-config/{new_config_name}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"Status: {response.status_code} OK")
            print(f"Success: {data.get('success', False)}")
            
            config = data.get('config', {})
            if config:
                print(f"Retrieved config: {config.get('config_name')}")
                
                # Verify a few key fields
                print("\nVerifying key fields:")
                print(f"  xg_shot_based_weight: {config.get('xg_shot_based_weight')} (expected: 0.45)")
                print(f"  xg_historical_weight: {config.get('xg_historical_weight')} (expected: 0.35)")
                print(f"  ppg_adjustment_factor: {config.get('ppg_adjustment_factor')} (expected: 0.2)")
                
                # Check if all fields from the original config are present
                missing_fields = []
                for field in new_config:
                    if field not in config:
                        missing_fields.append(field)
                
                if missing_fields:
                    print(f"❌ Missing fields in retrieved config: {', '.join(missing_fields)}")
                else:
                    print("✅ All fields are present in retrieved config")
        else:
            print(f"Error: {response.status_code}")
            print(response.text)
    
    # Step 4: Get all prediction configs (after creating new one)
    print("\nStep 4: Get all prediction configs (after)")
    response = requests.get(f"{BASE_URL}/prediction-configs")
    
    if response.status_code == 200:
        data = response.json()
        print(f"Status: {response.status_code} OK")
        print(f"Success: {data.get('success', False)}")
        
        configs_after = data.get('configs', [])
        print(f"Found {len(configs_after)} prediction configs:")
        
        # Check if the new config is in the list
        if new_config_name:
            found_new_config = False
            for config in configs_after:
                if config.get('config_name') == new_config_name:
                    found_new_config = True
                    break
            
            if found_new_config:
                print(f"✅ Newly created config '{new_config_name}' found in the list")
            else:
                print(f"❌ Newly created config '{new_config_name}' not found in the list")
        
        # Check if the number of configs increased
        if len(configs_after) > len(configs_before):
            print(f"✅ Number of configs increased: {len(configs_before)} -> {len(configs_after)}")
        else:
            print(f"❌ Number of configs did not increase: {len(configs_before)} -> {len(configs_after)}")
    else:
        print(f"Error: {response.status_code}")
        print(response.text)
    
    # Step 5: Delete the newly created config
    if new_config_name:
        print(f"\nStep 5: Delete the newly created config '{new_config_name}'")
        
        response = requests.delete(f"{BASE_URL}/prediction-config/{new_config_name}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"Status: {response.status_code} OK")
            print(f"Success: {data.get('success', False)}")
            print(f"Message: {data.get('message', '')}")
        else:
            print(f"Error: {response.status_code}")
            print(response.text)
        
        # Verify the config was deleted
        response = requests.get(f"{BASE_URL}/prediction-config/{new_config_name}")
        
        if response.status_code == 404 or (response.status_code == 200 and not response.json().get('success', False)):
            print(f"✅ Config '{new_config_name}' was successfully deleted")
        else:
            print(f"❌ Config '{new_config_name}' was not deleted")
    
    # Final summary
    print("\n=== Prediction Config CRUD Operations Summary ===")
    
    # Check if all endpoints exist and work properly
    endpoint_check_results = []
    
    # Check GET /prediction-configs endpoint
    response = requests.get(f"{BASE_URL}/prediction-configs")
    endpoint_check_results.append(response.status_code == 200)
    
    # Check GET /prediction-config/{config_name} endpoint
    response = requests.get(f"{BASE_URL}/prediction-config/default")
    endpoint_check_results.append(response.status_code == 200)
    
    # Check POST /prediction-config endpoint
    test_config = {"config_name": "test_crud_check", "xg_shot_based_weight": 0.4, "xg_historical_weight": 0.4, "xg_opponent_defense_weight": 0.2}
    response = requests.post(f"{BASE_URL}/prediction-config", json=test_config)
    post_success = response.status_code == 200
    endpoint_check_results.append(post_success)
    
    # Check DELETE /prediction-config/{config_name} endpoint
    if post_success:
        response = requests.delete(f"{BASE_URL}/prediction-config/test_crud_check")
        endpoint_check_results.append(response.status_code == 200)
    else:
        endpoint_check_results.append(False)
    
    if all(endpoint_check_results):
        print("✅ All prediction config CRUD endpoints exist and are accessible!")
        return True
    else:
        print("❌ Some prediction config CRUD endpoints failed the existence check")
        return False

def test_rbs_config_crud():
    """Test CRUD operations for RBS configs"""
    print("\n=== Testing RBS Config CRUD Operations ===")
    
    # Step 1: Get all RBS configs (before creating new one)
    print("\nStep 1: Get all RBS configs (before)")
    response = requests.get(f"{BASE_URL}/rbs-configs")
    
    if response.status_code == 200:
        data = response.json()
        print(f"Status: {response.status_code} OK")
        print(f"Success: {data.get('success', False)}")
        
        configs_before = data.get('configs', [])
        print(f"Found {len(configs_before)} RBS configs:")
        for config in configs_before:
            print(f"  - {config.get('config_name')}")
        
        # Check for required configs
        required_configs = ["test_rbs_config", "default", "rbs_fixed_test"]
        found_configs = [config.get('config_name') for config in configs_before]
        
        for req_config in required_configs:
            if req_config in found_configs:
                print(f"✅ Required config '{req_config}' exists")
            else:
                print(f"❌ Required config '{req_config}' not found")
    else:
        print(f"Error: {response.status_code}")
        print(response.text)
        configs_before = []
    
    # Step 2: Create a new RBS config
    print("\nStep 2: Create a new RBS config")
    
    # Generate a unique config name with timestamp
    timestamp = int(time.time())
    new_config_name = f"test_rbs_config_{timestamp}"
    
    new_config = {
        "config_name": new_config_name,
        "yellow_cards_weight": 0.35,
        "red_cards_weight": 0.55,
        "fouls_committed_weight": 0.15,
        "fouls_drawn_weight": 0.15,
        "penalties_awarded_weight": 0.6,
        "xg_difference_weight": 0.1,
        "possession_percentage_weight": 0.1,
        "confidence_matches_multiplier": 5,
        "max_confidence": 98,
        "min_confidence": 15,
        "confidence_threshold_low": 3,
        "confidence_threshold_medium": 6,
        "confidence_threshold_high": 12
    }
    
    response = requests.post(f"{BASE_URL}/rbs-config", json=new_config)
    
    if response.status_code == 200:
        data = response.json()
        print(f"Status: {response.status_code} OK")
        print(f"Success: {data.get('success', False)}")
        print(f"Message: {data.get('message', '')}")
        
        # Check if config was created with correct values
        created_config = data.get('config', {})
        if created_config:
            print(f"Created config: {created_config.get('config_name')}")
            
            # Verify a few key fields
            print("\nVerifying key fields:")
            print(f"  yellow_cards_weight: {created_config.get('yellow_cards_weight')} (expected: 0.35)")
            print(f"  red_cards_weight: {created_config.get('red_cards_weight')} (expected: 0.55)")
            print(f"  penalties_awarded_weight: {created_config.get('penalties_awarded_weight')} (expected: 0.6)")
            
            # Check timestamps
            created_at = created_config.get('created_at')
            updated_at = created_config.get('updated_at')
            
            print(f"\nCreated at: {created_at}")
            print(f"Updated at: {updated_at}")
            
            if created_at and updated_at:
                print("✅ Timestamps are present")
            else:
                print("❌ Timestamps are missing")
    else:
        print(f"Error: {response.status_code}")
        print(response.text)
        new_config_name = None
    
    # Step 3: Get the newly created config
    if new_config_name:
        print(f"\nStep 3: Get the newly created config '{new_config_name}'")
        
        response = requests.get(f"{BASE_URL}/rbs-config/{new_config_name}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"Status: {response.status_code} OK")
            print(f"Success: {data.get('success', False)}")
            
            config = data.get('config', {})
            if config:
                print(f"Retrieved config: {config.get('config_name')}")
                
                # Verify a few key fields
                print("\nVerifying key fields:")
                print(f"  yellow_cards_weight: {config.get('yellow_cards_weight')} (expected: 0.35)")
                print(f"  red_cards_weight: {config.get('red_cards_weight')} (expected: 0.55)")
                print(f"  penalties_awarded_weight: {config.get('penalties_awarded_weight')} (expected: 0.6)")
                
                # Check if all fields from the original config are present
                missing_fields = []
                for field in new_config:
                    if field not in config:
                        missing_fields.append(field)
                
                if missing_fields:
                    print(f"❌ Missing fields in retrieved config: {', '.join(missing_fields)}")
                else:
                    print("✅ All fields are present in retrieved config")
        else:
            print(f"Error: {response.status_code}")
            print(response.text)
    
    # Step 4: Get all RBS configs (after creating new one)
    print("\nStep 4: Get all RBS configs (after)")
    response = requests.get(f"{BASE_URL}/rbs-configs")
    
    if response.status_code == 200:
        data = response.json()
        print(f"Status: {response.status_code} OK")
        print(f"Success: {data.get('success', False)}")
        
        configs_after = data.get('configs', [])
        print(f"Found {len(configs_after)} RBS configs:")
        
        # Check if the new config is in the list
        if new_config_name:
            found_new_config = False
            for config in configs_after:
                if config.get('config_name') == new_config_name:
                    found_new_config = True
                    break
            
            if found_new_config:
                print(f"✅ Newly created config '{new_config_name}' found in the list")
            else:
                print(f"❌ Newly created config '{new_config_name}' not found in the list")
        
        # Check if the number of configs increased
        if len(configs_after) > len(configs_before):
            print(f"✅ Number of configs increased: {len(configs_before)} -> {len(configs_after)}")
        else:
            print(f"❌ Number of configs did not increase: {len(configs_before)} -> {len(configs_after)}")
    else:
        print(f"Error: {response.status_code}")
        print(response.text)
    
    # Step 5: Delete the newly created config
    if new_config_name:
        print(f"\nStep 5: Delete the newly created config '{new_config_name}'")
        
        response = requests.delete(f"{BASE_URL}/rbs-config/{new_config_name}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"Status: {response.status_code} OK")
            print(f"Success: {data.get('success', False)}")
            print(f"Message: {data.get('message', '')}")
        else:
            print(f"Error: {response.status_code}")
            print(response.text)
        
        # Verify the config was deleted
        response = requests.get(f"{BASE_URL}/rbs-config/{new_config_name}")
        
        if response.status_code == 404 or (response.status_code == 200 and not response.json().get('success', False)):
            print(f"✅ Config '{new_config_name}' was successfully deleted")
        else:
            print(f"❌ Config '{new_config_name}' was not deleted")
    
    # Final summary
    print("\n=== RBS Config CRUD Operations Summary ===")
    
    # Check if all endpoints exist and work properly
    endpoint_check_results = []
    
    # Check GET /rbs-configs endpoint
    response = requests.get(f"{BASE_URL}/rbs-configs")
    endpoint_check_results.append(response.status_code == 200)
    
    # Check GET /rbs-config/{config_name} endpoint
    response = requests.get(f"{BASE_URL}/rbs-config/default")
    endpoint_check_results.append(response.status_code == 200)
    
    # Check POST /rbs-config endpoint
    test_config = {"config_name": "test_rbs_crud_check", "yellow_cards_weight": 0.3, "red_cards_weight": 0.5, "fouls_committed_weight": 0.1, "fouls_drawn_weight": 0.1, "penalties_awarded_weight": 0.5}
    response = requests.post(f"{BASE_URL}/rbs-config", json=test_config)
    post_success = response.status_code == 200
    endpoint_check_results.append(post_success)
    
    # Check DELETE /rbs-config/{config_name} endpoint
    if post_success:
        response = requests.delete(f"{BASE_URL}/rbs-config/test_rbs_crud_check")
        endpoint_check_results.append(response.status_code == 200)
    else:
        endpoint_check_results.append(False)
    
    if all(endpoint_check_results):
        print("✅ All RBS config CRUD endpoints exist and are accessible!")
        return True
    else:
        print("❌ Some RBS config CRUD endpoints failed the existence check")
        return False

def test_config_usage_in_predictions():
    """Test using custom configs in predictions"""
    print("\n=== Testing Config Usage in Predictions ===")
    
    # Step 1: Create a custom prediction config with distinctive values
    print("\nStep 1: Create a custom prediction config")
    
    # Generate a unique config name with timestamp
    timestamp = int(time.time())
    custom_config_name = f"test_prediction_usage_{timestamp}"
    
    custom_config = {
        "config_name": custom_config_name,
        "xg_shot_based_weight": 0.6,  # Significantly higher than default (0.4)
        "xg_historical_weight": 0.2,  # Significantly lower than default (0.4)
        "xg_opponent_defense_weight": 0.2,
        "ppg_adjustment_factor": 0.3,  # Higher than default (0.15)
        "possession_adjustment_per_percent": 0.02,  # Higher than default (0.01)
        "fouls_drawn_factor": 0.03,
        "fouls_drawn_baseline": 9.0,
        "fouls_drawn_min_multiplier": 0.7,
        "fouls_drawn_max_multiplier": 1.4,
        "penalty_xg_value": 0.85,
        "rbs_scaling_factor": 0.3,  # Higher than default (0.2)
        "min_conversion_rate": 0.4,
        "max_conversion_rate": 2.2,
        "min_xg_per_match": 0.2,
        "confidence_matches_multiplier": 5,
        "max_confidence": 95,
        "min_confidence": 25
    }
    
    response = requests.post(f"{BASE_URL}/prediction-config", json=custom_config)
    
    if response.status_code == 200:
        data = response.json()
        print(f"Status: {response.status_code} OK")
        print(f"Success: {data.get('success', False)}")
        print(f"Message: {data.get('message', '')}")
        
        # Check if config was created
        if data.get('success', False):
            print(f"✅ Custom prediction config '{custom_config_name}' created successfully")
        else:
            print(f"❌ Failed to create custom prediction config")
            custom_config_name = None
    else:
        print(f"Error: {response.status_code}")
        print(response.text)
        custom_config_name = None
    
    # Step 2: Make a prediction with default config
    print("\nStep 2: Make a prediction with default config")
    
    prediction_request = {
        "home_team": "Arsenal",
        "away_team": "Chelsea",
        "referee_name": "Michael Oliver",
        "match_date": datetime.now().strftime("%Y-%m-%d"),
        "config_name": "default"
    }
    
    response = requests.post(f"{BASE_URL}/predict-match", json=prediction_request)
    
    if response.status_code == 200:
        data = response.json()
        print(f"Status: {response.status_code} OK")
        print(f"Success: {data.get('success', False)}")
        
        if data.get('success', False):
            # Store default prediction results for comparison
            default_prediction = {
                "home_xg": data.get('home_xg'),
                "away_xg": data.get('away_xg'),
                "predicted_home_goals": data.get('predicted_home_goals'),
                "predicted_away_goals": data.get('predicted_away_goals'),
                "home_win_probability": data.get('home_win_probability'),
                "draw_probability": data.get('draw_probability'),
                "away_win_probability": data.get('away_win_probability')
            }
            
            print("\nDefault prediction results:")
            print(f"  Home xG: {default_prediction['home_xg']}")
            print(f"  Away xG: {default_prediction['away_xg']}")
            print(f"  Predicted Home Goals: {default_prediction['predicted_home_goals']}")
            print(f"  Predicted Away Goals: {default_prediction['predicted_away_goals']}")
            print(f"  Home Win Probability: {default_prediction['home_win_probability']}%")
            print(f"  Draw Probability: {default_prediction['draw_probability']}%")
            print(f"  Away Win Probability: {default_prediction['away_win_probability']}%")
            
            # Check if prediction breakdown includes config info
            prediction_breakdown = data.get('prediction_breakdown', {})
            config_used = prediction_breakdown.get('config_used', {})
            
            if config_used:
                print("\nConfig used in prediction:")
                print(f"  Config Name: {config_used.get('config_name')}")
                print(f"  xG Shot-based Weight: {config_used.get('xg_shot_based_weight')}")
                print(f"  xG Historical Weight: {config_used.get('xg_historical_weight')}")
                print(f"  RBS Scaling Factor: {config_used.get('rbs_scaling_factor')}")
                
                if config_used.get('config_name') == 'default':
                    print("✅ Default config was correctly used in prediction")
                else:
                    print(f"❌ Wrong config was used: {config_used.get('config_name')} (expected: default)")
            else:
                print("❌ No config information in prediction breakdown")
                default_prediction = None
        else:
            print(f"❌ Prediction failed: {data.get('error', 'Unknown error')}")
            default_prediction = None
    else:
        print(f"Error: {response.status_code}")
        print(response.text)
        default_prediction = None
    
    # Step 3: Make a prediction with custom config
    if custom_config_name:
        print(f"\nStep 3: Make a prediction with custom config '{custom_config_name}'")
        
        prediction_request = {
            "home_team": "Arsenal",
            "away_team": "Chelsea",
            "referee_name": "Michael Oliver",
            "match_date": datetime.now().strftime("%Y-%m-%d"),
            "config_name": custom_config_name
        }
        
        response = requests.post(f"{BASE_URL}/predict-match", json=prediction_request)
        
        if response.status_code == 200:
            data = response.json()
            print(f"Status: {response.status_code} OK")
            print(f"Success: {data.get('success', False)}")
            
            if data.get('success', False):
                # Store custom prediction results for comparison
                custom_prediction = {
                    "home_xg": data.get('home_xg'),
                    "away_xg": data.get('away_xg'),
                    "predicted_home_goals": data.get('predicted_home_goals'),
                    "predicted_away_goals": data.get('predicted_away_goals'),
                    "home_win_probability": data.get('home_win_probability'),
                    "draw_probability": data.get('draw_probability'),
                    "away_win_probability": data.get('away_win_probability')
                }
                
                print("\nCustom prediction results:")
                print(f"  Home xG: {custom_prediction['home_xg']}")
                print(f"  Away xG: {custom_prediction['away_xg']}")
                print(f"  Predicted Home Goals: {custom_prediction['predicted_home_goals']}")
                print(f"  Predicted Away Goals: {custom_prediction['predicted_away_goals']}")
                print(f"  Home Win Probability: {custom_prediction['home_win_probability']}%")
                print(f"  Draw Probability: {custom_prediction['draw_probability']}%")
                print(f"  Away Win Probability: {custom_prediction['away_win_probability']}%")
                
                # Check if prediction breakdown includes config info
                prediction_breakdown = data.get('prediction_breakdown', {})
                config_used = prediction_breakdown.get('config_used', {})
                
                if config_used:
                    print("\nConfig used in prediction:")
                    print(f"  Config Name: {config_used.get('config_name')}")
                    print(f"  xG Shot-based Weight: {config_used.get('xg_shot_based_weight')}")
                    print(f"  xG Historical Weight: {config_used.get('xg_historical_weight')}")
                    print(f"  RBS Scaling Factor: {config_used.get('rbs_scaling_factor')}")
                    
                    if config_used.get('config_name') == custom_config_name:
                        print(f"✅ Custom config '{custom_config_name}' was correctly used in prediction")
                    else:
                        print(f"❌ Wrong config was used: {config_used.get('config_name')} (expected: {custom_config_name})")
                else:
                    print("❌ No config information in prediction breakdown")
                    custom_prediction = None
            else:
                print(f"❌ Prediction failed: {data.get('error', 'Unknown error')}")
                custom_prediction = None
        else:
            print(f"Error: {response.status_code}")
            print(response.text)
            custom_prediction = None
        
        # Step 4: Compare default and custom predictions
        if default_prediction and custom_prediction:
            print("\nStep 4: Compare default and custom predictions")
            
            # Check if predictions are different
            differences = []
            
            for key in default_prediction:
                default_val = default_prediction[key]
                custom_val = custom_prediction[key]
                
                if isinstance(default_val, (int, float)) and isinstance(custom_val, (int, float)):
                    if abs(default_val - custom_val) > 0.01:  # Allow for small floating-point differences
                        differences.append(key)
            
            if differences:
                print(f"✅ Found differences in {len(differences)} prediction values:")
                for key in differences:
                    print(f"  {key}: {default_prediction[key]} (default) vs {custom_prediction[key]} (custom)")
                print("\nThis confirms that the custom config affected the prediction results.")
            else:
                print("❌ No significant differences found between default and custom predictions.")
                print("This suggests that the custom config did not affect the prediction results.")
        
        # Step 5: Clean up - delete the custom config
        print(f"\nStep 5: Clean up - delete the custom config '{custom_config_name}'")
        
        response = requests.delete(f"{BASE_URL}/prediction-config/{custom_config_name}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"Status: {response.status_code} OK")
            print(f"Success: {data.get('success', False)}")
            print(f"Message: {data.get('message', '')}")
            
            if data.get('success', False):
                print(f"✅ Custom config '{custom_config_name}' deleted successfully")
            else:
                print(f"❌ Failed to delete custom config: {data.get('error', 'Unknown error')}")
        else:
            print(f"Error: {response.status_code}")
            print(response.text)
    
    # Step 6: Test enhanced prediction with custom config
    print("\nStep 6: Test enhanced prediction with custom config")
    
    # Create a new custom config for enhanced prediction
    enhanced_config_name = f"test_enhanced_prediction_{timestamp}"
    
    enhanced_config = {
        "config_name": enhanced_config_name,
        "xg_shot_based_weight": 0.5,
        "xg_historical_weight": 0.3,
        "xg_opponent_defense_weight": 0.2,
        "ppg_adjustment_factor": 0.25,
        "possession_adjustment_per_percent": 0.015,
        "fouls_drawn_factor": 0.025,
        "fouls_drawn_baseline": 9.5,
        "fouls_drawn_min_multiplier": 0.75,
        "fouls_drawn_max_multiplier": 1.35,
        "penalty_xg_value": 0.82,
        "rbs_scaling_factor": 0.28,
        "min_conversion_rate": 0.45,
        "max_conversion_rate": 2.1,
        "min_xg_per_match": 0.18,
        "confidence_matches_multiplier": 4.5,
        "max_confidence": 92,
        "min_confidence": 22
    }
    
    response = requests.post(f"{BASE_URL}/prediction-config", json=enhanced_config)
    
    if response.status_code == 200 and response.json().get('success', False):
        print(f"✅ Created enhanced prediction config '{enhanced_config_name}'")
        
        # Make enhanced prediction with custom config
        enhanced_request = {
            "home_team": "Arsenal",
            "away_team": "Chelsea",
            "referee_name": "Michael Oliver",
            "match_date": datetime.now().strftime("%Y-%m-%d"),
            "config_name": enhanced_config_name,
            "use_time_decay": True,
            "decay_preset": "moderate"
        }
        
        response = requests.post(f"{BASE_URL}/predict-match-enhanced", json=enhanced_request)
        
        if response.status_code == 200:
            data = response.json()
            print(f"Status: {response.status_code} OK")
            print(f"Success: {data.get('success', False)}")
            
            if data.get('success', False):
                print("\nEnhanced prediction results:")
                print(f"  Home xG: {data.get('home_xg')}")
                print(f"  Away xG: {data.get('away_xg')}")
                print(f"  Predicted Home Goals: {data.get('predicted_home_goals')}")
                print(f"  Predicted Away Goals: {data.get('predicted_away_goals')}")
                print(f"  Home Win Probability: {data.get('home_win_probability')}%")
                print(f"  Draw Probability: {data.get('draw_probability')}%")
                print(f"  Away Win Probability: {data.get('away_win_probability')}%")
                
                # Check if prediction breakdown includes config info
                prediction_breakdown = data.get('prediction_breakdown', {})
                config_used = prediction_breakdown.get('config_used', {})
                
                if config_used:
                    print("\nConfig used in enhanced prediction:")
                    print(f"  Config Name: {config_used.get('config_name')}")
                    
                    if config_used.get('config_name') == enhanced_config_name:
                        print(f"✅ Custom config '{enhanced_config_name}' was correctly used in enhanced prediction")
                    else:
                        print(f"❌ Wrong config was used: {config_used.get('config_name')} (expected: {enhanced_config_name})")
                else:
                    print("❌ No config information in enhanced prediction breakdown")
            else:
                print(f"❌ Enhanced prediction failed: {data.get('error', 'Unknown error')}")
        else:
            print(f"Error: {response.status_code}")
            print(response.text)
        
        # Clean up - delete the enhanced config
        response = requests.delete(f"{BASE_URL}/prediction-config/{enhanced_config_name}")
        if response.status_code == 200 and response.json().get('success', False):
            print(f"✅ Deleted enhanced prediction config '{enhanced_config_name}'")
        else:
            print(f"❌ Failed to delete enhanced prediction config '{enhanced_config_name}'")
    else:
        print(f"❌ Failed to create enhanced prediction config")
    
    # Final summary
    print("\n=== Config Usage in Predictions Summary ===")
    
    # Check if all endpoints exist and work properly
    endpoint_check_results = []
    
    # Check POST /predict-match endpoint with config_name parameter
    test_request = {
        "home_team": "Arsenal",
        "away_team": "Chelsea",
        "referee_name": "Michael Oliver",
        "config_name": "default"
    }
    response = requests.post(f"{BASE_URL}/predict-match", json=test_request)
    endpoint_check_results.append(response.status_code == 200)
    
    # Check POST /predict-match-enhanced endpoint with config_name parameter
    test_request = {
        "home_team": "Arsenal",
        "away_team": "Chelsea",
        "referee_name": "Michael Oliver",
        "config_name": "default",
        "use_time_decay": True,
        "decay_preset": "moderate"
    }
    response = requests.post(f"{BASE_URL}/predict-match-enhanced", json=test_request)
    endpoint_check_results.append(response.status_code == 200)
    
    if all(endpoint_check_results):
        print("✅ All prediction endpoints with config parameters exist and are accessible!")
        return True
    else:
        print("❌ Some prediction endpoints with config parameters failed the existence check")
        return False

def test_config_validation():
    """Test config validation to ensure it prevents invalid data"""
    print("\n=== Testing Config Validation ===")
    
    # Step 1: Test prediction config validation - xG weights must sum to 1.0
    print("\nStep 1: Test prediction config validation - xG weights must sum to 1.0")
    
    invalid_config = {
        "config_name": "invalid_prediction_config",
        "xg_shot_based_weight": 0.5,
        "xg_historical_weight": 0.4,
        "xg_opponent_defense_weight": 0.3,  # Total sum is 1.2, should be rejected
        "ppg_adjustment_factor": 0.15,
        "possession_adjustment_per_percent": 0.01,
        "fouls_drawn_factor": 0.02,
        "fouls_drawn_baseline": 10.0,
        "fouls_drawn_min_multiplier": 0.8,
        "fouls_drawn_max_multiplier": 1.3,
        "penalty_xg_value": 0.79,
        "rbs_scaling_factor": 0.2,
        "min_conversion_rate": 0.5,
        "max_conversion_rate": 2.0,
        "min_xg_per_match": 0.1,
        "confidence_matches_multiplier": 4,
        "max_confidence": 90,
        "min_confidence": 20
    }
    
    response = requests.post(f"{BASE_URL}/prediction-config", json=invalid_config)
    
    if response.status_code == 422:
        print(f"✅ Validation correctly rejected config with xG weights sum = 1.2 (status code: {response.status_code})")
        print(f"Error message: {response.json().get('detail', 'No error message')}")
    elif response.status_code == 200 and not response.json().get('success', False):
        print(f"✅ Validation correctly rejected config with xG weights sum = 1.2 (success: false)")
        print(f"Error message: {response.json().get('error', 'No error message')}")
    else:
        print(f"❌ Validation failed to reject invalid config with xG weights sum = 1.2")
        print(f"Status: {response.status_code}")
        print(response.text)
    
    # Step 2: Test RBS config validation - at least one weight must be positive
    print("\nStep 2: Test RBS config validation - at least one weight must be positive")
    
    invalid_rbs_config = {
        "config_name": "invalid_rbs_config",
        "yellow_cards_weight": 0.0,
        "red_cards_weight": 0.0,
        "fouls_committed_weight": 0.0,
        "fouls_drawn_weight": 0.0,
        "penalties_awarded_weight": 0.0,  # All weights are 0, should be rejected
        "xg_difference_weight": 0.0,
        "possession_percentage_weight": 0.0,
        "confidence_matches_multiplier": 4,
        "max_confidence": 95,
        "min_confidence": 10,
        "confidence_threshold_low": 2,
        "confidence_threshold_medium": 5,
        "confidence_threshold_high": 10
    }
    
    response = requests.post(f"{BASE_URL}/rbs-config", json=invalid_rbs_config)
    
    if response.status_code == 422:
        print(f"✅ Validation correctly rejected RBS config with all zero weights (status code: {response.status_code})")
        print(f"Error message: {response.json().get('detail', 'No error message')}")
    elif response.status_code == 200 and not response.json().get('success', False):
        print(f"✅ Validation correctly rejected RBS config with all zero weights (success: false)")
        print(f"Error message: {response.json().get('error', 'No error message')}")
    else:
        print(f"❌ Validation failed to reject invalid RBS config with all zero weights")
        print(f"Status: {response.status_code}")
        print(response.text)
    
    # Step 3: Test prediction config validation - min/max conversion rate validation
    print("\nStep 3: Test prediction config validation - min/max conversion rate validation")
    
    invalid_conversion_config = {
        "config_name": "invalid_conversion_config",
        "xg_shot_based_weight": 0.4,
        "xg_historical_weight": 0.4,
        "xg_opponent_defense_weight": 0.2,
        "ppg_adjustment_factor": 0.15,
        "possession_adjustment_per_percent": 0.01,
        "fouls_drawn_factor": 0.02,
        "fouls_drawn_baseline": 10.0,
        "fouls_drawn_min_multiplier": 0.8,
        "fouls_drawn_max_multiplier": 1.3,
        "penalty_xg_value": 0.79,
        "rbs_scaling_factor": 0.2,
        "min_conversion_rate": 2.5,  # Min is greater than max, should be rejected
        "max_conversion_rate": 2.0,
        "min_xg_per_match": 0.1,
        "confidence_matches_multiplier": 4,
        "max_confidence": 90,
        "min_confidence": 20
    }
    
    response = requests.post(f"{BASE_URL}/prediction-config", json=invalid_conversion_config)
    
    if response.status_code == 422:
        print(f"✅ Validation correctly rejected config with min > max conversion rate (status code: {response.status_code})")
        print(f"Error message: {response.json().get('detail', 'No error message')}")
    elif response.status_code == 200 and not response.json().get('success', False):
        print(f"✅ Validation correctly rejected config with min > max conversion rate (success: false)")
        print(f"Error message: {response.json().get('error', 'No error message')}")
    else:
        print(f"❌ Validation failed to reject invalid config with min > max conversion rate")
        print(f"Status: {response.status_code}")
        print(response.text)
    
    # Step 4: Test RBS config validation - confidence thresholds validation
    print("\nStep 4: Test RBS config validation - confidence thresholds validation")
    
    invalid_threshold_config = {
        "config_name": "invalid_threshold_config",
        "yellow_cards_weight": 0.3,
        "red_cards_weight": 0.5,
        "fouls_committed_weight": 0.1,
        "fouls_drawn_weight": 0.1,
        "penalties_awarded_weight": 0.5,
        "xg_difference_weight": 0.0,
        "possession_percentage_weight": 0.0,
        "confidence_matches_multiplier": 4,
        "max_confidence": 95,
        "min_confidence": 10,
        "confidence_threshold_low": 8,  # Low threshold > medium threshold, should be rejected
        "confidence_threshold_medium": 5,
        "confidence_threshold_high": 10
    }
    
    response = requests.post(f"{BASE_URL}/rbs-config", json=invalid_threshold_config)
    
    if response.status_code == 422:
        print(f"✅ Validation correctly rejected RBS config with invalid thresholds (status code: {response.status_code})")
        print(f"Error message: {response.json().get('detail', 'No error message')}")
    elif response.status_code == 200 and not response.json().get('success', False):
        print(f"✅ Validation correctly rejected RBS config with invalid thresholds (success: false)")
        print(f"Error message: {response.json().get('error', 'No error message')}")
    else:
        print(f"❌ Validation failed to reject invalid RBS config with invalid thresholds")
        print(f"Status: {response.status_code}")
        print(response.text)
    
    # Final summary
    print("\n=== Config Validation Summary ===")
    
    # Check if validation is working for both config types
    validation_check_results = []
    
    # Check prediction config validation
    invalid_prediction = {
        "config_name": "validation_test",
        "xg_shot_based_weight": 0.5,
        "xg_historical_weight": 0.6,  # Sum > 1.0
        "xg_opponent_defense_weight": 0.2
    }
    response = requests.post(f"{BASE_URL}/prediction-config", json=invalid_prediction)
    validation_check_results.append(
        response.status_code == 422 or 
        (response.status_code == 200 and not response.json().get('success', False))
    )
    
    # Check RBS config validation
    invalid_rbs = {
        "config_name": "validation_test",
        "yellow_cards_weight": 0.0,
        "red_cards_weight": 0.0,
        "fouls_committed_weight": 0.0,
        "fouls_drawn_weight": 0.0,
        "penalties_awarded_weight": 0.0  # All weights are 0
    }
    response = requests.post(f"{BASE_URL}/rbs-config", json=invalid_rbs)
    validation_check_results.append(
        response.status_code == 422 or 
        (response.status_code == 200 and not response.json().get('success', False))
    )
    
    if all(validation_check_results):
        print("✅ Config validation is working correctly for both prediction and RBS configs!")
        return True
    else:
        print("❌ Config validation is not working correctly for all config types")
        return False

def test_time_decay_presets():
    """Test time decay presets endpoint"""
    print("\n=== Testing Time Decay Presets ===")
    
    response = requests.get(f"{BASE_URL}/time-decay/presets")
    
    if response.status_code == 200:
        data = response.json()
        print(f"Status: {response.status_code} OK")
        print(f"Success: {data.get('success', False)}")
        
        presets = data.get('presets', [])
        print(f"Found {len(presets)} time decay presets:")
        
        # Check for required presets
        required_presets = ["aggressive", "moderate", "conservative", "linear", "none"]
        found_presets = [preset.get('preset_name') for preset in presets]
        
        for req_preset in required_presets:
            if req_preset in found_presets:
                print(f"✅ Required preset '{req_preset}' exists")
            else:
                print(f"❌ Required preset '{req_preset}' not found")
        
        # Check preset details
        for preset in presets:
            preset_name = preset.get('preset_name')
            decay_type = preset.get('decay_type')
            description = preset.get('description')
            
            print(f"\nPreset: {preset_name}")
            print(f"  Decay Type: {decay_type}")
            print(f"  Description: {description}")
            
            # Check specific parameters based on decay type
            if decay_type == "exponential":
                half_life = preset.get('half_life_months')
                print(f"  Half-life (months): {half_life}")
                
                # Verify half-life values for specific presets
                if preset_name == "aggressive" and half_life == 2.0:
                    print("  ✅ Aggressive preset has correct half-life (2 months)")
                elif preset_name == "moderate" and half_life == 4.0:
                    print("  ✅ Moderate preset has correct half-life (4 months)")
                elif preset_name == "conservative" and half_life == 8.0:
                    print("  ✅ Conservative preset has correct half-life (8 months)")
            elif decay_type == "linear":
                decay_rate = preset.get('decay_rate_per_month')
                print(f"  Decay Rate (per month): {decay_rate}")
                
                # Verify decay rate for linear preset
                if preset_name == "linear" and decay_rate == 0.1:
                    print("  ✅ Linear preset has correct decay rate (10% per month)")
            elif decay_type == "step":
                cutoff = preset.get('cutoff_months')
                print(f"  Cutoff (months): {cutoff}")
                
                # Verify none preset has no cutoff
                if preset_name == "none" and cutoff is None:
                    print("  ✅ None preset has correct cutoff (None)")
        
        return True
    else:
        print(f"Error: {response.status_code}")
        print(response.text)
        return False

def test_formations_endpoint():
    """Test formations endpoint"""
    print("\n=== Testing Formations Endpoint ===")
    
    response = requests.get(f"{BASE_URL}/formations")
    
    if response.status_code == 200:
        data = response.json()
        print(f"Status: {response.status_code} OK")
        print(f"Success: {data.get('success', False)}")
        
        formations = data.get('formations', [])
        print(f"Found {len(formations)} formations:")
        for formation in formations:
            print(f"  - {formation}")
        
        # Check for required formations
        required_formations = ["4-4-2", "4-3-3", "3-5-2", "4-5-1", "3-4-3"]
        
        for req_formation in required_formations:
            if req_formation in formations:
                print(f"✅ Required formation '{req_formation}' exists")
            else:
                print(f"❌ Required formation '{req_formation}' not found")
        
        return True
    else:
        print(f"Error: {response.status_code}")
        print(response.text)
        return False

def run_all_tests():
    """Run all configuration system tests"""
    print("\n\n========== TESTING COMPLETE CONFIGURATION SYSTEM ==========\n")
    
    # Test 1: Prediction Config CRUD Operations
    print("\n----- Test 1: Prediction Config CRUD Operations -----")
    prediction_config_result = test_prediction_config_crud()
    
    # Test 2: RBS Config CRUD Operations
    print("\n----- Test 2: RBS Config CRUD Operations -----")
    rbs_config_result = test_rbs_config_crud()
    
    # Test 3: Config Usage in Predictions
    print("\n----- Test 3: Config Usage in Predictions -----")
    config_usage_result = test_config_usage_in_predictions()
    
    # Test 4: Config Validation
    print("\n----- Test 4: Config Validation -----")
    config_validation_result = test_config_validation()
    
    # Test 5: Time Decay Presets
    print("\n----- Test 5: Time Decay Presets -----")
    time_decay_result = test_time_decay_presets()
    
    # Test 6: Formations Endpoint
    print("\n----- Test 6: Formations Endpoint -----")
    formations_result = test_formations_endpoint()
    
    # Final summary
    print("\n\n========== CONFIGURATION SYSTEM TEST SUMMARY ==========\n")
    
    test_results = {
        "Prediction Config CRUD Operations": prediction_config_result,
        "RBS Config CRUD Operations": rbs_config_result,
        "Config Usage in Predictions": config_usage_result,
        "Config Validation": config_validation_result,
        "Time Decay Presets": time_decay_result,
        "Formations Endpoint": formations_result
    }
    
    all_passed = all(test_results.values())
    
    print("Test Results:")
    for test_name, result in test_results.items():
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"  {test_name}: {status}")
    
    print("\nOverall Result:")
    if all_passed:
        print("✅ ALL TESTS PASSED - Configuration system is working correctly!")
    else:
        print("❌ SOME TESTS FAILED - Configuration system has issues that need to be addressed.")
    
    return all_passed

if __name__ == "__main__":
    run_all_tests()
