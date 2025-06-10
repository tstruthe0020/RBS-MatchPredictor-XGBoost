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
    """Test the /api/calculate-rbs endpoint to trigger RBS calculations"""
    print("\n=== Testing Calculate RBS Endpoint ===")
    
    # This is a POST request with no body required
    response = requests.post(f"{BASE_URL}/calculate-rbs")
    
    if response.status_code == 200:
        print(f"Status: {response.status_code} OK")
        data = response.json()
        print(f"Success: {data.get('success', False)}")
        
        # Check calculation results
        if 'calculations_performed' in data:
            print(f"Calculations Performed: {data['calculations_performed']}")
        if 'teams_analyzed' in data:
            print(f"Teams Analyzed: {data['teams_analyzed']}")
        if 'referees_analyzed' in data:
            print(f"Referees Analyzed: {data['referees_analyzed']}")
        if 'calculation_time' in data:
            print(f"Calculation Time: {data['calculation_time']} seconds")
        
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

def test_referee_analysis_detail_endpoint(referee_name="Michael Oliver"):
    """Test the /api/referee-analysis/{referee_name} endpoint to get detailed analysis for a specific referee"""
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
        
        # Check RBS calculations
        rbs_calculations = data.get('rbs_calculations', [])
        if isinstance(rbs_calculations, list):
            print(f"\nRBS Calculations: {len(rbs_calculations)}")
            
            if rbs_calculations:
                print("\nSample Team RBS Scores:")
                for calc in rbs_calculations[:3]:  # Show first 3 calculations
                    print(f"  - Team: {calc.get('team_name')}")
                    print(f"    RBS Score: {calc.get('rbs_score')}")
                    print(f"    Confidence: {calc.get('confidence_level')}")
                    print(f"    Matches with Referee: {calc.get('matches_with_ref')}")
                
                if len(rbs_calculations) > 3:
                    print("  ...")
        else:
            print(f"\nRBS Calculations: {rbs_calculations}")
        
        # Check match outcomes
        match_outcomes = data.get('match_outcomes', {})
        if match_outcomes:
            print("\nMatch Outcomes:")
            print(f"  Home Wins: {match_outcomes.get('home_wins')}")
            print(f"  Draws: {match_outcomes.get('draws')}")
            print(f"  Away Wins: {match_outcomes.get('away_wins')}")
            print(f"  Home Win %: {match_outcomes.get('home_win_percentage')}%")
        
        # Check cards and fouls
        cards_and_fouls = data.get('cards_and_fouls', {})
        if cards_and_fouls:
            print("\nCards and Fouls:")
            print(f"  Avg Yellow Cards: {cards_and_fouls.get('avg_yellow_cards')}")
            print(f"  Avg Red Cards: {cards_and_fouls.get('avg_red_cards')}")
            print(f"  Avg Fouls: {cards_and_fouls.get('avg_fouls')}")
        
        # Check bias analysis
        bias_analysis = data.get('bias_analysis', {})
        if bias_analysis:
            print("\nBias Analysis:")
            
            most_biased = bias_analysis.get('most_biased_teams', [])
            if most_biased:
                print("  Most Biased Teams:")
                for team in most_biased[:3]:
                    print(f"    - {team.get('team')}: {team.get('rbs_score')}")
            
            least_biased = bias_analysis.get('least_biased_teams', [])
            if least_biased:
                print("  Least Biased Teams:")
                for team in least_biased[:3]:
                    print(f"    - {team.get('team')}: {team.get('rbs_score')}")
        
        # Check team RBS details
        team_rbs_details = data.get('team_rbs_details', [])
        if isinstance(team_rbs_details, list):
            print(f"\nTeam RBS Details: {len(team_rbs_details)} teams")
            
            for team_detail in team_rbs_details[:2]:  # Show first 2 team details
                print(f"\n  Team: {team_detail.get('team_name')}")
                print(f"  RBS Score: {team_detail.get('rbs_score')}")
                
                # Check stat differentials
                stat_diffs = team_detail.get('stat_differentials', {})
                if stat_diffs:
                    print("  Stat Differentials:")
                    for stat, diff in stat_diffs.items():
                        print(f"    - {stat}: {diff}")
            
            if len(team_rbs_details) > 2:
                print("  ...")
        elif isinstance(team_rbs_details, dict):
            print(f"\nTeam RBS Details: {len(team_rbs_details.keys())} teams")
            
            for i, (team_name, team_detail) in enumerate(team_rbs_details.items()):
                if i >= 2:  # Only show first 2 team details
                    break
                    
                print(f"\n  Team: {team_name}")
                print(f"  RBS Score: {team_detail.get('rbs_score')}")
                
                # Check stat differentials
                stat_diffs = team_detail.get('stat_differentials', {})
                if stat_diffs:
                    print("  Stat Differentials:")
                    for stat, diff in stat_diffs.items():
                        print(f"    - {stat}: {diff}")
            
            if len(team_rbs_details) > 2:
                print("  ...")
        else:
            print(f"\nTeam RBS Details: {team_rbs_details}")
        
        # Verify required sections
        required_sections = [
            'referee_name', 'total_matches', 'teams_officiated', 
            'avg_bias_score', 'rbs_calculations', 'match_outcomes', 
            'cards_and_fouls', 'bias_analysis', 'team_rbs_details'
        ]
        
        missing_sections = [section for section in required_sections if section not in data or data[section] is None]
        
        if missing_sections:
            print(f"\n❌ Missing required sections: {', '.join(missing_sections)}")
        else:
            print("\n✅ All required sections are present")
        
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

