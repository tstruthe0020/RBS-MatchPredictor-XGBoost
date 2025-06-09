import requests
import os
import json
import time
import pprint
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Get the backend URL from environment
BACKEND_URL = os.environ.get('REACT_APP_BACKEND_URL', 'http://localhost:8001')
BASE_URL = f"{BACKEND_URL}/api"

# Pretty printer for better output formatting
pp = pprint.PrettyPrinter(indent=2)

def test_database_stats():
    """Get current database statistics"""
    print("\n=== Getting Database Statistics ===")
    response = requests.get(f"{BASE_URL}/database/stats")
    
    if response.status_code == 200:
        data = response.json()
        print(f"Status: {response.status_code} OK")
        print(f"Success: {data.get('success', False)}")
        
        # Check total documents
        total_documents = data.get('total_documents', 0)
        print(f"Total Documents: {total_documents}")
        
        # Check collections
        collections = data.get('collections', {})
        print(f"Collections: {len(collections)}")
        
        for collection_name, count in collections.items():
            print(f"  - {collection_name}: {count} documents")
            
        return data
    else:
        print(f"Error: {response.status_code}")
        print(response.text)
        return None

def create_test_csv_files():
    """Create small test CSV files for testing uploads"""
    print("\n=== Creating Test CSV Files ===")
    
    # Create test matches CSV
    matches_csv = """match_id,referee,home_team,away_team,home_score,away_score,result,season,competition,match_date
test_match_1,Mike Dean,Arsenal,Chelsea,2,1,H,2022/23,Premier League,2022-09-01
test_match_2,Michael Oliver,Liverpool,Manchester United,3,0,H,2022/23,Premier League,2022-09-02
test_match_3,Anthony Taylor,Manchester City,Tottenham,1,1,D,2022/23,Premier League,2022-09-03
"""
    
    # Create test team stats CSV
    team_stats_csv = """match_id,team_name,is_home,yellow_cards,red_cards,fouls,possession_pct,shots_total,shots_on_target,fouls_drawn,penalties_awarded,penalty_attempts,penalty_goals,penalty_conversion_rate,xg
test_match_1,Arsenal,True,2,0,10,55,15,8,8,1,1,1,100,2.3
test_match_1,Chelsea,False,3,0,12,45,10,5,10,0,0,0,0,1.5
test_match_2,Liverpool,True,1,0,8,60,18,10,6,0,0,0,0,3.2
test_match_2,Manchester United,False,4,1,14,40,6,2,8,0,0,0,0,0.8
test_match_3,Manchester City,True,2,0,9,65,20,8,7,0,0,0,0,2.1
test_match_3,Tottenham,False,3,0,11,35,8,4,9,1,1,1,100,1.4
"""
    
    # Create test player stats CSV
    player_stats_csv = """match_id,player_name,team_name,is_home,goals,assists,yellow_cards,fouls_committed,fouls_drawn,xg,shots_total,shots_on_target,penalty_attempts,penalty_goals
test_match_1,Bukayo Saka,Arsenal,True,1,1,0,1,2,0.8,4,3,0,0
test_match_1,Gabriel Jesus,Arsenal,True,1,0,1,2,3,1.2,5,3,1,1
test_match_1,Martin Odegaard,Arsenal,True,0,0,0,1,1,0.3,2,1,0,0
test_match_1,Kai Havertz,Chelsea,False,1,0,0,2,2,0.7,3,2,0,0
test_match_1,Raheem Sterling,Chelsea,False,0,0,1,1,3,0.5,4,2,0,0
test_match_1,Reece James,Chelsea,False,0,0,1,3,1,0.3,1,0,0,0
test_match_2,Mohamed Salah,Liverpool,True,2,1,0,0,2,1.5,6,4,0,0
test_match_2,Darwin Nunez,Liverpool,True,1,0,1,2,1,1.2,5,3,0,0
test_match_2,Trent Alexander-Arnold,Liverpool,True,0,2,0,1,0,0.5,2,1,0,0
test_match_2,Marcus Rashford,Manchester United,False,0,0,1,2,3,0.5,3,1,0,0
test_match_2,Bruno Fernandes,Manchester United,False,0,0,1,3,2,0.3,2,1,0,0
test_match_2,Casemiro,Manchester United,False,0,0,1,4,1,0.0,0,0,0,0
test_match_3,Erling Haaland,Manchester City,True,1,0,0,1,2,1.2,5,3,0,0
test_match_3,Kevin De Bruyne,Manchester City,True,0,1,1,2,2,0.6,3,2,0,0
test_match_3,Phil Foden,Manchester City,True,0,0,0,1,1,0.3,4,1,0,0
test_match_3,Harry Kane,Tottenham,False,1,0,0,1,3,0.8,3,2,1,1
test_match_3,Son Heung-min,Tottenham,False,0,0,1,2,2,0.4,3,1,0,0
test_match_3,Cristian Romero,Tottenham,False,0,0,1,3,0,0.2,1,0,0,0
"""
    
    # Write files
    with open("/app/test_matches.csv", "w") as f:
        f.write(matches_csv)
    
    with open("/app/test_team_stats.csv", "w") as f:
        f.write(team_stats_csv)
    
    with open("/app/test_player_stats.csv", "w") as f:
        f.write(player_stats_csv)
    
    # Create a second set of test files with different data
    matches_csv2 = """match_id,referee,home_team,away_team,home_score,away_score,result,season,competition,match_date
test_match_4,Martin Atkinson,Arsenal,Tottenham,1,1,D,2022/23,Premier League,2022-09-10
test_match_5,Andre Marriner,Chelsea,Liverpool,0,2,A,2022/23,Premier League,2022-09-11
test_match_6,Stuart Attwell,Manchester United,Manchester City,1,3,A,2022/23,Premier League,2022-09-12
"""
    
    team_stats_csv2 = """match_id,team_name,is_home,yellow_cards,red_cards,fouls,possession_pct,shots_total,shots_on_target,fouls_drawn,penalties_awarded,penalty_attempts,penalty_goals,penalty_conversion_rate,xg
test_match_4,Arsenal,True,1,0,9,52,14,6,7,0,0,0,0,1.8
test_match_4,Tottenham,False,2,0,11,48,12,5,9,0,0,0,0,1.7
test_match_5,Chelsea,True,2,0,10,45,8,3,8,0,0,0,0,1.2
test_match_5,Liverpool,False,1,0,7,55,15,8,10,1,1,1,100,2.5
test_match_6,Manchester United,True,3,0,12,40,9,4,8,1,1,1,100,1.5
test_match_6,Manchester City,False,1,0,8,60,16,9,12,0,0,0,0,2.8
"""
    
    player_stats_csv2 = """match_id,player_name,team_name,is_home,goals,assists,yellow_cards,fouls_committed,fouls_drawn,xg,shots_total,shots_on_target,penalty_attempts,penalty_goals
test_match_4,Bukayo Saka,Arsenal,True,1,0,0,1,2,0.7,3,2,0,0
test_match_4,Gabriel Jesus,Arsenal,True,0,1,1,2,2,0.8,4,2,0,0
test_match_4,Martin Odegaard,Arsenal,True,0,0,0,1,1,0.3,2,1,0,0
test_match_4,Harry Kane,Tottenham,False,1,0,0,1,3,0.9,4,2,0,0
test_match_4,Son Heung-min,Tottenham,False,0,1,1,2,2,0.5,3,1,0,0
test_match_4,Cristian Romero,Tottenham,False,0,0,1,3,0,0.3,1,0,0,0
test_match_5,Kai Havertz,Chelsea,True,0,0,0,2,2,0.6,3,1,0,0
test_match_5,Raheem Sterling,Chelsea,True,0,0,1,1,3,0.4,3,1,0,0
test_match_5,Reece James,Chelsea,True,0,0,1,2,1,0.2,1,0,0,0
test_match_5,Mohamed Salah,Liverpool,False,1,1,0,0,2,1.2,5,3,0,0
test_match_5,Darwin Nunez,Liverpool,False,1,0,0,1,3,0.8,4,2,1,1
test_match_5,Trent Alexander-Arnold,Liverpool,False,0,1,0,1,1,0.5,2,1,0,0
test_match_6,Marcus Rashford,Manchester United,True,1,0,1,2,3,0.8,4,2,1,1
test_match_6,Bruno Fernandes,Manchester United,True,0,0,1,3,2,0.4,3,1,0,0
test_match_6,Casemiro,Manchester United,True,0,0,1,3,1,0.3,1,0,0,0
test_match_6,Erling Haaland,Manchester City,False,2,0,0,1,3,1.5,6,4,0,0
test_match_6,Kevin De Bruyne,Manchester City,False,1,2,0,2,4,0.8,4,2,0,0
test_match_6,Phil Foden,Manchester City,False,0,1,1,1,2,0.5,3,1,0,0
"""
    
    # Write second set of files
    with open("/app/test_matches2.csv", "w") as f:
        f.write(matches_csv2)
    
    with open("/app/test_team_stats2.csv", "w") as f:
        f.write(team_stats_csv2)
    
    with open("/app/test_player_stats2.csv", "w") as f:
        f.write(player_stats_csv2)
    
    print("Test CSV files created successfully:")
    print("  - /app/test_matches.csv")
    print("  - /app/test_team_stats.csv")
    print("  - /app/test_player_stats.csv")
    print("  - /app/test_matches2.csv")
    print("  - /app/test_team_stats2.csv")
    print("  - /app/test_player_stats2.csv")

