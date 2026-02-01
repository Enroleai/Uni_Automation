"""
Main orchestrator - Coordinates the entire application workflow
"""
import os
import json
import time
from typing import Dict, Any, Optional
from pathlib import Path
from datetime import datetime

from models import init_db, Student, Application, StudentData
from document_extractor import DocumentExtractor
from email_handler import EmailVerificationHandler
from browser_automation import BrowserAutomation


class ApplicationOrchestrator:
    """Main orchestrator for automated university applications"""
    
    def __init__(self, 
                 db_path: str = 'student_data.db',
                 email_config: Dict[str, str] = None):
        """
        Initialize orchestrator
        
        Args:
            db_path: Path to SQLite database
            email_config: Email configuration dict with 'address' and 'password'
        """
        # Initialize database
        self.engine, self.SessionMaker = init_db(db_path)
        
        # Initialize components
        self.extractor = DocumentExtractor()
        self.browser = None
        self.email_handler = None
        
        if email_config:
            self.email_handler = EmailVerificationHandler(
                email_address=email_config['address'],
                email_password=email_config['password']
            )
    
    def extract_and_store_student(self, document_path: str) -> Optional[int]:
        """
        Extract student data from document and store in database
        
        Args:
            document_path: Path to document file
            
        Returns:
            Student ID if successful, None otherwise
        """
        try:
            print(f"\n📄 Extracting data from: {document_path}")
            
            # Extract data from document
            extracted_data = self.extractor.extract_from_document(document_path)
            
            print(f"✓ Extracted {len(extracted_data)} fields")
            
            # Validate data
            try:
                student_data = StudentData(**extracted_data)
            except Exception as e:
                print(f"⚠ Data validation warning: {e}")
                # Continue with partial data
                student_data = extracted_data
            
            # Store in database
            session = self.SessionMaker()
            try:
                student = Student(**extracted_data)
                session.add(student)
                session.commit()
                student_id = student.id
                print(f"✓ Stored student data with ID: {student_id}")
                return student_id
            finally:
                session.close()
                
        except Exception as e:
            print(f"✗ Error extracting/storing student data: {e}")
            return None
    
    def submit_application(self,
                          student_id: int,
                          university_config: Dict[str, Any],
                          password: str = None) -> bool:
        """
        Submit application to university
        
        Args:
            student_id: Student ID from database
            university_config: Configuration dict with:
                - name: University name
                - url: Base URL
                - signup_url: Signup page URL
                - login_url: Login page URL
                - application_url: Application form URL
                - field_mapping: Dict mapping student fields to form selectors
                - email_domain: Domain for verification emails
            password: Password for account creation
            
        Returns:
            bool: Success status
        """
        # Get student data
        session = self.SessionMaker()
        try:
            student = session.query(Student).filter_by(id=student_id).first()
            
            if not student:
                print(f"✗ Student with ID {student_id} not found")
                return False
            
            student_data = student.to_dict()
            
            print(f"\n🎓 Starting application for {student.first_name} {student.last_name}")
            print(f"   University: {university_config['name']}")
            
            # Create application tracking record
            application = Application(
                student_id=student_id,
                university_name=university_config['name'],
                university_url=university_config['url'],
                account_email=student.email,
                status='in_progress'
            )
            session.add(application)
            session.commit()
            application_id = application.id
            
            # Initialize browser
            self.browser = BrowserAutomation(headless=False, slow_mo=100)
            
            try:
                # Step 1: Create account
                print("\n📝 Step 1: Creating account...")
                
                account_created = self.browser.create_account(
                    signup_url=university_config['signup_url'],
                    student_data=student_data,
                    password=password or 'TempPassword123!',
                    field_mapping=university_config.get('signup_field_mapping')
                )
                
                if not account_created:
                    raise Exception("Failed to create account")
                
                print("✓ Account created successfully")
                application.account_created = True
                application.account_password = password or 'TempPassword123!'
                session.commit()
                
                # Step 2: Email verification
                if self.email_handler and university_config.get('requires_email_verification'):
                    print("\n📧 Step 2: Waiting for verification email...")
                    
                    email_data = self.email_handler.wait_for_verification_email(
                        from_domain=university_config['email_domain'],
                        subject_keywords=['verify', 'confirm', 'activate'],
                        timeout_minutes=5
                    )
                    
                    if email_data and email_data.get('verification_link'):
                        print(f"✓ Verification email received")
                        
                        # Click verification link
                        verified = self.browser.handle_verification_link(
                            email_data['verification_link']
                        )
                        
                        if verified:
                            print("✓ Email verified")
                            application.email_verified = True
                            session.commit()
                        else:
                            print("⚠ Could not confirm verification")
                    else:
                        print("⚠ Verification email not received within timeout")
                        # Continue anyway - some systems allow proceeding without verification
                
                # Step 3: Login
                print("\n🔐 Step 3: Logging in...")
                
                logged_in = self.browser.login(
                    login_url=university_config['login_url'],
                    email=student.email,
                    password=password or 'TempPassword123!'
                )
                
                if not logged_in:
                    raise Exception("Failed to login")
                
                print("✓ Logged in successfully")
                
                # Step 4: Fill application form
                print("\n📋 Step 4: Filling application form...")
                
                form_filled = self.browser.fill_application_form(
                    form_url=university_config['application_url'],
                    student_data=student_data,
                    field_mapping=university_config['field_mapping']
                )
                
                if not form_filled:
                    raise Exception("Failed to fill application form")
                
                print("✓ Application form filled")
                
                # Step 5: Submit application
                print("\n🚀 Step 5: Submitting application...")
                
                submitted = self.browser.submit_form()
                
                if not submitted:
                    raise Exception("Failed to submit application")
                
                print("✓ Application submitted successfully!")
                
                # Take confirmation screenshot
                screenshot = self.browser.take_screenshot(
                    f"submission_{student_id}_{university_config['name']}.png"
                )
                print(f"📸 Screenshot saved: {screenshot}")
                
                # Update application status
                application.status = 'submitted'
                application.submission_date = datetime.utcnow()
                session.commit()
                
                return True
                
            except Exception as e:
                print(f"\n✗ Application failed: {e}")
                
                # Update application with error
                application.status = 'failed'
                application.last_error = str(e)
                application.retry_count += 1
                session.commit()
                
                # Take error screenshot
                if self.browser and self.browser.page:
                    self.browser.take_screenshot(
                        f"error_{student_id}_{university_config['name']}.png"
                    )
                
                return False
                
            finally:
                if self.browser:
                    self.browser.close_browser()
                
        finally:
            session.close()
    
    def batch_submit_applications(self,
                                 student_ids: list,
                                 university_configs: list,
                                 password: str = None) -> Dict[str, Any]:
        """
        Submit applications for multiple students to multiple universities
        
        Args:
            student_ids: List of student IDs
            university_configs: List of university configuration dicts
            password: Default password for all accounts
            
        Returns:
            Dict with results summary
        """
        results = {
            'total': 0,
            'successful': 0,
            'failed': 0,
            'details': []
        }
        
        for student_id in student_ids:
            for uni_config in university_configs:
                results['total'] += 1
                
                success = self.submit_application(
                    student_id=student_id,
                    university_config=uni_config,
                    password=password
                )
                
                if success:
                    results['successful'] += 1
                else:
                    results['failed'] += 1
                
                results['details'].append({
                    'student_id': student_id,
                    'university': uni_config['name'],
                    'success': success,
                    'timestamp': datetime.utcnow().isoformat()
                })
                
                # Delay between applications
                time.sleep(5)
        
        return results
    
    def get_application_status(self, student_id: int = None) -> list:
        """
        Get application status
        
        Args:
            student_id: Optional student ID to filter by
            
        Returns:
            List of application records
        """
        session = self.SessionMaker()
        try:
            query = session.query(Application)
            
            if student_id:
                query = query.filter_by(student_id=student_id)
            
            applications = query.all()
            
            return [{
                'id': app.id,
                'student_id': app.student_id,
                'university': app.university_name,
                'status': app.status,
                'account_created': app.account_created,
                'email_verified': app.email_verified,
                'submission_date': app.submission_date.isoformat() if app.submission_date else None,
                'last_error': app.last_error
            } for app in applications]
            
        finally:
            session.close()


