
import requests
import sys
import time
import json

class SoccerRefereeAPITester:
    def __init__(self, base_url):
        self.base_url = base_url
        self.tests_run = 0
        self.tests_passed = 0
        self.test_results = []

    def run_test(self, name, method, endpoint, expected_status=200, data=None, params=None):
        """Run a single API test"""
        url = f"{self.base_url}/{endpoint}"
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
                try:
                    response_data = response.json()
                    print(f"Response: {json.dumps(response_data, indent=2)[:500]}...")
                except:
                    print(f"Response: {response.text[:500]}...")
            else:
                print(f"❌ Failed - Expected {expected_status}, got {response.status_code}")
                print(f"Response: {response.text[:500]}...")
            
            self.test_results.append({
                "name": name,
                "success": success,
                "status_code": response.status_code,
                "expected_status": expected_status
            })
            
            return success, response
            
        except Exception as e:
            print(f"❌ Failed - Error: {str(e)}")
            self.test_results.append({
                "name": name,
                "success": False,
                "error": str(e)
            })
            return False, None

    def test_root_endpoint(self):
        """Test the root API endpoint"""
        return self.run_test(
            "Root API Endpoint",
            "GET",
            "api"
        )

    def test_stats_endpoint(self):
        """Test the stats endpoint"""
        return self.run_test(
            "Stats Endpoint",
            "GET",
            "api/stats"
        )

    def test_teams_endpoint(self):
        """Test the teams endpoint"""
        return self.run_test(
            "Teams Endpoint",
            "GET",
            "api/teams"
        )

    def test_referees_endpoint(self):
        """Test the referees endpoint"""
        return self.run_test(
            "Referees Endpoint",
            "GET",
            "api/referees"
        )

    def test_rbs_results_endpoint(self):
        """Test the RBS results endpoint"""
        return self.run_test(
            "RBS Results Endpoint",
            "GET",
            "api/rbs-results"
        )

    def print_summary(self):
        """Print a summary of all test results"""
        print("\n" + "="*50)
        print(f"📊 TEST SUMMARY: {self.tests_passed}/{self.tests_run} tests passed")
        print("="*50)
        
        for i, result in enumerate(self.test_results, 1):
            status = "✅ PASSED" if result.get("success") else "❌ FAILED"
            print(f"{i}. {result.get('name')}: {status}")
            if not result.get("success") and "error" in result:
                print(f"   Error: {result.get('error')}")
            elif not result.get("success"):
                print(f"   Expected status: {result.get('expected_status')}, Got: {result.get('status_code')}")
        
        print("="*50)
        return self.tests_passed == self.tests_run

def main():
    # Get the backend URL from the frontend .env file
    backend_url = "https://e7fa081f-0d6b-4b42-b4c2-b224675e76d7.preview.emergentagent.com"
    
    print(f"Testing Soccer Referee Bias Analysis Platform API at: {backend_url}")
    
    # Initialize the tester
    tester = SoccerRefereeAPITester(backend_url)
    
    # Run the tests
    tester.test_root_endpoint()
    tester.test_stats_endpoint()
    tester.test_teams_endpoint()
    tester.test_referees_endpoint()
    tester.test_rbs_results_endpoint()
    
    # Print summary
    all_passed = tester.print_summary()
    
    return 0 if all_passed else 1

if __name__ == "__main__":
    sys.exit(main())