def test_referee_bias_functionality():
    """Test all Referee Bias Score (RBS) functionality"""
    print("\n\n========== TESTING REFEREE BIAS SCORE (RBS) FUNCTIONALITY ==========\n")
    
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
    print("\nStep 2: Testing Calculate RBS")
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
    
    # Step 4: Get Detailed Referee Analysis for Michael Oliver
    print("\nStep 4: Testing Detailed Referee Analysis for Michael Oliver")
    detail_data_oliver = test_referee_analysis_detail_endpoint("Michael Oliver")
    
    if not detail_data_oliver:
        print("❌ Detailed Referee Analysis endpoint test failed for Michael Oliver")
    elif not detail_data_oliver.get('success', False):
        print("❌ Detailed Referee Analysis endpoint returned success: false for Michael Oliver")
    else:
        print("✅ Detailed Referee Analysis endpoint test passed for Michael Oliver")
    
    # Step 5: Get Detailed Referee Analysis for Andrew Kitchen
    print("\nStep 5: Testing Detailed Referee Analysis for Andrew Kitchen")
    detail_data_kitchen = test_referee_analysis_detail_endpoint("Andrew Kitchen")
    
    if not detail_data_kitchen:
        print("❌ Detailed Referee Analysis endpoint test failed for Andrew Kitchen")
    elif not detail_data_kitchen.get('success', False):
        print("❌ Detailed Referee Analysis endpoint returned success: false for Andrew Kitchen")
    else:
        print("✅ Detailed Referee Analysis endpoint test passed for Andrew Kitchen")
    
    # Step 6: Test Error Handling
    print("\nStep 6: Testing Error Handling for Non-existent Referee")
    error_response = test_referee_analysis_error_handling()
    
    # Final summary
    print("\n========== REFEREE BIAS SCORE (RBS) FUNCTIONALITY TEST SUMMARY ==========")
    
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
    detail_response = requests.get(f"{BASE_URL}/referee-analysis/Michael%20Oliver")
    endpoint_check_results.append(detail_response.status_code == 200)
    
    if all(endpoint_check_results):
        print("✅ All RBS functionality endpoints exist and are accessible!")
        
        # Check for null/undefined RBS scores in referee list
        if list_data and list_data.get('success', False):
            referees = list_data.get('referees', [])
            null_rbs_scores = [ref for ref in referees if ref.get('avg_bias_score') is None]
            
            if null_rbs_scores:
                print(f"❌ Found {len(null_rbs_scores)} referees with null RBS scores")
            else:
                print("✅ All referees have numerical RBS scores")
        
        # Check for required sections in detailed analysis
        if detail_data_oliver and detail_data_oliver.get('success', False):
            required_sections = [
                'referee_name', 'total_matches', 'teams_officiated', 
                'avg_bias_score', 'rbs_calculations', 'match_outcomes', 
                'cards_and_fouls', 'bias_analysis', 'team_rbs_details'
            ]
            
            missing_sections = [section for section in required_sections if section not in detail_data_oliver or detail_data_oliver[section] is None]
            
            if missing_sections:
                print(f"❌ Missing required sections in detailed analysis: {', '.join(missing_sections)}")
            else:
                print("✅ All required sections are present in detailed analysis")
        
        return True
    else:
        print("❌ Some RBS functionality endpoints failed the existence check")
        return False

if __name__ == "__main__":
    # Test Referee Bias functionality
    test_referee_bias_functionality()