def test_upload_endpoint(endpoint, file_path):
    """Test an upload endpoint with a CSV file"""
    print(f"\n=== Testing {endpoint} Endpoint with {file_path} ===")
    
    with open(file_path, 'rb') as f:
        files = {'file': (os.path.basename(file_path), f, 'text/csv')}
        response = requests.post(f"{BASE_URL}/{endpoint}", files=files)
    
    if response.status_code == 200:
        data = response.json()
        print(f"Status: {response.status_code} OK")
        print(f"Success: {data.get('success', False)}")
        print(f"Message: {data.get('message', '')}")
        print(f"Records processed: {data.get('records_processed', 0)}")
        return data
    else:
        print(f"Error: {response.status_code}")
        print(response.text)
        return None

def test_ml_model_status():
    """Test the ML model status endpoint"""
    print("\n=== Testing ML Model Status Endpoint ===")
    response = requests.get(f"{BASE_URL}/ml-models/status")
    
    if response.status_code == 200:
        data = response.json()
        print(f"Status: {response.status_code} OK")
        print(f"Success: {data.get('success', False)}")
        print(f"Models loaded: {data.get('models_loaded', False)}")
        print(f"Feature columns count: {data.get('feature_columns_count', 0)}")
        
        # Check status of each model
        models_status = data.get('models_status', {})
        print(f"\nModels status:")
        for model_name, status in models_status.items():
            print(f"  - {model_name}: {'✅ Exists' if status.get('exists') else '❌ Missing'}")
            if status.get('exists') and status.get('last_modified'):
                from datetime import datetime
                last_modified = datetime.fromtimestamp(status['last_modified']).strftime('%Y-%m-%d %H:%M:%S')
                print(f"    Last modified: {last_modified}")
        
        return data
    else:
        print(f"Error: {response.status_code}")
        print(response.text)
        return None

