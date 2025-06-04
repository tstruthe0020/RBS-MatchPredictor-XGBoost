
import requests
import sys
import time
import json
import os

class SoccerRefereeAPITester:
    def __init__(self, base_url):
        self.base_url = base_url
        self.tests_run = 0
        self.tests_passed = 0
        self.test_results = []

    def run_test(self, name, method, endpoint, expected_status=200, data=None, params=None, files=None):
        """Run a single API test"""
        url = f"{self.base_url}/{endpoint}"
        headers = {}
        if not files:  # Don't set Content-Type for multipart/form-data
            headers['Content-Type'] = 'application/json'
        
        self.tests_run += 1
        print(f"\n🔍 Testing {name}...")
        
        try:
            if method == 'GET':
                response = requests.get(url, headers=headers, params=params)
            elif method == 'POST':
                if files:
                    response = requests.post(url, files=files)
                else:
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
        
    def test_upload_matches(self, file_path):
        """Test uploading matches CSV file"""
        with open(file_path, 'rb') as f:
            files = {'file': ('sample_matches.csv', f, 'text/csv')}
            return self.run_test(
                "Upload Matches CSV",
                "POST",
                "api/upload/matches",
                200,
                files=files
            )
            
    def test_upload_team_stats(self, file_path):
        """Test uploading team stats CSV file"""
        with open(file_path, 'rb') as f:
            files = {'file': ('sample_team_stats.csv', f, 'text/csv')}
            return self.run_test(
                "Upload Team Stats CSV",
                "POST",
                "api/upload/team-stats",
                200,
                files=files
            )
            
    def test_calculate_rbs(self):
        """Test calculating RBS scores"""
        return self.run_test(
            "Calculate RBS Scores",
            "POST",
            "api/calculate-rbs",
            200
        )
        
    def test_filtered_rbs_results(self, team=None, referee=None):
        """Test filtered RBS results"""
        params = {}
        if team:
            params['team'] = team
        if referee:
            params['referee'] = referee
            
        filter_desc = ""
        if team:
            filter_desc += f" for team '{team}'"
        if referee:
            filter_desc += f" with referee '{referee}'"
            
        return self.run_test(
            f"Filtered RBS Results{filter_desc}",
            "GET",
            "api/rbs-results",
            200,
            params=params
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
    
    # Run basic API tests
    print("\n=== Testing Basic API Endpoints ===")
    tester.test_root_endpoint()
    tester.test_stats_endpoint()
    tester.test_teams_endpoint()
    tester.test_referees_endpoint()
    
    # Test the RBS calculation flow
    print("\n=== Testing Complete RBS Calculation Flow ===")
    
    # 1. Upload sample data
    print("\n1. Uploading Sample Data...")
    success_matches, _ = tester.test_upload_matches("/app/sample_matches.csv")
    success_team_stats, _ = tester.test_upload_team_stats("/app/sample_team_stats.csv")
    
    if success_matches and success_team_stats:
        # 2. Calculate RBS scores
        print("\n2. Calculating RBS Scores...")
        success_calc, calc_response = tester.test_calculate_rbs()
        
        if success_calc:
            # 3. Check RBS results - this is where the serialization fix should be tested
            print("\n3. Checking RBS Results (Testing ObjectId Serialization Fix)...")
            success_results, results_response = tester.test_rbs_results_endpoint()
            
            if success_results and results_response:
                results = results_response.json().get('results', [])
                if results:
                    print(f"\n✅ Successfully retrieved {len(results)} RBS results")
                    
                    # Check if the results contain the expected fields
                    sample_result = results[0]
                    print("\nSample RBS Result:")
                    print(json.dumps(sample_result, indent=2))
                    
                    # Check for _id field to verify serialization fix
                    if '_id' in sample_result:
                        print(f"\n✅ _id field is properly serialized: {sample_result['_id']}")
                    
                    # 4. Test filtered results
                    print("\n4. Testing Result Filtering...")
                    team = sample_result.get('team_name')
                    referee = sample_result.get('referee')
                    
                    if team:
                        print(f"\nTesting filter by team: {team}")
                        success_team_filter, team_filter_response = tester.test_filtered_rbs_results(team=team)
                        if success_team_filter and team_filter_response:
                            team_results = team_filter_response.json().get('results', [])
                            if all(r.get('team_name') == team for r in team_results):
                                print(f"✅ Team filter working correctly - all {len(team_results)} results are for team '{team}'")
                            else:
                                print("❌ Team filter not working correctly")
                    
                    if referee:
                        print(f"\nTesting filter by referee: {referee}")
                        success_ref_filter, ref_filter_response = tester.test_filtered_rbs_results(referee=referee)
                        if success_ref_filter and ref_filter_response:
                            ref_results = ref_filter_response.json().get('results', [])
                            if all(r.get('referee') == referee for r in ref_results):
                                print(f"✅ Referee filter working correctly - all {len(ref_results)} results are for referee '{referee}'")
                            else:
                                print("❌ Referee filter not working correctly")
                    
                    if team and referee:
                        print(f"\nTesting filter by team and referee: {team}, {referee}")
                        success_both_filter, both_filter_response = tester.test_filtered_rbs_results(team=team, referee=referee)
                        if success_both_filter and both_filter_response:
                            both_results = both_filter_response.json().get('results', [])
                            if all(r.get('team_name') == team and r.get('referee') == referee for r in both_results):
                                print(f"✅ Combined filter working correctly - all {len(both_results)} results match both criteria")
                            else:
                                print("❌ Combined filter not working correctly")
                else:
                    print("❌ No RBS results found in the response")
            else:
                print("❌ Failed to retrieve RBS results")
        else:
            print("❌ Failed to calculate RBS scores")
    else:
        print("❌ Failed to upload sample data")
    
    # 5. Check stats endpoint to verify RBS results count
    print("\n5. Verifying RBS Results Count...")
    success, stats_response = tester.test_stats_endpoint()
    if success and stats_response:
        stats = stats_response.json()
        rbs_results_count = stats.get('rbs_results', 0)
        print(f"\nRBS Results Count: {rbs_results_count}")
        if rbs_results_count > 0:
            print("✅ RBS calculation is working correctly!")
        else:
            print("❌ RBS calculation may not be working correctly - no results found")
    
    # Print summary
    all_passed = tester.print_summary()
    
    return 0 if all_passed else 1

if __name__ == "__main__":
    sys.exit(main())
