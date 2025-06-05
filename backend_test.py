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

def test_comprehensive_regression_endpoint():
    """Test the comprehensive regression analysis endpoint"""
    print("\n=== Testing Comprehensive Regression Analysis Endpoint ===")
    
    # Test with a mix of RBS and Predictor variables
    test_data = {
        "selected_stats": [
            "yellow_cards", "red_cards", "fouls_committed", "fouls_drawn",  # RBS variables
            "xg", "shots_total", "xg_per_shot", "conversion_rate",  # Predictor variables
            "is_home"  # Context variable
        ],
        "target": "points_per_game",
        "test_size": 0.2,
        "random_state": 42
    }
    
    response = requests.post(f"{BASE_URL}/analyze-comprehensive-regression", json=test_data)
    
    if response.status_code == 200:
        print(f"Status: {response.status_code} OK")
        data = response.json()
        print(f"Success: {data['success']}")
        print(f"Target: {data.get('target')}")
        print(f"Model Type: {data.get('model_type')}")
        print(f"Sample Size: {data.get('sample_size')}")
        
        # Check selected stats
        selected_stats = data.get('selected_stats', [])
        print(f"\nSelected Stats: {len(selected_stats)}")
        print(f"  {', '.join(selected_stats)}")
        
        # Check results
        results = data.get('results', {})
        if 'coefficients' in results:
            print("\nCoefficients:")
            for var, coef in results['coefficients'].items():
                print(f"  - {var}: {coef}")
        
        if 'r2_score' in results:
            print(f"\nR² Score: {results['r2_score']}")
        
        # Check insights
        insights = data.get('insights', {})
        print(f"\nInsights sections: {len(insights)}")
        for section_name in insights.keys():
            print(f"  - {section_name}")
        
        # Check RBS variables insights
        if 'rbs_variables_in_analysis' in insights:
            rbs_insight = insights['rbs_variables_in_analysis']
            print("\nRBS Variables in Analysis:")
            print(f"  Variables: {', '.join(rbs_insight.get('variables', []))}")
            print(f"  Recommendation: {rbs_insight.get('recommendation')}")
        
        # Check Predictor variables insights
        if 'predictor_variables_in_analysis' in insights:
            predictor_insight = insights['predictor_variables_in_analysis']
            print("\nPredictor Variables in Analysis:")
            print(f"  Variables: {', '.join(predictor_insight.get('variables', []))}")
            print(f"  Recommendation: {predictor_insight.get('recommendation')}")
        
        # Check correlations
        if 'variable_correlations' in insights:
            correlations = insights['variable_correlations']
            print("\nVariable Correlations:")
            if 'strongest_positive' in correlations and correlations['strongest_positive']:
                var, corr = correlations['strongest_positive']
                print(f"  Strongest Positive: {var} ({corr})")
            if 'strongest_negative' in correlations and correlations['strongest_negative']:
                var, corr = correlations['strongest_negative']
                print(f"  Strongest Negative: {var} ({corr})")
        
        # Check data summary
        data_summary = data.get('data_summary', {})
        print(f"\nData Summary:")
        print(f"  Total Matches: {data_summary.get('total_matches')}")
        print(f"  Teams Analyzed: {data_summary.get('teams_analyzed')}")
        print(f"  Referees Analyzed: {data_summary.get('referees_analyzed')}")
        
        # Verify all required sections exist
        required_sections = ['insights', 'data_summary']
        missing_sections = [sec for sec in required_sections if sec not in data]
        
        if missing_sections:
            print(f"\n❌ Missing sections: {', '.join(missing_sections)}")
        else:
            print("\n✅ All required sections present")
        
        # Verify insights contain variable categorization
        required_insights = ['rbs_variables_in_analysis', 'predictor_variables_in_analysis', 'variable_correlations']
        missing_insights = [ins for ins in required_insights if ins not in insights]
        
        if missing_insights:
            print(f"❌ Missing insights: {', '.join(missing_insights)}")
        else:
            print("✅ All required insights present")
        
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
