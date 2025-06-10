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

def test_rbs_status_endpoint():
    """Test the /api/rbs-status endpoint to check RBS calculation status"""
    print("\n=== Testing RBS Status Endpoint ===")
    response = requests.get(f"{BASE_URL}/rbs-status")
    
    if response.status_code == 200:
        print(f"Status: {response.status_code} OK")
        data = response.json()
        print(f"Success: {data.get('success', False)}")
        
        # Check if RBS is calculated
        calculated = data.get('calculated', False)
        print(f"RBS Calculated: {calculated}")
        
        # Check other status information
        if 'referees_analyzed' in data:
            print(f"Referees Analyzed: {data['referees_analyzed']}")
        if 'teams_covered' in data:
            print(f"Teams Covered: {data['teams_covered']}")
        if 'total_calculations' in data:
            print(f"Total Calculations: {data['total_calculations']}")
        if 'last_calculated' in data:
            print(f"Last Calculated: {data['last_calculated']}")
        
        return data
    else:
        print(f"Error: {response.status_code}")
        print(response.text)
        return None

def test_calculate_rbs_endpoint():
    """Test the /api/calculate-rbs endpoint to verify no time decay is used"""
    print("\n=== Testing Calculate RBS Endpoint (No Time Decay) ===")
    
    response = requests.post(f"{BASE_URL}/calculate-rbs")
    
    if response.status_code == 200:
        print(f"Status: {response.status_code} OK")
        data = response.json()
        print(f"Success: {data.get('success', False)}")
        
        # Check calculation results
        if 'results_count' in data:
            print(f"Calculations Performed: {data['results_count']}")
        if 'config_used' in data:
            print(f"Configuration Used: {data['config_used']}")
        
        # Verify the message doesn't mention time decay
        message = data.get('message', '')
        print(f"Message: {message}")
        
        if 'time decay' in message.lower() or 'time-decay' in message.lower():
            print("❌ Message mentions time decay, which should not be used")
        else:
            print("✅ No mention of time decay in the response")
        
        return data
    else:
        print(f"Error: {response.status_code}")
        print(response.text)
        return None

def test_referee_analysis_list_endpoint():
    """Test the /api/referee-analysis endpoint to get list of referees with RBS scores"""
    print("\n=== Testing Referee Analysis List Endpoint ===")
    response = requests.get(f"{BASE_URL}/referee-analysis")
    
    if response.status_code == 200:
        print(f"Status: {response.status_code} OK")
        data = response.json()
        print(f"Success: {data.get('success', False)}")
        
        # Check referees list
        referees = data.get('referees', [])
        print(f"Referees Found: {len(referees)}")
        
        if referees:
            print("\nSample Referees:")
            for referee in referees[:5]:  # Show first 5 referees
                print(f"\n  - Name: {referee.get('name')}")
                print(f"    Matches: {referee.get('matches')}")
                print(f"    Teams: {referee.get('teams')}")
                print(f"    Avg Bias Score: {referee.get('avg_bias_score')}")
                print(f"    Confidence: {referee.get('confidence')}")
            
            if len(referees) > 5:
                print("  ...")
            
            # Check for null/undefined RBS scores
            null_rbs_scores = [ref for ref in referees if ref.get('avg_bias_score') is None]
            if null_rbs_scores:
                print(f"\n❌ Found {len(null_rbs_scores)} referees with null RBS scores")
                for ref in null_rbs_scores[:3]:  # Show first 3 with null scores
                    print(f"  - {ref.get('name')}")
                if len(null_rbs_scores) > 3:
                    print("  ...")
            else:
                print("\n✅ All referees have numerical RBS scores")
            
            # Verify required fields
            required_fields = ['name', 'matches', 'teams', 'avg_bias_score', 'confidence']
            missing_fields = []
            
            for field in required_fields:
                if any(field not in ref or ref[field] is None for ref in referees):
                    missing_fields.append(field)
            
            if missing_fields:
                print(f"\n❌ Missing required fields in some referee records: {', '.join(missing_fields)}")
            else:
                print("\n✅ All required fields are present in referee records")
        
        return data
    else:
        print(f"Error: {response.status_code}")
        print(response.text)
        return None

