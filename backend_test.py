
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
    
    # Test RBS results endpoint
    rbs_success, rbs_results = tester.test_rbs_results()
    
    # Print results
    print(f"\n📊 Tests passed: {tester.tests_passed}/{tester.tests_run}")
    
    if rbs_success:
        if len(rbs_results) == 0:
            print("\n⚠️ WARNING: RBS results endpoint is working but returned 0 results.")
            print("This could indicate that no RBS calculations have been performed yet.")
        else:
            print(f"\n✅ RBS results endpoint is working correctly and returned {len(rbs_results)} results.")
    
    return 0 if tester.tests_passed == tester.tests_run else 1

if __name__ == "__main__":
    sys.exit(main())