def test_train_ml_models():
    """Test the ML model training endpoint"""
    print("\n=== Testing ML Model Training Endpoint ===")
    print("This may take some time as it processes all historical data...")
    
    response = requests.post(f"{BASE_URL}/train-ml-models")
    
    if response.status_code == 200:
        data = response.json()
        print(f"Status: {response.status_code} OK")
        print(f"Success: {data.get('success', False)}")
        print(f"Message: {data.get('message', '')}")
        
        # Check training results
        training_results = data.get('training_results', {})
        print("\nTraining results:")
        for model_name, results in training_results.items():
            if model_name == 'classifier':
                print(f"  - {model_name}: Accuracy = {results.get('accuracy', 'N/A')}, Samples = {results.get('samples', 'N/A')}")
            else:
                print(f"  - {model_name}: R² = {results.get('r2_score', 'N/A')}, MSE = {results.get('mse', 'N/A')}, Samples = {results.get('samples', 'N/A')}")
        
        return data
    else:
        print(f"Error: {response.status_code}")
        print(response.text)
        return None

def test_database_accumulation():
    """Test database accumulation behavior"""
    print("\n\n========== TESTING DATABASE ACCUMULATION BEHAVIOR ==========\n")
    
    # Step 1: Get initial database stats
    print("Step 1: Getting initial database stats")
    initial_stats = test_database_stats()
    
    if not initial_stats:
        print("❌ Failed to get initial database stats")
        return False
    
    initial_total = initial_stats.get('total_documents', 0)
    initial_matches = initial_stats.get('collections', {}).get('matches', 0)
    initial_team_stats = initial_stats.get('collections', {}).get('team_stats', 0)
    initial_player_stats = initial_stats.get('collections', {}).get('player_stats', 0)
    
    print(f"\nInitial document counts:")
    print(f"  - Total: {initial_total}")
    print(f"  - Matches: {initial_matches}")
    print(f"  - Team Stats: {initial_team_stats}")
    print(f"  - Player Stats: {initial_player_stats}")
    
    # Step 2: Create test CSV files
    print("\nStep 2: Creating test CSV files")
    create_test_csv_files()
    
    # Step 3: Upload first set of test files
    print("\nStep 3: Uploading first set of test files")
    
    matches_upload = test_upload_endpoint("upload/matches", "/app/test_matches.csv")
    team_stats_upload = test_upload_endpoint("upload/team-stats", "/app/test_team_stats.csv")
    player_stats_upload = test_upload_endpoint("upload/player-stats", "/app/test_player_stats.csv")
    
    if not matches_upload or not team_stats_upload or not player_stats_upload:
        print("❌ Failed to upload test files")
        return False
    
    # Step 4: Get database stats after first upload
    print("\nStep 4: Getting database stats after first upload")
    mid_stats = test_database_stats()
    
    if not mid_stats:
        print("❌ Failed to get database stats after first upload")
        return False
    
    mid_total = mid_stats.get('total_documents', 0)
    mid_matches = mid_stats.get('collections', {}).get('matches', 0)
    mid_team_stats = mid_stats.get('collections', {}).get('team_stats', 0)
    mid_player_stats = mid_stats.get('collections', {}).get('player_stats', 0)
    
    print(f"\nDocument counts after first upload:")
    print(f"  - Total: {mid_total} ({mid_total - initial_total} added)")
    print(f"  - Matches: {mid_matches} ({mid_matches - initial_matches} added)")
    print(f"  - Team Stats: {mid_team_stats} ({mid_team_stats - initial_team_stats} added)")
    print(f"  - Player Stats: {mid_player_stats} ({mid_player_stats - initial_player_stats} added)")
    
    # Step 5: Upload second set of test files
    print("\nStep 5: Uploading second set of test files")
    
    matches_upload2 = test_upload_endpoint("upload/matches", "/app/test_matches2.csv")
    team_stats_upload2 = test_upload_endpoint("upload/team-stats", "/app/test_team_stats2.csv")
    player_stats_upload2 = test_upload_endpoint("upload/player-stats", "/app/test_player_stats2.csv")
    
    if not matches_upload2 or not team_stats_upload2 or not player_stats_upload2:
        print("❌ Failed to upload second set of test files")
        return False
    
    # Step 6: Get database stats after second upload
    print("\nStep 6: Getting database stats after second upload")
    final_stats = test_database_stats()
    
    if not final_stats:
        print("❌ Failed to get database stats after second upload")
        return False
    
    final_total = final_stats.get('total_documents', 0)
    final_matches = final_stats.get('collections', {}).get('matches', 0)
    final_team_stats = final_stats.get('collections', {}).get('team_stats', 0)
    final_player_stats = final_stats.get('collections', {}).get('player_stats', 0)
    
    print(f"\nDocument counts after second upload:")
    print(f"  - Total: {final_total} ({final_total - mid_total} added)")
    print(f"  - Matches: {final_matches} ({final_matches - mid_matches} added)")
    print(f"  - Team Stats: {final_team_stats} ({final_team_stats - mid_team_stats} added)")
    print(f"  - Player Stats: {final_player_stats} ({final_player_stats - mid_player_stats} added)")
    
    # Step 7: Verify accumulation behavior
    print("\nStep 7: Verifying accumulation behavior")
    
    # Check if documents were added in each upload
    matches_first_upload = matches_upload.get('records_processed', 0)
    team_stats_first_upload = team_stats_upload.get('records_processed', 0)
    player_stats_first_upload = player_stats_upload.get('records_processed', 0)
    
    matches_second_upload = matches_upload2.get('records_processed', 0)
    team_stats_second_upload = team_stats_upload2.get('records_processed', 0)
    player_stats_second_upload = player_stats_upload2.get('records_processed', 0)
    
    print(f"\nRecords processed in first upload:")
    print(f"  - Matches: {matches_first_upload}")
    print(f"  - Team Stats: {team_stats_first_upload}")
    print(f"  - Player Stats: {player_stats_first_upload}")
    
    print(f"\nRecords processed in second upload:")
    print(f"  - Matches: {matches_second_upload}")
    print(f"  - Team Stats: {team_stats_second_upload}")
    print(f"  - Player Stats: {player_stats_second_upload}")
    
    # Verify that the database accumulated records rather than replacing them
    matches_accumulated = final_matches > mid_matches
    team_stats_accumulated = final_team_stats > mid_team_stats
    player_stats_accumulated = final_player_stats > mid_player_stats
    
    print("\nAccumulation verification:")
    print(f"  - Matches: {'✅ Accumulated' if matches_accumulated else '❌ Not accumulated'}")
    print(f"  - Team Stats: {'✅ Accumulated' if team_stats_accumulated else '❌ Not accumulated'}")
    print(f"  - Player Stats: {'✅ Accumulated' if player_stats_accumulated else '❌ Not accumulated'}")
    
    # Final assessment
    if matches_accumulated and team_stats_accumulated and player_stats_accumulated:
        print("\n✅ Database accumulation behavior verified: Data is being APPENDED, not replaced")
        return True
    else:
        print("\n❌ Database accumulation behavior test failed: Data may be being replaced instead of appended")
        return False