def test_referee_analysis_detail_endpoint(referee_name="Andrew Kitchen"):
    """Test the /api/referee-analysis/{referee_name} endpoint to verify RBS data structure"""
    print(f"\n=== Testing Referee Analysis Detail Endpoint for {referee_name} ===")
    
    # URL encode the referee name
    import urllib.parse
    encoded_name = urllib.parse.quote(referee_name)
    
    response = requests.get(f"{BASE_URL}/referee-analysis/{encoded_name}")
    
    if response.status_code == 200:
        print(f"Status: {response.status_code} OK")
        data = response.json()
        print(f"Success: {data.get('success', False)}")
        
        # Check basic referee info
        print(f"Referee Name: {data.get('referee_name')}")
        print(f"Total Matches: {data.get('total_matches')}")
        print(f"Teams Officiated: {data.get('teams_officiated')}")
        print(f"Average Bias Score: {data.get('avg_bias_score')}")
        
        # Check team RBS details
        team_rbs_details = data.get('team_rbs_details', {})
        if team_rbs_details:
            print(f"\nTeam RBS Details: {len(team_rbs_details)} teams")
            
            # Check for Arsenal and Chelsea
            target_teams = ['Arsenal', 'Chelsea']
            found_teams = []
            
            for team_name, team_detail in team_rbs_details.items():
                if team_name in target_teams:
                    found_teams.append(team_name)
                    print(f"\n  Team: {team_name}")
                    
                    # Check required fields
                    required_fields = [
                        'rbs_score', 'rbs_raw', 'matches_with_ref', 
                        'matches_without_ref', 'confidence_level', 
                        'stats_breakdown', 'config_used'
                    ]
                    
                    missing_fields = [field for field in required_fields if field not in team_detail]
                    
                    if missing_fields:
                        print(f"  ❌ Missing required fields: {', '.join(missing_fields)}")
                    else:
                        print("  ✅ All required fields are present")
                        
                        # Print the values of the fields
                        print(f"  RBS Score (normalized): {team_detail.get('rbs_score')}")
                        print(f"  RBS Raw: {team_detail.get('rbs_raw')}")
                        print(f"  Matches with Referee: {team_detail.get('matches_with_ref')}")
                        print(f"  Matches without Referee: {team_detail.get('matches_without_ref')}")
                        print(f"  Confidence Level: {team_detail.get('confidence_level')}%")
                        print(f"  Config Used: {team_detail.get('config_used')}")
                        
                        # Check stats breakdown
                        stats_breakdown = team_detail.get('stats_breakdown', {})
                        print("\n  Stats Breakdown:")
                        
                        required_factors = [
                            'yellow_cards', 'red_cards', 'fouls_committed',
                            'fouls_drawn', 'penalties_awarded'
                        ]
                        
                        missing_factors = [factor for factor in required_factors if factor not in stats_breakdown]
                        
                        if missing_factors:
                            print(f"  ❌ Missing required factors: {', '.join(missing_factors)}")
                        else:
                            print("  ✅ All required factors are present")
                            
                            # Print the values of the factors
                            for factor, value in stats_breakdown.items():
                                print(f"    {factor}: {value}")
            
            # Check if both Arsenal and Chelsea were found
            missing_teams = [team for team in target_teams if team not in found_teams]
            if missing_teams:
                print(f"\n❌ Missing teams: {', '.join(missing_teams)}")
            else:
                print("\n✅ Both Arsenal and Chelsea have complete RBS data")
        else:
            print("\n❌ No team RBS details found")
        
        return data
    else:
        print(f"Error: {response.status_code}")
        print(response.text)
        return None

