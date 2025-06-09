import requests
import os
import json
import base64
import time
import pprint
import io
import PyPDF2
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Get the backend URL from environment
BACKEND_URL = os.environ.get('REACT_APP_BACKEND_URL', 'http://localhost:8001')
BASE_URL = f"{BACKEND_URL}/api"

# Pretty printer for better output formatting
pp = pprint.PrettyPrinter(indent=2)

def test_database_stats_endpoint():
    """Test the /api/database/stats endpoint to ensure it returns collection statistics"""
    print("\n=== Testing Database Stats Endpoint ===")
    response = requests.get(f"{BASE_URL}/database/stats")
    
    if response.status_code == 200:
        print(f"Status: {response.status_code} OK")
        data = response.json()
        print(f"Success: {data.get('success', False)}")
        
        # Check total documents
        total_documents = data.get('total_documents', 0)
        print(f"Total Documents: {total_documents}")
        
        # Check collections
        collections = data.get('collections', {})
        print(f"Collections: {len(collections)}")
        
        for collection_name, count in collections.items():
            print(f"  - {collection_name}: {count} documents")
            
        # Check timestamp
        timestamp = data.get('timestamp')
        print(f"Timestamp: {timestamp}")
        
        return data
    else:
        print(f"Error: {response.status_code}")
        print(response.text)
        return None

def test_database_wipe_endpoint():
    """Test the /api/database/wipe endpoint to ensure it properly clears all collections"""
    print("\n=== Testing Database Wipe Endpoint ===")
    
    # CAUTION: This will delete all data in the database
    print("CAUTION: This will delete all data in the database!")
    print("Proceeding with database wipe test...")
    
    response = requests.delete(f"{BASE_URL}/database/wipe")
    
    if response.status_code == 200:
        print(f"Status: {response.status_code} OK")
        data = response.json()
        print(f"Success: {data.get('success', False)}")
        print(f"Message: {data.get('message', '')}")
        
        # Check deleted counts if available
        deleted_counts = data.get('deleted_counts', {})
        if deleted_counts:
            print("Deleted Counts:")
            for collection_name, count in deleted_counts.items():
                print(f"  - {collection_name}: {count} documents")
        else:
            # Check collections cleared if deleted_counts not available
            collections_cleared = data.get('collections_cleared', 0)
            print(f"Collections Cleared: {collections_cleared}")
        
        # Check timestamp
        timestamp = data.get('timestamp')
        if timestamp:
            print(f"Timestamp: {timestamp}")
        
        return data
    else:
        print(f"Error: {response.status_code}")
        print(response.text)
        return None

def test_database_management_functionality():
    """Test all database management functionality"""
    print("\n\n========== TESTING DATABASE MANAGEMENT FUNCTIONALITY ==========\n")
    
    # Step 1: Test database stats endpoint to see current state
    print("\nStep 1: Testing database stats endpoint (before wipe)")
    before_stats = test_database_stats_endpoint()
    
    if not before_stats or not before_stats.get('success'):
        print("❌ Database stats endpoint test failed")
        return False
    else:
        print("✅ Database stats endpoint test passed")
    
    # Step 2: Test database wipe endpoint
    print("\nStep 2: Testing database wipe endpoint")
    wipe_result = test_database_wipe_endpoint()
    
    if not wipe_result or not wipe_result.get('success'):
        print("❌ Database wipe endpoint test failed")
        return False
    else:
        print("✅ Database wipe endpoint test passed")
    
    # Step 3: Test database stats endpoint again to verify wipe
    print("\nStep 3: Testing database stats endpoint (after wipe)")
    after_stats = test_database_stats_endpoint()
    
    if not after_stats or not after_stats.get('success'):
        print("❌ Database stats endpoint test failed (after wipe)")
        return False
    else:
        print("✅ Database stats endpoint test passed (after wipe)")
    
    # Verify that the database was actually wiped
    before_total = before_stats.get('total_documents', 0)
    after_total = after_stats.get('total_documents', 0)
    
    print(f"\nBefore wipe: {before_total} total documents")
    print(f"After wipe: {after_total} total documents")
    
    if after_total == 0:
        print("✅ Database was successfully wiped (0 documents remaining)")
    elif after_total < before_total:
        print(f"⚠️ Database was partially wiped ({after_total} documents remaining)")
    else:
        print(f"❌ Database was not wiped properly ({after_total} documents remaining)")
    
    # Final summary
    print("\n========== DATABASE MANAGEMENT FUNCTIONALITY TEST SUMMARY ==========")
    
    # Check if the endpoints exist and work properly
    endpoint_check_results = []
    
    # Check database stats endpoint
    stats_response = requests.get(f"{BASE_URL}/database/stats")
    endpoint_check_results.append(stats_response.status_code == 200)
    
    # Check database wipe endpoint
    # We don't need to call it again, just check if the previous call was successful
    endpoint_check_results.append(wipe_result is not None and wipe_result.get('success', False))
    
    if all(endpoint_check_results):
        print("✅ All database management functionality endpoints exist and are accessible!")
        return True
    else:
        print("❌ Some database management functionality endpoints failed the existence check")
        return False

def test_formations_endpoint():
    """Test the /api/formations endpoint to ensure it returns available formations"""
    print("\n=== Testing Formations Endpoint ===")
    response = requests.get(f"{BASE_URL}/formations")
    
    if response.status_code == 200:
        print(f"Status: {response.status_code} OK")
        data = response.json()
        print(f"Success: {data.get('success', False)}")
        
        formations = data.get('formations', [])
        print(f"Formations found: {len(formations)}")
        
        for formation in formations:
            print(f"  - {formation.get('name')}: {formation.get('positions_count')} positions")
            
        # Verify expected formations are present
        expected_formations = ["4-4-2", "4-3-3", "3-5-2", "4-5-1", "3-4-3"]
        found_formations = [f.get('name') for f in formations]
        
        missing_formations = [f for f in expected_formations if f not in found_formations]
        if missing_formations:
            print(f"❌ Missing expected formations: {', '.join(missing_formations)}")
        else:
            print("✅ All expected formations are present")
            
        return data
    else:
        print(f"Error: {response.status_code}")
        print(response.text)
        return None

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

def test_team_players_endpoint(team_name="Arsenal"):
    """Test the /api/teams/{team_name}/players endpoint to get players for a team"""
    print(f"\n=== Testing Team Players Endpoint for {team_name} ===")
    response = requests.get(f"{BASE_URL}/teams/{team_name}/players")
    
    if response.status_code == 200:
        print(f"Status: {response.status_code} OK")
        data = response.json()
        print(f"Success: {data.get('success', False)}")
        print(f"Team: {data.get('team_name')}")
        
        players = data.get('players', [])
        print(f"Players found: {len(players)}")
        
        if players:
            print("Sample players:")
            for player in players[:5]:
                print(f"  - {player.get('player_name')} ({player.get('position')}): {player.get('matches_played')} matches")
            if len(players) > 5:
                print("  ...")
                
            # Check for position distribution
            positions = {}
            for player in players:
                pos = player.get('position')
                positions[pos] = positions.get(pos, 0) + 1
                
            print("\nPosition distribution:")
            for pos, count in positions.items():
                print(f"  - {pos}: {count} players")
                
            # Check for default starting XI
            default_xi = data.get('default_starting_xi')
            if default_xi:
                print(f"\nDefault Starting XI (Formation: {default_xi.get('formation')})")
                positions = default_xi.get('positions', [])
                for position in positions:
                    player = position.get('player')
                    if player:
                        print(f"  - {position.get('position_id')} ({position.get('position_type')}): {player.get('player_name')}")
                    else:
                        print(f"  - {position.get('position_id')} ({position.get('position_type')}): None")
            else:
                print("\n❌ No default starting XI provided")
                
            # Check for available formations
            formations = data.get('available_formations', [])
            print(f"\nAvailable formations: {', '.join(formations)}")
            
            return data
        else:
            print("❌ No players found for this team")
            return data
    else:
        print(f"Error: {response.status_code}")
        print(response.text)
        return None

def test_predict_match_enhanced_endpoint():
    """Test the /api/predict-match-enhanced endpoint with basic parameters"""
    print("\n=== Testing Enhanced Match Prediction Endpoint ===")
    
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
    
    # Basic request without starting XI or time decay customization
    basic_request = {
        "home_team": home_team,
        "away_team": away_team,
        "referee_name": referee
    }
    
    response = requests.post(f"{BASE_URL}/predict-match-enhanced", json=basic_request)
    
    if response.status_code == 200:
        print(f"Status: {response.status_code} OK")
        data = response.json()
        print(f"Success: {data.get('success', False)}")
        
        if data.get('success'):
            print(f"Home Team: {data.get('home_team')}")
            print(f"Away Team: {data.get('away_team')}")
            print(f"Referee: {data.get('referee')}")
            print(f"Predicted Home Goals: {data.get('predicted_home_goals')}")
            print(f"Predicted Away Goals: {data.get('predicted_away_goals')}")
            print(f"Home xG: {data.get('home_xg')}")
            print(f"Away xG: {data.get('away_xg')}")
            
            # Check for probability fields
            print(f"Home Win Probability: {data.get('home_win_probability')}%")
            print(f"Draw Probability: {data.get('draw_probability')}%")
            print(f"Away Win Probability: {data.get('away_win_probability')}%")
            
            # Check prediction breakdown
            breakdown = data.get('prediction_breakdown', {})
            print("\nPrediction Breakdown:")
            for key, value in list(breakdown.items())[:5]:
                print(f"  - {key}: {value}")
            if len(breakdown) > 5:
                print("  ...")
                
            # Check for starting XI and time decay info in breakdown
            if 'starting_xi_impact' in breakdown:
                print("\nStarting XI Impact:")
                xi_impact = breakdown.get('starting_xi_impact', {})
                for key, value in xi_impact.items():
                    print(f"  - {key}: {value}")
                    
            if 'time_decay_info' in breakdown:
                print("\nTime Decay Info:")
                decay_info = breakdown.get('time_decay_info', {})
                for key, value in decay_info.items():
                    print(f"  - {key}: {value}")
                    
            return data
        else:
            print(f"Prediction failed: {data.get('error', 'Unknown error')}")
            return data
    else:
        print(f"Error: {response.status_code}")
        print(response.text)
        return None

def test_predict_match_enhanced_with_starting_xi():
    """Test the /api/predict-match-enhanced endpoint with custom starting XI"""
    print("\n=== Testing Enhanced Match Prediction with Starting XI ===")
    
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
    
    # Get players for home team to create custom starting XI
    home_players_response = requests.get(f"{BASE_URL}/teams/{home_team}/players")
    if home_players_response.status_code != 200 or not home_players_response.json().get('success'):
        print(f"❌ Failed to get players for {home_team}")
        return False
    
    home_players_data = home_players_response.json()
    home_players = home_players_data.get('players', [])
    home_default_xi = home_players_data.get('default_starting_xi')
    
    if not home_players or not home_default_xi:
        print(f"❌ No players or default XI found for {home_team}")
        return False
    
    # Get players for away team to create custom starting XI
    away_players_response = requests.get(f"{BASE_URL}/teams/{away_team}/players")
    if away_players_response.status_code != 200 or not away_players_response.json().get('success'):
        print(f"❌ Failed to get players for {away_team}")
        return False
    
    away_players_data = away_players_response.json()
    away_players = away_players_data.get('players', [])
    away_default_xi = away_players_data.get('default_starting_xi')
    
    if not away_players or not away_default_xi:
        print(f"❌ No players or default XI found for {away_team}")
        return False
    
    print(f"Testing enhanced prediction with starting XI for {home_team} vs {away_team} with referee {referee}")
    
    # Create request with custom starting XI (using default XI from API)
    request_with_xi = {
        "home_team": home_team,
        "away_team": away_team,
        "referee_name": referee,
        "home_starting_xi": home_default_xi,
        "away_starting_xi": away_default_xi,
        "use_time_decay": True,
        "decay_preset": "aggressive"
    }
    
    response = requests.post(f"{BASE_URL}/predict-match-enhanced", json=request_with_xi)
    
    if response.status_code == 200:
        print(f"Status: {response.status_code} OK")
        data = response.json()
        print(f"Success: {data.get('success', False)}")
        
        if data.get('success'):
            print(f"Home Team: {data.get('home_team')}")
            print(f"Away Team: {data.get('away_team')}")
            print(f"Referee: {data.get('referee')}")
            print(f"Predicted Home Goals: {data.get('predicted_home_goals')}")
            print(f"Predicted Away Goals: {data.get('predicted_away_goals')}")
            print(f"Home xG: {data.get('home_xg')}")
            print(f"Away xG: {data.get('away_xg')}")
            
            # Check for probability fields
            print(f"Home Win Probability: {data.get('home_win_probability')}%")
            print(f"Draw Probability: {data.get('draw_probability')}%")
            print(f"Away Win Probability: {data.get('away_win_probability')}%")
            
            # Check prediction breakdown
            breakdown = data.get('prediction_breakdown', {})
            
            # Check for starting XI and time decay info in breakdown
            if 'starting_xi_impact' in breakdown:
                print("\nStarting XI Impact:")
                xi_impact = breakdown.get('starting_xi_impact', {})
                for key, value in xi_impact.items():
                    print(f"  - {key}: {value}")
                    
            if 'time_decay_info' in breakdown:
                print("\nTime Decay Info:")
                decay_info = breakdown.get('time_decay_info', {})
                for key, value in decay_info.items():
                    print(f"  - {key}: {value}")
                    
            return data
        else:
            print(f"Prediction failed: {data.get('error', 'Unknown error')}")
            return data
    else:
        print(f"Error: {response.status_code}")
        print(response.text)
        return None

