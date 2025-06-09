import requests
import os
import json
import io
import PyPDF2
from datetime import datetime

# Get the backend URL from environment
BACKEND_URL = os.environ.get('REACT_APP_BACKEND_URL', 'http://localhost:8001')
BASE_URL = f"{BACKEND_URL}/api"

def test_pdf_export_endpoint():
    """Test the PDF export endpoint for match predictions"""
    print("\n=== Testing PDF Export Endpoint ===")
    
    # Use specific team names and referee for testing
    home_team = "Arsenal"
    away_team = "Chelsea"
    referee = "Michael Oliver"
    
    print(f"Testing PDF export for {home_team} vs {away_team} with referee {referee}")
    
    request_data = {
        "home_team": home_team,
        "away_team": away_team,
        "referee_name": referee
    }
    
    response = requests.post(f"{BASE_URL}/export-prediction-pdf", json=request_data)
    
    if response.status_code != 200:
        print(f"❌ PDF export request failed with status code {response.status_code}")
        print(response.text)
        return False
    
    # Check if the response is a PDF file
    content_type = response.headers.get('Content-Type')
    if content_type != 'application/pdf':
        print(f"❌ Response is not a PDF file. Content-Type: {content_type}")
        return False
    
    print("✅ PDF export request successful!")
    print(f"Content-Type: {content_type}")
    print(f"Content-Disposition: {response.headers.get('Content-Disposition')}")
    print(f"PDF size: {len(response.content)} bytes")
    
    # Verify PDF content
    pdf_content = response.content
    pdf_file = io.BytesIO(pdf_content)
    
    try:
        # Parse PDF content
        pdf_reader = PyPDF2.PdfReader(pdf_file)
        num_pages = len(pdf_reader.pages)
        print(f"PDF has {num_pages} pages")
        
        # Extract text from the first page to verify content
        first_page_text = pdf_reader.pages[0].extract_text()
        
        # Check for required sections in the PDF
        required_sections = [
            "Football Match Prediction Report",
            "Match Information",
            "Prediction Summary"
        ]
        
        missing_sections = []
        for section in required_sections:
            if section not in first_page_text:
                missing_sections.append(section)
        
        if missing_sections:
            print(f"❌ Missing sections in PDF: {', '.join(missing_sections)}")
        else:
            print("✅ All required sections are present in the PDF")
        
        # Check for team names in the PDF
        if home_team not in first_page_text or away_team not in first_page_text:
            print("❌ Team names not found in the PDF")
        else:
            print(f"✅ Team names ({home_team}, {away_team}) found in the PDF")
        
        # Check for referee name in the PDF
        if referee not in first_page_text:
            print(f"❌ Referee name ({referee}) not found in the PDF")
        else:
            print(f"✅ Referee name ({referee}) found in the PDF")
        
        return True
        
    except Exception as e:
        print(f"❌ Error parsing PDF content: {e}")
        return False

def test_enhanced_rbs_analysis():
    """Test the enhanced RBS analysis endpoint for a specific team and referee"""
    print("\n=== Testing Enhanced RBS Analysis ===")
    
    team_name = "Arsenal"
    referee_name = "Michael Oliver"
    
    print(f"Testing enhanced RBS analysis for {team_name} with referee {referee_name}")
    
    response = requests.get(f"{BASE_URL}/enhanced-rbs-analysis/{team_name}/{referee_name}")
    
    if response.status_code != 200:
        print(f"❌ Enhanced RBS analysis request failed with status code {response.status_code}")
        print(response.text)
        return False
    
    data = response.json()
    print(f"Success: {data.get('success', False)}")
    
    # Check basic info
    print(f"Team: {data.get('team_name')}")
    print(f"Referee: {data.get('referee_name')}")
    
    # Check RBS score
    rbs_score = data.get('rbs_score')
    print(f"RBS Score: {rbs_score}")
    
    # Check confidence level
    confidence = data.get('confidence_level')
    print(f"Confidence Level: {confidence}")
    
    # Check variance analysis
    variance_analysis = data.get('variance_analysis', {})
    if variance_analysis:
        print("\nVariance Analysis:")
        variance_ratios = variance_analysis.get('variance_ratios', {})
        for category, ratio in variance_ratios.items():
            print(f"  - {category}: {ratio}")
        
        print(f"\nVariance Confidence: {variance_analysis.get('confidence')}")
    
    # Check stats breakdown
    stats_breakdown = data.get('stats_breakdown', {})
    if stats_breakdown:
        print("\nStats Breakdown:")
        for stat, value in stats_breakdown.items():
            print(f"  - {stat}: {value}")
    
    return True