def demo_orchestrator():
    """Demo the complete workflow"""
    print("="*70)
    print("STUDENT APPLICATION AUTOMATION SYSTEM - DEMO")
    print("="*70)
    
    print("\n📚 SYSTEM COMPONENTS:")
    print("\n1. Document Extractor")
    print("   → Extracts student info from PDFs/images using OCR + AI")
    print("   → Supports intelligent field detection")
    
    print("\n2. Master Database")
    print("   → SQLite database for student records")
    print("   → Tracks all applications and their status")
    
    print("\n3. Browser Automation")
    print("   → Creates accounts on university portals")
    print("   → Fills and submits application forms")
    print("   → Handles multi-step processes")
    
    print("\n4. Email Verification")
    print("   → Monitors inbox for verification emails")
    print("   → Automatically extracts and clicks verification links")
    
    print("\n5. Orchestrator")
    print("   → Coordinates entire workflow")
    print("   → Error handling and retry logic")
    print("   → Batch processing support")
    
    print("\n" + "="*70)
    print("WORKFLOW EXAMPLE")
    print("="*70)
    
    workflow_steps = """
    # Initialize orchestrator
    orchestrator = ApplicationOrchestrator(
        email_config={
            'address': 'student@email.com',
            'password': 'app_password'
        }
    )
    
    # Extract and store student data
    student_id = orchestrator.extract_and_store_student(
        'student_documents.pdf'
    )
    
    # Configure university
    university_config = {
        'name': 'Sample University',
        'url': 'https://university.edu',
        'signup_url': 'https://university.edu/signup',
        'login_url': 'https://university.edu/login',
        'application_url': 'https://university.edu/apply',
        'email_domain': 'university.edu',
        'requires_email_verification': True,
        'field_mapping': {
            'first_name': '#firstName',
            'last_name': '#lastName',
            'email': '#email',
            # ... more fields
        }
    }
    
    # Submit application
    success = orchestrator.submit_application(
        student_id=student_id,
        university_config=university_config,
        password='SecurePassword123!'
    )
    
    # Check status
    status = orchestrator.get_application_status(student_id)
    """
    
    print(workflow_steps)
    
    print("\n" + "="*70)
    print("CUSTOMIZATION REQUIREMENTS")
    print("="*70)
    
    print("\nFor each university, you need to configure:")
    print("  1. URLs (signup, login, application)")
    print("  2. Field mapping (connect form fields to data)")
    print("  3. Email domain (for verification)")
    print("  4. Any special requirements (CAPTCHA, multi-page forms, etc.)")
    
    print("\n" + "="*70)
    print("NEXT STEPS")
    print("="*70)
    
    print("\n1. Install dependencies:")
    print("   pip install -r requirements.txt")
    print("   playwright install chromium")
    
    print("\n2. Configure email access:")
    print("   - Enable IMAP on your email")
    print("   - Generate app-specific password")
    
    print("\n3. Customize for target universities:")
    print("   - Inspect their signup/login/application forms")
    print("   - Create field mappings")
    print("   - Test with single application first")
    
    print("\n4. Run automation:")
    print("   - Start with document extraction")
    print("   - Test account creation manually")
    print("   - Run full automation")
    
    print("\n" + "="*70)

if __name__ == "__main__":
    demo_orchestrator()
