
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

            success = response.status_code == expected_status
            if success:
                self.tests_passed += 1
                print(f"✅ Passed - Status: {response.status_code}")
                return success, response.json()
            else:
                print(f"❌ Failed - Expected {expected_status}, got {response.status_code}")
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

def main():
    # Get backend URL from frontend .env
    with open('/app/frontend/.env', 'r') as f:
        for line in f:
            if line.startswith('REACT_APP_BACKEND_URL='):
                backend_url = line.strip().split('=')[1]
                break
    
    print(f"Using backend URL: {backend_url}")
    
    # Setup tester
    tester = RBSAPITester(backend_url)
    
    # Run tests
    print("\n=== Testing Backend API ===")
    
    # Test stats endpoint
    stats_success, stats = tester.test_stats()
    
    # Test teams endpoint
    teams_success, teams = tester.test_teams()
    
    # Test referees endpoint
    referees_success, referees = tester.test_referees()
    
    # Test referee summary endpoint (new test)
    summary_success, referee_summary, first_referee = tester.test_referee_summary()
    
    # Test referee details endpoint (new test)
    if first_referee:
        details_success, referee_details = tester.test_referee_details(first_referee)
    else:
        print("⚠️ Cannot test referee details endpoint without a valid referee name")
        details_success = False
    
    # Test RBS results endpoint
    rbs_success, rbs_results = tester.test_rbs_results()
    
    # Print results
    print(f"\n📊 Tests passed: {tester.tests_passed}/{tester.tests_run}")
    
    # Print summary of findings
    print("\n=== API Testing Summary ===")
    
    if summary_success:
        if len(referee_summary) == 0:
            print("⚠️ Referee summary endpoint is working but returned 0 referees.")
        else:
            print(f"✅ Referee summary endpoint is working correctly and returned {len(referee_summary)} referees.")
    else:
        print("❌ Referee summary endpoint is not working correctly.")
    
    if first_referee and details_success:
        print(f"✅ Referee details endpoint is working correctly for referee '{first_referee}'.")
    else:
        print("❌ Referee details endpoint is not working correctly.")
    
    if rbs_success:
        if len(rbs_results) == 0:
            print("⚠️ RBS results endpoint is working but returned 0 results.")
            print("This could indicate that no RBS calculations have been performed yet.")
        else:
            print(f"✅ RBS results endpoint is working correctly and returned {len(rbs_results)} results.")
    else:
        print("❌ RBS results endpoint is not working correctly.")
    
    return 0 if tester.tests_passed == tester.tests_run else 1

if __name__ == "__main__":
    sys.exit(main())
