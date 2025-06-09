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

def test_enhanced_prediction_without_starting_xi():
    """Test enhanced prediction without Starting XI data"""
    print("\n=== Test 1: Enhanced Prediction WITHOUT Starting XI ===")
    
    # Prepare request data
    request_data = {
        "home_team": "Arsenal",
        "away_team": "Chelsea",
        "referee_name": "Michael Oliver",
        "use_time_decay": True,
        "decay_preset": "moderate"
    }
    
    response = requests.post(f"{BASE_URL}/predict-match-enhanced", json=request_data)
    
    if response.status_code == 200:
        print(f"Status: {response.status_code} OK")
        data = response.json()
        print(f"Success: {data.get('success', False)}")
        
        if data.get('success'):
            print(f"Home Team: {data.get('home_team')}")
            print(f"Away Team: {data.get('away_team')}")
            print(f"Referee: {data.get('referee')}")
            print(f"Predicted Home Goals: {data.get('predicted_home_goals')}")
            print(f"Predicted Away Goals: {data.get('predicted_away_goals')}")
            print(f"Home xG: {data.get('home_xg')}")
            print(f"Away xG: {data.get('away_xg')}")
            
            # Check for probability fields
            print(f"Home Win Probability: {data.get('home_win_probability')}%")
            print(f"Draw Probability: {data.get('draw_probability')}%")
            print(f"Away Win Probability: {data.get('away_win_probability')}%")
            
            # Check prediction breakdown
            breakdown = data.get('prediction_breakdown', {})
            print("\nPrediction Breakdown:")
            
            # Check for Starting XI info in breakdown
            starting_xi_used = breakdown.get('starting_xi_used', {})
            print(f"Starting XI Used: Home={starting_xi_used.get('home_team', False)}, Away={starting_xi_used.get('away_team', False)}")
            
            # Check for time decay info
            time_decay_applied = breakdown.get('time_decay_applied', False)
            decay_preset = breakdown.get('decay_preset')
            print(f"Time Decay Applied: {time_decay_applied}")
            print(f"Decay Preset: {decay_preset}")
            
            return data
        else:
            print(f"Prediction failed: {data.get('error', 'Unknown error')}")
            return data
    else:
        print(f"Error: {response.status_code}")
        print(response.text)
        return None