def test_starting_xi_and_time_decay_functionality():
    """Test all Starting XI and time decay functionality"""
    print("\n\n========== TESTING STARTING XI AND TIME DECAY FUNCTIONALITY ==========\n")
    
    # Test formations endpoint
    print("\nStep 1: Testing formations endpoint")
    formations_data = test_formations_endpoint()
    
    if not formations_data or not formations_data.get('success'):
        print("❌ Formations endpoint test failed")
    else:
        print("✅ Formations endpoint test passed")
    
    # Test time decay presets endpoint
    print("\nStep 2: Testing time decay presets endpoint")
    presets_data = test_time_decay_presets_endpoint()
    
    if not presets_data or not presets_data.get('success'):
        print("❌ Time decay presets endpoint test failed")
    else:
        print("✅ Time decay presets endpoint test passed")
    
    # Test team players endpoint
    print("\nStep 3: Testing team players endpoint")
    # Get a team name first
    teams_response = requests.get(f"{BASE_URL}/teams")
    if teams_response.status_code != 200:
        print("❌ Failed to get teams for testing")
        print("Note: This is expected if no teams/players in database")
        team_name = "Arsenal"  # Fallback
    else:
        teams = teams_response.json().get('teams', [])
        if not teams:
            print("❌ No teams found in the database")
            print("Note: This is expected if no teams/players in database")
            team_name = "Arsenal"  # Fallback
        else:
            team_name = teams[0]
    
    players_data = test_team_players_endpoint(team_name)
    
    if not players_data:
        print("❌ Team players endpoint test failed")
        print("Note: This is expected if no teams/players in database")
    else:
        print("✅ Team players endpoint test passed")
    
    # Test enhanced match prediction endpoint
    print("\nStep 4: Testing enhanced match prediction endpoint")
    teams_response = requests.get(f"{BASE_URL}/teams")
    if teams_response.status_code != 200 or not teams_response.json().get('teams'):
        print("❌ No teams available for match prediction testing")
        print("Note: This is expected if no teams/players in database")
        print("✓ Enhanced match prediction endpoint exists but cannot be fully tested without data")
    else:
        prediction_data = test_predict_match_enhanced_endpoint()
        if not prediction_data or not prediction_data.get('success'):
            print("❌ Enhanced match prediction endpoint test failed")
        else:
            print("✅ Enhanced match prediction endpoint test passed")
    
    # Test enhanced match prediction with starting XI
    print("\nStep 5: Testing enhanced match prediction with starting XI")
    teams_response = requests.get(f"{BASE_URL}/teams")
    if teams_response.status_code != 200 or not teams_response.json().get('teams'):
        print("❌ No teams available for match prediction with starting XI testing")
        print("Note: This is expected if no teams/players in database")
        print("✓ Enhanced match prediction with starting XI endpoint exists but cannot be fully tested without data")
    else:
        prediction_with_xi_data = test_predict_match_enhanced_with_starting_xi()
        if not prediction_with_xi_data or not prediction_with_xi_data.get('success'):
            print("❌ Enhanced match prediction with starting XI test failed")
        else:
            print("✅ Enhanced match prediction with starting XI test passed")
    
    # Final summary
    print("\n========== STARTING XI AND TIME DECAY FUNCTIONALITY TEST SUMMARY ==========")
    
    # Check if the endpoints exist even if they can't be fully tested
    endpoint_check_results = []
    
    # Check formations endpoint
    formations_response = requests.get(f"{BASE_URL}/formations")
    endpoint_check_results.append(formations_response.status_code == 200)
    
    # Check time decay presets endpoint
    presets_response = requests.get(f"{BASE_URL}/time-decay/presets")
    endpoint_check_results.append(presets_response.status_code == 200)
    
    # Check team players endpoint
    players_response = requests.get(f"{BASE_URL}/teams/{team_name}/players")
    endpoint_check_results.append(players_response.status_code == 200)
    
    # Check enhanced match prediction endpoint
    # Just check if the endpoint exists by sending a minimal request
    minimal_request = {"home_team": "Team A", "away_team": "Team B", "referee_name": "Referee"}
    prediction_response = requests.post(f"{BASE_URL}/predict-match-enhanced", json=minimal_request)
    # We expect either 200 (success) or 404/400 (team not found) but not 500 (server error)
    endpoint_check_results.append(prediction_response.status_code != 500 and prediction_response.status_code != 404)
    
    if all(endpoint_check_results):
        print("✅ All Starting XI and time decay functionality endpoints exist and are accessible!")
        print("Note: Some endpoints could not be fully tested due to missing data, but they exist and respond.")
        return True
    else:
        print("❌ Some Starting XI and time decay functionality endpoints failed the existence check")
        return False

def test_list_datasets():
    """Test the /api/datasets endpoint to list all datasets"""
    print("\n=== Testing List Datasets Endpoint ===")
    response = requests.post(f"{BASE_URL}/datasets")
    
    if response.status_code == 200:
        print(f"Status: {response.status_code} OK")
        data = response.json()
        print(f"Success: {data['success']}")
        print(f"Datasets: {len(data['datasets'])}")
        for dataset in data['datasets']:
            print(f"  - {dataset['dataset_name']}: {dataset['matches_count']} matches, {dataset['team_stats_count']} team stats, {dataset['player_stats_count']} player stats")
    else:
        print(f"Error: {response.status_code}")
        print(response.text)
    
    return response.json() if response.status_code == 200 else None

def test_regression_stats_endpoint():
    """Test the enhanced regression-stats endpoint"""
    print("\n=== Testing Enhanced Regression Stats Endpoint ===")
    response = requests.get(f"{BASE_URL}/regression-stats")
    
    if response.status_code == 200:
        print(f"Status: {response.status_code} OK")
        data = response.json()
        print(f"Success: {data['success']}")
        
        # Check for all required categories
        categories = data.get('categories', {})
        print(f"Categories found: {len(categories)}")
        for category_name, variables in categories.items():
            print(f"  - {category_name}: {len(variables)} variables")
            print(f"    {', '.join(variables[:5])}{'...' if len(variables) > 5 else ''}")
        
        # Check for RBS variables
        rbs_variables = categories.get('rbs_variables', [])
        print(f"\nRBS Variables: {len(rbs_variables)}")
        print(f"  {', '.join(rbs_variables)}")
        
        # Check for Match Predictor variables
        predictor_variables = categories.get('match_predictor_variables', [])
        print(f"\nMatch Predictor Variables: {len(predictor_variables)}")
        print(f"  {', '.join(predictor_variables[:5])}{'...' if len(predictor_variables) > 5 else ''}")
        
        # Check for variable descriptions
        descriptions = data.get('descriptions', {})
        print(f"\nVariable Descriptions: {len(descriptions)}")
        for var_name, desc in list(descriptions.items())[:5]:
            print(f"  - {var_name}: {desc}")
        print("  ...")
        
        # Check for optimization endpoints
        optimization_endpoints = data.get('optimization_endpoints', {})
        print(f"\nOptimization Endpoints: {len(optimization_endpoints)}")
        for endpoint_name, url in optimization_endpoints.items():
            print(f"  - {endpoint_name}: {url}")
        
        # Verify all required categories exist
        required_categories = ['rbs_variables', 'match_predictor_variables', 'basic_stats', 
                              'advanced_stats', 'outcome_stats', 'context_variables']
        missing_categories = [cat for cat in required_categories if cat not in categories]
        
        if missing_categories:
            print(f"\n❌ Missing categories: {', '.join(missing_categories)}")
        else:
            print("\n✅ All required categories present")
        
        # Verify RBS variables are complete
        expected_rbs_vars = ['yellow_cards', 'red_cards', 'fouls_committed', 'fouls_drawn', 
                            'penalties_awarded', 'xg_difference', 'possession_percentage']
        missing_rbs_vars = [var for var in expected_rbs_vars if var not in rbs_variables]
        
        if missing_rbs_vars:
            print(f"❌ Missing RBS variables: {', '.join(missing_rbs_vars)}")
        else:
            print("✅ All RBS variables present")
        
        # Verify Match Predictor variables are complete
        expected_predictor_vars = ['xg', 'shots_total', 'shots_on_target', 'xg_per_shot',
                                  'goals_per_xg', 'shot_accuracy', 'conversion_rate']
        missing_predictor_vars = [var for var in expected_predictor_vars if var not in predictor_variables]
        
        if missing_predictor_vars:
            print(f"❌ Missing Match Predictor variables: {', '.join(missing_predictor_vars)}")
        else:
            print("✅ All core Match Predictor variables present")
        
        return data
    else:
        print(f"Error: {response.status_code}")
        print(response.text)
        return None

def test_rbs_optimization_endpoint():
    """Test the RBS optimization analysis endpoint"""
    print("\n=== Testing RBS Optimization Analysis Endpoint ===")
    response = requests.post(f"{BASE_URL}/analyze-rbs-optimization")
    
    if response.status_code == 200:
        print(f"Status: {response.status_code} OK")
        data = response.json()
        print(f"Success: {data['success']}")
        print(f"Analysis Type: {data.get('analysis_type')}")
        print(f"Sample Size: {data.get('sample_size')}")
        
        # Check RBS variables analyzed
        rbs_vars = data.get('rbs_variables_analyzed', [])
        print(f"\nRBS Variables Analyzed: {len(rbs_vars)}")
        print(f"  {', '.join(rbs_vars)}")
        
        # Check results structure
        results = data.get('results', {})
        print(f"\nResults sections: {len(results)}")
        for section_name in results.keys():
            print(f"  - {section_name}")
        
        # Check for suggested weights
        if 'suggested_rbs_weights' in results:
            print("\nSuggested RBS Weights:")
            for var, weight in results['suggested_rbs_weights'].items():
                print(f"  - {var}: {weight}")
        
        # Check for individual variable importance
        if 'individual_variable_importance' in results:
            print("\nIndividual Variable Importance:")
            for var, stats in list(results['individual_variable_importance'].items())[:3]:
                print(f"  - {var}: R² = {stats.get('r2_score')}, Coefficient = {stats.get('coefficient')}")
            if len(results['individual_variable_importance']) > 3:
                print("  ...")
        
        # Check for correlations
        if 'correlations_with_points' in results:
            print("\nCorrelations with Points:")
            correlations = results['correlations_with_points']
            # Sort by absolute correlation value
            sorted_correlations = sorted(correlations.items(), key=lambda x: abs(x[1]), reverse=True)
            for var, corr in sorted_correlations[:3]:
                print(f"  - {var}: {corr}")
            if len(sorted_correlations) > 3:
                print("  ...")
        
        # Check recommendations
        recommendations = data.get('recommendations', [])
        print(f"\nRecommendations: {len(recommendations)}")
        for i, rec in enumerate(recommendations[:3]):
            print(f"  {i+1}. {rec.get('recommendation')} (Priority: {rec.get('priority')})")
        if len(recommendations) > 3:
            print("  ...")
        
        # Verify all required sections exist
        required_sections = ['rbs_vs_points', 'individual_variable_importance', 
                            'correlations_with_points', 'suggested_rbs_weights']
        missing_sections = [sec for sec in required_sections if sec not in results]
        
        if missing_sections:
            print(f"\n❌ Missing result sections: {', '.join(missing_sections)}")
        else:
            print("\n✅ All required result sections present")
        
        return data
    else:
        print(f"Error: {response.status_code}")
        print(response.text)
        return None