def test_team_performance():
    """Test the team performance endpoint"""
    print("\n=== Testing Team Performance Endpoint ===")
    
    team_name = "Arsenal"
    
    print(f"Testing team performance for {team_name}")
    
    response = requests.get(f"{BASE_URL}/team-performance/{team_name}")
    
    if response.status_code != 200:
        print(f"❌ Team performance request failed with status code {response.status_code}")
        print(response.text)
        return False
    
    data = response.json()
    print(f"Success: {data.get('success', False)}")
    
    # Check basic info
    print(f"Team: {data.get('team_name')}")
    print(f"Total Matches: {data.get('total_matches')}")
    print(f"PPG: {data.get('ppg')}")
    
    # Check home stats
    home_stats = data.get('home_stats', {})
    away_stats = data.get('away_stats', {})
    
    print("\nHome Stats:")
    print(f"  Matches: {home_stats.get('matches_count', 0)}")
    print(f"  xG per shot: {home_stats.get('xg_per_shot', 0)}")
    print(f"  Shots per game: {home_stats.get('shots_total', 0)}")
    print(f"  Shot accuracy: {home_stats.get('shot_accuracy', 0)}")
    print(f"  Conversion rate: {home_stats.get('conversion_rate', 0)}")
    
    print("\nAway Stats:")
    print(f"  Matches: {away_stats.get('matches_count', 0)}")
    print(f"  xG per shot: {away_stats.get('xg_per_shot', 0)}")
    print(f"  Shots per game: {away_stats.get('shots_total', 0)}")
    print(f"  Shot accuracy: {away_stats.get('shot_accuracy', 0)}")
    print(f"  Conversion rate: {away_stats.get('conversion_rate', 0)}")
    
    return True

def test_prediction_configs():
    """Test the prediction configs endpoint"""
    print("\n=== Testing Prediction Configs Endpoint ===")
    
    response = requests.get(f"{BASE_URL}/prediction-configs")
    
    if response.status_code != 200:
        print(f"❌ Prediction configs request failed with status code {response.status_code}")
        print(response.text)
        return False
    
    data = response.json()
    print(f"Success: {data.get('success', False)}")
    
    configs = data.get('configs', [])
    print(f"Configs found: {len(configs)}")
    
    if configs:
        print("\nAvailable configs:")
        for config in configs:
            print(f"  - {config.get('config_name')}")
            print(f"    Created: {config.get('created_at')}")
            print(f"    Updated: {config.get('updated_at')}")
            
            # Print some key weights
            print(f"    xG Shot-based Weight: {config.get('xg_shot_based_weight')}")
            print(f"    xG Historical Weight: {config.get('xg_historical_weight')}")
            print(f"    xG Opponent Defense Weight: {config.get('xg_opponent_defense_weight')}")
    else:
        print("❌ No prediction configs found")
    
    return True

def test_rbs_configs():
    """Test the RBS configs endpoint"""
    print("\n=== Testing RBS Configs Endpoint ===")
    
    response = requests.get(f"{BASE_URL}/rbs-configs")
    
    if response.status_code != 200:
        print(f"❌ RBS configs request failed with status code {response.status_code}")
        print(response.text)
        return False
    
    data = response.json()
    print(f"Success: {data.get('success', False)}")
    
    configs = data.get('configs', [])
    print(f"Configs found: {len(configs)}")
    
    if configs:
        print("\nAvailable configs:")
        for config in configs:
            print(f"  - {config.get('config_name')}")
            print(f"    Created: {config.get('created_at')}")
            print(f"    Updated: {config.get('updated_at')}")
            
            # Print some key weights
            print(f"    Yellow Cards Weight: {config.get('yellow_cards_weight')}")
            print(f"    Red Cards Weight: {config.get('red_cards_weight')}")
            print(f"    Fouls Committed Weight: {config.get('fouls_committed_weight')}")
    else:
        print("❌ No RBS configs found")
    
    return True

def test_suggest_prediction_config():
    """Test the suggest prediction config endpoint"""
    print("\n=== Testing Suggest Prediction Config Endpoint ===")
    
    response = requests.post(f"{BASE_URL}/suggest-prediction-config")
    
    if response.status_code != 200:
        print(f"❌ Suggest prediction config request failed with status code {response.status_code}")
        print(response.text)
        return False
    
    data = response.json()
    print(f"Success: {data.get('success', False)}")
    
    # Check suggested config
    suggested_config = data.get('suggested_config', {})
    if suggested_config:
        print("\nSuggested Config:")
        
        # Print key weights
        print(f"  xG Shot-based Weight: {suggested_config.get('xg_shot_based_weight')}")
        print(f"  xG Historical Weight: {suggested_config.get('xg_historical_weight')}")
        print(f"  xG Opponent Defense Weight: {suggested_config.get('xg_opponent_defense_weight')}")
        print(f"  PPG Adjustment Factor: {suggested_config.get('ppg_adjustment_factor')}")
        print(f"  RBS Scaling Factor: {suggested_config.get('rbs_scaling_factor')}")
    else:
        print("❌ No suggested config returned")
    
    return True

