import requests
import os
import json
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Get the backend URL from environment
BACKEND_URL = os.environ.get('REACT_APP_BACKEND_URL', 'http://localhost:8001')
BASE_URL = f"{BACKEND_URL}/api"

def test_database_wipe_with_empty_db():
    """Test the /api/database/wipe endpoint with an empty database"""
    print("\n=== Testing Database Wipe Endpoint with Empty Database ===")
    
    # First, check if the database is already empty
    stats_response = requests.get(f"{BASE_URL}/database/stats")
    if stats_response.status_code == 200:
        stats_data = stats_response.json()
        total_documents = stats_data.get('total_documents', 0)
        print(f"Initial database state: {total_documents} total documents")
        
        # If database is not empty, wipe it first
        if total_documents > 0:
            print("Database is not empty. Wiping first...")
            pre_wipe_response = requests.delete(f"{BASE_URL}/database/wipe")
            if pre_wipe_response.status_code != 200:
                print(f"Error in pre-wipe: {pre_wipe_response.status_code}")
                print(pre_wipe_response.text)
                return False
            
            # Verify database is now empty
            stats_response = requests.get(f"{BASE_URL}/database/stats")
            if stats_response.status_code == 200:
                stats_data = stats_response.json()
                total_documents = stats_data.get('total_documents', 0)
                print(f"After pre-wipe: {total_documents} total documents")
                if total_documents > 0:
                    print("❌ Pre-wipe failed to empty the database")
                    return False
            else:
                print(f"Error checking stats after pre-wipe: {stats_response.status_code}")
                print(stats_response.text)
                return False
    else:
        print(f"Error checking initial database state: {stats_response.status_code}")
        print(stats_response.text)
        return False
    
    # Now test wiping an empty database
    print("\nTesting wipe on empty database...")
    response = requests.delete(f"{BASE_URL}/database/wipe")
    
    if response.status_code == 200:
        print(f"Status: {response.status_code} OK")
        data = response.json()
        print(f"Success: {data.get('success', False)}")
        print(f"Message: {data.get('message', '')}")
        
        # Check collections cleared
        collections_cleared = data.get('collections_cleared', 0)
        print(f"Collections Cleared: {collections_cleared}")
        
        # Check timestamp
        timestamp = data.get('timestamp')
        if timestamp:
            print(f"Timestamp: {timestamp}")
        
        # Verify success is True even with empty database
        if data.get('success', False):
            print("✅ Database wipe endpoint returns success=True with empty database")
            return True
        else:
            print("❌ Database wipe endpoint returns success=False with empty database")
            return False
    else:
        print(f"Error: {response.status_code}")
        print(response.text)
        return False

def test_ensemble_model_training_error_handling():
    """Test the /api/train-ensemble-models endpoint error handling"""
    print("\n=== Testing Ensemble Model Training Error Handling ===")
    
    # First, ensure database is empty to trigger the error
    print("Ensuring database is empty...")
    wipe_response = requests.delete(f"{BASE_URL}/database/wipe")
    if wipe_response.status_code != 200:
        print(f"Error wiping database: {wipe_response.status_code}")
        print(wipe_response.text)
        return False
    
    # Verify database is empty
    stats_response = requests.get(f"{BASE_URL}/database/stats")
    if stats_response.status_code == 200:
        stats_data = stats_response.json()
        total_documents = stats_data.get('total_documents', 0)
        print(f"Database state: {total_documents} total documents")
        if total_documents > 0:
            print("❌ Database is not empty, test may not be accurate")
    else:
        print(f"Error checking database state: {stats_response.status_code}")
        print(stats_response.text)
        return False
    
    # Now test training ensemble models with insufficient data
    print("\nTesting ensemble model training with insufficient data...")
    response = requests.post(f"{BASE_URL}/train-ensemble-models")
    
    if response.status_code == 200:
        print(f"Status: {response.status_code} OK")
        data = response.json()
        print(f"Success: {data.get('success', False)}")
        
        # Check for proper error message
        error_message = data.get('error', '')
        print(f"Error message: {error_message}")
        
        # Verify error message contains "Insufficient data for training"
        if "Insufficient data for training" in error_message:
            print("✅ Ensemble model training returns proper error message about insufficient data")
            return True
        else:
            print("❌ Ensemble model training does not return proper error message")
            return False
    else:
        print(f"Error: {response.status_code}")
        print(response.text)
        return False

if __name__ == "__main__":
    print("\n========== TESTING SPECIFIC FIXES ==========\n")
    
    # Test Fix 1: Database Wipe Function
    print("\nTesting Fix 1: Database Wipe Function")
    db_wipe_result = test_database_wipe_with_empty_db()
    if db_wipe_result:
        print("✅ Fix 1: Database Wipe Function is working correctly")
    else:
        print("❌ Fix 1: Database Wipe Function is not working correctly")
    
    # Test Fix 2: Ensemble Model Training
    print("\nTesting Fix 2: Ensemble Model Training")
    ensemble_result = test_ensemble_model_training_error_handling()
    if ensemble_result:
        print("✅ Fix 2: Ensemble Model Training is working correctly")
    else:
        print("❌ Fix 2: Ensemble Model Training is not working correctly")
    
    # Final summary
    print("\n========== FIXES TEST SUMMARY ==========")
    if db_wipe_result and ensemble_result:
        print("✅ All fixes are working correctly!")
    else:
        print("❌ Some fixes are not working correctly:")
        if not db_wipe_result:
            print("  - Database Wipe Function")
        if not ensemble_result:
            print("  - Ensemble Model Training")