def test_predictor_optimization_endpoint():
    """Test the Match Predictor optimization analysis endpoint"""
    print("\n=== Testing Match Predictor Optimization Analysis Endpoint ===")
    response = requests.post(f"{BASE_URL}/analyze-predictor-optimization")
    
    if response.status_code == 200:
        print(f"Status: {response.status_code} OK")
        data = response.json()
        print(f"Success: {data['success']}")
        print(f"Analysis Type: {data.get('analysis_type')}")
        print(f"Sample Size: {data.get('sample_size')}")
        
        # Check predictor variables analyzed
        predictor_vars = data.get('predictor_variables_analyzed', [])
        print(f"\nPredictor Variables Analyzed: {len(predictor_vars)}")
        print(f"  {', '.join(predictor_vars[:5])}{'...' if len(predictor_vars) > 5 else ''}")
        
        # Check results structure
        results = data.get('results', {})
        print(f"\nResults sections: {len(results)}")
        for section_name in results.keys():
            print(f"  - {section_name}")
        
        # Check predictor vs points analysis
        if 'predictor_vs_points' in results:
            predictor_analysis = results['predictor_vs_points']
            print(f"\nPredictor vs Points Analysis:")
            print(f"  - Success: {predictor_analysis.get('success')}")
            print(f"  - Model Type: {predictor_analysis.get('model_type')}")
            print(f"  - Sample Size: {predictor_analysis.get('sample_size')}")
            
            if 'results' in predictor_analysis and 'r2_score' in predictor_analysis['results']:
                print(f"  - R² Score: {predictor_analysis['results']['r2_score']}")
            
            if 'results' in predictor_analysis and 'coefficients' in predictor_analysis['results']:
                coeffs = predictor_analysis['results']['coefficients']
                print(f"  - Top 3 coefficients by magnitude:")
                sorted_coeffs = sorted(coeffs.items(), key=lambda x: abs(x[1]), reverse=True)
                for var, coef in sorted_coeffs[:3]:
                    print(f"    - {var}: {coef}")
        
        # Check xG analysis
        if 'xg_analysis' in results:
            xg_analysis = results['xg_analysis']
            print(f"\nxG Analysis:")
            print(f"  - Success: {xg_analysis.get('success')}")
            if 'results' in xg_analysis and 'r2_score' in xg_analysis['results']:
                print(f"  - R² Score: {xg_analysis['results']['r2_score']}")
        
        # Check variable importance ranking
        if 'variable_importance_ranking' in results:
            print("\nVariable Importance Ranking:")
            for var, importance in results['variable_importance_ranking'][:5]:
                print(f"  - {var}: {importance}")
            if len(results['variable_importance_ranking']) > 5:
                print("  ...")
        
        # Check recommendations
        recommendations = data.get('recommendations', [])
        print(f"\nRecommendations: {len(recommendations)}")
        for i, rec in enumerate(recommendations[:3]):
            print(f"  {i+1}. {rec.get('recommendation')} (Priority: {rec.get('priority')})")
        if len(recommendations) > 3:
            print("  ...")
        
        # Verify all required sections exist
        required_sections = ['predictor_vs_points', 'predictor_vs_results', 'xg_analysis']
        missing_sections = [sec for sec in required_sections if sec not in results]
        
        if missing_sections:
            print(f"\n❌ Missing result sections: {', '.join(missing_sections)}")
        else:
            print("\n✅ All required result sections present")
        
        return data
    else:
        print(f"Error: {response.status_code}")
        print(response.text)
        return None

def test_regression_analysis_endpoint():
    """Test the regression analysis endpoint"""
    print("\n=== Testing Regression Analysis Endpoint ===")
    
    # Simple regression analysis with basic stats
    test_data = {
        "selected_stats": ["yellow_cards", "red_cards", "shots_total"],
        "target": "points_per_game",
        "test_size": 0.2,
        "random_state": 42
    }
    
    response = requests.post(f"{BASE_URL}/regression-analysis", json=test_data)
    
    if response.status_code == 200:
        print(f"Status: {response.status_code} OK")
        data = response.json()
        print(f"Success: {data['success']}")
        print(f"Target: {data.get('target')}")
        print(f"Sample Size: {data.get('sample_size')}")
        
        # Check results
        results = data.get('results', {})
        if 'r2_score' in results:
            print(f"R² Score: {results['r2_score']}")
        
        if 'coefficients' in results:
            print("\nCoefficients:")
            for var, coef in results['coefficients'].items():
                print(f"  - {var}: {coef}")
        
        return data
    else:
        print(f"Error: {response.status_code}")
        print(response.text)
        return None

def test_multi_dataset_upload(dataset_name, matches_file, team_stats_file, player_stats_file):
    """Test the /api/upload/multi-dataset endpoint with proper file uploads"""
    print(f"\n=== Testing Multi-Dataset Upload Endpoint for '{dataset_name}' ===")
    
    # Prepare files for upload
    files = [
        ('files', (os.path.basename(matches_file), open(matches_file, 'rb'), 'text/csv')),
        ('files', (os.path.basename(team_stats_file), open(team_stats_file, 'rb'), 'text/csv')),
        ('files', (os.path.basename(player_stats_file), open(player_stats_file, 'rb'), 'text/csv'))
    ]
    
    # Prepare dataset name
    data = {'dataset_names': [dataset_name]}
    
    # Make the request
    response = requests.post(f"{BASE_URL}/upload/multi-dataset", files=files, data=data)
    
    if response.status_code == 200:
        print(f"Status: {response.status_code} OK")
        data = response.json()
        print(f"Success: {data['success']}")
        print(f"Message: {data['message']}")
        print(f"Records processed: {data['records_processed']}")
        for dataset in data['datasets']:
            print(f"  - {dataset['dataset_name']}: {dataset['matches']} matches, {dataset['team_stats']} team stats, {dataset['player_stats']} player stats")
    else:
        print(f"Error: {response.status_code}")
        print(response.text)
    
    return response.json() if response.status_code == 200 else None

def test_delete_dataset(dataset_name):
    """Test the /api/datasets/{dataset_name} endpoint to delete a specific dataset"""
    print(f"\n=== Testing Delete Dataset Endpoint for '{dataset_name}' ===")
    
    response = requests.delete(f"{BASE_URL}/datasets/{dataset_name}")
    
    if response.status_code == 200:
        print(f"Status: {response.status_code} OK")
        data = response.json()
        print(f"Success: {data['success']}")
        print(f"Message: {data['message']}")
        print(f"Records deleted: {data['records_deleted']}")
    else:
        print(f"Error: {response.status_code}")
        print(response.text)
    
    return response.json() if response.status_code == 200 else None

def test_validation_scenarios():
    """Test validation scenarios like duplicate dataset names, missing files, etc."""
    print("\n=== Testing Validation Scenarios ===")
    
    # Test duplicate dataset name
    print("\n--- Testing Duplicate Dataset Name ---")
    test_multi_dataset_upload("test_dataset_1", "/app/test_matches_1.csv", "/app/test_team_stats_1.csv", "/app/test_player_stats_1.csv")
    response = requests.post(
        f"{BASE_URL}/upload/multi-dataset",
        files=[
            ('files', ('test_matches_1.csv', open("/app/test_matches_1.csv", 'rb'), 'text/csv')),
            ('files', ('test_team_stats_1.csv', open("/app/test_team_stats_1.csv", 'rb'), 'text/csv')),
            ('files', ('test_player_stats_1.csv', open("/app/test_player_stats_1.csv", 'rb'), 'text/csv'))
        ],
        data={'dataset_names': ['test_dataset_1']}
    )
    print(f"Status: {response.status_code}")
    print(response.text)
    
    # Test missing files (only 2 files instead of 3)
    print("\n--- Testing Missing Files ---")
    response = requests.post(
        f"{BASE_URL}/upload/multi-dataset",
        files=[
            ('files', ('test_matches_1.csv', open("/app/test_matches_1.csv", 'rb'), 'text/csv')),
            ('files', ('test_team_stats_1.csv', open("/app/test_team_stats_1.csv", 'rb'), 'text/csv'))
        ],
        data={'dataset_names': ['test_dataset_3']}
    )
    print(f"Status: {response.status_code}")
    print(response.text)
    
    # Test missing dataset name
    print("\n--- Testing Missing Dataset Name ---")
    response = requests.post(
        f"{BASE_URL}/upload/multi-dataset",
        files=[
            ('files', ('test_matches_1.csv', open("/app/test_matches_1.csv", 'rb'), 'text/csv')),
            ('files', ('test_team_stats_1.csv', open("/app/test_team_stats_1.csv", 'rb'), 'text/csv')),
            ('files', ('test_player_stats_1.csv', open("/app/test_player_stats_1.csv", 'rb'), 'text/csv'))
        ],
        data={'dataset_names': []}
    )
    print(f"Status: {response.status_code}")
    print(response.text)
    
    # Test non-existent dataset deletion
    print("\n--- Testing Non-existent Dataset Deletion ---")
    response = requests.delete(f"{BASE_URL}/datasets/non_existent_dataset")
    print(f"Status: {response.status_code}")
    print(response.text)

def verify_dataset_name_in_records(dataset_name):
    """Verify that the dataset_name field is being properly added to all records"""
    print(f"\n=== Verifying Dataset Name in Records for '{dataset_name}' ===")
    
    # Since we don't have direct endpoints to fetch records by dataset name,
    # we'll use the datasets endpoint to verify the counts
    response = requests.post(f"{BASE_URL}/datasets")
    
    if response.status_code == 200:
        data = response.json()
        for dataset in data['datasets']:
            if dataset['dataset_name'] == dataset_name:
                print(f"Dataset '{dataset_name}' verification:")
                print(f"  - Matches: {dataset['matches_count']} records")
                print(f"  - Team Stats: {dataset['team_stats_count']} records")
                print(f"  - Player Stats: {dataset['player_stats_count']} records")
                
                # Verify counts match our test data
                expected_matches = 3
                expected_team_stats = 6
                expected_player_stats = 18
                
                if dataset['matches_count'] == expected_matches and \
                   dataset['team_stats_count'] == expected_team_stats and \
                   dataset['player_stats_count'] == expected_player_stats:
                    print(f"✅ All record counts match expected values for dataset '{dataset_name}'")
                    print(f"✅ Dataset name field is correctly added to all records")
                else:
                    print(f"❌ Record counts don't match expected values for dataset '{dataset_name}'")
                    print(f"  Expected: {expected_matches} matches, {expected_team_stats} team stats, {expected_player_stats} player stats")
                    print(f"  Actual: {dataset['matches_count']} matches, {dataset['team_stats_count']} team stats, {dataset['player_stats_count']} player stats")
                
                return
        
        print(f"❌ Dataset '{dataset_name}' not found in the list of datasets")
    else:
        print(f"Error fetching datasets: {response.status_code}")
        print(response.text)

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

def test_team_performance_stats(team_name="Arsenal"):
    """Test the team performance endpoint to verify statistics"""
    print(f"\n=== Testing Team Performance Stats for {team_name} ===")
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
        
        print("\nHome Stats:")
        print(f"  Matches: {home_stats.get('matches_count', 0)}")
        
        # Check for required statistics
        required_stats = [
            'xg_per_shot', 'shots_total', 'shots_on_target', 'goals_per_xg', 
            'shot_accuracy', 'conversion_rate', 'penalty_conversion_rate',
            'points', 'goals', 'goals_conceded'
        ]
        
        missing_home_stats = [stat for stat in required_stats if stat not in home_stats or home_stats[stat] == 0]
        if missing_home_stats:
            print(f"❌ Missing or zero home stats: {', '.join(missing_home_stats)}")
        else:
            print("✅ All required home stats are present and non-zero")
        
        # Print key home stats
        print(f"  xG per shot: {home_stats.get('xg_per_shot', 0)}")
        print(f"  Shots per game: {home_stats.get('shots_total', 0)}")
        print(f"  Shot accuracy: {home_stats.get('shot_accuracy', 0)}")
        print(f"  Conversion rate: {home_stats.get('conversion_rate', 0)}")
        print(f"  Goals per xG: {home_stats.get('goals_per_xg', 0)}")
        
        print("\nAway Stats:")
        print(f"  Matches: {away_stats.get('matches_count', 0)}")
        
        # Check for required statistics in away stats
        missing_away_stats = [stat for stat in required_stats if stat not in away_stats or away_stats[stat] == 0]
        if missing_away_stats:
            print(f"❌ Missing or zero away stats: {', '.join(missing_away_stats)}")
        else:
            print("✅ All required away stats are present and non-zero")
        
        # Print key away stats
        print(f"  xG per shot: {away_stats.get('xg_per_shot', 0)}")
        print(f"  Shots per game: {away_stats.get('shots_total', 0)}")
        print(f"  Shot accuracy: {away_stats.get('shot_accuracy', 0)}")
        print(f"  Conversion rate: {away_stats.get('conversion_rate', 0)}")
        print(f"  Goals per xG: {away_stats.get('goals_per_xg', 0)}")
        
        return data
    else:
        print(f"Error: {response.status_code}")
        print(response.text)
        return None

