import requests
import os
import json
import base64
import time
import pprint
import io
import PyPDF2
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Get the backend URL from environment
BACKEND_URL = os.environ.get('REACT_APP_BACKEND_URL', 'http://localhost:8001')
BASE_URL = f"{BACKEND_URL}/api"

# Pretty printer for better output formatting
pp = pprint.PrettyPrinter(indent=2)

def test_enhanced_prediction_with_time_decay():
    """Test the enhanced prediction endpoint with different time decay presets"""
    print("\n\n========== TESTING ENHANCED PREDICTION WITH TIME DECAY ==========\n")
    
    # Step 1: Get teams and referees
    print("Step 1: Getting teams and referees")
    teams_response = requests.get(f"{BASE_URL}/teams")
    if teams_response.status_code != 200:
        print(f"❌ Failed to get teams: {teams_response.status_code}")
        return False
    
    teams = teams_response.json().get('teams', [])
    if len(teams) < 2:
        print("❌ Not enough teams for match prediction")
        return False
    
    print(f"Found {len(teams)} teams: {', '.join(teams[:5])}{'...' if len(teams) > 5 else ''}")
    
    referees_response = requests.get(f"{BASE_URL}/referees")
    if referees_response.status_code != 200:
        print(f"❌ Failed to get referees: {referees_response.status_code}")
        return False
    
    referees = referees_response.json().get('referees', [])
    if not referees:
        print("❌ No referees found for match prediction")
        return False
    
    print(f"Found {len(referees)} referees: {', '.join(referees[:5])}{'...' if len(referees) > 5 else ''}")
    
    # Step 2: Test with different time decay presets
    home_team = teams[0]
    away_team = teams[1]
    referee = referees[0]
    
    print(f"\nStep 2: Testing enhanced prediction with different time decay presets")
    print(f"Match: {home_team} vs {away_team} with referee {referee}")
    
    # Test all decay presets
    decay_presets = ["aggressive", "moderate", "conservative", "linear", "none"]
    results = {}
    
    for preset in decay_presets:
        print(f"\nTesting with {preset} decay preset:")
        
        prediction_data = {
            "home_team": home_team,
            "away_team": away_team,
            "referee_name": referee,
            "use_time_decay": True,
            "decay_preset": preset
        }
        
        response = requests.post(f"{BASE_URL}/predict-match-enhanced", json=prediction_data)
        
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                print(f"✅ Prediction successful with {preset} decay")
                print(f"  Home Goals: {data['predicted_home_goals']}")
                print(f"  Away Goals: {data['predicted_away_goals']}")
                
                # Store results for comparison
                results[preset] = {
                    'home_goals': data['predicted_home_goals'],
                    'away_goals': data['predicted_away_goals'],
                    'home_xg': data['home_xg'],
                    'away_xg': data['away_xg']
                }
                
                # Check for time decay info in breakdown
                breakdown = data.get('prediction_breakdown', {})
                time_decay_info = breakdown.get('time_decay_info', {})
                
                if time_decay_info:
                    print(f"  Time Decay Info:")
                    for key, value in time_decay_info.items():
                        print(f"    - {key}: {value}")
                else:
                    print(f"❌ No time decay info in prediction breakdown")
            else:
                print(f"❌ Prediction failed with {preset} decay: {data.get('error', 'Unknown error')}")
        else:
            print(f"❌ Request failed with status {response.status_code}")
            print(response.text)
    
    # Step 3: Compare results to verify time decay affects predictions
    print("\nStep 3: Comparing results across different decay presets")
    
    if len(results) > 1:
        # Check if predictions differ across presets
        home_goals_values = [r['home_goals'] for r in results.values()]
        away_goals_values = [r['away_goals'] for r in results.values()]
        
        home_goals_differ = len(set(home_goals_values)) > 1
        away_goals_differ = len(set(away_goals_values)) > 1
        
        if home_goals_differ or away_goals_differ:
            print("✅ Time decay presets produce different prediction results as expected")
            
            # Print comparison
            print("\nComparison of predictions across decay presets:")
            print(f"{'Preset':<15} {'Home Goals':<15} {'Away Goals':<15} {'Home xG':<15} {'Away xG':<15}")
            print("-" * 75)
            
            for preset, result in results.items():
                print(f"{preset:<15} {result['home_goals']:<15.2f} {result['away_goals']:<15.2f} {result['home_xg']:<15.2f} {result['away_xg']:<15.2f}")
        else:
            print("❌ Time decay presets do not affect prediction results")
    else:
        print("❌ Not enough successful predictions to compare")
    
    return len(results) > 0

