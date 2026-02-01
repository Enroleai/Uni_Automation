"""
Email verification handler - Monitors email and extracts verification links
"""
import imaplib
import email
from email.header import decode_header
import time
import re
from typing import Optional, Dict
from datetime import datetime, timedelta

class EmailVerificationHandler:
    """Handle email verification for university applications"""
    
    def __init__(self, email_address: str, email_password: str, imap_server: str = None):
        """
        Initialize email handler
        
        Args:
            email_address: Email address to monitor
            email_password: Email password or app-specific password
            imap_server: IMAP server (auto-detected for common providers)
        """
        self.email_address = email_address
        self.email_password = email_password
        self.imap_server = imap_server or self._detect_imap_server(email_address)
        self.imap = None
    
    def _detect_imap_server(self, email_address: str) -> str:
        """Auto-detect IMAP server based on email domain"""
        domain = email_address.split('@')[1].lower()
        
        imap_servers = {
            'gmail.com': 'imap.gmail.com',
            'outlook.com': 'imap-mail.outlook.com',
            'hotmail.com': 'imap-mail.outlook.com',
            'yahoo.com': 'imap.mail.yahoo.com',
            'icloud.com': 'imap.mail.me.com',
        }
        
        return imap_servers.get(domain, f'imap.{domain}')
    
    def connect(self) -> bool:
        """Connect to email server"""
        try:
            self.imap = imaplib.IMAP4_SSL(self.imap_server)
            self.imap.login(self.email_address, self.email_password)
            return True
        except Exception as e:
            print(f"Failed to connect to email server: {e}")
            return False
    
    def disconnect(self):
        """Disconnect from email server"""
        if self.imap:
            try:
                self.imap.logout()
            except:
                pass
    
    def search_verification_email(self, 
                                  from_domain: str, 
                                  subject_keywords: list = None,
                                  since_minutes: int = 10) -> Optional[Dict]:
        """
        Search for verification email
        
        Args:
            from_domain: Domain to search emails from (e.g., 'university.edu')
            subject_keywords: Keywords to look for in subject
            since_minutes: Only check emails from last N minutes
            
        Returns:
            Dict with email details and verification link
        """
        if not self.imap:
            if not self.connect():
                return None
        
        try:
            self.imap.select('INBOX')
            
            # Calculate date for search
            since_date = (datetime.now() - timedelta(minutes=since_minutes)).strftime('%d-%b-%Y')
            
            # Search for emails
            search_criteria = f'(FROM "{from_domain}" SINCE {since_date})'
            status, messages = self.imap.search(None, search_criteria)
            
            if status != 'OK' or not messages[0]:
                return None
            
            # Get the most recent email
            email_ids = messages[0].split()
            latest_email_id = email_ids[-1]
            
            # Fetch the email
            status, msg_data = self.imap.fetch(latest_email_id, '(RFC822)')
            
            if status != 'OK':
                return None
            
            # Parse email
            email_body = msg_data[0][1]
            email_message = email.message_from_bytes(email_body)
            
            # Decode subject
            subject = decode_header(email_message['Subject'])[0][0]
            if isinstance(subject, bytes):
                subject = subject.decode()
            
            # Check subject keywords if provided
            if subject_keywords:
                if not any(keyword.lower() in subject.lower() for keyword in subject_keywords):
                    return None
            
            # Extract email body
            body = self._get_email_body(email_message)
            
            # Extract verification link
            verification_link = self._extract_verification_link(body)
            
            return {
                'subject': subject,
                'from': email_message['From'],
                'body': body,
                'verification_link': verification_link,
                'received_time': email_message['Date']
            }
            
        except Exception as e:
            print(f"Error searching emails: {e}")
            return None
    
    def _get_email_body(self, email_message) -> str:
        """Extract email body"""
        body = ""
        
        if email_message.is_multipart():
            for part in email_message.walk():
                content_type = part.get_content_type()
                if content_type == 'text/plain' or content_type == 'text/html':
                    try:
                        body = part.get_payload(decode=True).decode()
                        break
                    except:
                        pass
        else:
            try:
                body = email_message.get_payload(decode=True).decode()
            except:
                pass
        
        return body
    
    def _extract_verification_link(self, email_body: str) -> Optional[str]:
        """Extract verification/confirmation link from email body"""
        # Common patterns for verification links
        patterns = [
            r'https?://[^\s<>"]+(?:verify|confirm|activate|validation)[^\s<>"]*',
            r'https?://[^\s<>"]+[?&](?:token|code|key)=[^\s<>"&]+',
            r'https?://[^\s<>"]+/(?:verify|confirm|activate)/[^\s<>"]+',
        ]
        
        for pattern in patterns:
            matches = re.findall(pattern, email_body, re.IGNORECASE)
            if matches:
                # Return the first match, cleaned up
                link = matches[0].rstrip('.,;:)')
                return link
        
        return None
    
    def wait_for_verification_email(self,
                                   from_domain: str,
                                   subject_keywords: list = None,
                                   timeout_minutes: int = 5,
                                   check_interval: int = 10) -> Optional[Dict]:
        """
        Wait for verification email to arrive
        
        Args:
            from_domain: Domain to search emails from
            subject_keywords: Keywords to look for in subject
            timeout_minutes: Maximum time to wait
            check_interval: Seconds between checks
            
        Returns:
            Dict with email details and verification link
        """
        start_time = time.time()
        timeout_seconds = timeout_minutes * 60
        
        print(f"Waiting for verification email from {from_domain}...")
        
        while (time.time() - start_time) < timeout_seconds:
            result = self.search_verification_email(
                from_domain=from_domain,
                subject_keywords=subject_keywords,
                since_minutes=timeout_minutes
            )
            
            if result and result.get('verification_link'):
                print(f"✓ Verification email received!")
                return result
            
            time.sleep(check_interval)
        
        print("✗ Timeout waiting for verification email")
        return None


# Demo function
def demo_email_handler():
    """Demo email verification handling"""
    print("Email Verification Handler Demo")
    print("=" * 50)
    print("\nThis module can:")
    print("1. Monitor email inbox for verification emails")
    print("2. Extract verification links automatically")
    print("3. Handle multiple email providers (Gmail, Outlook, Yahoo, etc.)")
    print("\nConfiguration needed:")
    print("- Email address")
    print("- App-specific password (for Gmail: https://myaccount.google.com/apppasswords)")
    print("- IMAP access enabled")
    print("\nExample usage:")
    print("""
    handler = EmailVerificationHandler(
        email_address='student@email.com',
        email_password='app_specific_password'
    )
    
    # Wait for verification email
    email_data = handler.wait_for_verification_email(
        from_domain='university.edu',
        subject_keywords=['verify', 'confirm'],
        timeout_minutes=5
    )
    
    if email_data:
        verification_link = email_data['verification_link']
        # Use the link in browser automation
    """)

if __name__ == "__main__":
    demo_email_handler()
