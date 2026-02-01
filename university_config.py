"""
University Configuration Template Generator

This script helps you create configuration files for new universities
"""
import json
from pathlib import Path

def create_university_config_template():
    """Generate a blank university configuration template"""
    
    template = {
        "name": "University Name",
        "url": "https://university.edu",
        "signup_url": "https://university.edu/signup",
        "login_url": "https://university.edu/login",
        "application_url": "https://university.edu/apply",
        "email_domain": "university.edu",
        "requires_email_verification": True,
        
        "notes": {
            "signup_process": "Describe the signup process here",
            "special_requirements": "Any CAPTCHA, multi-step, or special requirements",
            "testing_notes": "Notes from testing"
        },
        
        "signup_field_mapping": {
            "first_name": "# CSS selector for first name",
            "last_name": "# CSS selector for last name",
            "email": "# CSS selector for email",
            "phone": "# CSS selector for phone (optional)",
            "password": "# CSS selector for password"
        },
        
        "field_mapping": {
            "first_name": "# CSS selector",
            "middle_name": "# CSS selector",
            "last_name": "# CSS selector",
            "email": "# CSS selector",
            "phone": "# CSS selector",
            "date_of_birth": "# CSS selector (format: YYYY-MM-DD)",
            "gender": "# CSS selector (select/dropdown)",
            "nationality": "# CSS selector",
            "address_line1": "# CSS selector",
            "address_line2": "# CSS selector",
            "city": "# CSS selector",
            "state": "# CSS selector (select/dropdown)",
            "postal_code": "# CSS selector",
            "country": "# CSS selector (select/dropdown)",
            "high_school_name": "# CSS selector",
            "graduation_year": "# CSS selector",
            "gpa": "# CSS selector",
            "sat_score": "# CSS selector",
            "act_score": "# CSS selector",
            "intended_major": "# CSS selector (select/dropdown)",
            "extracurriculars": "# CSS selector (textarea)"
        },
        
        "field_types": {
            "date_of_birth": "date",
            "gender": "select",
            "state": "select",
            "country": "select",
            "intended_major": "select",
            "extracurriculars": "textarea"
        },
        
        "multi_page": False,
        "pages": [
            {
                "page_number": 1,
                "url": "https://university.edu/apply/page1",
                "fields": ["first_name", "last_name", "email"],
                "next_button": "#nextButton"
            }
        ]
    }
    
    return template


def save_university_config(config: dict, filename: str):
    """Save university configuration to JSON file"""
    
    config_dir = Path('university_configs')
    config_dir.mkdir(exist_ok=True)
    
    filepath = config_dir / f"{filename}.json"
    
    with open(filepath, 'w') as f:
        json.dump(config, f, indent=2)
    
    print(f"✓ Configuration saved to: {filepath}")
    return filepath


def load_university_config(filename: str) -> dict:
    """Load university configuration from JSON file"""
    
    filepath = Path('university_configs') / f"{filename}.json"
    
    if not filepath.exists():
        raise FileNotFoundError(f"Configuration not found: {filepath}")
    
    with open(filepath, 'r') as f:
        config = json.load(f)
    
    return config