def test_referee_analysis_error_handling():
    """Test error handling for non-existent referee name"""
    print("\n=== Testing Referee Analysis Error Handling ===")
    
    non_existent_referee = "NonExistentReferee"
    response = requests.get(f"{BASE_URL}/referee-analysis/{non_existent_referee}")
    
    print(f"Status: {response.status_code}")
    
    if response.status_code == 404:
        print("✅ Proper 404 error returned for non-existent referee")
    elif response.status_code == 400:
        print("✅ Proper 400 error returned for non-existent referee")
    elif response.status_code == 200:
        data = response.json()
        if not data.get('success', False):
            print("✅ Success: false returned for non-existent referee")
            print(f"Error message: {data.get('error', 'No error message')}")
        else:
            print("❌ Unexpected success response for non-existent referee")
    else:
        print(f"❌ Unexpected status code: {response.status_code}")
        print(response.text)
    
    return response

def test_enhanced_rbs_functionality():
    """Test all enhanced RBS functionality without time decay"""
    print("\n\n========== TESTING ENHANCED RBS FUNCTIONALITY WITHOUT TIME DECAY ==========\n")
    
    # Step 1: Check RBS Status
    print("\nStep 1: Testing RBS Status")
    status_data = test_rbs_status_endpoint()
    
    if not status_data:
        print("❌ RBS Status endpoint test failed")
    elif not status_data.get('success', False):
        print("❌ RBS Status endpoint returned success: false")
    else:
        print("✅ RBS Status endpoint test passed")
    
    # Step 2: Calculate RBS
    print("\nStep 2: Testing Calculate RBS (No Time Decay)")
    calc_data = test_calculate_rbs_endpoint()
    
    if not calc_data:
        print("❌ Calculate RBS endpoint test failed")
    elif not calc_data.get('success', False):
        print("❌ Calculate RBS endpoint returned success: false")
    else:
        print("✅ Calculate RBS endpoint test passed")
    
    # Step 3: Get Referee Analysis List
    print("\nStep 3: Testing Referee Analysis List")
    list_data = test_referee_analysis_list_endpoint()
    
    if not list_data:
        print("❌ Referee Analysis List endpoint test failed")
    elif not list_data.get('success', False):
        print("❌ Referee Analysis List endpoint returned success: false")
    else:
        print("✅ Referee Analysis List endpoint test passed")
    
    # Step 4: Get Detailed Referee Analysis for Andrew Kitchen
    print("\nStep 4: Testing Detailed Referee Analysis for Andrew Kitchen")
    detail_data = test_referee_analysis_detail_endpoint("Andrew Kitchen")
    
    if not detail_data:
        print("❌ Detailed Referee Analysis endpoint test failed")
    elif not detail_data.get('success', False):
        print("❌ Detailed Referee Analysis endpoint returned success: false")
    else:
        print("✅ Detailed Referee Analysis endpoint test passed")
    
    # Step 5: Test Error Handling
    print("\nStep 5: Testing Error Handling for Non-existent Referee")
    error_response = test_referee_analysis_error_handling()
    
    # Final summary
    print("\n========== ENHANCED RBS FUNCTIONALITY TEST SUMMARY ==========")
    
    # Check if all endpoints exist and work properly
    endpoint_check_results = []
    
    # Check RBS Status endpoint
    status_response = requests.get(f"{BASE_URL}/rbs-status")
    endpoint_check_results.append(status_response.status_code == 200)
    
    # Check Calculate RBS endpoint
    calc_response = requests.post(f"{BASE_URL}/calculate-rbs")
    endpoint_check_results.append(calc_response.status_code == 200)
    
    # Check Referee Analysis List endpoint
    list_response = requests.get(f"{BASE_URL}/referee-analysis")
    endpoint_check_results.append(list_response.status_code == 200)
    
    # Check Detailed Referee Analysis endpoint
    detail_response = requests.get(f"{BASE_URL}/referee-analysis/Andrew%20Kitchen")
    endpoint_check_results.append(detail_response.status_code == 200)
    
    if all(endpoint_check_results):
        print("✅ All enhanced RBS functionality endpoints exist and are accessible!")
        
        # Check for required fields in team RBS details
        if detail_data and detail_data.get('success', False):
            team_rbs_details = detail_data.get('team_rbs_details', {})
            
            if team_rbs_details:
                # Check for Arsenal and Chelsea
                target_teams = ['Arsenal', 'Chelsea']
                found_teams = []
                all_fields_present = True
                all_factors_present = True
                
                for team_name, team_detail in team_rbs_details.items():
                    if team_name in target_teams:
                        found_teams.append(team_name)
                        
                        # Check required fields
                        required_fields = [
                            'rbs_score', 'rbs_raw', 'matches_with_ref', 
                            'matches_without_ref', 'confidence_level', 
                            'stats_breakdown', 'config_used'
                        ]
                        
                        if not all(field in team_detail for field in required_fields):
                            all_fields_present = False
                        
                        # Check stats breakdown
                        stats_breakdown = team_detail.get('stats_breakdown', {})
                        required_factors = [
                            'yellow_cards', 'red_cards', 'fouls_committed',
                            'fouls_drawn', 'penalties_awarded'
                        ]
                        
                        if not all(factor in stats_breakdown for factor in required_factors):
                            all_factors_present = False
                
                if len(found_teams) < len(target_teams):
                    print(f"❌ Missing teams: {', '.join([team for team in target_teams if team not in found_teams])}")
                else:
                    print("✅ Both Arsenal and Chelsea have RBS data")
                
                if not all_fields_present:
                    print("❌ Some required fields are missing in team RBS details")
                else:
                    print("✅ All required fields are present in team RBS details")
                
                if not all_factors_present:
                    print("❌ Some required factors are missing in stats breakdown")
                else:
                    print("✅ All 5 calculation factors are present in stats breakdown")
                
                # Final verdict
                if len(found_teams) == len(target_teams) and all_fields_present and all_factors_present:
                    print("\n✅ OVERALL: Enhanced RBS functionality is working correctly without time decay")
                else:
                    print("\n❌ OVERALL: Enhanced RBS functionality has issues")
            else:
                print("❌ No team RBS details found")
        else:
            print("❌ Could not verify team RBS details")
        
        return True
    else:
        print("❌ Some enhanced RBS functionality endpoints failed the existence check")
        return False