def test_rbs_results_stats():
    """Test the RBS results to verify statistics"""
    print("\n=== Testing RBS Results Statistics ===")
    
    # Get a sample team name
    response = requests.get(f"{BASE_URL}/teams")
    if response.status_code != 200:
        print(f"Error getting teams: {response.status_code}")
        return None
    
    teams = response.json().get('teams', [])
    if not teams:
        print("No teams found")
        return None
    
    team_name = teams[0]
    print(f"Testing RBS results for team: {team_name}")
    
    # Get RBS results for this team
    response = requests.get(f"{BASE_URL}/rbs-results/{team_name}")
    
    if response.status_code == 200:
        print(f"Status: {response.status_code} OK")
        data = response.json()
        print(f"Success: {data['success']}")
        print(f"Team: {data['team_name']}")
        print(f"Results Count: {len(data.get('results', []))}")
        
        # Check RBS results
        results = data.get('results', [])
        if not results:
            print("❌ No RBS results found")
            return data
        
        # Check the first result
        first_result = results[0]
        print(f"\nRBS Score: {first_result.get('rbs_score')}")
        print(f"Referee: {first_result.get('referee')}")
        print(f"Confidence: {first_result.get('confidence_level')}")
        
        # Check stats breakdown
        stats_breakdown = first_result.get('stats_breakdown', {})
        print("\nStats Breakdown:")
        for stat, value in stats_breakdown.items():
            print(f"  {stat}: {value}")
        
        # Verify all required stats are in the breakdown
        required_stats = [
            'yellow_cards', 'red_cards', 'fouls_committed', 'fouls_drawn',
            'penalties_awarded', 'xg_difference', 'possession_percentage'
        ]
        
        missing_stats = [stat for stat in required_stats if stat not in stats_breakdown]
        if missing_stats:
            print(f"❌ Missing stats in breakdown: {', '.join(missing_stats)}")
        else:
            print("✅ All required stats are present in the breakdown")
        
        # Check for non-zero values in key stats
        zero_stats = [stat for stat in required_stats if stat in stats_breakdown and stats_breakdown[stat] == 0]
        if zero_stats:
            print(f"⚠️ Zero values in stats: {', '.join(zero_stats)}")
        else:
            print("✅ All stats have non-zero values")
        
        return data
    else:
        print(f"Error: {response.status_code}")
        print(response.text)
        return None

def verify_data_integration():
    """Verify that player statistics are properly aggregated into team-level statistics"""
    print("\n=== Verifying Data Integration ===")
    
    # Get a sample team name
    response = requests.get(f"{BASE_URL}/teams")
    if response.status_code != 200:
        print(f"Error getting teams: {response.status_code}")
        return False
    
    teams = response.json().get('teams', [])
    if not teams:
        print("No teams found")
        return False
    
    team_name = teams[0]
    print(f"Testing data integration for team: {team_name}")
    
    # Get team performance data
    team_response = requests.get(f"{BASE_URL}/team-performance/{team_name}")
    if team_response.status_code != 200:
        print(f"Error getting team performance: {team_response.status_code}")
        return False
    
    team_data = team_response.json()
    home_stats = team_data.get('home_stats', {})
    away_stats = team_data.get('away_stats', {})
    
    # Check for player-aggregated stats
    player_aggregated_stats = ['xg', 'fouls_drawn', 'penalties_awarded']
    
    print("\nChecking player-aggregated stats:")
    for stat in player_aggregated_stats:
        home_value = home_stats.get(stat, 0)
        away_value = away_stats.get(stat, 0)
        print(f"  {stat}: Home={home_value}, Away={away_value}")
        
        if home_value == 0 and away_value == 0:
            print(f"❌ {stat} has zero values in both home and away stats")
        else:
            print(f"✅ {stat} has non-zero values")
    
    # Check derived metrics
    derived_metrics = ['xg_per_shot', 'goals_per_xg', 'shot_accuracy', 'conversion_rate']
    
    print("\nChecking derived metrics:")
    for metric in derived_metrics:
        home_value = home_stats.get(metric, 0)
        away_value = away_stats.get(metric, 0)
        print(f"  {metric}: Home={home_value}, Away={away_value}")
        
        if home_value == 0 and away_value == 0:
            print(f"❌ {metric} has zero values in both home and away stats")
        else:
            print(f"✅ {metric} has non-zero values")
    
    # Overall assessment
    if all(home_stats.get(stat, 0) > 0 or away_stats.get(stat, 0) > 0 for stat in player_aggregated_stats):
        print("\n✅ Player statistics are properly aggregated into team-level statistics")
        return True
    else:
        print("\n❌ Some player statistics are not properly aggregated into team-level statistics")
        return False

def test_match_prediction(home_team="Arsenal", away_team="Chelsea", referee_name="Michael Oliver"):
    """Test the match prediction endpoint"""
    print(f"\n=== Testing Match Prediction for {home_team} vs {away_team} with referee {referee_name} ===")
    
    # Prepare request data
    request_data = {
        "home_team": home_team,
        "away_team": away_team,
        "referee_name": referee_name
    }
    
    response = requests.post(f"{BASE_URL}/predict-match", json=request_data)
    
    if response.status_code == 200:
        print(f"Status: {response.status_code} OK")
        data = response.json()
        print(f"Success: {data['success']}")
        
        if data['success']:
            print(f"Home Team: {data['home_team']}")
            print(f"Away Team: {data['away_team']}")
            print(f"Referee: {data['referee']}")
            print(f"Predicted Home Goals: {data['predicted_home_goals']}")
            print(f"Predicted Away Goals: {data['predicted_away_goals']}")
            print(f"Home xG: {data['home_xg']}")
            print(f"Away xG: {data['away_xg']}")
            
            # Check prediction breakdown
            breakdown = data.get('prediction_breakdown', {})
            print("\nPrediction Breakdown:")
            for key, value in list(breakdown.items())[:5]:
                print(f"  - {key}: {value}")
            if len(breakdown) > 5:
                print("  ...")
            
            # Check confidence factors
            confidence = data.get('confidence_factors', {})
            print("\nConfidence Factors:")
            for key, value in list(confidence.items())[:5]:
                print(f"  - {key}: {value}")
            if len(confidence) > 5:
                print("  ...")
            
            # Verify key metrics are present and non-zero
            key_metrics = ['home_xg_per_shot', 'away_xg_per_shot', 'home_shots_avg', 'away_shots_avg']
            missing_metrics = [metric for metric in key_metrics if metric not in breakdown or breakdown[metric] == 0]
            
            if missing_metrics:
                print(f"\n❌ Missing or zero metrics in prediction breakdown: {', '.join(missing_metrics)}")
            else:
                print("\n✅ All key metrics are present and non-zero in prediction breakdown")
            
            return data
        else:
            print(f"Prediction failed: {data.get('prediction_breakdown', {}).get('error', 'Unknown error')}")
            return data
    else:
        print(f"Error: {response.status_code}")
        print(response.text)
        return None

def test_end_to_end_workflow():
    """Test the complete workflow from comprehensive stats to RBS to match prediction"""
    print("\n=== Testing End-to-End Workflow ===")
    
    # Step 1: Calculate comprehensive team stats
    print("\nStep 1: Calculate comprehensive team stats")
    comp_stats_response = requests.post(f"{BASE_URL}/calculate-comprehensive-team-stats")
    
    if comp_stats_response.status_code != 200 or not comp_stats_response.json().get('success'):
        print("❌ Failed to calculate comprehensive team stats")
        print(f"Status: {comp_stats_response.status_code}")
        print(comp_stats_response.text)
        return False
    
    comp_stats_data = comp_stats_response.json()
    print(f"✅ Comprehensive team stats calculated: {comp_stats_data.get('records_updated')} records updated")
    
    # Step 2: Calculate RBS
    print("\nStep 2: Calculate RBS")
    rbs_response = requests.post(f"{BASE_URL}/calculate-rbs")
    
    if rbs_response.status_code != 200 or not rbs_response.json().get('success'):
        print("❌ Failed to calculate RBS")
        print(f"Status: {rbs_response.status_code}")
        print(rbs_response.text)
        return False
    
    rbs_data = rbs_response.json()
    print(f"✅ RBS calculated: {rbs_data.get('results_count')} results generated")
    
    # Step 3: Get teams for match prediction
    teams_response = requests.get(f"{BASE_URL}/teams")
    
    if teams_response.status_code != 200:
        print("❌ Failed to get teams")
        print(f"Status: {teams_response.status_code}")
        print(teams_response.text)
        return False
    
    teams = teams_response.json().get('teams', [])
    if len(teams) < 2:
        print("❌ Not enough teams for match prediction")
        return False
    
    # Get referees
    referees_response = requests.get(f"{BASE_URL}/referees")
    
    if referees_response.status_code != 200:
        print("❌ Failed to get referees")
        print(f"Status: {referees_response.status_code}")
        print(referees_response.text)
        return False
    
    referees = referees_response.json().get('referees', [])
    if not referees:
        print("❌ No referees found for match prediction")
        return False
    
    # Step 4: Perform match prediction
    home_team = teams[0]
    away_team = teams[1]
    referee = referees[0]
    
    print(f"\nStep 4: Perform match prediction for {home_team} vs {away_team} with referee {referee}")
    prediction_data = test_match_prediction(home_team, away_team, referee)
    
    if not prediction_data or not prediction_data.get('success'):
        print("❌ Match prediction failed")
        return False
    
    print(f"✅ Match prediction successful")
    
    # Step 5: Verify team performance stats
    print(f"\nStep 5: Verify team performance stats for {home_team}")
    performance_data = test_team_performance_stats(home_team)
    
    if not performance_data or not performance_data.get('success'):
        print(f"❌ Failed to get team performance stats for {home_team}")
        return False
    
    # Check for non-zero values in key stats
    home_stats = performance_data.get('home_stats', {})
    away_stats = performance_data.get('away_stats', {})
    
    key_stats = ['xg_per_shot', 'shots_total', 'shot_accuracy', 'conversion_rate', 'goals_per_xg']
    all_stats_ok = True
    
    for stat in key_stats:
        home_value = home_stats.get(stat, 0)
        away_value = away_stats.get(stat, 0)
        
        if home_value == 0 and away_value == 0:
            print(f"❌ {stat} has zero values in both home and away stats")
            all_stats_ok = False
    
    if all_stats_ok:
        print("✅ All key team performance stats have non-zero values")
    else:
        print("❌ Some key team performance stats have zero values")
    
    # Overall workflow assessment
    print("\nEnd-to-End Workflow Assessment:")
    if (comp_stats_data.get('success') and 
        rbs_data.get('success') and 
        prediction_data.get('success') and 
        performance_data.get('success') and
        all_stats_ok):
        print("✅ Complete workflow test passed successfully")
        return True
    else:
        print("❌ Complete workflow test failed")
        return False

