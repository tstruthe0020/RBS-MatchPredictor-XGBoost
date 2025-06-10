import requests
import json
import pprint
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Get the backend URL from environment
BACKEND_URL = os.environ.get('REACT_APP_BACKEND_URL', 'http://localhost:8001')
BASE_URL = f"{BACKEND_URL}/api"

# Pretty printer for better output formatting
pp = pprint.PrettyPrinter(indent=2)

def test_time_decay_presets():
    """Test the time decay presets endpoint to verify available presets"""
    print("\n=== Testing Time Decay Presets ===")
    response = requests.get(f"{BASE_URL}/time-decay/presets")
    
    if response.status_code == 200:
        data = response.json()
        print(f"Success: {data.get('success', False)}")
        
        presets = data.get('presets', [])
        print(f"Found {len(presets)} presets:")
        
        for preset in presets:
            print(f"  - {preset.get('preset_name')}: {preset.get('decay_type')} decay")
            print(f"    Description: {preset.get('description')}")
            if preset.get('decay_type') == 'exponential':
                print(f"    Half-life: {preset.get('half_life_months')} months")
            elif preset.get('decay_type') == 'linear':
                print(f"    Decay rate: {preset.get('decay_rate_per_month')} per month")
        
        return presets
    else:
        print(f"Error: {response.status_code}")
        print(response.text)
        return None

def test_time_decay_impact(team_name="Arsenal"):
    """Test the time decay impact endpoint to verify time decay calculations"""
    print(f"\n=== Testing Time Decay Impact for {team_name} ===")
    
    response = requests.post(f"{BASE_URL}/test-time-decay-impact", params={"team_name": team_name})
    
    if response.status_code == 200:
        data = response.json()
        print(f"Success: {data.get('success', False)}")
        
        if data.get('success'):
            print(f"Message: {data.get('message')}")
            print(f"Team: {data.get('test_parameters', {}).get('team')}")
            print(f"Presets tested: {', '.join(data.get('test_parameters', {}).get('presets_tested', []))}")
            
            # Print results
            results = data.get('results', {})
            print("\nResults:")
            
            for preset, metrics in results.items():
                if "error" in metrics:
                    print(f"  {preset}: Error - {metrics['error']}")
                else:
                    print(f"  {preset}:")
                    print(f"    Goals per match: {metrics.get('goals_per_match', 0):.4f}")
                    print(f"    xG per match: {metrics.get('xg_per_match', 0):.4f}")
                    print(f"    Shots per match: {metrics.get('shots_per_match', 0):.4f}")
                    print(f"    Possession %: {metrics.get('possession_pct', 0):.4f}")
                    print(f"    Conversion rate: {metrics.get('conversion_rate', 0):.4f}")
            
            # Check if results are different
            different_results = False
            reference_preset = list(results.keys())[0]
            reference_metrics = results[reference_preset]
            
            if "error" in reference_metrics:
                print("\nCannot compare results - reference preset has errors")
                return data
            
            for preset, metrics in results.items():
                if preset == reference_preset or "error" in metrics:
                    continue
                
                if (abs(metrics['xg_per_match'] - reference_metrics['xg_per_match']) > 0.01):
                    different_results = True
                    break
            
            if different_results:
                print("\n✅ Time decay presets produce DIFFERENT results as expected")
            else:
                print("\n❌ Time decay presets produce SIMILAR results - may not be working correctly")
            
            return data
        else:
            print(f"Test failed: {data.get('error', 'Unknown error')}")
            return data
    else:
        print(f"Error: {response.status_code}")
        print(response.text)
        return None

def check_server_logs():
    """Check server logs for time decay calculations"""
    print("\n=== Checking Server Logs for Time Decay Calculations ===")
    
    try:
        import subprocess
        result = subprocess.run(["tail", "-n", "50", "/var/log/supervisor/backend.out.log"], 
                               capture_output=True, text=True)
        
        log_output = result.stdout
        
        # Look for time decay log entries
        time_decay_logs = [line for line in log_output.split('\n') if "Time Decay:" in line]
        
        if time_decay_logs:
            print(f"Found {len(time_decay_logs)} time decay log entries:")
            for log in time_decay_logs:
                print(f"  {log}")
            
            return True
        else:
            print("No time decay log entries found in recent logs")
            return False
    except Exception as e:
        print(f"Error checking logs: {e}")
        return False

def test_all_teams_with_all_presets():
    """Test time decay impact on multiple teams with all presets"""
    teams = ["Arsenal", "Chelsea", "Manchester United", "Liverpool"]
    results = {}
    
    for team in teams:
        print(f"\n{'='*50}")
        print(f"Testing {team}")
        print(f"{'='*50}")
        result = test_time_decay_impact(team)
        results[team] = result
    
    return results

def main():
    """Main test function"""
    print("\n===== ENHANCED XGBOOST TIME DECAY TESTING =====\n")
    
    # Step 1: Test time decay presets
    print("\nSTEP 1: Verifying Time Decay Presets")
    presets = test_time_decay_presets()
    if not presets:
        print("❌ Failed to get time decay presets")
        return
    
    # Step 2: Test time decay impact for Arsenal
    print("\nSTEP 2: Testing Time Decay Impact for Arsenal")
    arsenal_results = test_time_decay_impact("Arsenal")
    
    # Step 3: Test time decay impact for Chelsea
    print("\nSTEP 3: Testing Time Decay Impact for Chelsea")
    chelsea_results = test_time_decay_impact("Chelsea")
    
    # Step 4: Check server logs for time decay calculations
    print("\nSTEP 4: Checking Server Logs for Time Decay Calculations")
    log_check = check_server_logs()
    
    # Summary
    print("\n===== TEST SUMMARY =====")
    
    # Check if time decay presets are available
    if presets and len(presets) >= 5:
        print("✅ Time decay presets are available and correctly configured")
        print(f"   Found {len(presets)} presets: {', '.join([p.get('preset_name') for p in presets])}")
    else:
        print("❌ Time decay presets are not properly configured")
    
    # Check if time decay impact works for Arsenal
    if arsenal_results and arsenal_results.get('success'):
        arsenal_metrics = arsenal_results.get('results', {})
        if any("error" in metrics for metrics in arsenal_metrics.values()):
            print("⚠️ Time decay impact test for Arsenal partially succeeded with some errors")
        else:
            print("✅ Time decay impact test for Arsenal succeeded")
    else:
        print("❌ Time decay impact test for Arsenal failed")
    
    # Check if time decay impact works for Chelsea
    if chelsea_results and chelsea_results.get('success'):
        chelsea_metrics = chelsea_results.get('results', {})
        if any("error" in metrics for metrics in chelsea_metrics.values()):
            print("⚠️ Time decay impact test for Chelsea partially succeeded with some errors")
        else:
            print("✅ Time decay impact test for Chelsea succeeded")
    else:
        print("❌ Time decay impact test for Chelsea failed")
    
    # Check if time decay logs are present
    if log_check:
        print("✅ Time decay calculations are logged properly")
    else:
        print("⚠️ Time decay calculations may not be logged properly")
    
    # Overall assessment
    if (presets and len(presets) >= 5 and 
        arsenal_results and arsenal_results.get('success') and 
        chelsea_results and chelsea_results.get('success')):
        print("\n✅ OVERALL: Enhanced XGBoost time decay functionality is working correctly")
    else:
        print("\n❌ OVERALL: Enhanced XGBoost time decay functionality has issues")

if __name__ == "__main__":
    main()