def test_stored_predictions_endpoint():
    """Test the /api/stored-predictions endpoint to retrieve predictions with filtering"""
    print("\n=== Testing Stored Predictions Endpoint ===")
    
    # Test with default parameters
    response = requests.get(f"{BASE_URL}/stored-predictions")
    
    if response.status_code == 200:
        print(f"Status: {response.status_code} OK")
        data = response.json()
        print(f"Success: {data.get('success', False)}")
        
        # Check predictions list
        predictions = data.get('predictions', [])
        print(f"Predictions Found: {len(predictions)}")
        
        # Check available methods
        available_methods = data.get('available_methods', [])
        print(f"Available Prediction Methods: {available_methods}")
        
        # Check if we have predictions
        if predictions:
            print("\nSample Predictions:")
            for prediction in predictions[:3]:  # Show first 3 predictions
                print(f"\n  - ID: {prediction.get('prediction_id')}")
                print(f"    Timestamp: {prediction.get('timestamp')}")
                print(f"    Teams: {prediction.get('home_team')} vs {prediction.get('away_team')}")
                print(f"    Method: {prediction.get('prediction_method')}")
                print(f"    Predicted Goals: {prediction.get('predicted_home_goals')} - {prediction.get('predicted_away_goals')}")
            
            if len(predictions) > 3:
                print("  ...")
            
            # Verify required fields
            required_fields = [
                'prediction_id', 'timestamp', 'home_team', 'away_team', 
                'referee', 'prediction_method', 'predicted_home_goals', 
                'predicted_away_goals', 'home_xg', 'away_xg', 
                'home_win_probability', 'draw_probability', 'away_win_probability'
            ]
            
            missing_fields = []
            for field in required_fields:
                if any(field not in pred for pred in predictions):
                    missing_fields.append(field)
            
            if missing_fields:
                print(f"\n❌ Missing required fields in some prediction records: {', '.join(missing_fields)}")
            else:
                print("\n✅ All required fields are present in prediction records")
        
        # Test with method filter if available
        if available_methods:
            test_method = available_methods[0]
            print(f"\nTesting with method filter: {test_method}")
            
            method_response = requests.get(f"{BASE_URL}/stored-predictions?method={test_method}")
            
            if method_response.status_code == 200:
                method_data = method_response.json()
                method_predictions = method_data.get('predictions', [])
                
                print(f"Filtered Predictions Found: {len(method_predictions)}")
                
                # Verify all predictions have the requested method
                if method_predictions:
                    incorrect_methods = [p for p in method_predictions if p.get('prediction_method') != test_method]
                    
                    if incorrect_methods:
                        print(f"❌ Found {len(incorrect_methods)} predictions with incorrect method")
                    else:
                        print(f"✅ All filtered predictions have the correct method: {test_method}")
            else:
                print(f"❌ Method filter request failed: {method_response.status_code}")
        
        return data
    else:
        print(f"Error: {response.status_code}")
        print(response.text)
        return None