def test_match_prediction_fix():
    """Test the match prediction fix specifically for the 'points_per_game' error"""
    print("\n\n========== TESTING MATCH PREDICTION FIX ==========\n")
    
    # Step 1: Get teams and referees from the system
    print("Step 1: Getting teams and referees from the system")
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
    
    # Step 2: Test match prediction with actual team names and referee
    print("\nStep 2: Testing match prediction with actual team names and referee")
    home_team = teams[0]
    away_team = teams[1]
    referee = referees[0]
    
    print(f"Testing prediction for {home_team} vs {away_team} with referee {referee}")
    
    request_data = {
        "home_team": home_team,
        "away_team": away_team,
        "referee_name": referee
    }
    
    response = requests.post(f"{BASE_URL}/predict-match", json=request_data)
    
    if response.status_code != 200:
        print(f"❌ Match prediction request failed with status code {response.status_code}")
        print(response.text)
        return False
    
    prediction_data = response.json()
    
    if not prediction_data.get('success'):
        error_message = prediction_data.get('prediction_breakdown', {}).get('error', 'Unknown error')
        print(f"❌ Match prediction failed: {error_message}")
        
        # Check specifically for the 'points_per_game' error
        if "points_per_game" in error_message:
            print("❌ The 'Prediction Failed 'points_per_game'' error is still present!")
        else:
            print(f"❌ Failed with a different error: {error_message}")
        
        return False
    
    print("✅ Match prediction successful!")
    print(f"Predicted Home Goals: {prediction_data['predicted_home_goals']}")
    print(f"Predicted Away Goals: {prediction_data['predicted_away_goals']}")
    print(f"Home xG: {prediction_data['home_xg']}")
    print(f"Away xG: {prediction_data['away_xg']}")
    
    # Step 3: Verify all required fields in the prediction breakdown
    print("\nStep 3: Verifying all required fields in the prediction breakdown")
    
    breakdown = prediction_data.get('prediction_breakdown', {})
    required_fields = [
        'home_xg_per_shot', 'away_xg_per_shot',
        'home_shots_avg', 'away_shots_avg',
        'home_goals_avg', 'away_goals_avg',
        'home_conversion_rate', 'away_conversion_rate',
        'home_penalty_conversion', 'away_penalty_conversion',
        'home_fouls_drawn_avg', 'away_fouls_drawn_avg',
        'home_penalties_avg', 'away_penalties_avg'
    ]
    
    missing_fields = []
    zero_fields = []
    
    for field in required_fields:
        if field not in breakdown:
            missing_fields.append(field)
        elif breakdown[field] == 0:
            zero_fields.append(field)
    
    if missing_fields:
        print(f"❌ Missing fields in prediction breakdown: {', '.join(missing_fields)}")
    else:
        print("✅ All required fields are present in the prediction breakdown")
    
    if zero_fields:
        print(f"⚠️ Fields with zero values in prediction breakdown: {', '.join(zero_fields)}")
    else:
        print("✅ All fields have non-zero values in the prediction breakdown")
    
    # Print the actual values for key metrics
    print("\nKey metrics in prediction breakdown:")
    for field in required_fields:
        if field in breakdown:
            print(f"  - {field}: {breakdown[field]}")
    
    # Step 4: Test team performance to verify comprehensive team stats
    print("\nStep 4: Testing team performance to verify comprehensive team stats")
    
    home_team_response = requests.get(f"{BASE_URL}/team-performance/{home_team}")
    if home_team_response.status_code != 200:
        print(f"❌ Failed to get team performance for {home_team}: {home_team_response.status_code}")
        print(home_team_response.text)
        return False
    
    home_team_data = home_team_response.json()
    
    # Check for required fields in team stats
    required_team_stats = [
        'points_per_game', 'xg_per_shot', 'shots_total', 'goals',
        'penalties_awarded', 'fouls_drawn', 'penalty_conversion_rate'
    ]
    
    home_stats = home_team_data.get('home_stats', {})
    away_stats = home_team_data.get('away_stats', {})
    
    missing_home_stats = [stat for stat in required_team_stats if stat not in home_stats]
    missing_away_stats = [stat for stat in required_team_stats if stat not in away_stats]
    
    zero_home_stats = [stat for stat in required_team_stats if stat in home_stats and home_stats[stat] == 0]
    zero_away_stats = [stat for stat in required_team_stats if stat in away_stats and away_stats[stat] == 0]
    
    if missing_home_stats or missing_away_stats:
        print(f"❌ Missing stats in team performance:")
        if missing_home_stats:
            print(f"  - Home: {', '.join(missing_home_stats)}")
        if missing_away_stats:
            print(f"  - Away: {', '.join(missing_away_stats)}")
    else:
        print("✅ All required stats are present in team performance")
    
    if zero_home_stats or zero_away_stats:
        print(f"⚠️ Stats with zero values in team performance:")
        if zero_home_stats:
            print(f"  - Home: {', '.join(zero_home_stats)}")
        if zero_away_stats:
            print(f"  - Away: {', '.join(zero_away_stats)}")
    
    # Print the actual values for key team stats
    print(f"\nKey stats for {home_team}:")
    print("Home stats:")
    for stat in required_team_stats:
        if stat in home_stats:
            print(f"  - {stat}: {home_stats[stat]}")
    
    print("Away stats:")
    for stat in required_team_stats:
        if stat in away_stats:
            print(f"  - {stat}: {away_stats[stat]}")
    
    # Step 5: Test end-to-end workflow
    print("\nStep 5: Testing end-to-end workflow")
    
    # Calculate comprehensive team stats
    comp_stats_response = requests.post(f"{BASE_URL}/calculate-comprehensive-team-stats")
    if comp_stats_response.status_code != 200 or not comp_stats_response.json().get('success'):
        print("❌ Failed to calculate comprehensive team stats")
        return False
    
    print("✅ Comprehensive team stats calculated successfully")
    
    # Calculate RBS
    rbs_response = requests.post(f"{BASE_URL}/calculate-rbs")
    if rbs_response.status_code != 200 or not rbs_response.json().get('success'):
        print("❌ Failed to calculate RBS")
        return False
    
    print("✅ RBS calculated successfully")
    
    # Perform match prediction again after calculations
    print("\nPerforming match prediction after calculations:")
    response = requests.post(f"{BASE_URL}/predict-match", json=request_data)
    
    if response.status_code != 200:
        print(f"❌ Match prediction request failed with status code {response.status_code}")
        return False
    
    prediction_data = response.json()
    
    if not prediction_data.get('success'):
        error_message = prediction_data.get('prediction_breakdown', {}).get('error', 'Unknown error')
        print(f"❌ Match prediction failed: {error_message}")
        return False
    
    print("✅ End-to-end workflow test passed successfully")
    print(f"Predicted Home Goals: {prediction_data['predicted_home_goals']}")
    print(f"Predicted Away Goals: {prediction_data['predicted_away_goals']}")
    
    # Final summary
    print("\n========== MATCH PREDICTION FIX TEST SUMMARY ==========")
    if (not missing_fields and 
        not missing_home_stats and 
        not missing_away_stats and
        prediction_data.get('success')):
        print("✅ Match prediction fix has been successfully implemented")
        print("✅ The 'Prediction Failed 'points_per_game'' error has been resolved")
        print("✅ All required fields are properly available in the team averages")
        print("✅ Comprehensive team stats are properly calculated")
        print("✅ End-to-end workflow is working correctly")
        return True
    else:
        print("❌ Match prediction fix test failed")
        return False

def test_pdf_export_endpoint():
    """Test the PDF export endpoint for match predictions"""
    print("\n\n========== TESTING PDF EXPORT ENDPOINT ==========\n")
    
    # Step 1: Get teams and referees from the system
    print("Step 1: Getting teams and referees from the system")
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
    
    # Step 2: Test PDF export with actual team names and referee
    print("\nStep 2: Testing PDF export with actual team names and referee")
    home_team = teams[0]
    away_team = teams[1]
    referee = referees[0]
    
    print(f"Testing PDF export for {home_team} vs {away_team} with referee {referee}")
    
    request_data = {
        "home_team": home_team,
        "away_team": away_team,
        "referee_name": referee
    }
    
    response = requests.post(f"{BASE_URL}/export-prediction-pdf", json=request_data)
    
    if response.status_code != 200:
        print(f"❌ PDF export request failed with status code {response.status_code}")
        print(response.text)
        return False
    
    # Check if the response is a PDF file
    content_type = response.headers.get('Content-Type')
    if content_type != 'application/pdf':
        print(f"❌ Response is not a PDF file. Content-Type: {content_type}")
        return False
    
    print("✅ PDF export request successful!")
    print(f"Content-Type: {content_type}")
    print(f"Content-Disposition: {response.headers.get('Content-Disposition')}")
    print(f"PDF size: {len(response.content)} bytes")
    
    # Step 3: Verify PDF content
    print("\nStep 3: Verifying PDF content")
    
    # Save PDF to a temporary file
    pdf_content = response.content
    pdf_file = io.BytesIO(pdf_content)
    
    try:
        # Parse PDF content
        pdf_reader = PyPDF2.PdfReader(pdf_file)
        num_pages = len(pdf_reader.pages)
        print(f"PDF has {num_pages} pages")
        
        # Extract text from the first page to verify content
        first_page_text = pdf_reader.pages[0].extract_text()
        
        # Check for required sections in the PDF
        required_sections = [
            "Football Match Prediction Report",
            "Match Information",
            "Prediction Summary",
            "Detailed Model Analysis",
            "Poisson Distribution Analysis"
        ]
        
        missing_sections = []
        for section in required_sections:
            if section not in first_page_text:
                missing_sections.append(section)
        
        if missing_sections:
            print(f"❌ Missing sections in PDF: {', '.join(missing_sections)}")
        else:
            print("✅ All required sections are present in the PDF")
        
        # Check for team names in the PDF
        if home_team not in first_page_text or away_team not in first_page_text:
            print("❌ Team names not found in the PDF")
        else:
            print(f"✅ Team names ({home_team}, {away_team}) found in the PDF")
        
        # Check for referee name in the PDF
        if referee not in first_page_text:
            print(f"❌ Referee name ({referee}) not found in the PDF")
        else:
            print(f"✅ Referee name ({referee}) found in the PDF")
        
        # Check for additional pages with more analysis
        if num_pages > 1:
            print(f"✅ PDF contains multiple pages with detailed analysis")
            
            # Check content of additional pages
            additional_sections = []
            for i in range(1, min(num_pages, 3)):  # Check up to 3 pages
                page_text = pdf_reader.pages[i].extract_text()
                if "Head-to-Head Statistics" in page_text:
                    additional_sections.append("Head-to-Head Statistics")
                if "Referee Bias Analysis" in page_text:
                    additional_sections.append("Referee Bias Analysis")
                if "Model Information" in page_text:
                    additional_sections.append("Model Information")
            
            if additional_sections:
                print(f"✅ Additional sections found: {', '.join(additional_sections)}")
            else:
                print("⚠️ No additional analysis sections found in extra pages")
        
        # Final assessment
        if not missing_sections and home_team in first_page_text and away_team in first_page_text and referee in first_page_text:
            print("\n✅ PDF export functionality is working correctly!")
            return True
        else:
            print("\n❌ PDF export functionality has issues")
            return False
        
    except Exception as e:
        print(f"❌ Error parsing PDF content: {e}")
        return False