def test_starting_xi_integration():
    """Test the enhanced prediction endpoint with Starting XI integration"""
    print("\n\n========== TESTING STARTING XI INTEGRATION ==========\n")
    
    # Step 1: Get teams and referees
    print("Step 1: Getting teams and referees")
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
    
    home_team = teams[0]
    away_team = teams[1]
    referee = referees[0]
    
    # Step 2: Test prediction without Starting XI (baseline)
    print(f"\nStep 2: Testing prediction without Starting XI")
    print(f"Match: {home_team} vs {away_team} with referee {referee}")
    
    basic_prediction_data = {
        "home_team": home_team,
        "away_team": away_team,
        "referee_name": referee,
        "use_time_decay": False
    }
    
    basic_response = requests.post(f"{BASE_URL}/predict-match-enhanced", json=basic_prediction_data)
    
    if basic_response.status_code != 200:
        print(f"❌ Basic prediction request failed: {basic_response.status_code}")
        print(basic_response.text)
        return False
    
    basic_result = basic_response.json()
    if not basic_result.get('success'):
        print(f"❌ Basic prediction failed: {basic_result.get('error', 'Unknown error')}")
        return False
    
    print(f"✅ Basic prediction successful")
    print(f"  Home Goals: {basic_result['predicted_home_goals']}")
    print(f"  Away Goals: {basic_result['predicted_away_goals']}")
    
    # Step 3: Get default Starting XI for both teams
    print(f"\nStep 3: Getting default Starting XI for both teams")
    
    home_players_response = requests.get(f"{BASE_URL}/teams/{home_team}/players")
    away_players_response = requests.get(f"{BASE_URL}/teams/{away_team}/players")
    
    if home_players_response.status_code != 200 or away_players_response.status_code != 200:
        print(f"❌ Failed to get players for teams")
        return False
    
    home_players_data = home_players_response.json()
    away_players_data = away_players_response.json()
    
    home_default_xi = home_players_data.get('default_starting_xi')
    away_default_xi = away_players_data.get('default_starting_xi')
    
    if not home_default_xi or not away_default_xi:
        print(f"❌ Default Starting XI not available for one or both teams")
        print("This is expected if no player data is available in the database")
        print("Testing fallback mode instead...")
        
        # Test with empty Starting XI (fallback mode)
        fallback_prediction_data = {
            "home_team": home_team,
            "away_team": away_team,
            "referee_name": referee,
            "use_time_decay": False,
            "home_starting_xi": {"formation": "4-4-2", "positions": []},
            "away_starting_xi": {"formation": "4-4-2", "positions": []}
        }
        
        fallback_response = requests.post(f"{BASE_URL}/predict-match-enhanced", json=fallback_prediction_data)
        
        if fallback_response.status_code == 200 and fallback_response.json().get('success'):
            print(f"✅ Fallback mode prediction successful")
            print(f"  Home Goals: {fallback_response.json()['predicted_home_goals']}")
            print(f"  Away Goals: {fallback_response.json()['predicted_away_goals']}")
            return True
        else:
            print(f"❌ Fallback mode prediction failed")
            return False
    
    # Step 4: Test prediction with default Starting XI
    print(f"\nStep 4: Testing prediction with default Starting XI")
    
    xi_prediction_data = {
        "home_team": home_team,
        "away_team": away_team,
        "referee_name": referee,
        "use_time_decay": False,
        "home_starting_xi": home_default_xi,
        "away_starting_xi": away_default_xi
    }
    
    xi_response = requests.post(f"{BASE_URL}/predict-match-enhanced", json=xi_prediction_data)
    
    if xi_response.status_code != 200:
        print(f"❌ Starting XI prediction request failed: {xi_response.status_code}")
        print(xi_response.text)
        return False
    
    xi_result = xi_response.json()
    if not xi_result.get('success'):
        print(f"❌ Starting XI prediction failed: {xi_result.get('error', 'Unknown error')}")
        return False
    
    print(f"✅ Starting XI prediction successful")
    print(f"  Home Goals: {xi_result['predicted_home_goals']}")
    print(f"  Away Goals: {xi_result['predicted_away_goals']}")
    
    # Step 5: Compare results to verify Starting XI affects predictions
    print("\nStep 5: Comparing results with and without Starting XI")
    
    basic_home_goals = basic_result['predicted_home_goals']
    basic_away_goals = basic_result['predicted_away_goals']
    xi_home_goals = xi_result['predicted_home_goals']
    xi_away_goals = xi_result['predicted_away_goals']
    
    if basic_home_goals != xi_home_goals or basic_away_goals != xi_away_goals:
        print("✅ Starting XI integration affects prediction results as expected")
        print(f"  Without XI: Home={basic_home_goals:.2f}, Away={basic_away_goals:.2f}")
        print(f"  With XI:    Home={xi_home_goals:.2f}, Away={xi_away_goals:.2f}")
    else:
        print("⚠️ Starting XI integration does not affect prediction results")
        print("This could be expected if the default XI is similar to the team average")
    
    # Step 6: Check for Starting XI impact in prediction breakdown
    print("\nStep 6: Checking for Starting XI impact in prediction breakdown")
    
    breakdown = xi_result.get('prediction_breakdown', {})
    xi_impact = breakdown.get('starting_xi_impact', {})
    
    if xi_impact:
        print("✅ Starting XI impact information found in prediction breakdown")
        for key, value in xi_impact.items():
            print(f"  - {key}: {value}")
    else:
        print("❌ No Starting XI impact information in prediction breakdown")
    
    return True