def test_prediction_stats_endpoint():
    """Test the /api/stored-predictions/stats endpoint for prediction statistics"""
    print("\n=== Testing Prediction Statistics Endpoint ===")
    
    response = requests.get(f"{BASE_URL}/stored-predictions/stats")
    
    if response.status_code == 200:
        print(f"Status: {response.status_code} OK")
        data = response.json()
        print(f"Success: {data.get('success', False)}")
        
        # Check total predictions
        total_predictions = data.get('total_predictions', 0)
        print(f"Total Predictions: {total_predictions}")
        
        # Check recent predictions
        recent_predictions = data.get('recent_predictions_7_days', 0)
        print(f"Recent Predictions (7 days): {recent_predictions}")
        
        # Check method breakdown
        method_breakdown = data.get('method_breakdown', {})
        if method_breakdown:
            print("\nPrediction Method Breakdown:")
            for method, count in method_breakdown.items():
                print(f"  - {method}: {count} predictions")
        
        # Check storage status
        storage_enabled = data.get('storage_enabled', False)
        print(f"\nPrediction Storage Enabled: {storage_enabled}")
        
        return data
    else:
        print(f"Error: {response.status_code}")
        print(response.text)
        return None

def test_data_summary_endpoint():
    """Test the /api/data-summary endpoint for comprehensive data overview"""
    print("\n=== Testing Data Summary Endpoint ===")
    
    response = requests.get(f"{BASE_URL}/data-summary")
    
    if response.status_code == 200:
        print(f"Status: {response.status_code} OK")
        data = response.json()
        print(f"Success: {data.get('success', False)}")
        
        # Check data counts
        data_counts = data.get('data_counts', {})
        if data_counts:
            print("\nData Counts:")
            for collection, count in data_counts.items():
                print(f"  - {collection}: {count} documents")
        
        # Check unique entities
        unique_entities = data.get('unique_entities', {})
        if unique_entities:
            print("\nUnique Entities:")
            for entity_type, count in unique_entities.items():
                print(f"  - {entity_type}: {count}")
        
        # Check data range
        data_range = data.get('data_range', {})
        if data_range:
            print("\nData Date Range:")
            print(f"  - Oldest: {data_range.get('oldest')}")
            print(f"  - Newest: {data_range.get('newest')}")
        
        # Check total documents
        total_documents = data.get('total_documents', 0)
        print(f"\nTotal Documents: {total_documents}")
        
        # Check optimization readiness
        optimization_ready = data.get('optimization_ready', False)
        print(f"Optimization Ready: {optimization_ready}")
        
        return data
    else:
        print(f"Error: {response.status_code}")
        print(response.text)
        return None

def test_prediction_storage_clear_endpoint():
    """Test the /api/prediction-storage endpoint to clear stored predictions"""
    print("\n=== Testing Prediction Storage Clear Endpoint ===")
    
    # CAUTION: This will delete all stored predictions
    print("CAUTION: This will delete all stored predictions!")
    print("Proceeding with prediction storage clear test...")
    
    response = requests.delete(f"{BASE_URL}/prediction-storage")
    
    if response.status_code == 200:
        print(f"Status: {response.status_code} OK")
        data = response.json()
        print(f"Success: {data.get('success', False)}")
        print(f"Message: {data.get('message', '')}")
        
        # Check deleted count
        deleted_count = data.get('deleted_count', 0)
        print(f"Deleted Count: {deleted_count} predictions")
        
        return data
    else:
        print(f"Error: {response.status_code}")
        print(response.text)
        return None