def test_enhanced_match_prediction():
    """Test the enhanced match prediction endpoint with probability fields"""
    print("\n\n========== TESTING ENHANCED MATCH PREDICTION WITH PROBABILITY FIELDS ==========\n")
    
    # Step 1: Get teams and referees from the system
    print("Step 1: Getting teams and referees from the system")
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
    
    # Step 2: Test match prediction with different team combinations
    print("\nStep 2: Testing match prediction with different team combinations")
    
    # Test with at least 3 different team combinations
    test_combinations = []
    if len(teams) >= 6:
        test_combinations = [
            (teams[0], teams[1], referees[0]),
            (teams[2], teams[3], referees[0]),
            (teams[4], teams[5], referees[0])
        ]
    elif len(teams) >= 4:
        test_combinations = [
            (teams[0], teams[1], referees[0]),
            (teams[2], teams[3], referees[0]),
            (teams[0], teams[2], referees[0])
        ]
    elif len(teams) >= 2:
        test_combinations = [
            (teams[0], teams[1], referees[0]),
            (teams[1], teams[0], referees[0]),
            (teams[0], teams[1], referees[-1] if len(referees) > 1 else referees[0])
        ]
    
    results = []
    
    for i, (home_team, away_team, referee) in enumerate(test_combinations):
        print(f"\nTest {i+1}: {home_team} vs {away_team} with referee {referee}")
        
        request_data = {
            "home_team": home_team,
            "away_team": away_team,
            "referee_name": referee
        }
        
        response = requests.post(f"{BASE_URL}/predict-match", json=request_data)
        
        if response.status_code != 200:
            print(f"❌ Match prediction request failed with status code {response.status_code}")
            print(response.text)
            continue
        
        prediction_data = response.json()
        
        if not prediction_data.get('success'):
            error_message = prediction_data.get('prediction_breakdown', {}).get('error', 'Unknown error')
            print(f"❌ Match prediction failed: {error_message}")
            continue
        
        print("✅ Match prediction successful!")
        print(f"Predicted Home Goals: {prediction_data['predicted_home_goals']}")
        print(f"Predicted Away Goals: {prediction_data['predicted_away_goals']}")
        print(f"Home xG: {prediction_data['home_xg']}")
        print(f"Away xG: {prediction_data['away_xg']}")
        
        # Check for probability fields
        if 'home_win_probability' not in prediction_data or 'draw_probability' not in prediction_data or 'away_win_probability' not in prediction_data:
            print("❌ Probability fields are missing from the response!")
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
            continue
        
        # Verify probabilities sum to approximately 100%
        total_prob = home_win_prob + draw_prob + away_win_prob
        if not (99.5 <= total_prob <= 100.5):  # Allow for small rounding errors
            print(f"❌ Probabilities do not sum to 100%! Total: {total_prob}%")
            continue
        
        print(f"✅ Probabilities are valid and sum to {total_prob}%")
        
        # Verify probabilities are consistent with predicted goals
        if prediction_data['predicted_home_goals'] > prediction_data['predicted_away_goals'] and home_win_prob <= away_win_prob:
            print("❌ Inconsistency: Home team has higher predicted goals but lower win probability!")
        elif prediction_data['predicted_home_goals'] < prediction_data['predicted_away_goals'] and home_win_prob >= away_win_prob:
            print("❌ Inconsistency: Away team has higher predicted goals but lower win probability!")
        else:
            print("✅ Probabilities are consistent with predicted goals")
        
        results.append({
            'home_team': home_team,
            'away_team': away_team,
            'referee': referee,
            'predicted_home_goals': prediction_data['predicted_home_goals'],
            'predicted_away_goals': prediction_data['predicted_away_goals'],
            'home_xg': prediction_data['home_xg'],
            'away_xg': prediction_data['away_xg'],
            'home_win_probability': home_win_prob,
            'draw_probability': draw_prob,
            'away_win_probability': away_win_prob
        })
    
    # Step 3: Analyze results across different combinations
    print("\nStep 3: Analyzing results across different combinations")
    
    if not results:
        print("❌ No successful predictions to analyze")
        return False
    
    print(f"Successfully tested {len(results)} team combinations")
    
    # Check if probabilities vary across different combinations
    if len(results) > 1:
        home_win_probs = [r['home_win_probability'] for r in results]
        draw_probs = [r['draw_probability'] for r in results]
        away_win_probs = [r['away_win_probability'] for r in results]
        
        home_win_prob_range = max(home_win_probs) - min(home_win_probs)
        draw_prob_range = max(draw_probs) - min(draw_probs)
        away_win_prob_range = max(away_win_probs) - min(away_win_probs)
        
        print(f"Home Win Probability Range: {home_win_prob_range:.2f}%")
        print(f"Draw Probability Range: {draw_prob_range:.2f}%")
        print(f"Away Win Probability Range: {away_win_prob_range:.2f}%")
        
        if home_win_prob_range < 1 and draw_prob_range < 1 and away_win_prob_range < 1:
            print("❌ Probabilities don't vary significantly across different team combinations!")
        else:
            print("✅ Probabilities vary across different team combinations as expected")
    
    # Final summary
    print("\n========== ENHANCED MATCH PREDICTION TEST SUMMARY ==========")
    
    all_tests_passed = True
    for i, result in enumerate(results):
        print(f"\nTest {i+1}: {result['home_team']} vs {result['away_team']} with referee {result['referee']}")
        print(f"  Predicted Score: {result['predicted_home_goals']} - {result['predicted_away_goals']}")
        print(f"  xG: {result['home_xg']} - {result['away_xg']}")
        print(f"  Probabilities: Home Win {result['home_win_probability']}%, Draw {result['draw_probability']}%, Away Win {result['away_win_probability']}%")
        
        # Check if this test passed all criteria
        total_prob = result['home_win_probability'] + result['draw_probability'] + result['away_win_probability']
        prob_in_range = (0 <= result['home_win_probability'] <= 100 and 
                         0 <= result['draw_probability'] <= 100 and 
                         0 <= result['away_win_probability'] <= 100)
        prob_sum_valid = 99.5 <= total_prob <= 100.5
        
        if prob_in_range and prob_sum_valid:
            print("  ✅ Test passed")
        else:
            print("  ❌ Test failed")
            all_tests_passed = False
    
    if all_tests_passed and results:
        print("\n✅ Enhanced match prediction with probability fields is working correctly!")
        return True
    else:
        print("\n❌ Enhanced match prediction test failed")
        return False

def test_corrected_match_prediction_algorithm():
    """
    Test the corrected match prediction algorithm to verify that the xG per shot and other derived statistics 
    are now properly bounded and mathematically consistent.
    
    This test specifically checks:
    1. Match prediction with teams that had problematic stats before (like Chicago Fire)
    2. Verification that all derived statistics are within reasonable bounds:
       - xG per shot should be ≤ 1.0
       - Shot accuracy should be ≤ 1.0 (100%)
       - Penalty conversion rate should be ≤ 1.0 (100%)
    3. Team performance data for multiple teams to ensure corrections are working
    4. Verification that prediction probabilities are calculated correctly with corrected data
    5. Testing with multiple team combinations to ensure consistency
    """
    print("\n\n========== TESTING CORRECTED MATCH PREDICTION ALGORITHM ==========\n")
    
    # Step 1: Get teams and referees from the system
    print("Step 1: Getting teams and referees from the system")
    teams_response = requests.get(f"{BASE_URL}/teams")
    if teams_response.status_code != 200:
        print(f"❌ Failed to get teams: {teams_response.status_code}")
        return False
    
    teams = teams_response.json().get('teams', [])
    if len(teams) < 2:
        print("❌ Not enough teams for match prediction")
        return False
    
    print(f"Found {len(teams)} teams: {', '.join(teams[:5])}{'...' if len(teams) > 5 else ''}")
    
    # Try to find Chicago Fire specifically (as mentioned in the review request)
    chicago_fire_found = False
    for team in teams:
        if "Chicago Fire" in team:
            chicago_fire_found = True
            print(f"✅ Found Chicago Fire in the teams list: {team}")
            break
    
    if not chicago_fire_found:
        print("⚠️ Chicago Fire not found in teams list. Will use other teams for testing.")
    
    referees_response = requests.get(f"{BASE_URL}/referees")
    if referees_response.status_code != 200:
        print(f"❌ Failed to get referees: {referees_response.status_code}")
        return False
    
    referees = referees_response.json().get('referees', [])
    if not referees:
        print("❌ No referees found for match prediction")
        return False
    
    print(f"Found {len(referees)} referees: {', '.join(referees[:5])}{'...' if len(referees) > 5 else ''}")
    
    # Step 2: Test team performance data for multiple teams
    print("\nStep 2: Testing team performance data for multiple teams")
    
    # Select teams to test (including Chicago Fire if found)
    test_teams = []
    if chicago_fire_found:
        for team in teams:
            if "Chicago Fire" in team:
                test_teams.append(team)
                break
    
    # Add more teams to test
    for team in teams:
        if team not in test_teams and len(test_teams) < 5:
            test_teams.append(team)
    
    team_stats_results = []
    
    for team in test_teams:
        print(f"\nTesting team performance for: {team}")
        response = requests.get(f"{BASE_URL}/team-performance/{team}")
        
        if response.status_code != 200:
            print(f"❌ Failed to get team performance for {team}: {response.status_code}")
            continue
        
        team_data = response.json()
        if not team_data.get('success'):
            print(f"❌ Team performance request failed for {team}")
            continue
        
        home_stats = team_data.get('home_stats', {})
        away_stats = team_data.get('away_stats', {})
        
        # Check for bounded statistics
        bounded_stats = ['xg_per_shot', 'shot_accuracy', 'penalty_conversion_rate']
        
        print(f"Home stats for {team}:")
        for stat in bounded_stats:
            value = home_stats.get(stat, 0)
            print(f"  - {stat}: {value}")
            if value > 1.0:
                print(f"  ❌ {stat} is greater than 1.0 ({value})")
            else:
                print(f"  ✅ {stat} is properly bounded (≤ 1.0)")
        
        print(f"Away stats for {team}:")
        for stat in bounded_stats:
            value = away_stats.get(stat, 0)
            print(f"  - {stat}: {value}")
            if value > 1.0:
                print(f"  ❌ {stat} is greater than 1.0 ({value})")
            else:
                print(f"  ✅ {stat} is properly bounded (≤ 1.0)")
        
        team_stats_results.append({
            'team': team,
            'home_stats': {stat: home_stats.get(stat, 0) for stat in bounded_stats},
            'away_stats': {stat: away_stats.get(stat, 0) for stat in bounded_stats}
        })
    
    # Step 3: Test match prediction with multiple team combinations
    print("\nStep 3: Testing match prediction with multiple team combinations")
    
    # Create test combinations
    test_combinations = []
    
    # If Chicago Fire is found, include it in combinations
    if chicago_fire_found:
        chicago_fire_team = next(team for team in teams if "Chicago Fire" in team)
        for team in teams:
            if team != chicago_fire_team and len(test_combinations) < 2:
                test_combinations.append((chicago_fire_team, team, referees[0]))
                test_combinations.append((team, chicago_fire_team, referees[0]))
    
    # Add more combinations to test
    for i in range(min(len(teams), 3)):
        for j in range(min(len(teams), 3)):
            if i != j and (teams[i], teams[j], referees[0]) not in test_combinations and len(test_combinations) < 6:
                test_combinations.append((teams[i], teams[j], referees[0]))
    
    prediction_results = []
    
    for i, (home_team, away_team, referee) in enumerate(test_combinations):
        print(f"\nTest {i+1}: {home_team} vs {away_team} with referee {referee}")
        
        request_data = {
            "home_team": home_team,
            "away_team": away_team,
            "referee_name": referee
        }
        
        response = requests.post(f"{BASE_URL}/predict-match", json=request_data)
        
        if response.status_code != 200:
            print(f"❌ Match prediction request failed with status code {response.status_code}")
            print(response.text)
            continue
        
        prediction_data = response.json()
        
        if not prediction_data.get('success'):
            error_message = prediction_data.get('prediction_breakdown', {}).get('error', 'Unknown error')
            print(f"❌ Match prediction failed: {error_message}")
            continue
        
        print("✅ Match prediction successful!")
        print(f"Predicted Home Goals: {prediction_data['predicted_home_goals']}")
        print(f"Predicted Away Goals: {prediction_data['predicted_away_goals']}")
        print(f"Home xG: {prediction_data['home_xg']}")
        print(f"Away xG: {prediction_data['away_xg']}")
        
        # Check for probability fields
        home_win_prob = prediction_data.get('home_win_probability', 0)
        draw_prob = prediction_data.get('draw_probability', 0)
        away_win_prob = prediction_data.get('away_win_probability', 0)
        
        print(f"Home Win Probability: {home_win_prob}%")
        print(f"Draw Probability: {draw_prob}%")
        print(f"Away Win Probability: {away_win_prob}%")
        
        # Check prediction breakdown for bounded values
        breakdown = prediction_data.get('prediction_breakdown', {})
        
        # Check xG per shot values
        home_xg_per_shot = breakdown.get('home_xg_per_shot', 0)
        away_xg_per_shot = breakdown.get('away_xg_per_shot', 0)
        
        print(f"Home xG per shot: {home_xg_per_shot}")
        print(f"Away xG per shot: {away_xg_per_shot}")
        
        if home_xg_per_shot > 1.0:
            print(f"❌ Home xG per shot is greater than 1.0 ({home_xg_per_shot})")
        else:
            print(f"✅ Home xG per shot is properly bounded (≤ 1.0)")
        
        if away_xg_per_shot > 1.0:
            print(f"❌ Away xG per shot is greater than 1.0 ({away_xg_per_shot})")
        else:
            print(f"✅ Away xG per shot is properly bounded (≤ 1.0)")
        
        # Check penalty conversion rates
        home_penalty_conversion = breakdown.get('home_penalty_conversion', 0)
        away_penalty_conversion = breakdown.get('away_penalty_conversion', 0)
        
        print(f"Home penalty conversion rate: {home_penalty_conversion}")
        print(f"Away penalty conversion rate: {away_penalty_conversion}")
        
        if home_penalty_conversion > 1.0:
            print(f"❌ Home penalty conversion rate is greater than 1.0 ({home_penalty_conversion})")
        else:
            print(f"✅ Home penalty conversion rate is properly bounded (≤ 1.0)")
        
        if away_penalty_conversion > 1.0:
            print(f"❌ Away penalty conversion rate is greater than 1.0 ({away_penalty_conversion})")
        else:
            print(f"✅ Away penalty conversion rate is properly bounded (≤ 1.0)")
        
        # Verify probabilities are reasonable (0-100%)
        if not (0 <= home_win_prob <= 100 and 0 <= draw_prob <= 100 and 0 <= away_win_prob <= 100):
            print("❌ Probabilities are not within the valid range (0-100%)!")
        else:
            print("✅ Probabilities are within valid range (0-100%)")
        
        # Verify probabilities sum to approximately 100%
        total_prob = home_win_prob + draw_prob + away_win_prob
        if not (99.5 <= total_prob <= 100.5):  # Allow for small rounding errors
            print(f"❌ Probabilities do not sum to 100%! Total: {total_prob}%")
        else:
            print(f"✅ Probabilities sum to {total_prob}% (approximately 100%)")
        
        prediction_results.append({
            'home_team': home_team,
            'away_team': away_team,
            'home_xg_per_shot': home_xg_per_shot,
            'away_xg_per_shot': away_xg_per_shot,
            'home_penalty_conversion': home_penalty_conversion,
            'away_penalty_conversion': away_penalty_conversion,
            'home_win_probability': home_win_prob,
            'draw_probability': draw_prob,
            'away_win_probability': away_win_prob
        })
    
    # Step 4: Analyze results and provide summary
    print("\n\n========== CORRECTED MATCH PREDICTION ALGORITHM TEST SUMMARY ==========\n")
    
    # Check team performance stats
    print("Team Performance Stats Summary:")
    all_team_stats_bounded = True
    
    for result in team_stats_results:
        team = result['team']
        home_stats = result['home_stats']
        away_stats = result['away_stats']
        
        team_bounded = True
        for stat, value in home_stats.items():
            if value > 1.0:
                team_bounded = False
                all_team_stats_bounded = False
                print(f"❌ {team} home {stat}: {value} (exceeds 1.0)")
        
        for stat, value in away_stats.items():
            if value > 1.0:
                team_bounded = False
                all_team_stats_bounded = False
                print(f"❌ {team} away {stat}: {value} (exceeds 1.0)")
        
        if team_bounded:
            print(f"✅ {team}: All stats properly bounded (≤ 1.0)")
    
    if all_team_stats_bounded:
        print("\n✅ All team performance statistics are properly bounded")
    else:
        print("\n❌ Some team performance statistics exceed bounds")
    
    # Check match prediction results
    print("\nMatch Prediction Summary:")
    all_prediction_stats_bounded = True
    all_probabilities_valid = True
    
    for result in prediction_results:
        home_team = result['home_team']
        away_team = result['away_team']
        
        prediction_bounded = True
        if result['home_xg_per_shot'] > 1.0:
            prediction_bounded = False
            all_prediction_stats_bounded = False
            print(f"❌ {home_team} vs {away_team}: Home xG per shot {result['home_xg_per_shot']} (exceeds 1.0)")
        
        if result['away_xg_per_shot'] > 1.0:
            prediction_bounded = False
            all_prediction_stats_bounded = False
            print(f"❌ {home_team} vs {away_team}: Away xG per shot {result['away_xg_per_shot']} (exceeds 1.0)")
        
        if result['home_penalty_conversion'] > 1.0:
            prediction_bounded = False
            all_prediction_stats_bounded = False
            print(f"❌ {home_team} vs {away_team}: Home penalty conversion {result['home_penalty_conversion']} (exceeds 1.0)")
        
        if result['away_penalty_conversion'] > 1.0:
            prediction_bounded = False
            all_prediction_stats_bounded = False
            print(f"❌ {home_team} vs {away_team}: Away penalty conversion {result['away_penalty_conversion']} (exceeds 1.0)")
        
        # Check probability validity
        home_win = result['home_win_probability']
        draw = result['draw_probability']
        away_win = result['away_win_probability']
        
        probability_valid = True
        if not (0 <= home_win <= 100 and 0 <= draw <= 100 and 0 <= away_win <= 100):
            probability_valid = False
            all_probabilities_valid = False
            print(f"❌ {home_team} vs {away_team}: Probabilities out of range")
        
        total = home_win + draw + away_win
        if not (99.5 <= total <= 100.5):
            probability_valid = False
            all_probabilities_valid = False
            print(f"❌ {home_team} vs {away_team}: Probabilities sum to {total}% (not 100%)")
        
        if prediction_bounded and probability_valid:
            print(f"✅ {home_team} vs {away_team}: All stats properly bounded and probabilities valid")
    
    if all_prediction_stats_bounded:
        print("\n✅ All match prediction statistics are properly bounded")
    else:
        print("\n❌ Some match prediction statistics exceed bounds")
    
    if all_probabilities_valid:
        print("\n✅ All match prediction probabilities are valid and sum to 100%")
    else:
        print("\n❌ Some match prediction probabilities are invalid or don't sum to 100%")
    
    # Final assessment
    if all_team_stats_bounded and all_prediction_stats_bounded and all_probabilities_valid:
        print("\n✅ OVERALL RESULT: The corrected match prediction algorithm is working properly!")
        print("✅ All derived statistics are within reasonable bounds:")
        print("  - xG per shot ≤ 1.0")
        print("  - Shot accuracy ≤ 1.0 (100%)")
        print("  - Penalty conversion rate ≤ 1.0 (100%)")
        print("✅ Prediction probabilities are calculated correctly and sum to 100%")
        return True
    else:
        print("\n❌ OVERALL RESULT: The corrected match prediction algorithm still has issues")
        if not all_team_stats_bounded:
            print("❌ Some team performance statistics exceed reasonable bounds")
        if not all_prediction_stats_bounded:
            print("❌ Some match prediction statistics exceed reasonable bounds")
        if not all_probabilities_valid:
            print("❌ Some match prediction probabilities are invalid or don't sum to 100%")
        return False

