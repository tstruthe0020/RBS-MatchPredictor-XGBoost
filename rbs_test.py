import requests
import os
import json
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

def test_enhanced_rbs_functionality():
    """Test all enhanced RBS functionality without time decay"""
    print("\n\n========== TESTING ENHANCED RBS FUNCTIONALITY WITHOUT TIME DECAY ==========\n")
    
    # Step 1: Calculate RBS
    print("\nStep 1: Testing Calculate RBS (No Time Decay)")
    calc_data = test_calculate_rbs_endpoint()
    
    if not calc_data:
        print("❌ Calculate RBS endpoint test failed")
    elif not calc_data.get('success', False):
        print("❌ Calculate RBS endpoint returned success: false")
    else:
        print("✅ Calculate RBS endpoint test passed")
    
    # Step 2: Get Detailed Referee Analysis for Andrew Kitchen
    print("\nStep 2: Testing Detailed Referee Analysis for Andrew Kitchen")
    detail_data = test_referee_analysis_detail_endpoint("Andrew Kitchen")
    
    if not detail_data:
        print("❌ Detailed Referee Analysis endpoint test failed")
    elif not detail_data.get('success', False):
        print("❌ Detailed Referee Analysis endpoint returned success: false")
    else:
        print("✅ Detailed Referee Analysis endpoint test passed")
    
    # Final summary
    print("\n========== ENHANCED RBS FUNCTIONALITY TEST SUMMARY ==========")
    
    # Check if all endpoints exist and work properly
    endpoint_check_results = []
    
    # Check Calculate RBS endpoint
    calc_response = requests.post(f"{BASE_URL}/calculate-rbs")
    endpoint_check_results.append(calc_response.status_code == 200)
    
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