def test_make_prediction_and_verify_storage(prediction_type="standard"):
    """Make a prediction and verify it's stored in the database"""
    print(f"\n=== Testing Prediction Storage for {prediction_type.capitalize()} Prediction ===")
    
    # Define prediction data based on type
    if prediction_type == "standard":
        endpoint = f"{BASE_URL}/predict-match"
        prediction_data = {
            "home_team": "Arsenal",
            "away_team": "Chelsea",
            "referee_name": "Michael Oliver",
            "match_date": datetime.now().strftime("%Y-%m-%d")
        }
    elif prediction_type == "enhanced":
        endpoint = f"{BASE_URL}/predict-match-enhanced"
        prediction_data = {
            "home_team": "Arsenal",
            "away_team": "Chelsea",
            "referee_name": "Michael Oliver",
            "match_date": datetime.now().strftime("%Y-%m-%d"),
            "use_time_decay": True,
            "decay_preset": "moderate"
        }
    elif prediction_type == "ensemble":
        endpoint = f"{BASE_URL}/predict-match-ensemble"
        prediction_data = {
            "home_team": "Arsenal",
            "away_team": "Chelsea",
            "referee_name": "Michael Oliver",
            "match_date": datetime.now().strftime("%Y-%m-%d")
        }
    else:
        print(f"❌ Unknown prediction type: {prediction_type}")
        return None
    
    # Make the prediction
    print(f"Making {prediction_type} prediction...")
    response = requests.post(endpoint, json=prediction_data)
    
    if response.status_code == 200:
        print(f"Status: {response.status_code} OK")
        prediction_result = response.json()
        
        if not prediction_result.get('success', False):
            print(f"❌ Prediction failed: {prediction_result.get('error', 'Unknown error')}")
            return None
        
        print("✅ Prediction successful")
        
        # Check if prediction has an ID
        prediction_id = None
        if 'prediction_id' in prediction_result:
            prediction_id = prediction_result['prediction_id']
            print(f"Prediction ID: {prediction_id}")
        else:
            print("❌ No prediction ID returned")
            return prediction_result
        
        # Verify the prediction is stored
        print("\nVerifying prediction storage...")
        time.sleep(1)  # Give a moment for async storage to complete
        
        storage_response = requests.get(f"{BASE_URL}/stored-predictions")
        
        if storage_response.status_code == 200:
            storage_data = storage_response.json()
            stored_predictions = storage_data.get('predictions', [])
            
            # Look for our prediction ID
            matching_predictions = [p for p in stored_predictions if p.get('prediction_id') == prediction_id]
            
            if matching_predictions:
                print("✅ Prediction successfully stored in database")
                stored_prediction = matching_predictions[0]
                
                # Verify prediction method
                expected_method = {
                    "standard": "standard",
                    "enhanced": "enhanced_xgboost",
                    "ensemble": "ensemble"
                }.get(prediction_type)
                
                actual_method = stored_prediction.get('prediction_method')
                
                if actual_method == expected_method:
                    print(f"✅ Correct prediction method stored: {actual_method}")
                else:
                    print(f"❌ Incorrect prediction method stored: {actual_method} (expected {expected_method})")
                
                # Verify teams
                if (stored_prediction.get('home_team') == prediction_data['home_team'] and 
                    stored_prediction.get('away_team') == prediction_data['away_team']):
                    print("✅ Team information correctly stored")
                else:
                    print("❌ Team information incorrectly stored")
                
                # Verify referee
                if stored_prediction.get('referee') == prediction_data['referee_name']:
                    print("✅ Referee information correctly stored")
                else:
                    print("❌ Referee information incorrectly stored")
                
                # Verify enhanced features if applicable
                if prediction_type == "enhanced":
                    time_decay_used = stored_prediction.get('time_decay_used', False)
                    if time_decay_used:
                        print("✅ Time decay flag correctly stored")
                    else:
                        print("❌ Time decay flag incorrectly stored")
                
                return stored_prediction
            else:
                print("❌ Prediction not found in storage")
                return None
        else:
            print(f"❌ Failed to verify storage: {storage_response.status_code}")
            return None
    else:
        print(f"Error: {response.status_code}")
        print(response.text)
        return None