def test_enhanced_prediction_with_starting_xi():
    """Test enhanced prediction with Starting XI data"""
    print("\n=== Test 2: Enhanced Prediction WITH Starting XI ===")
    
    # First, get players for home team (Arsenal)
    home_players_response = requests.get(f"{BASE_URL}/teams/Arsenal/players")
    if home_players_response.status_code != 200 or not home_players_response.json().get('success'):
        print(f"❌ Failed to get players for Arsenal")
        # Create a mock starting XI
        home_xi = {
            "formation": "4-4-2",
            "positions": [
                {"position_id": "GK1", "position_type": "GK", "player": {"player_name": "Ramsdale", "position": "GK"}},
                {"position_id": "DEF1", "position_type": "DEF", "player": {"player_name": "White", "position": "DEF"}},
                {"position_id": "DEF2", "position_type": "DEF", "player": {"player_name": "Gabriel", "position": "DEF"}},
                {"position_id": "DEF3", "position_type": "DEF", "player": {"player_name": "Saliba", "position": "DEF"}},
                {"position_id": "DEF4", "position_type": "DEF", "player": {"player_name": "Timber", "position": "DEF"}},
                {"position_id": "MID1", "position_type": "MID", "player": {"player_name": "Odegaard", "position": "MID"}},
                {"position_id": "MID2", "position_type": "MID", "player": {"player_name": "Partey", "position": "MID"}},
                {"position_id": "MID3", "position_type": "MID", "player": {"player_name": "Rice", "position": "MID"}},
                {"position_id": "MID4", "position_type": "MID", "player": {"player_name": "Saka", "position": "MID"}},
                {"position_id": "FWD1", "position_type": "FWD", "player": {"player_name": "Martinelli", "position": "FWD"}},
                {"position_id": "FWD2", "position_type": "FWD", "player": {"player_name": "Jesus", "position": "FWD"}}
            ]
        }
    else:
        home_players_data = home_players_response.json()
        home_default_xi = home_players_data.get('default_starting_xi')
        if home_default_xi:
            home_xi = home_default_xi
        else:
            # Create a mock starting XI
            home_xi = {
                "formation": "4-4-2",
                "positions": [
                    {"position_id": "GK1", "position_type": "GK", "player": {"player_name": "Ramsdale", "position": "GK"}},
                    {"position_id": "DEF1", "position_type": "DEF", "player": {"player_name": "White", "position": "DEF"}},
                    {"position_id": "DEF2", "position_type": "DEF", "player": {"player_name": "Gabriel", "position": "DEF"}},
                    {"position_id": "DEF3", "position_type": "DEF", "player": {"player_name": "Saliba", "position": "DEF"}},
                    {"position_id": "DEF4", "position_type": "DEF", "player": {"player_name": "Timber", "position": "DEF"}},
                    {"position_id": "MID1", "position_type": "MID", "player": {"player_name": "Odegaard", "position": "MID"}},
                    {"position_id": "MID2", "position_type": "MID", "player": {"player_name": "Partey", "position": "MID"}},
                    {"position_id": "MID3", "position_type": "MID", "player": {"player_name": "Rice", "position": "MID"}},
                    {"position_id": "MID4", "position_type": "MID", "player": {"player_name": "Saka", "position": "MID"}},
                    {"position_id": "FWD1", "position_type": "FWD", "player": {"player_name": "Martinelli", "position": "FWD"}},
                    {"position_id": "FWD2", "position_type": "FWD", "player": {"player_name": "Jesus", "position": "FWD"}}
                ]
            }
    
    # Get players for away team (Chelsea)
    away_players_response = requests.get(f"{BASE_URL}/teams/Chelsea/players")
    if away_players_response.status_code != 200 or not away_players_response.json().get('success'):
        print(f"❌ Failed to get players for Chelsea")
        # Create a mock starting XI
        away_xi = {
            "formation": "4-3-3",
            "positions": [
                {"position_id": "GK1", "position_type": "GK", "player": {"player_name": "Kepa", "position": "GK"}},
                {"position_id": "DEF1", "position_type": "DEF", "player": {"player_name": "James", "position": "DEF"}},
                {"position_id": "DEF2", "position_type": "DEF", "player": {"player_name": "Silva", "position": "DEF"}},
                {"position_id": "DEF3", "position_type": "DEF", "player": {"player_name": "Fofana", "position": "DEF"}},
                {"position_id": "DEF4", "position_type": "DEF", "player": {"player_name": "Chilwell", "position": "DEF"}},
                {"position_id": "MID1", "position_type": "MID", "player": {"player_name": "Fernandez", "position": "MID"}},
                {"position_id": "MID2", "position_type": "MID", "player": {"player_name": "Gallagher", "position": "MID"}},
                {"position_id": "MID3", "position_type": "MID", "player": {"player_name": "Caicedo", "position": "MID"}},
                {"position_id": "FWD1", "position_type": "FWD", "player": {"player_name": "Sterling", "position": "FWD"}},
                {"position_id": "FWD2", "position_type": "FWD", "player": {"player_name": "Jackson", "position": "FWD"}},
                {"position_id": "FWD3", "position_type": "FWD", "player": {"player_name": "Mudryk", "position": "FWD"}}
            ]
        }
    else:
        away_players_data = away_players_response.json()
        away_default_xi = away_players_data.get('default_starting_xi')
        if away_default_xi:
            away_xi = away_default_xi
        else:
            # Create a mock starting XI
            away_xi = {
                "formation": "4-3-3",
                "positions": [
                    {"position_id": "GK1", "position_type": "GK", "player": {"player_name": "Kepa", "position": "GK"}},
                    {"position_id": "DEF1", "position_type": "DEF", "player": {"player_name": "James", "position": "DEF"}},
                    {"position_id": "DEF2", "position_type": "DEF", "player": {"player_name": "Silva", "position": "DEF"}},
                    {"position_id": "DEF3", "position_type": "DEF", "player": {"player_name": "Fofana", "position": "DEF"}},
                    {"position_id": "DEF4", "position_type": "DEF", "player": {"player_name": "Chilwell", "position": "DEF"}},
                    {"position_id": "MID1", "position_type": "MID", "player": {"player_name": "Fernandez", "position": "MID"}},
                    {"position_id": "MID2", "position_type": "MID", "player": {"player_name": "Gallagher", "position": "MID"}},
                    {"position_id": "MID3", "position_type": "MID", "player": {"player_name": "Caicedo", "position": "MID"}},
                    {"position_id": "FWD1", "position_type": "FWD", "player": {"player_name": "Sterling", "position": "FWD"}},
                    {"position_id": "FWD2", "position_type": "FWD", "player": {"player_name": "Jackson", "position": "FWD"}},
                    {"position_id": "FWD3", "position_type": "FWD", "player": {"player_name": "Mudryk", "position": "FWD"}}
                ]
            }
    
    # Prepare request data with Starting XI
    request_data = {
        "home_team": "Arsenal",
        "away_team": "Chelsea",
        "referee_name": "Michael Oliver",
        "use_time_decay": True,
        "decay_preset": "moderate",
        "home_starting_xi": home_xi,
        "away_starting_xi": away_xi
    }
    
    response = requests.post(f"{BASE_URL}/predict-match-enhanced", json=request_data)
    
    if response.status_code == 200:
        print(f"Status: {response.status_code} OK")
        data = response.json()
        print(f"Success: {data.get('success', False)}")
        
        if data.get('success'):
            print(f"Home Team: {data.get('home_team')}")
            print(f"Away Team: {data.get('away_team')}")
            print(f"Referee: {data.get('referee')}")
            print(f"Predicted Home Goals: {data.get('predicted_home_goals')}")
            print(f"Predicted Away Goals: {data.get('predicted_away_goals')}")
            print(f"Home xG: {data.get('home_xg')}")
            print(f"Away xG: {data.get('away_xg')}")
            
            # Check for probability fields
            print(f"Home Win Probability: {data.get('home_win_probability')}%")
            print(f"Draw Probability: {data.get('draw_probability')}%")
            print(f"Away Win Probability: {data.get('away_win_probability')}%")
            
            # Check prediction breakdown
            breakdown = data.get('prediction_breakdown', {})
            print("\nPrediction Breakdown:")
            
            # Check for Starting XI info in breakdown
            starting_xi_used = breakdown.get('starting_xi_used', {})
            print(f"Starting XI Used: Home={starting_xi_used.get('home_team', False)}, Away={starting_xi_used.get('away_team', False)}")
            
            # Check for time decay info
            time_decay_applied = breakdown.get('time_decay_applied', False)
            decay_preset = breakdown.get('decay_preset')
            print(f"Time Decay Applied: {time_decay_applied}")
            print(f"Decay Preset: {decay_preset}")
            
            return data
        else:
            print(f"Prediction failed: {data.get('error', 'Unknown error')}")
            return data
    else:
        print(f"Error: {response.status_code}")
        print(response.text)
        return None

