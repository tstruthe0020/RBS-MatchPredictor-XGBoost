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

def test_api_endpoint(endpoint, method="GET", data=None, expected_status=200, description=""):
    """Generic function to test an API endpoint"""
    print(f"\n=== Testing {endpoint} ({description}) ===")
    
    url = f"{BASE_URL}/{endpoint}"
    
    try:
        if method.upper() == "GET":
            response = requests.get(url)
        elif method.upper() == "POST":
            response = requests.post(url, json=data)
        elif method.upper() == "DELETE":
            response = requests.delete(url)
        else:
            print(f"Unsupported method: {method}")
            return False
        
        print(f"Status: {response.status_code}")
        
        if response.status_code == expected_status:
            print("✅ Endpoint test passed")
            try:
                data = response.json()
                print("Response data (sample):")
                if isinstance(data, dict):
                    # Print first few keys and values
                    sample_data = {k: data[k] for k in list(data.keys())[:5]} if len(data) > 5 else data
                    pp.pprint(sample_data)
                    if len(data) > 5:
                        print(f"... and {len(data) - 5} more keys")
                elif isinstance(data, list):
                    # Print first few items
                    pp.pprint(data[:5])
                    if len(data) > 5:
                        print(f"... and {len(data) - 5} more items")
                else:
                    pp.pprint(data)
                return data
            except:
                print("Response is not JSON")
                print(response.text[:200] + "..." if len(response.text) > 200 else response.text)
                return response.text
        else:
            print(f"❌ Endpoint test failed - Expected status {expected_status}, got {response.status_code}")
            print(f"Response: {response.text[:200]}...")
            return False
    except Exception as e:
        print(f"❌ Error testing endpoint: {e}")
        return False

def test_teams_endpoint():
    """Test the /api/teams endpoint"""
    return test_api_endpoint("teams", "GET", description="Get all teams")

def test_referees_endpoint():
    """Test the /api/referees endpoint"""
    return test_api_endpoint("referees", "GET", description="Get all referees")

def test_stats_endpoint():
    """Test the /api/stats endpoint"""
    return test_api_endpoint("stats", "GET", description="Get general statistics")

def test_database_stats_endpoint():
    """Test the /api/database/stats endpoint"""
    return test_api_endpoint("database/stats", "GET", description="Get database statistics")

def test_ml_models_status_endpoint():
    """Test the /api/ml-models/status endpoint"""
    return test_api_endpoint("ml-models/status", "GET", description="Get ML models status")

def test_ensemble_model_status_endpoint():
    """Test the /api/ensemble-model-status endpoint"""
    return test_api_endpoint("ensemble-model-status", "GET", description="Get ensemble model status")

def test_formations_endpoint():
    """Test the /api/formations endpoint"""
    return test_api_endpoint("formations", "GET", description="Get available formations")

def test_time_decay_presets_endpoint():
    """Test the /api/time-decay/presets endpoint"""
    return test_api_endpoint("time-decay/presets", "GET", description="Get time decay presets")

def test_prediction_configs_endpoint():
    """Test the /api/prediction-configs endpoint"""
    return test_api_endpoint("prediction-configs", "GET", description="Get prediction configurations")

def test_rbs_configs_endpoint():
    """Test the /api/rbs-configs endpoint"""
    return test_api_endpoint("rbs-configs", "GET", description="Get RBS configurations")

def test_datasets_endpoint():
    """Test the /api/datasets endpoint"""
    return test_api_endpoint("datasets", "GET", description="Get available datasets")

def test_standard_prediction_endpoint():
    """Test the /api/predict-match endpoint with test data"""
    test_data = {
        "home_team": "Arsenal",
        "away_team": "Chelsea",
        "referee_name": "Michael Oliver"
    }
    return test_api_endpoint("predict-match", "POST", test_data, description="Standard match prediction")

def test_enhanced_prediction_endpoint():
    """Test the /api/predict-match-enhanced endpoint with test data"""
    test_data = {
        "home_team": "Arsenal",
        "away_team": "Chelsea",
        "referee_name": "Michael Oliver",
        "use_time_decay": True,
        "decay_preset": "moderate"
    }
    return test_api_endpoint("predict-match-enhanced", "POST", test_data, description="Enhanced match prediction")

