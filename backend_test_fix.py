import requests
import os
import json
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Get the backend URL from environment
BACKEND_URL = os.environ.get('REACT_APP_BACKEND_URL', 'http://localhost:8001')
BASE_URL = f"{BACKEND_URL}/api"

def test_upload_endpoint_fix():
    """Test the fix for upload endpoints to ensure they append data instead of replacing it"""
    print("\n=== Testing Upload Endpoint Fix ===")
    
    # Step 1: Get initial database stats
    print("\nStep 1: Getting initial database stats")
    response = requests.get(f"{BASE_URL}/database/stats")
    
    if response.status_code == 200:
        initial_stats = response.json()
        print(f"Initial total documents: {initial_stats.get('total_documents', 0)}")
        print(f"Initial matches: {initial_stats.get('collections', {}).get('matches', 0)}")
        print(f"Initial team stats: {initial_stats.get('collections', {}).get('team_stats', 0)}")
        print(f"Initial player stats: {initial_stats.get('collections', {}).get('player_stats', 0)}")
    else:
        print(f"Error getting initial stats: {response.status_code}")
        print(response.text)
        return
    
    # Step 2: Create a small test match CSV
    print("\nStep 2: Creating test match CSV")
    test_match_csv = """match_id,referee,home_team,away_team,home_score,away_score,result,season,competition,match_date
test_match_fix_1,Mike Dean,Arsenal,Chelsea,2,1,H,2022/23,Premier League,2022-09-01
"""
    
    with open("/app/test_match_fix.csv", "w") as f:
        f.write(test_match_csv)
    
    # Step 3: Upload the test match CSV
    print("\nStep 3: Uploading test match CSV")
    with open("/app/test_match_fix.csv", "rb") as f:
        files = {'file': ('test_match_fix.csv', f, 'text/csv')}
        response = requests.post(f"{BASE_URL}/upload/matches", files=files)
    
    if response.status_code == 200:
        upload_result = response.json()
        print(f"Upload success: {upload_result.get('success', False)}")
        print(f"Records processed: {upload_result.get('records_processed', 0)}")
    else:
        print(f"Error uploading: {response.status_code}")
        print(response.text)
        return
    
    # Step 4: Get database stats after upload
    print("\nStep 4: Getting database stats after upload")
    response = requests.get(f"{BASE_URL}/database/stats")
    
    if response.status_code == 200:
        mid_stats = response.json()
        print(f"Total documents after upload: {mid_stats.get('total_documents', 0)}")
        print(f"Matches after upload: {mid_stats.get('collections', {}).get('matches', 0)}")
        
        # Check if matches were added
        initial_matches = initial_stats.get('collections', {}).get('matches', 0)
        mid_matches = mid_stats.get('collections', {}).get('matches', 0)
        
        if mid_matches > initial_matches:
            print(f"✅ Matches increased from {initial_matches} to {mid_matches}")
            print("✅ Upload endpoint is now APPENDING data instead of replacing it")
        else:
            print(f"❌ Matches did not increase: {initial_matches} -> {mid_matches}")
            print("❌ Upload endpoint is still REPLACING data instead of appending it")
    else:
        print(f"Error getting stats after upload: {response.status_code}")
        print(response.text)
        return
    
    # Step 5: Create a second test match CSV
    print("\nStep 5: Creating second test match CSV")
    test_match_csv2 = """match_id,referee,home_team,away_team,home_score,away_score,result,season,competition,match_date
test_match_fix_2,Michael Oliver,Liverpool,Manchester United,3,0,H,2022/23,Premier League,2022-09-02
"""
    
    with open("/app/test_match_fix2.csv", "w") as f:
        f.write(test_match_csv2)
    
    # Step 6: Upload the second test match CSV
    print("\nStep 6: Uploading second test match CSV")
    with open("/app/test_match_fix2.csv", "rb") as f:
        files = {'file': ('test_match_fix2.csv', f, 'text/csv')}
        response = requests.post(f"{BASE_URL}/upload/matches", files=files)
    
    if response.status_code == 200:
        upload_result = response.json()
        print(f"Upload success: {upload_result.get('success', False)}")
        print(f"Records processed: {upload_result.get('records_processed', 0)}")
    else:
        print(f"Error uploading: {response.status_code}")
        print(response.text)
        return
    
    # Step 7: Get final database stats
    print("\nStep 7: Getting final database stats")
    response = requests.get(f"{BASE_URL}/database/stats")
    
    if response.status_code == 200:
        final_stats = response.json()
        print(f"Final total documents: {final_stats.get('total_documents', 0)}")
        print(f"Final matches: {final_stats.get('collections', {}).get('matches', 0)}")
        
        # Check if matches were added again
        mid_matches = mid_stats.get('collections', {}).get('matches', 0)
        final_matches = final_stats.get('collections', {}).get('matches', 0)
        
        if final_matches > mid_matches:
            print(f"✅ Matches increased from {mid_matches} to {final_matches}")
            print("✅ Upload endpoint is now APPENDING data instead of replacing it")
        else:
            print(f"❌ Matches did not increase: {mid_matches} -> {final_matches}")
            print("❌ Upload endpoint is still REPLACING data instead of appending it")
    else:
        print(f"Error getting final stats: {response.status_code}")
        print(response.text)
        return

if __name__ == "__main__":
    test_upload_endpoint_fix()
