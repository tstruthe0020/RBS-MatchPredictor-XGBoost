
import requests
import sys
import json

class RBSAPITester:
    def __init__(self, base_url):
        self.base_url = base_url
        self.tests_run = 0
        self.tests_passed = 0
        
    def test_regression_stats(self):
        """Test the regression-stats endpoint"""
        success, response = self.run_test(
            "Get Available Regression Stats",
            "GET",
            "regression-stats",
            200
        )
        
        if success:
            print(f"Successfully retrieved available regression stats")
            
            # Check if the response has the expected structure
            if 'available_stats' in response:
                print(f"Available stats: {response.get('available_stats', [])}")
            else:
                print("⚠️ Response is missing 'available_stats' field")
                
            if 'targets' in response:
                print(f"Available targets: {response.get('targets', [])}")
            else:
                print("⚠️ Response is missing 'targets' field")
                
            if 'descriptions' in response:
                print(f"Stat descriptions included: {len(response.get('descriptions', {}))}")
            else:
                print("⚠️ Response is missing 'descriptions' field")
                
            return success, response
        return False, None
        
    def test_regression_analysis(self, selected_stats, target, test_size=0.2, random_state=42):
        """Test the regression-analysis endpoint"""
        data = {
            "selected_stats": selected_stats,
            "target": target,
            "test_size": test_size,
            "random_state": random_state
        }
        
        success, response = self.run_test(
            f"Perform Regression Analysis (Target: {target}, Stats: {', '.join(selected_stats)})",
            "POST",
            "regression-analysis",
            200,
            data=data
        )
        
        if success:
            print(f"Regression analysis successful: {response.get('success', False)}")
            if response.get('success', False):
                print(f"Model type: {response.get('model_type', 'unknown')}")
                print(f"Sample size: {response.get('sample_size', 0)}")
                
                # Check model-specific results
                results = response.get('results', {})
                if target == 'points_per_game':
                    if 'r2_score' in results:
                        print(f"R² score: {results.get('r2_score', 0)}")
                    if 'rmse' in results:
                        print(f"RMSE: {results.get('rmse', 0)}")
                    if 'coefficients' in results:
                        print("Coefficients included in response")
                        for stat, coef in results.get('coefficients', {}).items():
                            print(f"  {stat}: {coef}")
                elif target == 'match_result':
                    if 'accuracy' in results:
                        print(f"Accuracy: {results.get('accuracy', 0)}")
                    if 'feature_importance' in results:
                        print("Feature importance included in response")
                        for stat, importance in results.get('feature_importance', {}).items():
                            print(f"  {stat}: {importance}")
                    if 'classification_report' in results:
                        print("Classification report included in response")
            else:
                print(f"Regression analysis failed with error: {response.get('message', 'Unknown error')}")
                
            return success, response
        return False, None
        
    def test_regression_analysis_invalid_stats(self, target='points_per_game'):
        """Test the regression-analysis endpoint with invalid stats"""
        data = {
            "selected_stats": ["invalid_stat_1", "invalid_stat_2"],
            "target": target
        }
        
        success, response = self.run_test(
            f"Regression Analysis with Invalid Stats (Target: {target})",
            "POST",
            "regression-analysis",
            200,  # Should still return 200 with success=False in the response
            data=data
        )
        
        if success:
            if not response.get('success', True):
                print("✅ Correctly handled invalid stats")
                print(f"Error message: {response.get('message', 'No error message')}")
            else:
                print("⚠️ API accepted invalid stats without error")
                
            return success, response
        return False, None
        
    def test_regression_analysis_empty_stats(self, target='points_per_game'):
        """Test the regression-analysis endpoint with empty stats list"""
        data = {
            "selected_stats": [],
            "target": target
        }
        
        success, response = self.run_test(
            f"Regression Analysis with Empty Stats (Target: {target})",
            "POST",
            "regression-analysis",
            200,  # Should still return 200 with success=False in the response
            data=data
        )
        
        if success:
            if not response.get('success', True):
                print("✅ Correctly handled empty stats list")
                print(f"Error message: {response.get('message', 'No error message')}")
            else:
                print("⚠️ API accepted empty stats list without error")
                
            return success, response
        return False, None
        
    def test_suggest_prediction_config(self):
        """Test the suggest-prediction-config endpoint"""
        success, response = self.run_test(
            "Suggest Prediction Config",
            "POST",
            "suggest-prediction-config",
            200
        )
        
        if success:
            print(f"Config suggestion successful: {response.get('success', False)}")
            if response.get('success', False):
                suggestions = response.get('suggestions', {})
                
                # Check if the response has the expected structure
                if 'suggested_config_name' in suggestions:
                    print(f"Suggested config name: {suggestions.get('suggested_config_name', '')}")
                else:
                    print("⚠️ Response is missing 'suggested_config_name' field")
                
                if 'analysis_basis' in suggestions:
                    analysis_basis = suggestions.get('analysis_basis', {})
                    print(f"R² score: {analysis_basis.get('r2_score', 0)}")
                    print(f"Sample size: {analysis_basis.get('sample_size', 0)}")
                    print(f"Stats analyzed: {analysis_basis.get('stats_analyzed', [])}")
                else:
                    print("⚠️ Response is missing 'analysis_basis' field")
                
                if 'suggestions' in suggestions:
                    suggestion_details = suggestions.get('suggestions', {})
                    print(f"Suggestion categories: {list(suggestion_details.keys())}")
                    
                    # Check for xg_calculation suggestions
                    if 'xg_calculation' in suggestion_details:
                        xg_calc = suggestion_details.get('xg_calculation', {})
                        print(f"xG calculation explanation: {xg_calc.get('explanation', '')}")
                        print(f"Current default weights: {xg_calc.get('current_default', {})}")
                    
                    # Check for adjustments suggestions
                    if 'adjustments' in suggestion_details:
                        adjustments = suggestion_details.get('adjustments', {})
                        if adjustments:
                            print(f"Adjustment recommendations: {list(adjustments.keys())}")
                            for adj_name, adj_details in adjustments.items():
                                print(f"  {adj_name}: {adj_details.get('recommendation', '')}")
                                print(f"    Reason: {adj_details.get('reason', '')}")
                    
                    # Check confidence level
                    if 'confidence_level' in suggestion_details:
                        print(f"Confidence level: {suggestion_details.get('confidence_level', '')}")
                else:
                    print("⚠️ Response is missing 'suggestions' field")
            else:
                print(f"Config suggestion failed with error: {response.get('message', 'Unknown error')}")
                
            return success, response
        return False, None

    def run_test(self, name, method, endpoint, expected_status, data=None, params=None):
        """Run a single API test"""
        url = f"{self.base_url}/api/{endpoint}"
        headers = {'Content-Type': 'application/json'}
        
        self.tests_run += 1
        print(f"\n🔍 Testing {name}...")
        
        try:
            if method == 'GET':
                response = requests.get(url, headers=headers, params=params)
            elif method == 'POST':
                response = requests.post(url, json=data, headers=headers)
            elif method == 'DELETE':
                response = requests.delete(url, headers=headers)

            success = response.status_code == expected_status
            if success:
                self.tests_passed += 1
                print(f"✅ Passed - Status: {response.status_code}")
                return success, response.json()
            else:
                print(f"❌ Failed - Expected {expected_status}, got {response.status_code}")
                try:
                    error_details = response.json()
                    print(f"Error details: {json.dumps(error_details, indent=2)}")
                except:
                    print(f"Response text: {response.text}")
                return False, None

        except Exception as e:
            print(f"❌ Failed - Error: {str(e)}")
            return False, None

    def test_referee_summary(self):
        """Test the referee-summary endpoint"""
        success, response = self.run_test(
            "Get Referee Summary",
            "GET",
            "referee-summary",
            200
        )
        
        if success:
            referees = response.get('referees', [])
            print(f"Found {len(referees)} referees in summary")
            
            if len(referees) > 0:
                print("\nSample Referee Summary:")
                for i, referee in enumerate(referees[:3]):  # Show first 3 referees
                    print(f"{i+1}. Referee: {referee['_id']}, Matches: {referee.get('total_matches', 0)}, RBS Count: {referee.get('rbs_count', 0)}")
                
                # Return the first referee name for further testing
                first_referee = referees[0]['_id'] if referees else None
                return success, referees, first_referee
            return success, referees, None
        return False, [], None

    def test_referee_details(self, referee_name):
        """Test the referee/{referee_name} endpoint"""
        if not referee_name:
            print("⚠️ No referee name provided for testing referee details")
            return False, None
            
        success, response = self.run_test(
            f"Get Referee Details for '{referee_name}'",
            "GET",
            f"referee/{referee_name}",
            200
        )
        
        if success:
            print(f"Successfully retrieved details for referee: {referee_name}")
            print(f"Total matches: {response.get('total_matches', 0)}")
            print(f"Total teams: {response.get('total_teams', 0)}")
            
            # Check if the response has the expected structure
            if 'rbs_results' in response:
                print(f"RBS results count: {len(response['rbs_results'])}")
            else:
                print("⚠️ Response is missing 'rbs_results' field")
                
            if 'overall_averages' in response:
                print("Overall averages included in response")
            else:
                print("⚠️ Response is missing 'overall_averages' field")
                
            if 'matches' in response:
                print(f"Sample matches included: {len(response['matches'])}")
            else:
                print("⚠️ Response is missing 'matches' field")
                
            return success, response
        return False, None

    def test_rbs_results(self):
        """Test the RBS results endpoint"""
        success, response = self.run_test(
            "Get RBS Results",
            "GET",
            "rbs-results",
            200
        )
        
        if success:
            results = response.get('results', [])
            print(f"Found {len(results)} RBS results")
            
            if len(results) > 0:
                print("\nSample RBS Results:")
                for i, result in enumerate(results[:5]):  # Show first 5 results
                    print(f"{i+1}. Team: {result['team_name']}, Referee: {result['referee']}, RBS Score: {result['rbs_score']}")
            
            return success, results
        return False, []

    def test_teams(self):
        """Test the teams endpoint"""
        success, response = self.run_test(
            "Get Teams",
            "GET",
            "teams",
            200
        )
        
        if success:
            teams = response.get('teams', [])
            print(f"Found {len(teams)} teams")
            return success, teams
        return False, []

    def test_referees(self):
        """Test the referees endpoint"""
        success, response = self.run_test(
            "Get Referees",
            "GET",
            "referees",
            200
        )
        
        if success:
            referees = response.get('referees', [])
            print(f"Found {len(referees)} referees")
            return success, referees
        return False, []

    def test_stats(self):
        """Test the stats endpoint"""
        success, response = self.run_test(
            "Get Stats",
            "GET",
            "stats",
            200
        )
        
        if success:
            print(f"Stats: {json.dumps(response, indent=2)}")
            return success, response
        return False, {}
        
    def test_predict_match(self, home_team, away_team, referee_name, match_date=None):
        """Test the match prediction endpoint"""
        data = {
            "home_team": home_team,
            "away_team": away_team,
            "referee_name": referee_name
        }
        
        if match_date:
            data["match_date"] = match_date
            
        success, response = self.run_test(
            f"Predict Match: {home_team} vs {away_team} (Referee: {referee_name})",
            "POST",
            "predict-match",
            200,
            data=data
        )
        
        if success:
            print(f"Prediction successful: {response.get('success', False)}")
            if response.get('success', False):
                print(f"Predicted score: {response.get('home_team', '')} {response.get('predicted_home_goals', 0)} - {response.get('predicted_away_goals', 0)} {response.get('away_team', '')}")
                print(f"Home xG: {response.get('home_xg', 0)}, Away xG: {response.get('away_xg', 0)}")
                
                # Check if the response has the expected structure
                if 'prediction_breakdown' in response:
                    print("Prediction breakdown included in response")
                else:
                    print("⚠️ Response is missing 'prediction_breakdown' field")
                    
                if 'confidence_factors' in response:
                    print("Confidence factors included in response")
                else:
                    print("⚠️ Response is missing 'confidence_factors' field")
            else:
                print(f"Prediction failed with error: {response.get('prediction_breakdown', {}).get('error', 'Unknown error')}")
                
            return success, response
        return False, None
        
    def test_predict_match_invalid_team(self, home_team, away_team, referee_name):
        """Test the match prediction endpoint with invalid team names"""
        data = {
            "home_team": home_team,
            "away_team": away_team,
            "referee_name": referee_name
        }
            
        success, response = self.run_test(
            f"Predict Match with Invalid Team: {home_team} vs {away_team}",
            "POST",
            "predict-match",
            200,  # Should still return 200 with success=False in the response
            data=data
        )
        
        if success:
            if not response.get('success', True):
                print("✅ Correctly handled invalid team name")
                print(f"Error message: {response.get('prediction_breakdown', {}).get('error', 'No error message')}")
            else:
                print("⚠️ API accepted invalid team name without error")
                
            return success, response
        return False, None
        
    def test_predict_match_missing_fields(self):
        """Test the match prediction endpoint with missing required fields"""
        # Missing home_team
        data1 = {
            "away_team": "Team A",
            "referee_name": "Referee X"
        }
        
        # Missing away_team
        data2 = {
            "home_team": "Team B",
            "referee_name": "Referee X"
        }
        
        # Missing referee_name
        data3 = {
            "home_team": "Team B",
            "away_team": "Team A"
        }
        
        test_cases = [
            ("Missing home_team", data1),
            ("Missing away_team", data2),
            ("Missing referee_name", data3)
        ]
        
        results = []
        for name, data in test_cases:
            success, response = self.run_test(
                f"Predict Match with {name}",
                "POST",
                "predict-match",
                422,  # Should return 422 Unprocessable Entity
                data=data
            )
            results.append((name, success, response))
            
        return results
        
    def test_team_performance(self, team_name):
        """Test the team performance endpoint"""
        success, response = self.run_test(
            f"Get Team Performance for '{team_name}'",
            "GET",
            f"team-performance/{team_name}",
            200
        )
        
        if success:
            print(f"Successfully retrieved performance data for team: {team_name}")
            print(f"Total matches: {response.get('total_matches', 0)}")
            
            # Check if the response has the expected structure
            if 'home_stats' in response:
                print("Home stats included in response")
                home_stats = response.get('home_stats', {})
                if home_stats:
                    print(f"Home matches: {home_stats.get('matches_count', 0)}")
                    print(f"Home xG average: {home_stats.get('xg', 0)}")
            else:
                print("⚠️ Response is missing 'home_stats' field")
                
            if 'away_stats' in response:
                print("Away stats included in response")
                away_stats = response.get('away_stats', {})
                if away_stats:
                    print(f"Away matches: {away_stats.get('matches_count', 0)}")
                    print(f"Away xG average: {away_stats.get('xg', 0)}")
            else:
                print("⚠️ Response is missing 'away_stats' field")
                
            if 'ppg' in response:
                print(f"Points Per Game (PPG): {response.get('ppg', 0)}")
            else:
                print("⚠️ Response is missing 'ppg' field")
                
            return success, response
        return False, None
        
    def test_team_performance_invalid(self, team_name):
        """Test the team performance endpoint with an invalid team name"""
        success, response = self.run_test(
            f"Get Team Performance for invalid team '{team_name}'",
            "GET",
            f"team-performance/{team_name}",
            500  # Should return 500 Internal Server Error
        )
        
        if not success:
            print("✅ Correctly rejected invalid team name")
            return True, response
        else:
            print("⚠️ API accepted invalid team name without error")
            return False, response
            
    # RBS Configuration Tests
    def test_initialize_default_rbs_config(self):
        """Test initializing the default RBS configuration"""
        success, response = self.run_test(
            "Initialize Default RBS Config",
            "POST",
            "initialize-default-rbs-config",
            200
        )
        
        if success:
            print(f"Default RBS config initialized: {response.get('success', False)}")
            if response.get('success', False):
                config = response.get('config', {})
                print(f"Config name: {config.get('config_name', 'unknown')}")
                print(f"Yellow cards weight: {config.get('yellow_cards_weight', 0)}")
                print(f"Red cards weight: {config.get('red_cards_weight', 0)}")
                print(f"Fouls committed weight: {config.get('fouls_committed_weight', 0)}")
                print(f"Fouls drawn weight: {config.get('fouls_drawn_weight', 0)}")
                print(f"Penalties awarded weight: {config.get('penalties_awarded_weight', 0)}")
                print(f"xG difference weight: {config.get('xg_difference_weight', 0)}")
                print(f"Possession percentage weight: {config.get('possession_percentage_weight', 0)}")
            return success, response
        return False, None
        
    def test_create_custom_rbs_config(self, config_name="test_config"):
        """Test creating a custom RBS configuration"""
        data = {
            "config_name": config_name,
            "yellow_cards_weight": 0.4,
            "red_cards_weight": 0.6,
            "fouls_committed_weight": 0.2,
            "fouls_drawn_weight": 0.2,
            "penalties_awarded_weight": 0.7,
            "xg_difference_weight": 0.5,
            "possession_percentage_weight": 0.3,
            "confidence_matches_multiplier": 5,
            "max_confidence": 90,
            "min_confidence": 15,
            "confidence_threshold_low": 3,
            "confidence_threshold_medium": 6,
            "confidence_threshold_high": 12
        }
        
        success, response = self.run_test(
            f"Create Custom RBS Config '{config_name}'",
            "POST",
            "rbs-config",
            200,
            data=data
        )
        
        if success:
            print(f"Custom RBS config created: {response.get('success', False)}")
            if response.get('success', False):
                config = response.get('config', {})
                print(f"Config name: {config.get('config_name', 'unknown')}")
                print(f"Yellow cards weight: {config.get('yellow_cards_weight', 0)}")
                print(f"Red cards weight: {config.get('red_cards_weight', 0)}")
                print(f"xG difference weight: {config.get('xg_difference_weight', 0)}")
            return success, response
        return False, None
        
    def test_list_rbs_configs(self):
        """Test listing all RBS configurations"""
        success, response = self.run_test(
            "List RBS Configs",
            "GET",
            "rbs-configs",
            200
        )
        
        if success:
            configs = response.get('configs', [])
            print(f"Found {len(configs)} RBS configurations")
            
            if len(configs) > 0:
                print("\nAvailable RBS Configurations:")
                for i, config in enumerate(configs):
                    print(f"{i+1}. {config.get('config_name', 'unknown')}")
            return success, configs
        return False, []
        
    def test_get_specific_rbs_config(self, config_name):
        """Test getting a specific RBS configuration"""
        success, response = self.run_test(
            f"Get RBS Config '{config_name}'",
            "GET",
            f"rbs-config/{config_name}",
            200
        )
        
        if success:
            print(f"Successfully retrieved RBS config: {config_name}")
            config = response.get('config', {})
            if config:
                print(f"Yellow cards weight: {config.get('yellow_cards_weight', 0)}")
                print(f"Red cards weight: {config.get('red_cards_weight', 0)}")
                print(f"Fouls committed weight: {config.get('fouls_committed_weight', 0)}")
                print(f"Fouls drawn weight: {config.get('fouls_drawn_weight', 0)}")
                print(f"Penalties awarded weight: {config.get('penalties_awarded_weight', 0)}")
                print(f"xG difference weight: {config.get('xg_difference_weight', 0)}")
                print(f"Possession percentage weight: {config.get('possession_percentage_weight', 0)}")
            return success, config
        return False, None
        
    def test_delete_rbs_config(self, config_name):
        """Test deleting an RBS configuration"""
        success, response = self.run_test(
            f"Delete RBS Config '{config_name}'",
            "DELETE",
            f"rbs-config/{config_name}",
            200
        )
        
        if success:
            print(f"Successfully deleted RBS config: {config_name}")
            return success, response
        return False, None
        
    def test_delete_default_rbs_config(self):
        """Test attempting to delete the default RBS configuration (should fail)"""
        success, response = self.run_test(
            "Delete Default RBS Config (should fail)",
            "DELETE",
            "rbs-config/default",
            400  # Should return 400 Bad Request
        )
        
        if not success:
            print("✅ Correctly prevented deletion of default RBS config")
            return True, response
        else:
            print("❌ API incorrectly allowed deletion of default RBS config")
            return False, response
            
    def test_calculate_rbs(self, config_name="default"):
        """Test calculating RBS scores with a specific configuration"""
        success, response = self.run_test(
            f"Calculate RBS with config '{config_name}'",
            "POST",
            "calculate-rbs",
            200,
            params={"config_name": config_name}
        )
        
        if success:
            print(f"RBS calculation successful: {response.get('success', False)}")
            if response.get('success', False):
                print(f"Results count: {response.get('results_count', 0)}")
                print(f"Config used: {response.get('config_used', 'unknown')}")
            return success, response
        return False, None

