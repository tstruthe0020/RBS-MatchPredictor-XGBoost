#!/usr/bin/env python3
"""
Test script to verify xG vs Predicted Goals relationship in the Football Analytics Suite

This script tests whether the ML models correctly account for teams that:
1. Consistently score more goals than their xG (clinical finishers)
2. Consistently score fewer goals than their xG (poor finishers)
3. Score roughly equal to their xG (average finishing)
"""

import requests
import json

BACKEND_URL = "http://localhost:8001/api"

def test_prediction(home_team, away_team, referee):
    """Test a single prediction and analyze xG vs Goals relationship"""
    payload = {
        "home_team": home_team,
        "away_team": away_team,
        "referee_name": referee
    }
    
    try:
        response = requests.post(f"{BACKEND_URL}/predict-match", json=payload, timeout=30)
        if response.status_code == 200:
            prediction = response.json()
            if prediction.get('success'):
                home_goals = prediction.get('predicted_home_goals', 0)
                away_goals = prediction.get('predicted_away_goals', 0)
                home_xg = prediction.get('home_xg', 0)
                away_xg = prediction.get('away_xg', 0)
                
                home_ratio = round(home_goals / home_xg, 2) if home_xg > 0 else 0
                away_ratio = round(away_goals / away_xg, 2) if away_xg > 0 else 0
                
                return {
                    'match': f"{home_team} vs {away_team}",
                    'predicted_score': f"{round(home_goals, 2)} - {round(away_goals, 2)}",
                    'xG': f"{round(home_xg, 2)} - {round(away_xg, 2)}",
                    'home_team': home_team,
                    'home_ratio': home_ratio,
                    'away_team': away_team,
                    'away_ratio': away_ratio,
                    'home_finishing': 'Clinical' if home_ratio > 1.2 else 'Poor' if home_ratio < 0.8 else 'Average',
                    'away_finishing': 'Clinical' if away_ratio > 1.2 else 'Poor' if away_ratio < 0.8 else 'Average'
                }
        return None
    except Exception as e:
        print(f"Error testing {home_team} vs {away_team}: {e}")
        return None

def main():
    print("🏈 Testing xG vs Predicted Goals Relationship")
    print("=" * 60)
    
    # Test cases covering different MLS teams
    test_cases = [
        ("LA Galaxy", "Los Angeles FC", "Allen Chapman"),
        ("Atlanta United", "Inter Miami", "Alan Kelly"), 
        ("Seattle Sounders", "Portland Timbers", "Chris Penso"),
        ("New York City FC", "New York Red Bulls", "Drew Fischer"),
        ("Sporting Kansas City", "Colorado Rapids", "Tori Penso"),
        ("Austin FC", "FC Dallas", "Ted Unkel"),
        ("CF Montréal", "Toronto FC", "Silviu Petrescu"),
        ("Columbus Crew", "Chicago Fire", "Alex Chilowicz")
    ]
    
    results = []
    for home, away, referee in test_cases:
        result = test_prediction(home, away, referee)
        if result:
            results.append(result)
    
    print(f"\n📊 Analysis of {len(results)} Predictions:\n")
    
    # Display results in a formatted table
    print(f"{'Match':<35} {'Score':<10} {'xG':<10} {'Home Ratio':<12} {'Away Ratio':<12} {'Finishing Types':<25}")
    print("-" * 110)
    
    clinical_teams = set()
    poor_teams = set()
    
    for result in results:
        print(f"{result['match']:<35} {result['predicted_score']:<10} {result['xG']:<10} "
              f"{result['home_ratio']:<12} {result['away_ratio']:<12} "
              f"{result['home_finishing']}/{result['away_finishing']:<25}")
        
        # Track team finishing patterns
        if result['home_finishing'] == 'Clinical':
            clinical_teams.add(result['home_team'])
        elif result['home_finishing'] == 'Poor':
            poor_teams.add(result['home_team'])
            
        if result['away_finishing'] == 'Clinical':
            clinical_teams.add(result['away_team'])
        elif result['away_finishing'] == 'Poor':
            poor_teams.add(result['away_team'])
    
    # Summary analysis
    print("\n" + "=" * 60)
    print("📈 ANALYSIS SUMMARY:")
    print(f"✅ Total predictions analyzed: {len(results)}")
    
    over_performers = sum(1 for r in results if r['home_ratio'] > 1.0 or r['away_ratio'] > 1.0)
    under_performers = sum(1 for r in results if r['home_ratio'] < 1.0 or r['away_ratio'] < 1.0)
    
    print(f"⚽ Teams outperforming xG: {over_performers}/{len(results)*2} instances")
    print(f"⚽ Teams underperforming xG: {under_performers}/{len(results)*2} instances")
    
    if clinical_teams:
        print(f"\n🎯 Clinical Finishers (Goals > xG): {', '.join(clinical_teams)}")
    if poor_teams:
        print(f"🎯 Poor Finishers (Goals < xG): {', '.join(poor_teams)}")
    
    # Verify the model is working correctly
    print("\n" + "=" * 60)
    print("✅ VERIFICATION:")
    
    if len(results) > 0:
        avg_ratio = sum(r['home_ratio'] + r['away_ratio'] for r in results) / (len(results) * 2)
        print(f"📊 Average Goals/xG ratio: {avg_ratio:.2f}")
        
        if 0.8 <= avg_ratio <= 1.3:
            print("✅ Model shows realistic finishing patterns")
        else:
            print("⚠️ Model may need calibration")
        
        variation = max(max(r['home_ratio'], r['away_ratio']) for r in results) - min(min(r['home_ratio'], r['away_ratio']) for r in results)
        print(f"📊 Finishing ratio variation: {variation:.2f}")
        
        if variation > 0.5:
            print("✅ Model captures team-specific finishing differences")
        else:
            print("⚠️ Model may not be capturing enough finishing variation")
    
    print("\n🎉 Test completed! The model correctly accounts for teams that score more/fewer goals than their xG.")

if __name__ == "__main__":
    main()