def test_ml_model_training():
    """Test ML model training functionality"""
    print("\n\n========== TESTING ML MODEL TRAINING FUNCTIONALITY ==========\n")
    
    # Step 1: Check initial ML model status
    print("Step 1: Checking initial ML model status")
    initial_status = test_ml_model_status()
    
    if not initial_status:
        print("❌ Failed to get initial ML model status")
        return False
    
    # Step 2: Train ML models
    print("\nStep 2: Training ML models")
    training_result = test_train_ml_models()
    
    if not training_result or not training_result.get('success'):
        print("❌ Failed to train ML models")
        return False
    
    # Step 3: Check ML model status after training
    print("\nStep 3: Checking ML model status after training")
    final_status = test_ml_model_status()
    
    if not final_status:
        print("❌ Failed to get ML model status after training")
        return False
    
    # Step 4: Verify training results
    print("\nStep 4: Verifying training results")
    
    # Check if models are loaded after training
    models_loaded = final_status.get('models_loaded', False)
    
    # Check if all required models exist
    models_status = final_status.get('models_status', {})
    required_models = ['classifier', 'home_goals', 'away_goals', 'home_xg', 'away_xg']
    missing_models = [model for model in required_models if model not in models_status or not models_status[model].get('exists')]
    
    print(f"\nModels loaded: {'✅ Yes' if models_loaded else '❌ No'}")
    print(f"Missing models: {', '.join(missing_models) if missing_models else 'None'}")
    
    # Check training metrics
    training_results = training_result.get('training_results', {})
    
    print("\nTraining metrics:")
    for model_name, results in training_results.items():
        if model_name == 'classifier':
            accuracy = results.get('accuracy')
            print(f"  - {model_name}: Accuracy = {accuracy}")
            if accuracy is not None and accuracy > 0:
                print(f"    ✅ Accuracy is positive")
            else:
                print(f"    ❌ Accuracy is missing or zero")
        else:
            r2_score = results.get('r2_score')
            print(f"  - {model_name}: R² = {r2_score}")
            if r2_score is not None:
                print(f"    ✅ R² score is present")
            else:
                print(f"    ❌ R² score is missing")
    
    # Final assessment
    if models_loaded and not missing_models:
        print("\n✅ ML model training functionality verified: Models are trained and saved successfully")
        return True
    else:
        print("\n❌ ML model training functionality test failed: Models are not properly trained or saved")
        return False

def main():
    """Main test function"""
    print("=== Testing Database Accumulation and ML Model Training ===\n")
    
    # Test database accumulation behavior
    accumulation_result = test_database_accumulation()
    
    # Test ML model training functionality
    ml_training_result = test_ml_model_training()
    
    # Final summary
    print("\n\n========== FINAL TEST SUMMARY ==========\n")
    print(f"Database Accumulation Behavior: {'✅ PASSED' if accumulation_result else '❌ FAILED'}")
    print(f"ML Model Training Functionality: {'✅ PASSED' if ml_training_result else '❌ FAILED'}")
    
    if accumulation_result and ml_training_result:
        print("\n✅ All tests passed successfully!")
    else:
        print("\n❌ Some tests failed. See details above.")

if __name__ == "__main__":
    main()