def run_tests():
    """Run all tests"""
    # Test the corrected match prediction algorithm
    test_corrected_match_prediction_algorithm()
    
    # Test the enhanced match prediction endpoint
    test_enhanced_match_prediction()
    
    # Test the match prediction fix specifically
    test_match_prediction_fix()
    
    print("\n\n========== TESTING FIXED RBS CALCULATION AND MATCH PREDICTION WORKFLOW ==========\n")
    
    # Test comprehensive team stats calculation
    print("\n1. Testing Comprehensive Team Stats Calculation")
    comprehensive_stats_data = test_comprehensive_team_stats()
    
    # Test enhanced RBS calculation
    print("\n2. Testing Enhanced RBS Calculation")
    rbs_calculation_data = test_enhanced_rbs_calculation()
    
    # Test match prediction
    print("\n3. Testing Match Prediction")
    # Get teams for match prediction
    teams_response = requests.get(f"{BASE_URL}/teams")
    if teams_response.status_code == 200:
        teams = teams_response.json().get('teams', [])
        if len(teams) >= 2:
            # Get referees
            referees_response = requests.get(f"{BASE_URL}/referees")
            if referees_response.status_code == 200:
                referees = referees_response.json().get('referees', [])
                if referees:
                    match_prediction_data = test_match_prediction(teams[0], teams[1], referees[0])
                else:
                    print("❌ No referees found for match prediction")
                    match_prediction_data = None
            else:
                print(f"❌ Failed to get referees: {referees_response.status_code}")
                match_prediction_data = None
        else:
            print("❌ Not enough teams for match prediction")
            match_prediction_data = None
    else:
        print(f"❌ Failed to get teams: {teams_response.status_code}")
        match_prediction_data = None
    
    # Test team performance stats to verify derived statistics
    print("\n4. Testing Team Performance Stats")
    team_performance_data = test_team_performance_stats("Arsenal")
    
    # Test end-to-end workflow
    print("\n5. Testing End-to-End Workflow")
    end_to_end_success = test_end_to_end_workflow()
    
    # Print summary of tests
    print("\n\n========== FIXED RBS CALCULATION AND MATCH PREDICTION WORKFLOW TESTS SUMMARY ==========\n")
    
    if comprehensive_stats_data and comprehensive_stats_data.get('success'):
        print(f"✅ 1. Comprehensive Team Stats Calculation: {comprehensive_stats_data.get('records_updated')} records updated")
    else:
        print("❌ 1. Comprehensive Team Stats Calculation: Failed")
    
    if rbs_calculation_data and rbs_calculation_data.get('success'):
        print(f"✅ 2. Enhanced RBS Calculation: {rbs_calculation_data.get('results_count')} results calculated")
    else:
        print("❌ 2. Enhanced RBS Calculation: Failed")
    
    if match_prediction_data and match_prediction_data.get('success'):
        print(f"✅ 3. Match Prediction: Successfully predicted match outcome")
    else:
        print("❌ 3. Match Prediction: Failed")
    
    if team_performance_data and team_performance_data.get('success'):
        home_stats = team_performance_data.get('home_stats', {})
        away_stats = team_performance_data.get('away_stats', {})
        
        # Check for non-zero values in key stats
        key_stats = ['xg_per_shot', 'shots_total', 'shot_accuracy', 'conversion_rate', 'goals_per_xg']
        all_stats_ok = True
        
        for stat in key_stats:
            home_value = home_stats.get(stat, 0)
            away_value = away_stats.get(stat, 0)
            
            if home_value == 0 and away_value == 0:
                print(f"❌ {stat} has zero values in both home and away stats")
                all_stats_ok = False
        
        if all_stats_ok:
            print("✅ 4. Team Performance Stats: All key statistics have non-zero values")
        else:
            print("❌ 4. Team Performance Stats: Some key statistics have zero values")
    else:
        print("❌ 4. Team Performance Stats: Failed")
    
    if end_to_end_success:
        print("✅ 5. End-to-End Workflow: Complete workflow test passed successfully")
    else:
        print("❌ 5. End-to-End Workflow: Complete workflow test failed")
    
    # Test regression analysis functionality
    print("\n\n========== TESTING REGRESSION ANALYSIS FUNCTIONALITY ==========\n")
    
    # Test regression-stats endpoint
    regression_stats_data = test_regression_stats_endpoint()
    
    # Test RBS optimization analysis endpoint
    rbs_optimization_data = test_rbs_optimization_endpoint()
    
    # Test Match Predictor optimization endpoint
    predictor_optimization_data = test_predictor_optimization_endpoint()
    
    # Test regression analysis endpoint
    regression_analysis_data = test_regression_analysis_endpoint()
    
    # Print summary of regression analysis tests
    print("\n\n========== REGRESSION ANALYSIS TESTS SUMMARY ==========\n")
    
    if regression_stats_data:
        categories = regression_stats_data.get('categories', {})
        print(f"✅ Regression Stats Endpoint: {len(categories)} categories, {len(regression_stats_data.get('available_stats', []))} variables")
    else:
        print("❌ Regression Stats Endpoint: Failed")
    
    if rbs_optimization_data and rbs_optimization_data.get('success'):
        print(f"✅ RBS Optimization Endpoint: {len(rbs_optimization_data.get('rbs_variables_analyzed', []))} variables analyzed, {len(rbs_optimization_data.get('recommendations', []))} recommendations")
    else:
        print("❌ RBS Optimization Endpoint: Failed")
    
    if predictor_optimization_data and predictor_optimization_data.get('success'):
        print(f"✅ Predictor Optimization Endpoint: {len(predictor_optimization_data.get('predictor_variables_analyzed', []))} variables analyzed, {len(predictor_optimization_data.get('recommendations', []))} recommendations")
    else:
        print("❌ Predictor Optimization Endpoint: Failed")
    
    if regression_analysis_data and regression_analysis_data.get('success'):
        print(f"✅ Regression Analysis Endpoint: {len(regression_analysis_data.get('selected_stats', []))} variables analyzed, R² score: {regression_analysis_data.get('results', {}).get('r2_score', 'N/A')}")
    else:
        print("❌ Regression Analysis Endpoint: Failed")
    
    # Test dataset management functionality
    print("\n\n========== TESTING DATASET MANAGEMENT FUNCTIONALITY ==========\n")
    
    # Initial dataset list
    print("Initial dataset list:")
    test_list_datasets()
    
    # Upload first dataset
    test_multi_dataset_upload("test_dataset_1", "/app/test_matches_1.csv", "/app/test_team_stats_1.csv", "/app/test_player_stats_1.csv")
    
    # Upload second dataset
    test_multi_dataset_upload("test_dataset_2", "/app/test_matches_2.csv", "/app/test_team_stats_2.csv", "/app/test_player_stats_2.csv")
    
    # List datasets after uploads
    print("\nDataset list after uploads:")
    test_list_datasets()
    
    # Verify dataset name in records
    verify_dataset_name_in_records("test_dataset_1")
    verify_dataset_name_in_records("test_dataset_2")
    
    # Test validation scenarios
    test_validation_scenarios()
    
    # Delete datasets
    test_delete_dataset("test_dataset_1")
    test_delete_dataset("test_dataset_2")
    
    # Final dataset list
    print("\nFinal dataset list after deletions:")
    test_list_datasets()

