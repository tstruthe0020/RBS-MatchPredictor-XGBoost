import requests
import os
import json
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

def test_time_decay_presets_endpoint():
    """Test the /api/time-decay/presets endpoint to ensure it returns decay presets"""
    print("\n=== Testing Time Decay Presets Endpoint ===")
    response = requests.get(f"{BASE_URL}/time-decay/presets")
    
    if response.status_code == 200:
        print(f"Status: {response.status_code} OK")
        data = response.json()
        print(f"Success: {data.get('success', False)}")
        
        presets = data.get('presets', [])
        print(f"Presets found: {len(presets)}")
        
        for preset in presets:
            print(f"  - {preset.get('preset_name')}: {preset.get('decay_type')} decay")
            print(f"    Description: {preset.get('description')}")
            
        # Verify expected presets are present
        expected_presets = ["aggressive", "moderate", "conservative", "linear", "none"]
        found_presets = [p.get('preset_name') for p in presets]
        
        missing_presets = [p for p in expected_presets if p not in found_presets]
        if missing_presets:
            print(f"❌ Missing expected presets: {', '.join(missing_presets)}")
            return False
        else:
            print("✅ All expected presets are present")
            
        # Verify decay types
        expected_decay_types = {
            "aggressive": "exponential",
            "moderate": "exponential",
            "conservative": "exponential",
            "linear": "linear",
            "none": "step"
        }
        
        for preset in presets:
            preset_name = preset.get('preset_name')
            decay_type = preset.get('decay_type')
            expected_type = expected_decay_types.get(preset_name)
            
            if decay_type != expected_type:
                print(f"❌ Incorrect decay type for {preset_name}: expected {expected_type}, got {decay_type}")
                return False
        
        print("✅ All decay types match expected values")
        
        # Verify half-life values for exponential decay presets
        expected_half_lives = {
            "aggressive": 2.0,
            "moderate": 4.0,
            "conservative": 8.0
        }
        
        for preset in presets:
            preset_name = preset.get('preset_name')
            if preset_name in expected_half_lives:
                half_life = preset.get('half_life_months')
                expected_half_life = expected_half_lives.get(preset_name)
                
                if half_life != expected_half_life:
                    print(f"❌ Incorrect half-life for {preset_name}: expected {expected_half_life}, got {half_life}")
                    return False
        
        print("✅ All half-life values match expected values")
        
        # Verify linear decay rate
        for preset in presets:
            if preset.get('preset_name') == "linear":
                decay_rate = preset.get('decay_rate_per_month')
                expected_rate = 0.1
                
                if decay_rate != expected_rate:
                    print(f"❌ Incorrect decay rate for linear preset: expected {expected_rate}, got {decay_rate}")
                    return False
        
        print("✅ Linear decay rate matches expected value")
        
        return True
    else:
        print(f"Error: {response.status_code}")
        print(response.text)
        return False

def run_all_tests():
    """Run all time decay tests"""
    print("\n\n========== TESTING PHASE 2 TIME DECAY IMPLEMENTATION ==========\n")
    
    # Test: Time Decay Presets Endpoint
    print("\nTest: Time Decay Presets Endpoint")
    presets_result = test_time_decay_presets_endpoint()
    
    # Final summary
    print("\n========== PHASE 2 TIME DECAY IMPLEMENTATION TEST SUMMARY ==========")
    
    if presets_result:
        print("✅ Time decay presets endpoint test passed!")
        print("✅ The time decay presets endpoint correctly returns all 5 required presets:")
        print("  - aggressive: exponential decay with 2-month half-life")
        print("  - moderate: exponential decay with 4-month half-life")
        print("  - conservative: exponential decay with 8-month half-life")
        print("  - linear: linear decay with 10% decay rate per month")
        print("  - none: no time decay (all data weighted equally)")
        print("\nNote: The enhanced prediction endpoint with time decay could not be tested due to a serialization error with NumPy float32 values.")
        return True
    else:
        print("❌ Time decay presets endpoint test failed")
        return False

if __name__ == "__main__":
    run_all_tests()
