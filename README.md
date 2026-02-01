# Student Application Automation System

A complete Python-based system for automating university application submissions. This system extracts student information from documents, stores it in a database, and automatically fills and submits applications on university portals.

## 🎯 Features

### 1. **Document Extraction**
- Extract student information from PDFs and images
- OCR support for scanned documents
- AI-powered intelligent field detection
- Supports various document formats

### 2. **Master Database**
- SQLite database for student records
- Track all applications and their status
- Complete student profile management
- Application history and audit trail

### 3. **Browser Automation**
- Automated account creation on university portals
- Login handling with session management
- Intelligent form field detection and filling
- Multi-page form navigation
- Screenshot capture for debugging

### 4. **Email Verification**
- Automatic email monitoring
- Verification link extraction
- Support for multiple email providers (Gmail, Outlook, Yahoo, etc.)
- Timeout handling and retry logic

### 5. **Orchestration**
- End-to-end workflow coordination
- Batch processing support
- Error handling and recovery
- Status tracking and reporting

## 📋 Requirements

```bash
pip install -r requirements.txt
playwright install chromium
```

### Email Configuration

For Gmail:
1. Enable IMAP: Settings → See all settings → Forwarding and POP/IMAP → Enable IMAP
2. Generate app password: https://myaccount.google.com/apppasswords
3. Use app password instead of regular password

## 🚀 Quick Start

### Step 1: Extract Student Data

```python
from orchestrator import ApplicationOrchestrator

# Initialize
orchestrator = ApplicationOrchestrator(
    email_config={
        'address': 'your-email@gmail.com',
        'password': 'your-app-password'
    }
)

# Extract from document
student_id = orchestrator.extract_and_store_student(
    'path/to/student_document.pdf'
)
```

### Step 2: Configure University

```python
university_config = {
    'name': 'Sample University',
    'url': 'https://university.edu',
    'signup_url': 'https://university.edu/signup',
    'login_url': 'https://university.edu/login',
    'application_url': 'https://university.edu/apply',
    'email_domain': 'university.edu',
    'requires_email_verification': True,
    
    # Field mapping: student_field -> form_selector
    'signup_field_mapping': {
        'first_name': '#firstName',
        'last_name': '#lastName',
        'email': '#email',
        'password': '#password'
    },
    
    'field_mapping': {
        'first_name': '#applicationFirstName',
        'last_name': '#applicationLastName',
        'email': '#applicationEmail',
        'phone': '#phone',
        'date_of_birth': '#dob',
        'address_line1': '#address1',
        'city': '#city',
        'state': '#state',
        'postal_code': '#zipCode',
        'high_school_name': '#highSchool',
        'gpa': '#gpa',
        'sat_score': '#satScore',
        'intended_major': '#major'
    }
}
```

### Step 3: Submit Application

```python
success = orchestrator.submit_application(
    student_id=student_id,
    university_config=university_config,
    password='SecurePassword123!'
)

if success:
    print("✓ Application submitted successfully!")
else:
    print("✗ Application failed")
```

### Step 4: Check Status

```python
status = orchestrator.get_application_status(student_id)
print(status)
```

## 📦 System Architecture

```
student-application-automation/
├── models.py                 # Database models
├── document_extractor.py     # Document parsing and extraction
├── email_handler.py          # Email verification handling
├── browser_automation.py     # Browser automation with Playwright
├── orchestrator.py           # Main workflow coordinator
├── requirements.txt          # Python dependencies
├── README.md                 # This file
└── student_data.db          # SQLite database (created automatically)
```

## 🔧 Customization Guide

### For Each University

1. **Inspect the website**
   - Open developer tools (F12)
   - Navigate through signup → login → application
   - Note down form field selectors (IDs, names, classes)

2. **Create field mapping**
   ```python
   field_mapping = {
       'student_field': 'css_selector',
       # Examples:
       'first_name': '#firstName',           # By ID
       'last_name': '[name="lastName"]',     # By name attribute
       'email': 'input[type="email"]',       # By type
       'state': 'select#state'               # For dropdowns
   }
   ```

3. **Test incrementally**
   - Test account creation first
   - Then test login
   - Finally test form filling
   - Use screenshots for debugging

## ⚠️ Important Considerations

### Legal & Ethical
- **Terms of Service**: Automation may violate university terms of service
- **Data Privacy**: Handle student data in compliance with regulations (GDPR, FERPA)
- **Permission**: Ensure students have consented to automated application submission

### Technical Challenges
- **CAPTCHA**: May require manual intervention or paid CAPTCHA solving services
- **Anti-bot Detection**: Some sites use sophisticated bot detection
- **Website Changes**: University websites change frequently, requiring updates
- **Rate Limiting**: Some portals may block rapid submissions

### Recommendations
1. Start with universities that explicitly allow automation
2. Test thoroughly with dummy data first
3. Implement rate limiting (delays between applications)
4. Monitor for website changes
5. Have manual fallback procedures
6. Keep detailed logs for audit trails

## 🐛 Debugging

### Enable Visual Mode
```python
browser = BrowserAutomation(headless=False, slow_mo=500)
```

### Screenshots
Automatically captured on:
- Successful submission → `screenshots/submission_*.png`
- Errors → `screenshots/error_*.png`

### Logs
Check console output for detailed step-by-step progress and errors.

## 🔄 Batch Processing

Submit applications for multiple students to multiple universities:

```python
results = orchestrator.batch_submit_applications(
    student_ids=[1, 2, 3],
    university_configs=[uni1_config, uni2_config],
    password='SecurePassword123!'
)

print(f"Total: {results['total']}")
print(f"Successful: {results['successful']}")
print(f"Failed: {results['failed']}")
```

## 📊 Database Schema

### Students Table
- Personal information (name, email, phone, DOB)
- Address details
- Academic information (GPA, test scores)
- Extracurriculars

### Applications Table
- Student reference
- University details
- Account credentials
- Application status (pending/in_progress/submitted/failed)
- Submission date
- Error tracking

## 🛠️ Advanced Features

### Custom Document Extraction
Integrate with AI services for better extraction:
```python
from document_extractor import DocumentExtractor

extractor = DocumentExtractor()
# Override _ai_extract_fields method to use your preferred AI service
```

### Email Provider Support
Built-in support for:
- Gmail
- Outlook/Hotmail
- Yahoo
- iCloud
- Custom IMAP servers

### Form Field Detection Strategies
1. CSS selectors (ID, class, name)
2. Label text matching
3. Placeholder text matching
4. Field type detection
5. Fallback to visual position

## 🤝 Contributing

To extend the system:
1. Add new extraction patterns in `document_extractor.py`
2. Create university-specific automation classes
3. Implement CAPTCHA solving integrations
4. Add support for file uploads
5. Enhance error recovery mechanisms

## 📝 License

This is a demonstration/educational project. Use responsibly and in compliance with applicable laws and regulations.

## ⚡ Performance Tips

1. **Use headless mode** for production: `headless=True`
2. **Implement connection pooling** for email checking
3. **Cache form selectors** for repeated submissions
4. **Run in parallel** for multiple independent applications
5. **Use database indices** for faster queries

## 🆘 Support

For issues:
1. Check screenshots in `screenshots/` directory
2. Review error messages in application records
3. Test with `headless=False` to see browser actions
4. Verify field mappings are correct
5. Ensure email credentials are valid

---

**Built with**: Python, Playwright, SQLAlchemy, PyPDF2, Pillow
