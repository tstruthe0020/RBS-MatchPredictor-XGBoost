#!/usr/bin/env python3
"""
Test script to verify referee analysis and RBS stat differentials

This script tests:
1. Basic referee analysis endpoint
2. Detailed referee analysis with stat breakdowns
3. RBS calculation differentials
4. Data quality and completeness
"""

import requests
import json

BACKEND_URL = "http://localhost:8001/api"

def test_referee_analysis():
    """Test the main referee analysis endpoint"""
    print("🏈 Testing Referee Analysis Functionality")
    print("=" * 60)
    
    try:
        # Test main referee analysis
        response = requests.get(f"{BACKEND_URL}/referee-analysis", timeout=30)
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Main referee analysis working")
            print(f"   📊 Total referees: {data.get('total_referees', 0)}")
            print(f"   📊 Total matches: {data.get('total_matches', 0)}")
            print(f"   📊 Teams covered: {data.get('teams_covered', 0)}")
            print(f"   📊 Average bias score: {data.get('avg_bias_score', 0):.3f}")
            
            referees = data.get('referees', [])
            print(f"   📊 Referee profiles returned: {len(referees)}")
            
            if referees:
                # Test detailed analysis for top referee
                top_referee = referees[0]
                print(f"\n🔍 Testing detailed analysis for: {top_referee['name']}")
                return test_detailed_referee_analysis(top_referee['name'])
            else:
                print("❌ No referees found in analysis")
                return False
        else:
            print(f"❌ Referee analysis failed: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Error in referee analysis test: {e}")
        return False

def test_detailed_referee_analysis(referee_name):
    """Test detailed referee analysis with stat differentials"""
    try:
        response = requests.get(f"{BACKEND_URL}/referee-analysis/{requests.utils.quote(referee_name)}", timeout=30)
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Detailed analysis working for {referee_name}")
            
            # Check basic info
            print(f"   📊 Total matches: {data.get('total_matches', 0)}")
            print(f"   📊 Teams officiated: {data.get('teams_officiated', 0)}")
            print(f"   📊 Average bias score: {data.get('avg_bias_score', 0):.3f}")
            print(f"   📊 RBS calculations: {data.get('rbs_calculations', 0)}")
            
            # Check match outcomes
            match_outcomes = data.get('match_outcomes', {})
            if match_outcomes:
                print(f"   🏆 Match outcomes: {match_outcomes.get('home_wins', 0)}H-{match_outcomes.get('draws', 0)}D-{match_outcomes.get('away_wins', 0)}A")
                print(f"   🏆 Home win rate: {match_outcomes.get('home_win_percentage', 0)}%")
            
            # Check bias extremes
            bias_analysis = data.get('bias_analysis', {})
            if bias_analysis and bias_analysis.get('most_biased_team'):
                most_biased = bias_analysis['most_biased_team']
                print(f"   🎯 Most biased team: {most_biased.get('team')} (RBS: {most_biased.get('rbs_score', 0):.3f}, {most_biased.get('bias_direction')})")
                
                least_biased = bias_analysis.get('least_biased_team')
                if least_biased:
                    print(f"   🎯 Least biased team: {least_biased.get('team')} (RBS: {least_biased.get('rbs_score', 0):.3f})")
            
            # Check team RBS details and stat differentials
            team_rbs = data.get('team_rbs_details', {})
            if team_rbs:
                print(f"   📋 Team RBS calculations: {len(team_rbs)}")
                
                # Analyze stat differentials for top teams
                sorted_teams = sorted(team_rbs.items(), key=lambda x: abs(x[1].get('rbs_score', 0)), reverse=True)
                
                print(f"\n📊 Top 3 Teams by Bias Magnitude:")
                for i, (team_name, team_data) in enumerate(sorted_teams[:3]):
                    rbs_score = team_data.get('rbs_score', 0)
                    matches_with_ref = team_data.get('matches_with_ref', 0)
                    stats_breakdown = team_data.get('stats_breakdown', {})
                    
                    print(f"\n   {i+1}. {team_name}")
                    print(f"      RBS Score: {rbs_score:.3f}")
                    print(f"      Matches with referee: {matches_with_ref}")
                    print(f"      Confidence: {team_data.get('confidence_level', 0)}%")
                    
                    if stats_breakdown:
                        print(f"      📈 Stat Differentials:")
                        for stat_name, value in stats_breakdown.items():
                            direction = "↑" if value > 0 else "↓" if value < 0 else "→"
                            significance = "🔥" if abs(value) > 0.3 else "⚡" if abs(value) > 0.1 else ""
                            print(f"         {stat_name.replace('_', ' ').title()}: {direction} {value:+.3f} {significance}")
                
                # Check data quality
                print(f"\n🔍 Data Quality Analysis:")
                teams_with_stats = sum(1 for team_data in team_rbs.values() if team_data.get('stats_breakdown'))
                print(f"   Teams with stat breakdowns: {teams_with_stats}/{len(team_rbs)}")
                
                # Check stat differential variety
                all_stats = set()
                for team_data in team_rbs.values():
                    if team_data.get('stats_breakdown'):
                        all_stats.update(team_data['stats_breakdown'].keys())
                
                print(f"   Stat types tracked: {len(all_stats)}")
                print(f"   Stats available: {', '.join(sorted(all_stats))}")
                
                return True
            else:
                print("❌ No team RBS details found")
                return False
        else:
            print(f"❌ Detailed analysis failed: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Error in detailed analysis test: {e}")
        return False

def test_rbs_data_quality():
    """Test RBS data quality and coverage"""
    print(f"\n🔍 Testing RBS Data Quality")
    print("-" * 40)
    
    try:
        response = requests.get(f"{BACKEND_URL}/rbs-results", timeout=30)
        
        if response.status_code == 200:
            data = response.json()
            results = data.get('results', [])
            
            print(f"✅ RBS Results accessible")
            print(f"   📊 Total RBS calculations: {len(results)}")
            
            if results:
                # Analyze first few results
                sample_result = results[0]
                print(f"   📋 Sample RBS calculation:")
                print(f"      Team: {sample_result.get('team_name')}")
                print(f"      Referee: {sample_result.get('referee')}")
                print(f"      RBS Score: {sample_result.get('rbs_score', 0):.3f}")
                print(f"      Matches with referee: {sample_result.get('matches_with_ref', 0)}")
                
                stats_breakdown = sample_result.get('stats_breakdown', {})
                if stats_breakdown:
                    print(f"      Stat differentials: {len(stats_breakdown)} categories")
                    for stat, value in stats_breakdown.items():
                        print(f"         {stat}: {value:+.3f}")
                
                return True
            else:
                print("❌ No RBS results found")
                return False
        else:
            print(f"❌ RBS results failed: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Error in RBS data test: {e}")
        return False

def main():
    """Run all referee analysis tests"""
    print("🏈 Football Analytics Suite - Referee Analysis Test")
    print("=" * 60)
    
    success_count = 0
    total_tests = 3
    
    # Test 1: Basic referee analysis
    if test_referee_analysis():
        success_count += 1
    
    # Test 2: RBS data quality  
    if test_rbs_data_quality():
        success_count += 1
    
    # Results
    print("\n" + "=" * 60)
    print("📋 TEST SUMMARY:")
    print(f"   Passed: {success_count}/{total_tests}")
    print(f"   Success rate: {(success_count/total_tests)*100:.1f}%")
    
    if success_count == total_tests:
        print("🎉 ALL TESTS PASSED! Referee analysis with RBS stat differentials is working correctly.")
        return True
    else:
        print("⚠️ Some tests failed. Please check the implementation.")
        return False

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)