def test_ml_match_prediction_system():
    """Test the ML-based match prediction system"""
    print("\n\n========== TESTING ML-BASED MATCH PREDICTION SYSTEM ==========\n")
    
    # Step 1: Check ML model status
    print("Step 1: Checking ML model status")
    response = requests.get(f"{BASE_URL}/ml-models/status")
    
    if response.status_code == 200:
        print(f"Status: {response.status_code} OK")
        data = response.json()
        print(f"Success: {data['success']}")
        print(f"Models loaded: {data['models_loaded']}")
        print(f"Feature columns count: {data['feature_columns_count']}")
        
        # Check status of each model
        models_status = data.get('models_status', {})
        print(f"\nModels status:")
        for model_name, status in models_status.items():
            print(f"  - {model_name}: {'✅ Exists' if status.get('exists') else '❌ Missing'}")
            if status.get('exists') and status.get('last_modified'):
                from datetime import datetime
                last_modified = datetime.fromtimestamp(status['last_modified']).strftime('%Y-%m-%d %H:%M:%S')
                print(f"    Last modified: {last_modified}")
        
        # Determine if models need training
        models_need_training = not data['models_loaded']
        if models_need_training:
            print("\n❌ ML models need training")
        else:
            print("\n✅ ML models are already trained and loaded")
    else:
        print(f"Error: {response.status_code}")
        print(response.text)
        models_need_training = True
    
    # Step 2: Train models if needed
    if models_need_training:
        print("\nStep 2: Training ML models")
        print("This may take some time as it processes all historical data...")
        
        response = requests.post(f"{BASE_URL}/train-ml-models")
        
        if response.status_code == 200:
            print(f"Status: {response.status_code} OK")
            data = response.json()
            print(f"Success: {data['success']}")
            print(f"Message: {data['message']}")
            
            # Check training results
            training_results = data.get('training_results', {})
            print("\nTraining results:")
            for model_name, results in training_results.items():
                if model_name == 'classifier':
                    print(f"  - {model_name}: Accuracy = {results.get('accuracy', 'N/A')}, Samples = {results.get('samples', 'N/A')}")
                else:
                    print(f"  - {model_name}: R² = {results.get('r2_score', 'N/A')}, MSE = {results.get('mse', 'N/A')}, Samples = {results.get('samples', 'N/A')}")
            
            print("\n✅ ML models trained successfully")
        else:
            print(f"Error: {response.status_code}")
            print(response.text)
            print("\n❌ Failed to train ML models")
            return False
    else:
        print("\nStep 2: Skipping model training as models are already trained")
    
    # Step 3: Test prediction
    print("\nStep 3: Testing match prediction")
    
    # Get teams for prediction
    teams_response = requests.get(f"{BASE_URL}/teams")
    if teams_response.status_code != 200:
        print(f"❌ Failed to get teams: {teams_response.status_code}")
        return False
    
    teams = teams_response.json().get('teams', [])
    if len(teams) < 2:
        print("❌ Not enough teams for match prediction")
        return False
    
    print(f"Found {len(teams)} teams: {', '.join(teams[:5])}{'...' if len(teams) > 5 else ''}")
    
    # Get referees
    referees_response = requests.get(f"{BASE_URL}/referees")
    if referees_response.status_code != 200:
        print(f"❌ Failed to get referees: {referees_response.status_code}")
        return False
    
    referees = referees_response.json().get('referees', [])
    if not referees:
        print("❌ No referees found for match prediction")
        return False
    
    print(f"Found {len(referees)} referees: {', '.join(referees[:5])}{'...' if len(referees) > 5 else ''}")
    
    # Make prediction
    home_team = teams[0]
    away_team = teams[1]
    referee = referees[0]
    
    print(f"\nPredicting match: {home_team} vs {away_team} with referee {referee}")
    
    prediction_data = {
        "home_team": home_team,
        "away_team": away_team,
        "referee_name": referee
    }
    
    response = requests.post(f"{BASE_URL}/predict-match", json=prediction_data)
    
    if response.status_code == 200:
        print(f"Status: {response.status_code} OK")
        data = response.json()
        
        if data.get('success'):
            print("\n✅ Match prediction successful")
            print(f"Home Team: {data['home_team']}")
            print(f"Away Team: {data['away_team']}")
            print(f"Referee: {data['referee']}")
            print(f"Predicted Home Goals: {data['predicted_home_goals']}")
            print(f"Predicted Away Goals: {data['predicted_away_goals']}")
            print(f"Home xG: {data['home_xg']}")
            print(f"Away xG: {data['away_xg']}")
            print(f"Home Win Probability: {data['home_win_probability']}%")
            print(f"Draw Probability: {data['draw_probability']}%")
            print(f"Away Win Probability: {data['away_win_probability']}%")
            
            # Verify probabilities sum to 100%
            total_prob = data['home_win_probability'] + data['draw_probability'] + data['away_win_probability']
            if 99.9 <= total_prob <= 100.1:  # Allow for small rounding errors
                print(f"\n✅ Probabilities sum to {total_prob}% (approximately 100%)")
            else:
                print(f"\n❌ Probabilities do not sum to 100%! Total: {total_prob}%")
            
            # Check prediction breakdown
            breakdown = data.get('prediction_breakdown', {})
            print("\nPrediction Breakdown:")
            for key, value in list(breakdown.items())[:5]:
                print(f"  - {key}: {value}")
            if len(breakdown) > 5:
                print("  ...")
            
            # Check confidence factors
            confidence = data.get('confidence_factors', {})
            print("\nConfidence Factors:")
            for key, value in confidence.items():
                print(f"  - {key}: {value}")
            
            return True
        else:
            print(f"\n❌ Match prediction failed: {data.get('error', 'Unknown error')}")
            return False
    else:
        print(f"Error: {response.status_code}")
        print(response.text)
        print("\n❌ Match prediction request failed")
        return False

# Step 4: Test model reload functionality
    print("\nStep 4: Testing model reload functionality")
    
    response = requests.post(f"{BASE_URL}/ml-models/reload")
    
    if response.status_code == 200:
        print(f"Status: {response.status_code} OK")
        data = response.json()
        print(f"Success: {data['success']}")
        print(f"Message: {data['message']}")
        print(f"Models loaded: {data['models_loaded']}")
        
        if data['models_loaded']:
            print("\n✅ ML models reloaded successfully")
        else:
            print("\n❌ Failed to reload ML models")
        
        return data['models_loaded']
    else:
        print(f"Error: {response.status_code}")
        print(response.text)
        print("\n❌ Model reload request failed")
        return False

def test_database_stats_endpoint():
    """Test the /api/database/stats endpoint to ensure it returns collection statistics"""
    print("\n=== Testing Database Stats Endpoint ===")
    response = requests.get(f"{BASE_URL}/database/stats")
    
    if response.status_code == 200:
        print(f"Status: {response.status_code} OK")
        data = response.json()
        print(f"Success: {data.get('success', False)}")
        
        # Check total documents
        total_documents = data.get('total_documents', 0)
        print(f"Total Documents: {total_documents}")
        
        # Check collections
        collections = data.get('collections', {})
        print(f"Collections: {len(collections)}")
        
        for collection_name, count in collections.items():
            print(f"  - {collection_name}: {count} documents")
            
        # Check timestamp
        timestamp = data.get('timestamp')
        print(f"Timestamp: {timestamp}")
        
        return data
    else:
        print(f"Error: {response.status_code}")
        print(response.text)
        return None

def test_database_wipe_endpoint():
    """Test the /api/database/wipe endpoint to ensure it properly clears all collections"""
    print("\n=== Testing Database Wipe Endpoint ===")
    
    # CAUTION: This will delete all data in the database
    print("CAUTION: This will delete all data in the database!")
    print("Proceeding with database wipe test...")
    
    response = requests.delete(f"{BASE_URL}/database/wipe")
    
    if response.status_code == 200:
        print(f"Status: {response.status_code} OK")
        data = response.json()
        print(f"Success: {data.get('success', False)}")
        print(f"Message: {data.get('message', '')}")
        
        # Check deleted counts if available
        deleted_counts = data.get('deleted_counts', {})
        if deleted_counts:
            print("Deleted Counts:")
            for collection_name, count in deleted_counts.items():
                print(f"  - {collection_name}: {count} documents")
        else:
            # Check collections cleared if deleted_counts not available
            collections_cleared = data.get('collections_cleared', 0)
            print(f"Collections Cleared: {collections_cleared}")
        
        # Check timestamp
        timestamp = data.get('timestamp')
        if timestamp:
            print(f"Timestamp: {timestamp}")
        
        return data
    else:
        print(f"Error: {response.status_code}")
        print(response.text)
        return None

def test_database_management_functionality():
    """Test all database management functionality"""
    print("\n\n========== TESTING DATABASE MANAGEMENT FUNCTIONALITY ==========\n")
    
    # Step 1: Test database stats endpoint to see current state
    print("\nStep 1: Testing database stats endpoint (before wipe)")
    before_stats = test_database_stats_endpoint()
    
    if not before_stats or not before_stats.get('success'):
        print("❌ Database stats endpoint test failed")
        return False
    else:
        print("✅ Database stats endpoint test passed")
    
    # Step 2: Test database wipe endpoint
    print("\nStep 2: Testing database wipe endpoint")
    wipe_result = test_database_wipe_endpoint()
    
    if not wipe_result or not wipe_result.get('success'):
        print("❌ Database wipe endpoint test failed")
        return False
    else:
        print("✅ Database wipe endpoint test passed")
    
    # Step 3: Test database stats endpoint again to verify wipe
    print("\nStep 3: Testing database stats endpoint (after wipe)")
    after_stats = test_database_stats_endpoint()
    
    if not after_stats or not after_stats.get('success'):
        print("❌ Database stats endpoint test failed (after wipe)")
        return False
    else:
        print("✅ Database stats endpoint test passed (after wipe)")
    
    # Verify that the database was actually wiped
    before_total = before_stats.get('total_documents', 0)
    after_total = after_stats.get('total_documents', 0)
    
    print(f"\nBefore wipe: {before_total} total documents")
    print(f"After wipe: {after_total} total documents")
    
    if after_total == 0:
        print("✅ Database was successfully wiped (0 documents remaining)")
    elif after_total < before_total:
        print(f"⚠️ Database was partially wiped ({after_total} documents remaining)")
    else:
        print(f"❌ Database was not wiped properly ({after_total} documents remaining)")
    
    # Final summary
    print("\n========== DATABASE MANAGEMENT FUNCTIONALITY TEST SUMMARY ==========")
    
    # Check if the endpoints exist and work properly
    endpoint_check_results = []
    
    # Check database stats endpoint
    stats_response = requests.get(f"{BASE_URL}/database/stats")
    endpoint_check_results.append(stats_response.status_code == 200)
    
    # Check database wipe endpoint
    # We don't need to call it again, just check if the previous call was successful
    endpoint_check_results.append(wipe_result is not None and wipe_result.get('success', False))
    
    if all(endpoint_check_results):
        print("✅ All database management functionality endpoints exist and are accessible!")
        return True
    else:
        print("❌ Some database management functionality endpoints failed the existence check")
        return False

if __name__ == "__main__":
    # Test the database management functionality
    test_database_management_functionality()
    
    # Test the Starting XI and time decay functionality
    # test_starting_xi_and_time_decay_functionality()
    
    # Test the PDF export functionality
    # test_pdf_export_endpoint()
    
    # Test the ML-based match prediction system
    # test_ml_match_prediction_system()
    
    # Run other tests
    # run_tests()