def inspect_university_website():
    """Guide for inspecting university websites to create configuration"""
    
    guide = """
    ═══════════════════════════════════════════════════════════════════
    GUIDE: How to Inspect University Website and Create Configuration
    ═══════════════════════════════════════════════════════════════════
    
    STEP 1: Open the University Website
    ───────────────────────────────────
    - Navigate to the university's application portal
    - Open browser Developer Tools (F12 or Right-click → Inspect)
    
    STEP 2: Inspect Signup Page
    ────────────────────────────
    1. Go to the signup/registration page
    2. Right-click on each form field → Inspect
    3. Note down the selector for each field:
       
       Examples:
       <input id="firstName" ...>           → #firstName
       <input name="lastName" ...>          → [name="lastName"]
       <input type="email" ...>             → input[type="email"]
       <select id="state" ...>              → select#state
    
    4. Common selector patterns:
       - By ID:    #fieldId
       - By name:  [name="fieldName"]
       - By class: .className
       - By type:  input[type="text"]
    
    STEP 3: Inspect Login Page
    ───────────────────────────
    1. Go to the login page
    2. Inspect email/username field
    3. Inspect password field
    4. Inspect login button
    
    STEP 4: Inspect Application Form
    ─────────────────────────────────
    1. Create a test account manually
    2. Log in and navigate to application form
    3. Inspect EVERY field you need to fill:
       - Personal information
       - Contact details
       - Address
       - Academic information
       - Test scores
       - Essays/extracurriculars
    
    4. For multi-page forms:
       - Note the URL of each page
       - Note which fields are on which page
       - Find the "Next" button selectors
    
    STEP 5: Test Field Selectors
    ─────────────────────────────
    In browser console (F12 → Console tab), test your selectors:
    
    document.querySelector('#firstName')        // Should return element
    document.querySelector('[name="email"]')    // Should return element
    
    If returns null, the selector is wrong!
    
    STEP 6: Check for Special Requirements
    ───────────────────────────────────────
    - CAPTCHA (reCAPTCHA, hCaptcha, etc.)
    - Email verification required?
    - Phone verification?
    - Document uploads?
    - Multi-step process?
    
    STEP 7: Create Configuration
    ─────────────────────────────
    Use the template and fill in:
    
    1. URLs:
       - Base URL
       - Signup URL
       - Login URL  
       - Application URL
    
    2. Field mappings:
       - Map each student data field to its CSS selector
       - Specify field types (text, select, date, textarea)
    
    3. Special settings:
       - Email domain for verification
       - Multi-page configuration if needed
    
    STEP 8: Test Configuration
    ───────────────────────────
    1. Test with browser in non-headless mode first
    2. Watch each step execute
    3. Take screenshots at each stage
    4. Fix any selector issues
    5. Once working, enable headless mode
    
    ═══════════════════════════════════════════════════════════════════
    TIPS FOR ROBUST SELECTORS
    ═══════════════════════════════════════════════════════════════════
    
    ✓ PREFER:
      - IDs: #firstName (most stable)
      - Names: [name="firstName"]
      - Specific attributes: [data-testid="firstName"]
    
    ✗ AVOID:
      - Generated classes: .css-12345-field (change often)
      - Deep hierarchies: div > div > div > input
      - Position-based: :nth-child(3)
    
    ✓ FALLBACK STRATEGY:
      Use multiple selectors:
      '#firstName, [name="firstName"], input[placeholder*="First"]'
    
    ═══════════════════════════════════════════════════════════════════
    """
    
    print(guide)


def create_example_configs():
    """Create example configurations for common university platforms"""
    
    # Common Application (Coalition App style)
    common_app_style = {
        "name": "Common Application Style University",
        "url": "https://apply.university.edu",
        "signup_url": "https://apply.university.edu/account/create",
        "login_url": "https://apply.university.edu/login",
        "application_url": "https://apply.university.edu/application",
        "email_domain": "university.edu",
        "requires_email_verification": True,
        "field_mapping": {
            "first_name": "#profile_first_name",
            "last_name": "#profile_last_name",
            "email": "#profile_email",
            "phone": "#profile_phone",
            "date_of_birth": "#profile_birth_date",
            "address_line1": "#profile_address_1",
            "city": "#profile_city",
            "state": "#profile_state",
            "postal_code": "#profile_zip"
        }
    }
    
    # Slate-based system (popular admissions platform)
    slate_style = {
        "name": "Slate-Based University",
        "url": "https://admissions.university.edu",
        "signup_url": "https://admissions.university.edu/register",
        "login_url": "https://admissions.university.edu/apply",
        "application_url": "https://admissions.university.edu/apply/status",
        "email_domain": "university.edu",
        "requires_email_verification": True,
        "field_mapping": {
            "first_name": "[name='first']",
            "last_name": "[name='last']",
            "email": "[name='email']",
            "phone": "[name='mobile']",
            "date_of_birth": "[name='birthdate']"
        }
    }
    
    # Save examples
    save_university_config(common_app_style, 'common_app_style_example')
    save_university_config(slate_style, 'slate_style_example')
    
    print("\n✓ Example configurations created:")
    print("  - common_app_style_example.json")
    print("  - slate_style_example.json")


def main():
    """Main function"""
    
    print("\n" + "="*70)
    print("UNIVERSITY CONFIGURATION TEMPLATE GENERATOR")
    print("="*70)
    
    print("\n📋 Options:")
    print("  1. Create blank configuration template")
    print("  2. View inspection guide")
    print("  3. Create example configurations")
    
    print("\n💡 Usage:")
    print("  python university_config.py")
    
    # Create template
    template = create_university_config_template()
    save_university_config(template, 'template')
    
    # Show guide
    inspect_university_website()
    
    # Create examples
    create_example_configs()


if __name__ == "__main__":
    main()
