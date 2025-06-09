#!/usr/bin/env python3
"""
PDF Export Test Script for Football Analytics Suite

This script tests the PDF export functionality by:
1. Making a match prediction
2. Exporting the prediction as a PDF
3. Saving the PDF to the project directory
4. Verifying the PDF was created successfully
"""

import requests
import json
import os
import sys
from datetime import datetime

# Configuration
BACKEND_URL = "http://localhost:8001/api"
OUTPUT_DIR = "/app/test_pdfs"
TEST_CASES = [
    {
        "name": "MLS_Classic_Rivalry",
        "home_team": "LA Galaxy",
        "away_team": "Los Angeles FC", 
        "referee": "Allen Chapman",
        "match_date": "2024-07-20"
    },
    {
        "name": "Eastern_Conference_Match",
        "home_team": "Atlanta United",
        "away_team": "Inter Miami",
        "referee": "Drew Fischer",
        "match_date": "2024-08-15"
    },
    {
        "name": "Western_Conference_Match",
        "home_team": "Seattle Sounders",
        "away_team": "Portland Timbers",
        "referee": "Chris Penso",
        "match_date": "2024-09-10"
    }
]

def print_status(message, status="INFO"):
    """Print formatted status message"""
    timestamp = datetime.now().strftime("%H:%M:%S")
    print(f"[{timestamp}] {status}: {message}")

def test_backend_connectivity():
    """Test if backend is accessible"""
    print_status("Testing backend connectivity...")
    try:
        response = requests.get(f"{BACKEND_URL}/stats", timeout=10)
        if response.status_code == 200:
            stats = response.json()
            print_status(f"✅ Backend connected. Database has {stats['matches']} matches")
            return True
        else:
            print_status(f"❌ Backend returned status {response.status_code}", "ERROR")
            return False
    except Exception as e:
        print_status(f"❌ Backend connection failed: {e}", "ERROR")
        return False

def test_ml_models():
    """Test if ML models are ready"""
    print_status("Checking ML model status...")
    try:
        response = requests.get(f"{BACKEND_URL}/ml-models/status", timeout=10)
        if response.status_code == 200:
            status = response.json()
            if status.get('models_loaded'):
                print_status(f"✅ ML models ready with {status['feature_columns_count']} features")
                return True
            else:
                print_status("❌ ML models not loaded", "ERROR")
                return False
        else:
            print_status(f"❌ ML status check failed with status {response.status_code}", "ERROR")
            return False
    except Exception as e:
        print_status(f"❌ ML status check failed: {e}", "ERROR")
        return False

def make_prediction(test_case):
    """Make a match prediction"""
    print_status(f"Making prediction for {test_case['name']}...")
    
    payload = {
        "home_team": test_case["home_team"],
        "away_team": test_case["away_team"],
        "referee_name": test_case["referee"],
        "match_date": test_case.get("match_date")
    }
    
    try:
        response = requests.post(
            f"{BACKEND_URL}/predict",
            json=payload,
            timeout=30
        )
        
        if response.status_code == 200:
            prediction = response.json()
            if prediction.get('success'):
                print_status(f"✅ Prediction successful: {prediction.get('predicted_home_goals', 0):.1f} - {prediction.get('predicted_away_goals', 0):.1f}")
                return prediction
            else:
                print_status(f"❌ Prediction failed: {prediction.get('error', 'Unknown error')}", "ERROR")
                return None
        else:
            print_status(f"❌ Prediction API returned status {response.status_code}", "ERROR")
            return None
            
    except Exception as e:
        print_status(f"❌ Prediction request failed: {e}", "ERROR")
        return None

def export_pdf(test_case):
    """Export prediction as PDF"""
    print_status(f"Exporting PDF for {test_case['name']}...")
    
    payload = {
        "home_team": test_case["home_team"],
        "away_team": test_case["away_team"],
        "referee_name": test_case["referee"],
        "match_date": test_case.get("match_date")
    }
    
    try:
        response = requests.post(
            f"{BACKEND_URL}/export-prediction-pdf",
            json=payload,
            timeout=60
        )
        
        if response.status_code == 200:
            # Ensure output directory exists
            os.makedirs(OUTPUT_DIR, exist_ok=True)
            
            # Create filename
            filename = f"{test_case['name']}_{test_case['home_team'].replace(' ', '_')}_vs_{test_case['away_team'].replace(' ', '_')}.pdf"
            filepath = os.path.join(OUTPUT_DIR, filename)
            
            # Save PDF
            with open(filepath, 'wb') as f:
                f.write(response.content)
            
            # Verify file was created and has content
            if os.path.exists(filepath) and os.path.getsize(filepath) > 0:
                file_size = os.path.getsize(filepath)
                print_status(f"✅ PDF exported successfully: {filename} ({file_size:,} bytes)")
                return filepath
            else:
                print_status(f"❌ PDF file was not created properly", "ERROR")
                return None
                
        else:
            print_status(f"❌ PDF export failed with status {response.status_code}", "ERROR")
            if response.headers.get('content-type', '').startswith('application/json'):
                error_data = response.json()
                print_status(f"Error details: {error_data.get('detail', 'Unknown error')}", "ERROR")
            return None
            
    except Exception as e:
        print_status(f"❌ PDF export request failed: {e}", "ERROR")
        return None