def test_enhanced_prediction_with_different_starting_xi():
    """Test enhanced prediction with a different Starting XI"""
    print("\n=== Test 3: Enhanced Prediction with DIFFERENT Starting XI ===")
    
    # Create a different starting XI for Arsenal
    home_xi = {
        "formation": "4-4-2",
        "positions": [
            {"position_id": "GK1", "position_type": "GK", "player": {"player_name": "Leno", "position": "GK"}},
            {"position_id": "DEF1", "position_type": "DEF", "player": {"player_name": "Tomiyasu", "position": "DEF"}},
            {"position_id": "DEF2", "position_type": "DEF", "player": {"player_name": "Holding", "position": "DEF"}},
            {"position_id": "DEF3", "position_type": "DEF", "player": {"player_name": "Kiwior", "position": "DEF"}},
            {"position_id": "DEF4", "position_type": "DEF", "player": {"player_name": "Zinchenko", "position": "DEF"}},
            {"position_id": "MID1", "position_type": "MID", "player": {"player_name": "Jorginho", "position": "MID"}},
            {"position_id": "MID2", "position_type": "MID", "player": {"player_name": "Xhaka", "position": "MID"}},
            {"position_id": "MID3", "position_type": "MID", "player": {"player_name": "Vieira", "position": "MID"}},
            {"position_id": "MID4", "position_type": "MID", "player": {"player_name": "Smith Rowe", "position": "MID"}},
            {"position_id": "FWD1", "position_type": "FWD", "player": {"player_name": "Nketiah", "position": "FWD"}},
            {"position_id": "FWD2", "position_type": "FWD", "player": {"player_name": "Trossard", "position": "FWD"}}
        ]
    }
    
    # Create a different starting XI for Chelsea
    away_xi = {
        "formation": "4-3-3",
        "positions": [
            {"position_id": "GK1", "position_type": "GK", "player": {"player_name": "Mendy", "position": "GK"}},
            {"position_id": "DEF1", "position_type": "DEF", "player": {"player_name": "Chalobah", "position": "DEF"}},
            {"position_id": "DEF2", "position_type": "DEF", "player": {"player_name": "Badiashile", "position": "DEF"}},
            {"position_id": "DEF3", "position_type": "DEF", "player": {"player_name": "Colwill", "position": "DEF"}},
            {"position_id": "DEF4", "position_type": "DEF", "player": {"player_name": "Cucurella", "position": "DEF"}},
            {"position_id": "MID1", "position_type": "MID", "player": {"player_name": "Loftus-Cheek", "position": "MID"}},
            {"position_id": "MID2", "position_type": "MID", "player": {"player_name": "Kante", "position": "MID"}},
            {"position_id": "MID3", "position_type": "MID", "player": {"player_name": "Mount", "position": "MID"}},
            {"position_id": "FWD1", "position_type": "FWD", "player": {"player_name": "Pulisic", "position": "FWD"}},
            {"position_id": "FWD2", "position_type": "FWD", "player": {"player_name": "Havertz", "position": "FWD"}},
            {"position_id": "FWD3", "position_type": "FWD", "player": {"player_name": "Felix", "position": "FWD"}}
        ]
    }
    
    # Prepare request data with different Starting XI
    request_data = {
        "home_team": "Arsenal",
        "away_team": "Chelsea",
        "referee_name": "Michael Oliver",
        "use_time_decay": True,
        "decay_preset": "moderate",
        "home_starting_xi": home_xi,
        "away_starting_xi": away_xi
    }
    
    response = requests.post(f"{BASE_URL}/predict-match-enhanced", json=request_data)
    
    if response.status_code == 200:
        print(f"Status: {response.status_code} OK")
        data = response.json()
        print(f"Success: {data.get('success', False)}")
        
        if data.get('success'):
            print(f"Home Team: {data.get('home_team')}")
            print(f"Away Team: {data.get('away_team')}")
            print(f"Referee: {data.get('referee')}")
            print(f"Predicted Home Goals: {data.get('predicted_home_goals')}")
            print(f"Predicted Away Goals: {data.get('predicted_away_goals')}")
            print(f"Home xG: {data.get('home_xg')}")
            print(f"Away xG: {data.get('away_xg')}")
            
            # Check for probability fields
            print(f"Home Win Probability: {data.get('home_win_probability')}%")
            print(f"Draw Probability: {data.get('draw_probability')}%")
            print(f"Away Win Probability: {data.get('away_win_probability')}%")
            
            # Check prediction breakdown
            breakdown = data.get('prediction_breakdown', {})
            print("\nPrediction Breakdown:")
            
            # Check for Starting XI info in breakdown
            starting_xi_used = breakdown.get('starting_xi_used', {})
            print(f"Starting XI Used: Home={starting_xi_used.get('home_team', False)}, Away={starting_xi_used.get('away_team', False)}")
            
            # Check for time decay info
            time_decay_applied = breakdown.get('time_decay_applied', False)
            decay_preset = breakdown.get('decay_preset')
            print(f"Time Decay Applied: {time_decay_applied}")
            print(f"Decay Preset: {decay_preset}")
            
            return data
        else:
            print(f"Prediction failed: {data.get('error', 'Unknown error')}")
            return data
    else:
        print(f"Error: {response.status_code}")
        print(response.text)
        return None