def main():
    # Get backend URL from frontend .env
    with open('/app/frontend/.env', 'r') as f:
        for line in f:
            if line.startswith('REACT_APP_BACKEND_URL='):
                backend_url = line.strip().split('=')[1].strip('"\'')
                break
    
    print(f"Using backend URL: {backend_url}")
    
    # Setup tester
    tester = RBSAPITester(backend_url)
    
    # Run tests
    print("\n=== Testing Backend API ===")
    
    # Test stats endpoint to check if we have data
    stats_success, stats = tester.test_stats()
    
    # Test teams endpoint to get available teams for testing
    teams_success, teams = tester.test_teams()
    
    # Test referees endpoint to get available referees for testing
    referees_success, referees = tester.test_referees()
    
    # Store valid teams and referees for prediction testing
    valid_teams = teams if teams_success and teams else []
    valid_referees = referees if referees_success and referees else []
    
    # Test the new match prediction endpoint with valid data
    if valid_teams and len(valid_teams) >= 2 and valid_referees:
        home_team = valid_teams[0]
        away_team = valid_teams[1]
        referee_name = valid_referees[0]
        
        print("\n=== Testing Match Prediction API ===")
        prediction_success, prediction = tester.test_predict_match(home_team, away_team, referee_name)
        
        # Test with invalid team names
        invalid_home = "NonExistentTeam123"
        invalid_away = "FakeTeam456"
        
        print("\n=== Testing Match Prediction with Invalid Teams ===")
        invalid_team_success, invalid_prediction = tester.test_predict_match_invalid_team(
            invalid_home, away_team, referee_name
        )
        
        # Test with missing required fields
        print("\n=== Testing Match Prediction with Missing Fields ===")
        missing_fields_results = tester.test_predict_match_missing_fields()
        
        # Test team performance endpoint
        if valid_teams:
            print("\n=== Testing Team Performance API ===")
            team_performance_success, team_performance = tester.test_team_performance(valid_teams[0])
            
            # Test with invalid team name
            print("\n=== Testing Team Performance with Invalid Team ===")
            invalid_team_performance_success, invalid_team_performance = tester.test_team_performance_invalid("NonExistentTeam789")
    else:
        print("\n⚠️ Cannot test prediction endpoints without valid teams and referees")
        prediction_success = False
        team_performance_success = False
    
    # Test RBS Configuration System
    print("\n=== Testing RBS Configuration System ===")
    
    # Initialize default RBS config
    init_default_success, default_config = tester.test_initialize_default_rbs_config()
    
    # Create custom RBS config
    custom_config_name = "test_custom_rbs_config"
    create_custom_success, custom_config = tester.test_create_custom_rbs_config(custom_config_name)
    
    # List all RBS configs
    list_configs_success, configs = tester.test_list_rbs_configs()
    
    # Get specific RBS configs
    get_default_success, default_config_details = tester.test_get_specific_rbs_config("default")
    get_custom_success, custom_config_details = tester.test_get_specific_rbs_config(custom_config_name)
    
    # Try to delete default config (should fail)
    delete_default_success, delete_default_response = tester.test_delete_default_rbs_config()
    
    # Delete custom config
    delete_custom_success, delete_custom_response = tester.test_delete_rbs_config(custom_config_name)
    
    # Test RBS Calculation with Default Config
    print("\n=== Testing RBS Calculation ===")
    calculate_rbs_success, calculate_rbs_response = tester.test_calculate_rbs()
    
    # Create another custom config for testing calculation with custom config
    another_config_name = "another_test_config"
    create_another_success, another_config = tester.test_create_custom_rbs_config(another_config_name)
    
    # Calculate RBS with custom config
    calculate_custom_rbs_success, calculate_custom_rbs_response = tester.test_calculate_rbs(another_config_name)
    
    # Clean up by deleting the second custom config
    delete_another_success, delete_another_response = tester.test_delete_rbs_config(another_config_name)
    
    # Test Regression Analysis System
    print("\n=== Testing Regression Analysis System ===")
    
    # Test getting available regression stats
    regression_stats_success, regression_stats = tester.test_regression_stats()
    
    # Get available stats for regression testing
    available_stats = []
    if regression_stats_success and regression_stats and 'available_stats' in regression_stats:
        available_stats = regression_stats.get('available_stats', [])
    
    # Test regression analysis with different configurations
    if available_stats and len(available_stats) >= 2:
        # Test 1: Linear regression with xg_difference and possession_percentage
        linear_stats = ['xg_difference', 'possession_percentage']
        linear_stats = [stat for stat in linear_stats if stat in available_stats]
        if len(linear_stats) >= 2:
            linear_regression_success, linear_regression = tester.test_regression_analysis(
                linear_stats, 'points_per_game'
            )
        else:
            print("⚠️ Not enough valid stats for linear regression test")
            linear_regression_success = False
        
        # Test 2: Classification with yellow_cards and fouls_committed
        class_stats = ['yellow_cards', 'fouls_committed']
        class_stats = [stat for stat in class_stats if stat in available_stats]
        if len(class_stats) >= 2:
            classification_success, classification = tester.test_regression_analysis(
                class_stats, 'match_result'
            )
        else:
            print("⚠️ Not enough valid stats for classification test")
            classification_success = False
        
        # Test 3: Mixed analysis with multiple stats
        mixed_stats = ['xg_difference', 'yellow_cards', 'possession_percentage']
        mixed_stats = [stat for stat in mixed_stats if stat in available_stats]
        if len(mixed_stats) >= 2:
            mixed_analysis_success, mixed_analysis = tester.test_regression_analysis(
                mixed_stats, 'points_per_game'
            )
        else:
            print("⚠️ Not enough valid stats for mixed analysis test")
            mixed_analysis_success = False
        
        # Test 4: Error handling - invalid stats
        invalid_stats_success, invalid_stats = tester.test_regression_analysis_invalid_stats()
        
        # Test 5: Error handling - empty stats list
        empty_stats_success, empty_stats = tester.test_regression_analysis_empty_stats()
        
        # Test 6: Config suggestion endpoint
        config_suggestion_success, config_suggestion = tester.test_suggest_prediction_config()
    else:
        print("⚠️ Cannot test regression analysis without available stats")
        linear_regression_success = False
        classification_success = False
        mixed_analysis_success = False
        invalid_stats_success = False
        empty_stats_success = False
        config_suggestion_success = False
    
    # Print results
    print(f"\n📊 Tests passed: {tester.tests_passed}/{tester.tests_run}")
    
    # Print summary of findings
    print("\n=== API Testing Summary ===")
    
    if teams_success:
        print(f"✅ Found {len(valid_teams)} teams available for testing")
    else:
        print("❌ Could not retrieve teams list")
        
    if referees_success:
        print(f"✅ Found {len(valid_referees)} referees available for testing")
    else:
        print("❌ Could not retrieve referees list")
    
    if 'prediction_success' in locals() and prediction_success:
        print("✅ Match prediction endpoint is working correctly")
        if 'prediction' in locals() and prediction and prediction.get('success', False):
            print("✅ Prediction algorithm successfully generated predictions")
        else:
            print("⚠️ Prediction algorithm returned an error - this might be due to insufficient data")
    else:
        print("❌ Match prediction endpoint is not working correctly")
    
    if 'team_performance_success' in locals() and team_performance_success:
        print("✅ Team performance endpoint is working correctly")
    else:
        print("❌ Team performance endpoint is not working correctly")
    
    # RBS Configuration System Summary
    print("\n=== RBS Configuration System Summary ===")
    
    if init_default_success:
        print("✅ Default RBS configuration initialized successfully")
    else:
        print("❌ Failed to initialize default RBS configuration")
        
    if create_custom_success:
        print("✅ Custom RBS configuration created successfully")
    else:
        print("❌ Failed to create custom RBS configuration")
        
    if list_configs_success:
        print(f"✅ Successfully listed {len(configs)} RBS configurations")
    else:
        print("❌ Failed to list RBS configurations")
        
    if get_default_success:
        print("✅ Successfully retrieved default RBS configuration")
    else:
        print("❌ Failed to retrieve default RBS configuration")
        
    if get_custom_success:
        print("✅ Successfully retrieved custom RBS configuration")
    else:
        print("❌ Failed to retrieve custom RBS configuration")
        
    if delete_default_success:
        print("✅ Correctly prevented deletion of default RBS configuration")
    else:
        print("❌ Failed to prevent deletion of default RBS configuration")
        
    if delete_custom_success:
        print("✅ Successfully deleted custom RBS configuration")
    else:
        print("❌ Failed to delete custom RBS configuration")
    
    # RBS Calculation Summary
    print("\n=== RBS Calculation Summary ===")
    
    if calculate_rbs_success:
        print("✅ Successfully calculated RBS scores with default configuration")
        if calculate_rbs_response and calculate_rbs_response.get('success', False):
            print(f"✅ Generated {calculate_rbs_response.get('results_count', 0)} RBS results")
        else:
            print("⚠️ RBS calculation returned an error - this might be due to insufficient data")
    else:
        print("❌ Failed to calculate RBS scores with default configuration")
        
    if calculate_custom_rbs_success:
        print("✅ Successfully calculated RBS scores with custom configuration")
        if calculate_custom_rbs_response and calculate_custom_rbs_response.get('success', False):
            print(f"✅ Generated {calculate_custom_rbs_response.get('results_count', 0)} RBS results")
        else:
            print("⚠️ RBS calculation with custom config returned an error")
    else:
        print("❌ Failed to calculate RBS scores with custom configuration")
    
    # Regression Analysis Summary
    print("\n=== Regression Analysis Summary ===")
    
    if regression_stats_success:
        print("✅ Successfully retrieved available regression stats")
        if regression_stats:
            print(f"✅ Found {len(regression_stats.get('available_stats', []))} available stats for analysis")
            print(f"✅ Found {len(regression_stats.get('targets', []))} available targets for analysis")
    else:
        print("❌ Failed to retrieve available regression stats")
    
    if 'linear_regression_success' in locals() and linear_regression_success:
        print("✅ Successfully performed linear regression analysis")
        if 'linear_regression' in locals() and linear_regression and linear_regression.get('success', False):
            results = linear_regression.get('results', {})
            print(f"✅ Linear regression R² score: {results.get('r2_score', 0)}")
            print(f"✅ Linear regression RMSE: {results.get('rmse', 0)}")
        else:
            print("⚠️ Linear regression analysis returned an error")
    else:
        print("❌ Failed to perform linear regression analysis")
    
    if 'classification_success' in locals() and classification_success:
        print("✅ Successfully performed classification analysis")
        if 'classification' in locals() and classification and classification.get('success', False):
            results = classification.get('results', {})
            print(f"✅ Classification accuracy: {results.get('accuracy', 0)}")
        else:
            print("⚠️ Classification analysis returned an error")
    else:
        print("❌ Failed to perform classification analysis")
    
    if 'mixed_analysis_success' in locals() and mixed_analysis_success:
        print("✅ Successfully performed mixed analysis")
    else:
        print("❌ Failed to perform mixed analysis")
    
    if 'invalid_stats_success' in locals() and invalid_stats_success:
        print("✅ Successfully tested invalid stats handling")
    else:
        print("❌ Failed to test invalid stats handling")
    
    if 'empty_stats_success' in locals() and empty_stats_success:
        print("✅ Successfully tested empty stats list handling")
    else:
        print("❌ Failed to test empty stats list handling")
    
    if 'config_suggestion_success' in locals() and config_suggestion_success:
        print("✅ Successfully tested prediction config suggestion endpoint")
        if 'config_suggestion' in locals() and config_suggestion and config_suggestion.get('success', False):
            print("✅ Config suggestion algorithm generated meaningful recommendations")
        else:
            print("⚠️ Config suggestion returned an error - this might be due to insufficient data")
    else:
        print("❌ Failed to test prediction config suggestion endpoint")
    
    return 0 if tester.tests_passed == tester.tests_run else 1

if __name__ == "__main__":
    sys.exit(main())