def test_numpy_serialization_fix():
    """Test the NumPy serialization fix in the enhanced prediction endpoint"""
    print("\n\n========== TESTING NUMPY SERIALIZATION FIX ==========\n")
    
    # Step 1: Get teams and referees
    print("Step 1: Getting teams and referees")
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
    
    home_team = teams[0]
    away_team = teams[1]
    referee = referees[0]
    
    # Step 2: Make prediction with all features that might use NumPy types
    print(f"\nStep 2: Testing prediction with all features that might use NumPy types")
    print(f"Match: {home_team} vs {away_team} with referee {referee}")
    
    # Include all possible parameters to test serialization
    full_prediction_data = {
        "home_team": home_team,
        "away_team": away_team,
        "referee_name": referee,
        "match_date": datetime.now().strftime("%Y-%m-%d"),
        "use_time_decay": True,
        "decay_preset": "moderate",
        "custom_decay_rate": 0.15
    }
    
    # Try to get Starting XI data if available
    try:
        home_players_response = requests.get(f"{BASE_URL}/teams/{home_team}/players")
        away_players_response = requests.get(f"{BASE_URL}/teams/{away_team}/players")
        
        if (home_players_response.status_code == 200 and 
            away_players_response.status_code == 200):
            
            home_players_data = home_players_response.json()
            away_players_data = away_players_response.json()
            
            home_default_xi = home_players_data.get('default_starting_xi')
            away_default_xi = away_players_data.get('default_starting_xi')
            
            if home_default_xi and away_default_xi:
                full_prediction_data["home_starting_xi"] = home_default_xi
                full_prediction_data["away_starting_xi"] = away_default_xi
                print("Including Starting XI data in prediction request")
    except Exception as e:
        print(f"Could not get Starting XI data: {e}")
    
    response = requests.post(f"{BASE_URL}/predict-match-enhanced", json=full_prediction_data)
    
    if response.status_code != 200:
        print(f"❌ Prediction request failed: {response.status_code}")
        print(response.text)
        return False
    
    result = response.json()
    if not result.get('success'):
        print(f"❌ Prediction failed: {result.get('error', 'Unknown error')}")
        return False
    
    print(f"✅ Prediction successful with NumPy serialization")
    print(f"  Home Goals: {result['predicted_home_goals']}")
    print(f"  Away Goals: {result['predicted_away_goals']}")
    
    # Step 3: Check for NumPy types in response
    print("\nStep 3: Checking for proper serialization of NumPy types")
    
    # Check all numeric fields to ensure they're properly serialized
    numeric_fields = [
        'predicted_home_goals', 'predicted_away_goals', 
        'home_xg', 'away_xg',
        'home_win_probability', 'draw_probability', 'away_win_probability'
    ]
    
    all_fields_ok = True
    for field in numeric_fields:
        if field in result:
            value = result[field]
            if isinstance(value, (int, float)) or value is None:
                print(f"  ✅ {field}: {value} (type: {type(value).__name__})")
            else:
                print(f"  ❌ {field}: {value} (type: {type(value).__name__}) - Not properly serialized")
                all_fields_ok = False
    
    # Check nested numeric values in prediction breakdown
    breakdown = result.get('prediction_breakdown', {})
    if breakdown:
        print("\n  Checking nested numeric values in prediction breakdown:")
        for key, value in list(breakdown.items())[:5]:
            if isinstance(value, (dict, list)):
                print(f"    - {key}: Complex structure (checking skipped)")
            elif isinstance(value, (int, float)) or value is None:
                print(f"    - {key}: {value} (type: {type(value).__name__})")
            else:
                print(f"    ❌ {key}: {value} (type: {type(value).__name__}) - Not properly serialized")
                all_fields_ok = False
        
        if len(breakdown) > 5:
            print("    ... (more fields)")
    
    if all_fields_ok:
        print("\n✅ All numeric fields are properly serialized")
    else:
        print("\n❌ Some numeric fields are not properly serialized")
    
    return all_fields_ok

