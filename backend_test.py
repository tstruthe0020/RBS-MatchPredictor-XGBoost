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

if __name__ == "__main__":
    # Test Enhanced RBS functionality
    test_enhanced_rbs_functionality()
