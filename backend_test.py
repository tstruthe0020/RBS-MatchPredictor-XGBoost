import requests
import os
import json
import base64
import time
import pprint

# Base URL for API
BASE_URL = "http://localhost:8001/api"

# Pretty printer for better output formatting
pp = pprint.PrettyPrinter(indent=2)

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

def run_tests():
    """Run all tests"""
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

if __name__ == "__main__":
    run_tests()