def test_cross_session_persistence():
    """Test that data persists between backend restarts"""
    print("\n=== Testing Cross-Session Persistence ===")
    
    # Step 1: Get current database stats
    print("\nStep 1: Getting current database stats")
    before_stats = test_database_stats_endpoint()
    
    if not before_stats or not before_stats.get('success'):
        print("❌ Failed to get database stats")
        return False
    
    before_total = before_stats.get('total_documents', 0)
    print(f"Current total documents: {before_total}")
    
    # Step 2: Restart the backend
    print("\nStep 2: Restarting backend")
    restart_response = os.system("sudo supervisorctl restart backend")
    
    if restart_response != 0:
        print(f"❌ Failed to restart backend: {restart_response}")
        return False
    
    print("Backend restarted")
    
    # Wait for backend to come back up
    print("Waiting for backend to restart...")
    max_retries = 10
    retry_count = 0
    backend_up = False
    
    while retry_count < max_retries and not backend_up:
        try:
            time.sleep(2)  # Wait 2 seconds between retries
            response = requests.get(f"{BASE_URL}/database/stats")
            if response.status_code == 200:
                backend_up = True
                print("Backend is up!")
            else:
                retry_count += 1
                print(f"Retry {retry_count}/{max_retries}...")
        except Exception as e:
            retry_count += 1
            print(f"Retry {retry_count}/{max_retries}... ({str(e)})")
    
    if not backend_up:
        print("❌ Backend did not come back up after restart")
        return False
    
    # Step 3: Get database stats after restart
    print("\nStep 3: Getting database stats after restart")
    after_stats = test_database_stats_endpoint()
    
    if not after_stats or not after_stats.get('success'):
        print("❌ Failed to get database stats after restart")
        return False
    
    after_total = after_stats.get('total_documents', 0)
    print(f"Total documents after restart: {after_total}")
    
    # Compare document counts
    if after_total == before_total:
        print("✅ Data persisted correctly between backend restarts")
        
        # Check collections
        before_collections = before_stats.get('collections', {})
        after_collections = after_stats.get('collections', {})
        
        collection_diffs = []
        for collection, count in before_collections.items():
            if collection in after_collections:
                if after_collections[collection] != count:
                    collection_diffs.append(f"{collection}: {count} -> {after_collections[collection]}")
            else:
                collection_diffs.append(f"{collection}: {count} -> missing")
        
        for collection, count in after_collections.items():
            if collection not in before_collections:
                collection_diffs.append(f"{collection}: missing -> {count}")
        
        if collection_diffs:
            print("❌ Collection differences detected:")
            for diff in collection_diffs:
                print(f"  - {diff}")
            return False
        else:
            print("✅ All collections maintained the same document counts")
            return True
    else:
        print(f"❌ Data did not persist correctly: {before_total} -> {after_total} documents")
        return False

