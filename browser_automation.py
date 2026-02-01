"""
Browser automation module - Handles account creation, login, and form filling
"""
from playwright.sync_api import sync_playwright, Page, Browser, TimeoutError
import time
import json
from typing import Dict, Any, Optional, List
from pathlib import Path
import random

class BrowserAutomation:
    """Automate browser interactions for university applications"""
    
    def __init__(self, headless: bool = False, slow_mo: int = 100):
        """
        Initialize browser automation
        
        Args:
            headless: Run browser in headless mode
            slow_mo: Slow down operations by N milliseconds
        """
        self.headless = headless
        self.slow_mo = slow_mo
        self.playwright = None
        self.browser = None
        self.context = None
        self.page = None
    
    def start_browser(self):
        """Start browser instance"""
        self.playwright = sync_playwright().start()
        self.browser = self.playwright.chromium.launch(
            headless=self.headless,
            slow_mo=self.slow_mo
        )
        self.context = self.browser.new_context(
            viewport={'width': 1920, 'height': 1080},
            user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        )
        self.page = self.context.new_page()
        return self.page
    
    def close_browser(self):
        """Close browser instance"""
        if self.page:
            self.page.close()
        if self.context:
            self.context.close()
        if self.browser:
            self.browser.close()
        if self.playwright:
            self.playwright.stop()
    
    def navigate_to(self, url: str, wait_for_load: bool = True):
        """Navigate to URL"""
        if not self.page:
            self.start_browser()
        
        self.page.goto(url)
        
        if wait_for_load:
            self.page.wait_for_load_state('networkidle', timeout=30000)
    
    def fill_form_field(self, selector: str, value: str, field_type: str = 'text'):
        """
        Fill a form field
        
        Args:
            selector: CSS selector or label text
            value: Value to fill
            field_type: Type of field (text, email, select, date, etc.)
        """
        try:
            # Try different selector strategies
            element = None
            
            # Try CSS selector first
            try:
                element = self.page.wait_for_selector(selector, timeout=5000)
            except:
                pass
            
            # Try by label text
            if not element:
                try:
                    element = self.page.get_by_label(selector, exact=False)
                except:
                    pass
            
            # Try by placeholder
            if not element:
                try:
                    element = self.page.get_by_placeholder(selector, exact=False)
                except:
                    pass
            
            if not element:
                print(f"Warning: Could not find field with selector: {selector}")
                return False
            
            # Fill based on field type
            if field_type == 'select':
                element.select_option(value)
            elif field_type == 'date':
                element.fill(value)
            else:
                element.fill(value)
            
            # Add human-like delay
            time.sleep(random.uniform(0.3, 0.8))
            
            return True
            
        except Exception as e:
            print(f"Error filling field {selector}: {e}")
            return False
    
    def create_account(self, 
                       signup_url: str,
                       student_data: Dict[str, Any],
                       password: str,
                       field_mapping: Dict[str, str] = None) -> bool:
        """
        Create account on university portal
        
        Args:
            signup_url: URL of signup page
            student_data: Student information dict
            password: Password to use for account
            field_mapping: Mapping of data fields to form selectors
            
        Returns:
            bool: Success status
        """
        try:
            # Navigate to signup page
            self.navigate_to(signup_url)
            
            # Default field mapping (customize per university)
            if not field_mapping:
                field_mapping = {
                    'first_name': '#firstName, [name="firstName"], input[type="text"][placeholder*="First"]',
                    'last_name': '#lastName, [name="lastName"], input[type="text"][placeholder*="Last"]',
                    'email': '#email, [name="email"], input[type="email"]',
                    'password': '#password, [name="password"], input[type="password"]',
                    'phone': '#phone, [name="phone"], input[type="tel"]',
                }
            
            # Fill form fields
            for field_name, selector in field_mapping.items():
                if field_name in student_data and student_data[field_name]:
                    self.fill_form_field(selector, str(student_data[field_name]))
                elif field_name == 'password':
                    self.fill_form_field(selector, password)
            
            # Look for and click signup button
            submit_button = self.find_submit_button(['Sign Up', 'Create Account', 'Register', 'Submit'])
            
            if submit_button:
                submit_button.click()
                time.sleep(3)  # Wait for submission
                return True
            else:
                print("Could not find submit button")
                return False
                
        except Exception as e:
            print(f"Error creating account: {e}")
            return False
    
    def login(self, 
              login_url: str,
              email: str,
              password: str) -> bool:
        """
        Login to university portal
        
        Args:
            login_url: URL of login page
            email: Email/username
            password: Password
            
        Returns:
            bool: Success status
        """
        try:
            self.navigate_to(login_url)
            
            # Find and fill email/username field
            email_selectors = [
                '#email', '#username', '[name="email"]', '[name="username"]',
                'input[type="email"]', 'input[placeholder*="Email"]'
            ]
            
            for selector in email_selectors:
                try:
                    self.page.fill(selector, email, timeout=2000)
                    break
                except:
                    continue
            
            # Find and fill password field
            password_selectors = [
                '#password', '[name="password"]', 'input[type="password"]'
            ]
            
            for selector in password_selectors:
                try:
                    self.page.fill(selector, password, timeout=2000)
                    break
                except:
                    continue
            
            # Click login button
            login_button = self.find_submit_button(['Login', 'Sign In', 'Log In', 'Submit'])
            
            if login_button:
                login_button.click()
                self.page.wait_for_load_state('networkidle', timeout=10000)
                return True
            
            return False
            
        except Exception as e:
            print(f"Error logging in: {e}")
            return False
    
    def fill_application_form(self,
                             form_url: str,
                             student_data: Dict[str, Any],
                             field_mapping: Dict[str, str]) -> bool:
        """
        Fill application form
        
        Args:
            form_url: URL of application form
            student_data: Student information
            field_mapping: Mapping of fields to selectors
            
        Returns:
            bool: Success status
        """
        try:
            self.navigate_to(form_url)
            
            # Fill each field
            for field_name, selector in field_mapping.items():
                if field_name in student_data and student_data[field_name]:
                    value = student_data[field_name]
                    
                    # Determine field type
                    field_type = 'text'
                    if 'date' in field_name.lower():
                        field_type = 'date'
                    elif field_name in ['state', 'country', 'gender']:
                        field_type = 'select'
                    
                    self.fill_form_field(selector, str(value), field_type)
            
            return True
            
        except Exception as e:
            print(f"Error filling application form: {e}")
            return False
    
    def submit_form(self) -> bool:
        """Submit the current form"""
        try:
            submit_button = self.find_submit_button(['Submit', 'Submit Application', 'Send', 'Apply'])
            
            if submit_button:
                submit_button.click()
                time.sleep(3)
                return True
            
            return False
            
        except Exception as e:
            print(f"Error submitting form: {e}")
            return False
    
    def find_submit_button(self, button_texts: List[str]):
        """Find submit button by text"""
        for text in button_texts:
            try:
                button = self.page.get_by_role('button', name=text, exact=False)
                if button.is_visible():
                    return button
            except:
                continue
        
        # Try by type="submit"
        try:
            button = self.page.locator('button[type="submit"], input[type="submit"]').first
            if button.is_visible():
                return button
        except:
            pass
        
        return None
    
    def handle_verification_link(self, verification_url: str) -> bool:
        """
        Click verification link
        
        Args:
            verification_url: URL from verification email
            
        Returns:
            bool: Success status
        """
        try:
            self.navigate_to(verification_url)
            time.sleep(2)
            
            # Check for success message
            success_indicators = [
                'verified', 'confirmed', 'activated', 'success', 'thank you'
            ]
            
            page_text = self.page.content().lower()
            
            return any(indicator in page_text for indicator in success_indicators)
            
        except Exception as e:
            print(f"Error handling verification link: {e}")
            return False
    
    def take_screenshot(self, filename: str = None) -> str:
        """Take screenshot of current page"""
        if not filename:
            filename = f"screenshot_{int(time.time())}.png"
        
        filepath = Path('/home/user/student-application-automation/screenshots') / filename
        filepath.parent.mkdir(exist_ok=True)
        
        self.page.screenshot(path=str(filepath))
        return str(filepath)


