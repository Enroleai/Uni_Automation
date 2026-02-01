
╔══════════════════════════════════════════════════════════════════════╗
║                    QUICK START GUIDE - 5 MINUTES                     ║
╔══════════════════════════════════════════════════════════════════════╗

STEP 1: INSTALL DEPENDENCIES (2 minutes)
─────────────────────────────────────────────────────────────────────
pip install playwright sqlalchemy pypdf2 pillow pydantic requests beautifulsoup4
playwright install chromium

Note: For production, install all dependencies:
pip install -r requirements.txt


STEP 2: TEST DOCUMENT EXTRACTION (1 minute)
─────────────────────────────────────────────────────────────────────
Create a test file: test_extraction.py

```python
from document_extractor import DocumentExtractor

# Test with sample text
extractor = DocumentExtractor()
sample_text = """
Student: John Smith
Email: john.smith@email.com
Phone: (555) 123-4567
GPA: 3.85
SAT Score: 1450
"""

data = extractor.extract_structured_data(sample_text)
print("Extracted:", data)
```

Run: python test_extraction.py


STEP 3: CONFIGURE EMAIL (1 minute)
─────────────────────────────────────────────────────────────────────
For Gmail:
1. Go to: https://myaccount.google.com/apppasswords
2. Create app password for "Mail"
3. Save the 16-character password

For other providers:
- Enable IMAP in email settings
- Use regular password or app-specific password


STEP 4: INSPECT TARGET UNIVERSITY (5-10 minutes)
─────────────────────────────────────────────────────────────────────
1. Open university application portal
2. Press F12 (Developer Tools)
3. Navigate to signup page
4. Right-click each field → Inspect
5. Note the selectors (e.g., #firstName, [name="email"])

Quick test in browser console:
  document.querySelector('#firstName')
  // Should highlight the field


STEP 5: CREATE UNIVERSITY CONFIG (2 minutes)
─────────────────────────────────────────────────────────────────────
Create file: my_university.json

```json
{
  "name": "My University",
  "url": "https://apply.myuni.edu",
  "signup_url": "https://apply.myuni.edu/signup",
  "login_url": "https://apply.myuni.edu/login",
  "application_url": "https://apply.myuni.edu/application",
  "email_domain": "myuni.edu",
  "requires_email_verification": true,
  
  "signup_field_mapping": {
    "first_name": "#firstName",
    "last_name": "#lastName",
    "email": "#email"
  },
  
  "field_mapping": {
    "first_name": "#app_firstName",
    "last_name": "#app_lastName",
    "email": "#app_email",
    "phone": "#app_phone",
    "gpa": "#app_gpa"
  }
}
```


STEP 6: RUN YOUR FIRST APPLICATION (1 minute)
─────────────────────────────────────────────────────────────────────
Create file: my_first_application.py

```python
from orchestrator import ApplicationOrchestrator
import json

# Initialize with email config
orchestrator = ApplicationOrchestrator(
    email_config={
        'address': 'your-email@gmail.com',
        'password': 'your-app-password'  # From Step 3
    }
)

# Manual student entry (for testing)
from models import init_db, Student
from datetime import date

engine, SessionMaker = init_db()
session = SessionMaker()

student = Student(
    first_name='Test',
    last_name='Student',
    email='test.student@email.com',
    phone='5551234567',
    gpa='3.5',
    sat_score=1200
)
session.add(student)
session.commit()
student_id = student.id
session.close()

# Load university config
with open('my_university.json') as f:
    uni_config = json.load(f)

# Submit application
print("Starting application submission...")
success = orchestrator.submit_application(
    student_id=student_id,
    university_config=uni_config,
    password='TestPassword123!'
)

if success:
    print("✓ SUCCESS! Application submitted")
else:
    print("✗ FAILED - Check screenshots folder")
```

Run: python my_first_application.py


╔══════════════════════════════════════════════════════════════════════╗
║                            TROUBLESHOOTING                            ║
╚══════════════════════════════════════════════════════════════════════╝

Problem: "ModuleNotFoundError"
Solution: pip install <missing-module>

Problem: "Could not find field with selector"
Solution: 
  - Open in non-headless mode (headless=False)
  - Check selector in browser console
  - Try alternative selectors

Problem: "Email verification timeout"
Solution:
  - Check email credentials
  - Verify IMAP is enabled
  - Check spam folder
  - Increase timeout (timeout_minutes=10)

Problem: "Failed to login"
Solution:
  - Verify account was created successfully
  - Check for email verification requirement
  - Look for CAPTCHA on login page

Problem: Screenshots show wrong page
Solution:
  - Add wait times: time.sleep(3)
  - Use page.wait_for_load_state('networkidle')
  - Check for redirects


╔══════════════════════════════════════════════════════════════════════╗
║                         TESTING STRATEGY                              ║
╚══════════════════════════════════════════════════════════════════════╝

1. TEST INCREMENTALLY
   □ Test document extraction alone
   □ Test account creation alone
   □ Test login alone
   □ Test form filling alone
   □ Finally, test end-to-end

2. USE VISUAL MODE FIRST
   Set headless=False to watch what's happening
   BrowserAutomation(headless=False, slow_mo=500)

3. CHECK SCREENSHOTS
   Screenshots saved to: screenshots/
   - submission_*.png = Success
   - error_*.png = Failure point

4. START WITH ONE UNIVERSITY
   Don't configure 10 universities at once
   Perfect the process with one first

5. USE DUMMY DATA
   Don't use real student data during testing
   Create test accounts with test@example.com


╔══════════════════════════════════════════════════════════════════════╗
║                         PRODUCTION CHECKLIST                          ║
╚══════════════════════════════════════════════════════════════════════╝

Before going to production:

□ Test with 10+ applications successfully
□ Handle all error cases gracefully
□ Implement retry logic for failures
□ Set up proper logging
□ Encrypt passwords in database
□ Add rate limiting between submissions
□ Get legal approval for automation
□ Obtain student consent for data processing
□ Set up monitoring and alerts
□ Create backup procedures
□ Document all university-specific quirks
□ Train team on manual fallback procedures


╔══════════════════════════════════════════════════════════════════════╗
║                            NEXT STEPS                                 ║
╚══════════════════════════════════════════════════════════════════════╝

1. Read README.md for detailed documentation
2. Study examples.py for more usage patterns
3. Run university_config.py to create templates
4. Customize for your specific universities
5. Test thoroughly with dummy data
6. Gradually scale to production

Need help? Check the documentation or ask questions!

═══════════════════════════════════════════════════════════════════════