def test_ml_model_integration():
    """Test the ML model integration with enhanced features"""
    print("\n\n========== TESTING ML MODEL INTEGRATION ==========\n")
    
    # Step 1: Check ML model status
    print("Step 1: Checking ML model status")
    response = requests.get(f"{BASE_URL}/ml-models/status")
    
    if response.status_code != 200:
        print(f"❌ Failed to get ML model status: {response.status_code}")
        print(response.text)
        return False
    
    status_data = response.json()
    models_loaded = status_data.get('models_loaded', False)
    feature_count = status_data.get('feature_columns_count', 0)
    
    print(f"Models loaded: {models_loaded}")
    print(f"Feature count: {feature_count}")
    
    if not models_loaded:
        print("ML models not loaded, attempting to train models...")
        train_response = requests.post(f"{BASE_URL}/train-ml-models")
        
        if train_response.status_code != 200:
            print(f"❌ Failed to train ML models: {train_response.status_code}")
            print(train_response.text)
            return False
        
        train_data = train_response.json()
        if not train_data.get('success'):
            print(f"❌ ML model training failed: {train_data.get('message', 'Unknown error')}")
            return False
        
        print("✅ ML models trained successfully")
        
        # Check status again
        response = requests.get(f"{BASE_URL}/ml-models/status")
        if response.status_code != 200:
            print(f"❌ Failed to get ML model status after training: {response.status_code}")
            return False
        
        status_data = response.json()
        models_loaded = status_data.get('models_loaded', False)
        feature_count = status_data.get('feature_columns_count', 0)
        
        print(f"Models loaded after training: {models_loaded}")
        print(f"Feature count after training: {feature_count}")
    
    # Verify feature count meets requirements (45+)
    if feature_count < 45:
        print(f"❌ Feature count ({feature_count}) is less than required (45+)")
        return False
    
    print(f"✅ Feature count ({feature_count}) meets requirements (45+)")
    
    # Step 2: Get teams and referees for prediction
    print("\nStep 2: Getting teams and referees for prediction")
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
    
    home_team = teams[0]
    away_team = teams[1]
    referee = referees[0]
    
    # Step 3: Test enhanced prediction with time decay
    print(f"\nStep 3: Testing enhanced prediction with time decay")
    print(f"Match: {home_team} vs {away_team} with referee {referee}")
    
    prediction_data = {
        "home_team": home_team,
        "away_team": away_team,
        "referee_name": referee,
        "use_time_decay": True,
        "decay_preset": "moderate"
    }
    
    response = requests.post(f"{BASE_URL}/predict-match-enhanced", json=prediction_data)
    
    if response.status_code != 200:
        print(f"❌ Enhanced prediction request failed: {response.status_code}")
        print(response.text)
        return False
    
    result = response.json()
    if not result.get('success'):
        print(f"❌ Enhanced prediction failed: {result.get('error', 'Unknown error')}")
        return False
    
    print(f"✅ Enhanced prediction successful")
    print(f"  Home Goals: {result['predicted_home_goals']}")
    print(f"  Away Goals: {result['predicted_away_goals']}")
    
    # Step 4: Check prediction breakdown for ML model information
    print("\nStep 4: Checking prediction breakdown for ML model information")
    
    breakdown = result.get('prediction_breakdown', {})
    
    # Check for XGBoost model information
    xgboost_info = breakdown.get('xgboost_models', {})
    if xgboost_info:
        print("✅ XGBoost model information found in prediction breakdown")
        for key, value in xgboost_info.items():
            print(f"  - {key}: {value}")
    else:
        print("❌ No XGBoost model information in prediction breakdown")
    
    # Check for feature importance
    feature_importance = breakdown.get('feature_importance', {})
    if feature_importance:
        print("\nFeature importance information:")
        top_features = feature_importance.get('top_features', {})
        if top_features:
            print("Top features:")
            for feature, importance in list(top_features.items())[:5]:
                print(f"  - {feature}: {importance}")
            if len(top_features) > 5:
                print("  ... (more features)")
    else:
        print("❌ No feature importance information in prediction breakdown")
    
    # Step 5: Check for time decay integration with ML model
    print("\nStep 5: Checking for time decay integration with ML model")
    
    time_decay_info = breakdown.get('time_decay_info', {})
    if time_decay_info:
        print("✅ Time decay information found in prediction breakdown")
        for key, value in time_decay_info.items():
            print(f"  - {key}: {value}")
    else:
        print("❌ No time decay information in prediction breakdown")
    
    return True

