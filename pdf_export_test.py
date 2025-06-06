import requests
import os
import json
import io
import PyPDF2
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Get the backend URL from environment
BACKEND_URL = os.environ.get('REACT_APP_BACKEND_URL', 'http://localhost:8001')
BASE_URL = f"{BACKEND_URL}/api"

def test_pdf_export_endpoint():
    """Test the PDF export endpoint for match predictions"""
    print("\n\n========== TESTING PDF EXPORT ENDPOINT ==========\n")
    
    # Step 1: Get teams and referees from the system
    print("Step 1: Getting teams and referees from the system")
    teams_response = requests.get(f"{BASE_URL}/teams")
    if teams_response.status_code != 200:
        print(f"❌ Failed to get teams: {teams_response.status_code}")
        return False
    
    teams = teams_response.json().get('teams', [])
    if len(teams) < 2:
        print("❌ Not enough teams for match prediction")
        return False
    
    print(f"Found {len(teams)} teams: {', '.join(teams[:5])}{'...' if len(teams) > 5 else ''}")
    
    referees_response = requests.get(f"{BASE_URL}/referees")
    if referees_response.status_code != 200:
        print(f"❌ Failed to get referees: {referees_response.status_code}")
        return False
    
    referees = referees_response.json().get('referees', [])
    if not referees:
        print("❌ No referees found for match prediction")
        return False
    
    print(f"Found {len(referees)} referees: {', '.join(referees[:5])}{'...' if len(referees) > 5 else ''}")
    
    # Step 2: Test PDF export with actual team names and referee
    print("\nStep 2: Testing PDF export with actual team names and referee")
    home_team = teams[0]
    away_team = teams[1]
    referee = referees[0]
    
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
    
    # Step 3: Verify PDF content
    print("\nStep 3: Verifying PDF content")
    
    # Save PDF to a temporary file
    pdf_content = response.content
    pdf_file = io.BytesIO(pdf_content)
    
    try:
        # Parse PDF content
        pdf_reader = PyPDF2.PdfReader(pdf_file)
        num_pages = len(pdf_reader.pages)
        print(f"PDF has {num_pages} pages")
        
        # Extract text from all pages to verify content
        all_pages_text = ""
        for i in range(num_pages):
            all_pages_text += pdf_reader.pages[i].extract_text()
        
        # Check for required sections in the PDF
        required_sections = [
            "Football Match Prediction Report",
            "Match Information",
            "Prediction Summary",
            "Detailed Model Analysis",
            "Poisson Distribution Analysis",
            "Head-to-Head Statistics",
            "Referee Bias Analysis",
            "Model Information"
        ]
        
        missing_sections = []
        for section in required_sections:
            if section not in all_pages_text:
                missing_sections.append(section)
        
        if missing_sections:
            print(f"❌ Missing sections in PDF: {', '.join(missing_sections)}")
        else:
            print("✅ All required sections are present in the PDF")
        
        # Check for team names in the PDF
        if home_team not in all_pages_text or away_team not in all_pages_text:
            print("❌ Team names not found in the PDF")
        else:
            print(f"✅ Team names ({home_team}, {away_team}) found in the PDF")
        
        # Check for referee name in the PDF
        if referee not in all_pages_text:
            print(f"❌ Referee name ({referee}) not found in the PDF")
        else:
            print(f"✅ Referee name ({referee}) found in the PDF")
        
        # Check for additional pages with more analysis
        if num_pages > 1:
            print(f"✅ PDF contains multiple pages with detailed analysis")
            
            # Check content of additional pages
            additional_sections_found = []
            for i in range(1, min(num_pages, 3)):  # Check up to 3 pages
                page_text = pdf_reader.pages[i].extract_text()
                for section in ["Head-to-Head Statistics", "Referee Bias Analysis", "Model Information"]:
                    if section in page_text and section not in additional_sections_found:
                        additional_sections_found.append(section)
            
            if additional_sections_found:
                print(f"✅ Additional sections found: {', '.join(additional_sections_found)}")
            else:
                print("⚠️ No additional analysis sections found in extra pages")
        
        # Final assessment
        if not missing_sections and home_team in all_pages_text and away_team in all_pages_text and referee in all_pages_text:
            print("\n✅ PDF export functionality is working correctly!")
            return True
        else:
            print("\n❌ PDF export functionality has issues")
            return False
        
    except Exception as e:
        print(f"❌ Error parsing PDF content: {e}")
        return False

if __name__ == "__main__":
    test_pdf_export_endpoint()
