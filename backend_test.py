import requests
import os
import json
import base64
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

def run_tests():
    """Run all tests"""
    print("\n\n========== TESTING ENHANCED RBS CALCULATION FUNCTIONALITY ==========\n")
    
    # Test comprehensive team stats calculation
    comprehensive_stats_data = test_comprehensive_team_stats()
    
    # Test enhanced RBS calculation
    rbs_calculation_data = test_enhanced_rbs_calculation()
    
    # Test team performance stats to verify derived statistics
    team_performance_data = test_team_performance_stats()
    
    # Test RBS results to verify statistics
    rbs_results_data = test_rbs_results_stats()
    
    # Verify data integration
    data_integration_success = verify_data_integration()
    
    # Print summary of tests
    print("\n\n========== ENHANCED RBS CALCULATION TESTS SUMMARY ==========\n")
    
    if comprehensive_stats_data and comprehensive_stats_data.get('success'):
        print(f"✅ Comprehensive Team Stats Calculation: {comprehensive_stats_data.get('records_updated')} records updated")
    else:
        print("❌ Comprehensive Team Stats Calculation: Failed")
    
    if rbs_calculation_data and rbs_calculation_data.get('success'):
        print(f"✅ Enhanced RBS Calculation: {rbs_calculation_data.get('results_count')} results calculated")
    else:
        print("❌ Enhanced RBS Calculation: Failed")
    
    if team_performance_data and team_performance_data.get('success'):
        home_stats = team_performance_data.get('home_stats', {})
        away_stats = team_performance_data.get('away_stats', {})
        
        # Check for non-zero values in key stats
        key_stats = ['xg_per_shot', 'shots_total']
        all_stats_ok = all(home_stats.get(stat, 0) > 0 or away_stats.get(stat, 0) > 0 for stat in key_stats)
        
        if all_stats_ok:
            print("✅ Team Performance Stats: All key statistics have non-zero values")
        else:
            print("❌ Team Performance Stats: Some key statistics have zero values")
    else:
        print("❌ Team Performance Stats: Failed")
    
    if rbs_results_data and rbs_results_data.get('success'):
        results = rbs_results_data.get('results', [])
        if results:
            print(f"✅ RBS Results Stats: {len(results)} results verified")
        else:
            print("❌ RBS Results Stats: No results found")
    else:
        print("❌ RBS Results Stats: Failed")
    
    if data_integration_success:
        print("✅ Data Integration: Player statistics are properly aggregated into team-level statistics")
    else:
        print("❌ Data Integration: Player statistics are not properly aggregated into team-level statistics")
    
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

if __name__ == "__main__":
    run_tests()