def test_data_persistence_and_storage():
    """Test comprehensive data persistence and storage functionality"""
    print("\n\n========== TESTING DATA PERSISTENCE & STORAGE FUNCTIONALITY ==========\n")
    
    # Step 1: Test data summary endpoint
    print("\nStep 1: Testing Data Summary Endpoint")
    summary_data = test_data_summary_endpoint()
    
    if not summary_data or not summary_data.get('success'):
        print("❌ Data summary endpoint test failed")
    else:
        print("✅ Data summary endpoint test passed")
        
        # Verify data counts match expected values
        data_counts = summary_data.get('data_counts', {})
        expected_counts = {
            'matches': 2264,
            'team_stats': 4528,
            'player_stats': 68038,
            'predictions': 3,
            'rbs_results': 833
        }
        
        count_mismatches = []
        for collection, expected in expected_counts.items():
            actual = data_counts.get(collection, 0)
            if abs(actual - expected) > expected * 0.1:  # Allow 10% variance
                count_mismatches.append(f"{collection}: expected ~{expected}, got {actual}")
        
        if count_mismatches:
            print("⚠️ Some collection counts differ significantly from expected values:")
            for mismatch in count_mismatches:
                print(f"  - {mismatch}")
        else:
            print("✅ Collection counts are within expected ranges")
    
    # Step 2: Test stored predictions endpoint
    print("\nStep 2: Testing Stored Predictions Endpoint")
    predictions_data = test_stored_predictions_endpoint()
    
    if not predictions_data or not predictions_data.get('success'):
        print("❌ Stored predictions endpoint test failed")
    else:
        print("✅ Stored predictions endpoint test passed")
    
    # Step 3: Test prediction statistics endpoint
    print("\nStep 3: Testing Prediction Statistics Endpoint")
    stats_data = test_prediction_stats_endpoint()
    
    if not stats_data or not stats_data.get('success'):
        print("❌ Prediction statistics endpoint test failed")
    else:
        print("✅ Prediction statistics endpoint test passed")
    
    # Step 4: Test making and storing predictions of different types
    print("\nStep 4: Testing Prediction Storage for Different Prediction Types")
    
    # Standard prediction
    standard_prediction = test_make_prediction_and_verify_storage("standard")
    standard_success = standard_prediction is not None
    
    # Enhanced prediction
    enhanced_prediction = test_make_prediction_and_verify_storage("enhanced")
    enhanced_success = enhanced_prediction is not None
    
    # Ensemble prediction
    ensemble_prediction = test_make_prediction_and_verify_storage("ensemble")
    ensemble_success = ensemble_prediction is not None
    
    # Step 5: Test cross-session persistence
    print("\nStep 5: Testing Cross-Session Persistence")
    persistence_success = test_cross_session_persistence()
    
    # Final summary
    print("\n========== DATA PERSISTENCE & STORAGE FUNCTIONALITY TEST SUMMARY ==========")
    
    # Check if all endpoints exist and work properly
    endpoint_check_results = []
    
    # Check data summary endpoint
    summary_response = requests.get(f"{BASE_URL}/data-summary")
    endpoint_check_results.append(summary_response.status_code == 200)
    
    # Check stored predictions endpoint
    predictions_response = requests.get(f"{BASE_URL}/stored-predictions")
    endpoint_check_results.append(predictions_response.status_code == 200)
    
    # Check prediction statistics endpoint
    stats_response = requests.get(f"{BASE_URL}/stored-predictions/stats")
    endpoint_check_results.append(stats_response.status_code == 200)
    
    # Check prediction storage clear endpoint
    clear_response = requests.delete(f"{BASE_URL}/prediction-storage")
    endpoint_check_results.append(clear_response.status_code == 200)
    
    if all(endpoint_check_results):
        print("✅ All data persistence and storage endpoints exist and are accessible!")
        
        # Check prediction storage functionality
        prediction_storage_results = [standard_success, enhanced_success, ensemble_success]
        if all(prediction_storage_results):
            print("✅ All prediction types are successfully stored")
        else:
            failed_types = []
            if not standard_success:
                failed_types.append("Standard")
            if not enhanced_success:
                failed_types.append("Enhanced")
            if not ensemble_success:
                failed_types.append("Ensemble")
            
            print(f"❌ Failed to store some prediction types: {', '.join(failed_types)}")
        
        # Check cross-session persistence
        if persistence_success:
            print("✅ Data successfully persists between backend restarts")
        else:
            print("❌ Data does not persist correctly between backend restarts")
        
        # Final verdict
        if all(prediction_storage_results) and persistence_success:
            print("\n✅ OVERALL: Data persistence and storage functionality is working correctly")
            return True
        else:
            print("\n❌ OVERALL: Data persistence and storage functionality has issues")
            return False
    else:
        print("❌ Some data persistence and storage endpoints failed the existence check")
        return False

if __name__ == "__main__":
    # Test data persistence and storage functionality
    test_data_persistence_and_storage()