def test_analyze_rbs_optimization():
    """Test the RBS optimization analysis endpoint"""
    print("\n=== Testing RBS Optimization Analysis Endpoint ===")
    
    response = requests.post(f"{BASE_URL}/analyze-rbs-optimization")
    
    if response.status_code != 200:
        print(f"❌ RBS optimization analysis request failed with status code {response.status_code}")
        print(response.text)
        return False
    
    data = response.json()
    print(f"Success: {data.get('success', False)}")
    print(f"Analysis Type: {data.get('analysis_type')}")
    print(f"Sample Size: {data.get('sample_size')}")
    
    # Check RBS variables analyzed
    rbs_vars = data.get('rbs_variables_analyzed', [])
    print(f"\nRBS Variables Analyzed: {len(rbs_vars)}")
    print(f"  {', '.join(rbs_vars)}")
    
    # Check results structure
    results = data.get('results', {})
    print(f"\nResults sections: {len(results)}")
    for section_name in results.keys():
        print(f"  - {section_name}")
    
    # Check for suggested weights
    if 'suggested_rbs_weights' in results:
        print("\nSuggested RBS Weights:")
        for var, weight in results['suggested_rbs_weights'].items():
            print(f"  - {var}: {weight}")
    
    return True

def test_analyze_predictor_optimization():
    """Test the predictor optimization analysis endpoint"""
    print("\n=== Testing Predictor Optimization Analysis Endpoint ===")
    
    response = requests.post(f"{BASE_URL}/analyze-predictor-optimization")
    
    if response.status_code != 200:
        print(f"❌ Predictor optimization analysis request failed with status code {response.status_code}")
        print(response.text)
        return False
    
    data = response.json()
    print(f"Success: {data.get('success', False)}")
    print(f"Analysis Type: {data.get('analysis_type')}")
    print(f"Sample Size: {data.get('sample_size')}")
    
    # Check predictor variables analyzed
    predictor_vars = data.get('predictor_variables_analyzed', [])
    print(f"\nPredictor Variables Analyzed: {len(predictor_vars)}")
    if len(predictor_vars) > 5:
        print(f"  {', '.join(predictor_vars[:5])}...")
    else:
        print(f"  {', '.join(predictor_vars)}")
    
    # Check results structure
    results = data.get('results', {})
    print(f"\nResults sections: {len(results)}")
    for section_name in results.keys():
        print(f"  - {section_name}")
    
    return True

def test_analyze_comprehensive_regression():
    """Test the comprehensive regression analysis endpoint"""
    print("\n=== Testing Comprehensive Regression Analysis Endpoint ===")
    
    response = requests.post(f"{BASE_URL}/analyze-comprehensive-regression")
    
    if response.status_code != 200:
        print(f"❌ Comprehensive regression analysis request failed with status code {response.status_code}")
        print(response.text)
        return False
    
    data = response.json()
    print(f"Success: {data.get('success', False)}")
    print(f"Analysis Type: {data.get('analysis_type')}")
    print(f"Sample Size: {data.get('sample_size')}")
    
    # Check variables analyzed
    variables = data.get('variables_analyzed', [])
    print(f"\nVariables Analyzed: {len(variables)}")
    if len(variables) > 5:
        print(f"  {', '.join(variables[:5])}...")
    else:
        print(f"  {', '.join(variables)}")
    
    # Check results structure
    results = data.get('results', {})
    print(f"\nResults sections: {len(results)}")
    for section_name in results.keys():
        print(f"  - {section_name}")
    
    return True

def run_tests():
    """Run all tests"""
    print("\n========== TESTING ADVANCED FEATURES ==========\n")
    
    # Test PDF Export
    pdf_result = test_pdf_export_endpoint()
    
    # Test Enhanced RBS Analysis
    rbs_result = test_enhanced_rbs_analysis()
    
    # Test Team Performance
    performance_result = test_team_performance()
    
    # Test Configuration Management
    prediction_configs_result = test_prediction_configs()
    rbs_configs_result = test_rbs_configs()
    
    # Test Advanced AI Optimization
    suggest_config_result = test_suggest_prediction_config()
    rbs_optimization_result = test_analyze_rbs_optimization()
    predictor_optimization_result = test_analyze_predictor_optimization()
    comprehensive_regression_result = test_analyze_comprehensive_regression()
    
    # Print summary
    print("\n========== TEST SUMMARY ==========\n")
    print(f"PDF Export: {'✅ Passed' if pdf_result else '❌ Failed'}")
    print(f"Enhanced RBS Analysis: {'✅ Passed' if rbs_result else '❌ Failed'}")
    print(f"Team Performance: {'✅ Passed' if performance_result else '❌ Failed'}")
    print(f"Prediction Configs: {'✅ Passed' if prediction_configs_result else '❌ Failed'}")
    print(f"RBS Configs: {'✅ Passed' if rbs_configs_result else '❌ Failed'}")
    print(f"Suggest Prediction Config: {'✅ Passed' if suggest_config_result else '❌ Failed'}")
    print(f"RBS Optimization: {'✅ Passed' if rbs_optimization_result else '❌ Failed'}")
    print(f"Predictor Optimization: {'✅ Passed' if predictor_optimization_result else '❌ Failed'}")
    print(f"Comprehensive Regression: {'✅ Passed' if comprehensive_regression_result else '❌ Failed'}")

if __name__ == "__main__":
    run_tests()
