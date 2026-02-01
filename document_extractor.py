"""
Document extraction module - Extracts student information from PDFs and images
"""
import re
import json
from typing import Dict, Any, Optional
from pathlib import Path
import PyPDF2
from PIL import Image
from io import BytesIO
import base64

class DocumentExtractor:
    """Extract student information from documents"""
    
    def __init__(self):
        self.extraction_patterns = {
            'email': r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',
            'phone': r'\b(?:\+?1[-.]?)?\(?([0-9]{3})\)?[-.]?([0-9]{3})[-.]?([0-9]{4})\b',
            'date': r'\b\d{1,2}[/-]\d{1,2}[/-]\d{2,4}\b',
            'gpa': r'\b[0-4]\.\d{1,2}\b',
            'sat_score': r'\b(?:SAT|sat)[\s:]*(\d{3,4})\b',
            'act_score': r'\b(?:ACT|act)[\s:]*(\d{1,2})\b',
        }
    
    def extract_from_pdf(self, pdf_path: str) -> str:
        """Extract text from PDF"""
        text = ""
        try:
            with open(pdf_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                for page in pdf_reader.pages:
                    text += page.extract_text() + "\n"
        except Exception as e:
            print(f"Error extracting PDF: {e}")
        return text
    
    def extract_from_image(self, image_path: str) -> str:
        """Extract text from image using OCR"""
        try:
            # In production, use pytesseract or cloud OCR
            # For demo, we'll simulate extraction
            import pytesseract
            image = Image.open(image_path)
            text = pytesseract.image_to_string(image)
            return text
        except Exception as e:
            print(f"Error extracting from image: {e}")
            return ""
    
    def extract_structured_data(self, text: str) -> Dict[str, Any]:
        """Extract structured student information from text using pattern matching and AI"""
        data = {}
        
        # Extract using regex patterns
        email_match = re.search(self.extraction_patterns['email'], text)
        if email_match:
            data['email'] = email_match.group(0)
        
        phone_match = re.search(self.extraction_patterns['phone'], text)
        if phone_match:
            data['phone'] = phone_match.group(0)
        
        # Extract GPA
        gpa_match = re.search(self.extraction_patterns['gpa'], text)
        if gpa_match:
            data['gpa'] = gpa_match.group(0)
        
        # Extract SAT score
        sat_match = re.search(self.extraction_patterns['sat_score'], text, re.IGNORECASE)
        if sat_match:
            data['sat_score'] = int(sat_match.group(1))
        
        # Extract ACT score
        act_match = re.search(self.extraction_patterns['act_score'], text, re.IGNORECASE)
        if act_match:
            data['act_score'] = int(act_match.group(1))
        
        # For names and complex fields, we'd use AI extraction
        # This is where you'd integrate GPT-4 or similar for intelligent extraction
        data.update(self._ai_extract_fields(text))
        
        return data
    
    def _ai_extract_fields(self, text: str) -> Dict[str, Any]:
        """
        Use AI (GPT-4, Claude, etc.) to extract complex fields
        In production, this would call an LLM API with a structured prompt
        """
        # Simulated AI extraction response
        # In production, replace with actual LLM API call
        
        prompt = f"""
        Extract the following student information from this text and return as JSON:
        - first_name
        - middle_name
        - last_name
        - date_of_birth (format: YYYY-MM-DD)
        - gender
        - nationality
        - address_line1
        - address_line2
        - city
        - state
        - postal_code
        - country
        - high_school_name
        - graduation_year
        - intended_major
        - extracurriculars
        
        Text:
        {text}
        
        Return only valid JSON.
        """
        
        # This is where you'd call OpenAI, Claude, or other LLM
        # For demo purposes, returning empty dict
        # In production: response = openai.chat.completions.create(...)
        
        return {}
    
    def extract_from_document(self, file_path: str) -> Dict[str, Any]:
        """Main extraction method - handles different file types"""
        file_path = Path(file_path)
        
        if not file_path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")
        
        # Extract text based on file type
        if file_path.suffix.lower() == '.pdf':
            text = self.extract_from_pdf(str(file_path))
        elif file_path.suffix.lower() in ['.jpg', '.jpeg', '.png', '.tiff']:
            text = self.extract_from_image(str(file_path))
        else:
            raise ValueError(f"Unsupported file type: {file_path.suffix}")
        
        # Extract structured data
        student_data = self.extract_structured_data(text)
        
        return student_data


# Demo/test function
def demo_extraction():
    """Demo the extraction capability"""
    # Create a sample text document
    sample_text = """
    Student Information Form
    
    Name: John Michael Smith
    Date of Birth: 05/15/2005
    Email: john.smith@email.com
    Phone: (555) 123-4567
    
    Address:
    123 Main Street
    Apartment 4B
    New York, NY 10001
    United States
    
    Academic Information:
    High School: Lincoln High School
    Graduation Year: 2023
    GPA: 3.85
    SAT Score: 1450
    ACT Score: 32
    
    Intended Major: Computer Science
    
    Extracurricular Activities:
    - President, Robotics Club
    - Varsity Soccer Team Captain
    - Volunteer, Local Food Bank (200+ hours)
    """
    
    extractor = DocumentExtractor()
    data = extractor.extract_structured_data(sample_text)
    
    print("Extracted Data:")
    print(json.dumps(data, indent=2))
    
    return data

if __name__ == "__main__":
    demo_extraction()