def compare_results(result1, result2, result3):
    """Compare the results of the three predictions"""
    print("\n=== Comparing Results ===")
    
    if not all([result1, result2, result3]):
        print("❌ Cannot compare results - one or more predictions failed")
        return False
    
    # Extract key metrics for comparison
    metrics = {
        "Test 1 (No XI)": {
            "home_goals": result1.get('predicted_home_goals'),
            "away_goals": result1.get('predicted_away_goals'),
            "home_xg": result1.get('home_xg'),
            "away_xg": result1.get('away_xg'),
            "home_win": result1.get('home_win_probability'),
            "draw": result1.get('draw_probability'),
            "away_win": result1.get('away_win_probability')
        },
        "Test 2 (With XI)": {
            "home_goals": result2.get('predicted_home_goals'),
            "away_goals": result2.get('predicted_away_goals'),
            "home_xg": result2.get('home_xg'),
            "away_xg": result2.get('away_xg'),
            "home_win": result2.get('home_win_probability'),
            "draw": result2.get('draw_probability'),
            "away_win": result2.get('away_win_probability')
        },
        "Test 3 (Different XI)": {
            "home_goals": result3.get('predicted_home_goals'),
            "away_goals": result3.get('predicted_away_goals'),
            "home_xg": result3.get('home_xg'),
            "away_xg": result3.get('away_xg'),
            "home_win": result3.get('home_win_probability'),
            "draw": result3.get('draw_probability'),
            "away_win": result3.get('away_win_probability')
        }
    }
    
    # Print comparison table
    print("\nMetric Comparison:")
    print(f"{'Metric':<15} {'Test 1 (No XI)':<20} {'Test 2 (With XI)':<20} {'Test 3 (Different XI)':<20}")
    print("-" * 75)
    
    for metric in ["home_goals", "away_goals", "home_xg", "away_xg", "home_win", "draw", "away_win"]:
        values = [metrics[test][metric] for test in metrics.keys()]
        print(f"{metric:<15} {values[0]:<20} {values[1]:<20} {values[2]:<20}")
    
    # Check if results are meaningfully different
    differences = []
    
    # Compare Test 1 vs Test 2
    if abs(metrics["Test 1 (No XI)"]["home_goals"] - metrics["Test 2 (With XI)"]["home_goals"]) > 0.1:
        differences.append("Home goals differ between Test 1 and Test 2")
    
    if abs(metrics["Test 1 (No XI)"]["away_goals"] - metrics["Test 2 (With XI)"]["away_goals"]) > 0.1:
        differences.append("Away goals differ between Test 1 and Test 2")
    
    if abs(metrics["Test 1 (No XI)"]["home_xg"] - metrics["Test 2 (With XI)"]["home_xg"]) > 0.1:
        differences.append("Home xG differs between Test 1 and Test 2")
    
    if abs(metrics["Test 1 (No XI)"]["away_xg"] - metrics["Test 2 (With XI)"]["away_xg"]) > 0.1:
        differences.append("Away xG differs between Test 1 and Test 2")
    
    # Compare Test 2 vs Test 3
    if abs(metrics["Test 2 (With XI)"]["home_goals"] - metrics["Test 3 (Different XI)"]["home_goals"]) > 0.1:
        differences.append("Home goals differ between Test 2 and Test 3")
    
    if abs(metrics["Test 2 (With XI)"]["away_goals"] - metrics["Test 3 (Different XI)"]["away_goals"]) > 0.1:
        differences.append("Away goals differ between Test 2 and Test 3")
    
    if abs(metrics["Test 2 (With XI)"]["home_xg"] - metrics["Test 3 (Different XI)"]["home_xg"]) > 0.1:
        differences.append("Home xG differs between Test 2 and Test 3")
    
    if abs(metrics["Test 2 (With XI)"]["away_xg"] - metrics["Test 3 (Different XI)"]["away_xg"]) > 0.1:
        differences.append("Away xG differs between Test 2 and Test 3")
    
    # Print differences
    if differences:
        print("\nMeaningful differences detected:")
        for diff in differences:
            print(f"✅ {diff}")
        print("\n✅ The Starting XI integration is working properly - predictions change based on the lineup")
        return True
    else:
        print("\n❌ No meaningful differences detected between predictions")
        print("The Starting XI integration may not be properly affecting the predictions")
        return False

def main():
    """Run all tests"""
    print("\n========== TESTING STARTING XI XGBOOST INTEGRATION ==========")
    
    # Run Test 1: Enhanced prediction without Starting XI
    result1 = test_enhanced_prediction_without_starting_xi()
    
    # Run Test 2: Enhanced prediction with Starting XI
    result2 = test_enhanced_prediction_with_starting_xi()
    
    # Run Test 3: Enhanced prediction with different Starting XI
    result3 = test_enhanced_prediction_with_different_starting_xi()
    
    # Compare results
    compare_results(result1, result2, result3)
    
    print("\n========== TESTING COMPLETE ==========")

if __name__ == "__main__":
    main()