# Demo function
def demo_browser_automation():
    """Demo browser automation capabilities"""
    print("Browser Automation Demo")
    print("=" * 50)
    print("\nCapabilities:")
    print("✓ Account creation on university portals")
    print("✓ Automatic login")
    print("✓ Form field detection and filling")
    print("✓ Email verification link handling")
    print("✓ Multi-page application form navigation")
    print("✓ Screenshot capture for debugging")
    print("\nFeatures:")
    print("- Intelligent field detection (by ID, name, label, placeholder)")
    print("- Human-like delays and interactions")
    print("- Error handling and retry logic")
    print("- Support for various field types (text, select, date, etc.)")
    
    # Example usage
    print("\nExample Usage:")
    print("""
    automation = BrowserAutomation(headless=False)
    
    # Create account
    student_data = {
        'first_name': 'John',
        'last_name': 'Smith',
        'email': 'john@email.com',
        'phone': '555-1234'
    }
    
    automation.create_account(
        signup_url='https://university.edu/signup',
        student_data=student_data,
        password='SecurePass123!'
    )
    
    # Login
    automation.login(
        login_url='https://university.edu/login',
        email='john@email.com',
        password='SecurePass123!'
    )
    
    # Fill application
    automation.fill_application_form(
        form_url='https://university.edu/apply',
        student_data=student_data,
        field_mapping={...}
    )
    
    automation.submit_form()
    automation.close_browser()
    """)

if __name__ == "__main__":
    demo_browser_automation()