def validate_pdf(filepath):
    """Basic PDF validation"""
    print_status(f"Validating PDF: {os.path.basename(filepath)}")
    
    try:
        # Check if file exists and has reasonable size
        if not os.path.exists(filepath):
            print_status("❌ PDF file does not exist", "ERROR")
            return False
            
        file_size = os.path.getsize(filepath)
        if file_size < 1000:  # Less than 1KB is probably an error
            print_status(f"❌ PDF file too small ({file_size} bytes)", "ERROR")
            return False
            
        # Check PDF header
        with open(filepath, 'rb') as f:
            header = f.read(5)
            if header != b'%PDF-':
                print_status("❌ File does not have valid PDF header", "ERROR")
                return False
                
        print_status(f"✅ PDF validation passed ({file_size:,} bytes)")
        return True
        
    except Exception as e:
        print_status(f"❌ PDF validation failed: {e}", "ERROR")
        return False

def run_comprehensive_test():
    """Run comprehensive PDF export test"""
    print_status("🚀 Starting Football Analytics Suite PDF Export Test", "START")
    print_status("=" * 60)
    
    # Test 1: Backend connectivity
    if not test_backend_connectivity():
        print_status("❌ Cannot proceed without backend connectivity", "FATAL")
        return False
    
    # Test 2: ML models ready
    if not test_ml_models():
        print_status("❌ Cannot proceed without ML models", "FATAL")
        return False
    
    print_status("=" * 60)
    
    # Test 3: Run PDF export tests for each case
    successful_tests = 0
    total_tests = len(TEST_CASES)
    exported_pdfs = []
    
    for i, test_case in enumerate(TEST_CASES, 1):
        print_status(f"📝 Running Test {i}/{total_tests}: {test_case['name']}")
        print_status(f"   Match: {test_case['home_team']} vs {test_case['away_team']}")
        print_status(f"   Referee: {test_case['referee']}")
        
        # Make prediction first (optional verification)
        prediction = make_prediction(test_case)
        if not prediction:
            print_status(f"⚠️ Prediction failed for {test_case['name']}, but continuing with PDF test", "WARN")
        
        # Export PDF
        pdf_path = export_pdf(test_case)
        if pdf_path:
            # Validate PDF
            if validate_pdf(pdf_path):
                successful_tests += 1
                exported_pdfs.append(pdf_path)
            else:
                print_status(f"❌ PDF validation failed for {test_case['name']}", "ERROR")
        
        print_status("-" * 40)
    
    # Summary
    print_status("=" * 60)
    print_status(f"📊 TEST SUMMARY")
    print_status(f"   Total Tests: {total_tests}")
    print_status(f"   Successful: {successful_tests}")
    print_status(f"   Failed: {total_tests - successful_tests}")
    print_status(f"   Success Rate: {(successful_tests/total_tests)*100:.1f}%")
    
    if exported_pdfs:
        print_status(f"📁 Exported PDFs saved to: {OUTPUT_DIR}")
        for pdf_path in exported_pdfs:
            print_status(f"   - {os.path.basename(pdf_path)}")
    
    # Overall result
    if successful_tests == total_tests:
        print_status("🎉 ALL TESTS PASSED! PDF export functionality is working correctly.", "SUCCESS")
        return True
    elif successful_tests > 0:
        print_status(f"⚠️ PARTIAL SUCCESS: {successful_tests}/{total_tests} tests passed", "WARN")
        return True
    else:
        print_status("❌ ALL TESTS FAILED! PDF export functionality is not working.", "FAIL")
        return False

def create_sample_pdf():
    """Create a sample PDF using the first test case"""
    print_status("📄 Creating sample PDF for repository...")
    
    if TEST_CASES:
        test_case = TEST_CASES[0]  # Use first test case
        pdf_path = export_pdf(test_case)
        
        if pdf_path and validate_pdf(pdf_path):
            # Copy to repository root with a standard name
            repo_pdf_path = "/app/sample_match_prediction.pdf"
            try:
                import shutil
                shutil.copy2(pdf_path, repo_pdf_path)
                print_status(f"✅ Sample PDF created: {repo_pdf_path}")
                return repo_pdf_path
            except Exception as e:
                print_status(f"❌ Failed to copy sample PDF: {e}", "ERROR")
                return None
        else:
            print_status("❌ Failed to create sample PDF", "ERROR")
            return None
    else:
        print_status("❌ No test cases available", "ERROR")
        return None

if __name__ == "__main__":
    try:
        # Run comprehensive test
        success = run_comprehensive_test()
        
        # Create sample PDF for repository
        sample_pdf = create_sample_pdf()
        
        # Exit with appropriate code
        if success:
            print_status("✅ PDF Export Test Suite completed successfully!")
            sys.exit(0)
        else:
            print_status("❌ PDF Export Test Suite completed with errors!")
            sys.exit(1)
            
    except KeyboardInterrupt:
        print_status("Test interrupted by user", "STOP")
        sys.exit(1)
    except Exception as e:
        print_status(f"Unexpected error: {e}", "FATAL")
        sys.exit(1)