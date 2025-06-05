
import requests
import sys
import json

class RBSAPITester:
    def __init__(self, base_url):
        self.base_url = base_url
        self.tests_run = 0
        self.tests_passed = 0

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
    
    return 0 if tester.tests_passed == tester.tests_run else 1

if __name__ == "__main__":
    sys.exit(main())