def test_ensemble_prediction_endpoint():
    """Test the /api/predict-match-ensemble endpoint with test data"""
    test_data = {
        "home_team": "Arsenal",
        "away_team": "Chelsea",
        "referee_name": "Michael Oliver"
    }
    return test_api_endpoint("predict-match-ensemble", "POST", test_data, description="Ensemble match prediction")

def test_compare_prediction_methods_endpoint():
    """Test the /api/compare-prediction-methods endpoint with test data"""
    test_data = {
        "home_team": "Arsenal",
        "away_team": "Chelsea",
        "referee_name": "Michael Oliver"
    }
    return test_api_endpoint("compare-prediction-methods", "POST", test_data, description="Compare prediction methods")

def test_team_players_endpoint():
    """Test the /api/teams/{team_name}/players endpoint"""
    team_name = "Arsenal"
    return test_api_endpoint(f"teams/{team_name}/players", "GET", description=f"Get players for {team_name}")

def test_team_performance_endpoint():
    """Test the /api/team-performance/{team_name} endpoint"""
    team_name = "Arsenal"
    return test_api_endpoint(f"team-performance/{team_name}", "GET", description=f"Get performance stats for {team_name}")

def test_enhanced_rbs_analysis_endpoint():
    """Test the /api/enhanced-rbs-analysis/{team_name}/{referee_name} endpoint"""
    team_name = "Arsenal"
    referee_name = "Michael Oliver"
    return test_api_endpoint(f"enhanced-rbs-analysis/{team_name}/{referee_name}", "GET", 
                            description=f"Get enhanced RBS analysis for {team_name} with {referee_name}")

def test_referee_analysis_endpoint():
    """Test the /api/referee-analysis endpoint"""
    return test_api_endpoint("referee-analysis", "GET", description="Get referee analysis")

def test_regression_stats_endpoint():
    """Test the /api/regression-stats endpoint"""
    return test_api_endpoint("regression-stats", "GET", description="Get regression statistics")