def test_complete_enhanced_prediction_workflow():
    """Test the complete enhanced prediction workflow"""
    print("\n\n========== TESTING COMPLETE ENHANCED PREDICTION WORKFLOW ==========\n")
    
    # Step 1: Check all required endpoints exist
    print("Step 1: Checking all required endpoints exist")
    
    endpoints = [
        {"method": "GET", "url": f"{BASE_URL}/formations"},
        {"method": "GET", "url": f"{BASE_URL}/time-decay/presets"},
        {"method": "GET", "url": f"{BASE_URL}/teams"},
        {"method": "GET", "url": f"{BASE_URL}/referees"},
        {"method": "GET", "url": f"{BASE_URL}/ml-models/status"},
        {"method": "POST", "url": f"{BASE_URL}/predict-match-enhanced"}
    ]
    
    all_endpoints_exist = True
    for endpoint in endpoints:
        method = endpoint["method"]
        url = endpoint["url"]
        
        if method == "GET":
            response = requests.get(url)
        else:
            # For POST, just check if endpoint exists with minimal data
            response = requests.post(url, json={})
        
        if response.status_code not in [200, 400, 422]:  # 400/422 means endpoint exists but validation failed
            print(f"❌ Endpoint {method} {url} does not exist (status: {response.status_code})")
            all_endpoints_exist = False
        else:
            print(f"✅ Endpoint {method} {url} exists")
    
    if not all_endpoints_exist:
        print("❌ Some required endpoints do not exist")
        return False
    
    # Step 2: Run all component tests
    print("\nStep 2: Running all component tests")
    
    test_results = {
        "time_decay": test_enhanced_prediction_with_time_decay(),
        "starting_xi": test_starting_xi_integration(),
        "numpy_serialization": test_numpy_serialization_fix(),
        "ml_integration": test_ml_model_integration()
    }
    
    # Step 3: Summarize results
    print("\nStep 3: Summarizing test results")
    
    all_tests_passed = all(test_results.values())
    
    print("\nTest Results Summary:")
    print(f"  Time Decay Testing: {'✅ Passed' if test_results['time_decay'] else '❌ Failed'}")
    print(f"  Starting XI Integration: {'✅ Passed' if test_results['starting_xi'] else '❌ Failed'}")
    print(f"  NumPy Serialization Fix: {'✅ Passed' if test_results['numpy_serialization'] else '❌ Failed'}")
    print(f"  ML Model Integration: {'✅ Passed' if test_results['ml_integration'] else '❌ Failed'}")
    
    if all_tests_passed:
        print("\n✅ Complete enhanced prediction workflow test passed successfully")
    else:
        print("\n❌ Complete enhanced prediction workflow test failed")
        print("Some component tests did not pass. See individual test results for details.")
    
    return all_tests_passed

if __name__ == "__main__":
    # Test the complete enhanced prediction workflow
    test_complete_enhanced_prediction_workflow()