def run_core_api_tests():
    """Run tests for core API endpoints"""
    print("\n========== TESTING CORE BACKEND FUNCTIONALITY ==========\n")
    
    # Basic API endpoints
    print("\n----- Testing Basic API Endpoints -----")
    teams_result = test_teams_endpoint()
    referees_result = test_referees_endpoint()
    stats_result = test_stats_endpoint()
    
    # Database connectivity
    print("\n----- Testing Database Connectivity -----")
    db_stats_result = test_database_stats_endpoint()
    datasets_result = test_datasets_endpoint()
    
    # ML model status
    print("\n----- Testing ML Model Status -----")
    ml_status_result = test_ml_models_status_endpoint()
    ensemble_status_result = test_ensemble_model_status_endpoint()
    
    # Configuration endpoints
    print("\n----- Testing Configuration Endpoints -----")
    formations_result = test_formations_endpoint()
    time_decay_result = test_time_decay_presets_endpoint()
    prediction_configs_result = test_prediction_configs_endpoint()
    rbs_configs_result = test_rbs_configs_endpoint()
    
    # Team and player data endpoints
    print("\n----- Testing Team and Player Data Endpoints -----")
    team_players_result = test_team_players_endpoint()
    team_performance_result = test_team_performance_endpoint()
    
    # Analysis endpoints
    print("\n----- Testing Analysis Endpoints -----")
    rbs_analysis_result = test_enhanced_rbs_analysis_endpoint()
    referee_analysis_result = test_referee_analysis_endpoint()
    regression_stats_result = test_regression_stats_endpoint()
    
    # Prediction endpoints
    print("\n----- Testing Prediction Endpoints -----")
    standard_prediction_result = test_standard_prediction_endpoint()
    enhanced_prediction_result = test_enhanced_prediction_endpoint()
    ensemble_prediction_result = test_ensemble_prediction_endpoint()
    compare_prediction_result = test_compare_prediction_methods_endpoint()
    
    # Summarize results
    print("\n========== TEST SUMMARY ==========\n")
    
    # Basic API endpoints
    print("Basic API Endpoints:")
    print(f"  Teams Endpoint: {'✅ Passed' if teams_result else '❌ Failed'}")
    print(f"  Referees Endpoint: {'✅ Passed' if referees_result else '❌ Failed'}")
    print(f"  Stats Endpoint: {'✅ Passed' if stats_result else '❌ Failed'}")
    
    # Database connectivity
    print("\nDatabase Connectivity:")
    print(f"  Database Stats Endpoint: {'✅ Passed' if db_stats_result else '❌ Failed'}")
    print(f"  Datasets Endpoint: {'✅ Passed' if datasets_result else '❌ Failed'}")
    
    # ML model status
    print("\nML Model Status:")
    print(f"  ML Models Status Endpoint: {'✅ Passed' if ml_status_result else '❌ Failed'}")
    print(f"  Ensemble Model Status Endpoint: {'✅ Passed' if ensemble_status_result else '❌ Failed'}")
    
    # Configuration endpoints
    print("\nConfiguration Endpoints:")
    print(f"  Formations Endpoint: {'✅ Passed' if formations_result else '❌ Failed'}")
    print(f"  Time Decay Presets Endpoint: {'✅ Passed' if time_decay_result else '❌ Failed'}")
    print(f"  Prediction Configs Endpoint: {'✅ Passed' if prediction_configs_result else '❌ Failed'}")
    print(f"  RBS Configs Endpoint: {'✅ Passed' if rbs_configs_result else '❌ Failed'}")
    
    # Team and player data endpoints
    print("\nTeam and Player Data Endpoints:")
    print(f"  Team Players Endpoint: {'✅ Passed' if team_players_result else '❌ Failed'}")
    print(f"  Team Performance Endpoint: {'✅ Passed' if team_performance_result else '❌ Failed'}")
    
    # Analysis endpoints
    print("\nAnalysis Endpoints:")
    print(f"  Enhanced RBS Analysis Endpoint: {'✅ Passed' if rbs_analysis_result else '❌ Failed'}")
    print(f"  Referee Analysis Endpoint: {'✅ Passed' if referee_analysis_result else '❌ Failed'}")
    print(f"  Regression Stats Endpoint: {'✅ Passed' if regression_stats_result else '❌ Failed'}")
    
    # Prediction endpoints
    print("\nPrediction Endpoints:")
    print(f"  Standard Prediction Endpoint: {'✅ Passed' if standard_prediction_result else '❌ Failed'}")
    print(f"  Enhanced Prediction Endpoint: {'✅ Passed' if enhanced_prediction_result else '❌ Failed'}")
    print(f"  Ensemble Prediction Endpoint: {'✅ Passed' if ensemble_prediction_result else '❌ Failed'}")
    print(f"  Compare Prediction Methods Endpoint: {'✅ Passed' if compare_prediction_result else '❌ Failed'}")
    
    # Overall assessment
    all_tests = [
        teams_result, referees_result, stats_result,
        db_stats_result, datasets_result,
        ml_status_result, ensemble_status_result,
        formations_result, time_decay_result, prediction_configs_result, rbs_configs_result,
        team_players_result, team_performance_result,
        rbs_analysis_result, referee_analysis_result, regression_stats_result,
        standard_prediction_result, enhanced_prediction_result, ensemble_prediction_result, compare_prediction_result
    ]
    
    passed_tests = sum(1 for test in all_tests if test)
    total_tests = len(all_tests)
    
    print(f"\nOverall: {passed_tests}/{total_tests} tests passed ({passed_tests/total_tests*100:.1f}%)")
    
    if passed_tests == total_tests:
        print("\n✅ All backend API endpoints are working correctly!")
    else:
        print(f"\n⚠️ {total_tests - passed_tests} tests failed. See details above.")

if __name__ == "__main__":
    # Run the core API tests
    run_core_api_tests()