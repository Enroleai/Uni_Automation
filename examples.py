"""
Example usage script demonstrating the complete workflow
"""
from orchestrator import ApplicationOrchestrator
import json

def example_single_application():
    """Example: Submit single application"""
    
    print("="*70)
    print("EXAMPLE 1: Single Application Submission")
    print("="*70)
    
    # Step 1: Initialize orchestrator with email config
    orchestrator = ApplicationOrchestrator(
        email_config={
            'address': 'your-email@gmail.com',  # Replace with your email
            'password': 'your-app-password'      # Replace with app password
        }
    )
    
    # Step 2: Extract student data from document
    print("\n📄 Extracting student data...")
    student_id = orchestrator.extract_and_store_student(
        'sample_student_profile.pdf'  # Replace with actual document path
    )
    
    if not student_id:
        print("✗ Failed to extract student data")
        return
    
    print(f"✓ Student data extracted and stored with ID: {student_id}")
    
    # Step 3: Configure university
    university_config = {
        'name': 'Demo University',
        'url': 'https://apply.demouniversity.edu',
        'signup_url': 'https://apply.demouniversity.edu/signup',
        'login_url': 'https://apply.demouniversity.edu/login',
        'application_url': 'https://apply.demouniversity.edu/application',
        'email_domain': 'demouniversity.edu',
        'requires_email_verification': True,
        
        # Signup form fields
        'signup_field_mapping': {
            'first_name': '#firstName',
            'last_name': '#lastName',
            'email': '#email',
        },
        
        # Application form fields
        'field_mapping': {
            'first_name': '#app_firstName',
            'last_name': '#app_lastName',
            'middle_name': '#app_middleName',
            'email': '#app_email',
            'phone': '#app_phone',
            'date_of_birth': '#app_dob',
            'gender': '#app_gender',
            'address_line1': '#app_address1',
            'address_line2': '#app_address2',
            'city': '#app_city',
            'state': '#app_state',
            'postal_code': '#app_zipCode',
            'country': '#app_country',
            'high_school_name': '#app_highSchool',
            'graduation_year': '#app_gradYear',
            'gpa': '#app_gpa',
            'sat_score': '#app_satScore',
            'intended_major': '#app_major',
            'extracurriculars': '#app_activities'
        }
    }
    
    # Step 4: Submit application
    print("\n🚀 Submitting application...")
    success = orchestrator.submit_application(
        student_id=student_id,
        university_config=university_config,
        password='SecurePassword123!'
    )
    
    # Step 5: Check status
    print("\n📊 Application Status:")
    status = orchestrator.get_application_status(student_id)
    print(json.dumps(status, indent=2))
    
    return success


def example_batch_applications():
    """Example: Batch submit applications"""
    
    print("\n" + "="*70)
    print("EXAMPLE 2: Batch Application Submission")
    print("="*70)
    
    # Initialize orchestrator
    orchestrator = ApplicationOrchestrator(
        email_config={
            'address': 'your-email@gmail.com',
            'password': 'your-app-password'
        }
    )
    
    # Extract data for multiple students
    student_ids = []
    documents = [
        'student1_profile.pdf',
        'student2_profile.pdf',
        'student3_profile.pdf'
    ]
    
    print("\n📄 Extracting student data...")
    for doc in documents:
        student_id = orchestrator.extract_and_store_student(doc)
        if student_id:
            student_ids.append(student_id)
            print(f"  ✓ Student {student_id} extracted")
    
    # Configure multiple universities
    universities = [
        {
            'name': 'University A',
            'url': 'https://universitya.edu',
            'signup_url': 'https://universitya.edu/signup',
            'login_url': 'https://universitya.edu/login',
            'application_url': 'https://universitya.edu/apply',
            'email_domain': 'universitya.edu',
            'requires_email_verification': True,
            'field_mapping': {
                # Add field mappings
            }
        },
        {
            'name': 'University B',
            'url': 'https://universityb.edu',
            'signup_url': 'https://universityb.edu/register',
            'login_url': 'https://universityb.edu/signin',
            'application_url': 'https://universityb.edu/application',
            'email_domain': 'universityb.edu',
            'requires_email_verification': False,
            'field_mapping': {
                # Add field mappings
            }
        }
    ]
    
    # Submit batch applications
    print("\n🚀 Submitting batch applications...")
    results = orchestrator.batch_submit_applications(
        student_ids=student_ids,
        university_configs=universities,
        password='SecurePassword123!'
    )
    
    # Print results
    print("\n📊 Batch Results:")
    print(f"  Total Applications: {results['total']}")
    print(f"  Successful: {results['successful']}")
    print(f"  Failed: {results['failed']}")
    print(f"  Success Rate: {results['successful']/results['total']*100:.1f}%")


def example_manual_student_entry():
    """Example: Manually enter student data (no document)"""
    
    print("\n" + "="*70)
    print("EXAMPLE 3: Manual Student Data Entry")
    print("="*70)
    
    from models import init_db, Student
    from datetime import date
    
    # Initialize database
    engine, SessionMaker = init_db()
    session = SessionMaker()
    
    # Create student record manually
    student = Student(
        first_name='Jane',
        middle_name='Marie',
        last_name='Doe',
        email='jane.doe@email.com',
        phone='(555) 987-6543',
        date_of_birth=date(2005, 3, 15),
        gender='Female',
        nationality='USA',
        address_line1='456 Oak Avenue',
        address_line2='Suite 200',
        city='Boston',
        state='MA',
        postal_code='02101',
        country='United States',
        high_school_name='Boston Latin School',
        graduation_year=2023,
        gpa='4.0',
        sat_score=1520,
        act_score=35,
        intended_major='Biology',
        extracurriculars='Science Olympiad Captain, Debate Team, Volunteer at Hospital'
    )
    
    session.add(student)
    session.commit()
    student_id = student.id
    
    print(f"✓ Student data entered with ID: {student_id}")
    
    session.close()
    
    # Now proceed with application submission
    orchestrator = ApplicationOrchestrator()
    
    # ... continue with university config and submission


def example_status_check():
    """Example: Check application status"""
    
    print("\n" + "="*70)
    print("EXAMPLE 4: Check Application Status")
    print("="*70)
    
    orchestrator = ApplicationOrchestrator()
    
    # Get all applications
    all_applications = orchestrator.get_application_status()
    
    print(f"\n📊 Total Applications: {len(all_applications)}")
    
    for app in all_applications:
        print(f"\n Student ID: {app['student_id']}")
        print(f"   University: {app['university']}")
        print(f"   Status: {app['status']}")
        print(f"   Account Created: {app['account_created']}")
        print(f"   Email Verified: {app['email_verified']}")
        print(f"   Submission Date: {app['submission_date']}")
        
        if app['last_error']:
            print(f"   ⚠ Error: {app['last_error']}")


def main():
    """Main demo function"""
    
    print("\n" + "="*70)
    print("STUDENT APPLICATION AUTOMATION - USAGE EXAMPLES")
    print("="*70)
    
    print("\n📚 Available Examples:")
    print("  1. Single Application Submission")
    print("  2. Batch Application Submission")
    print("  3. Manual Student Data Entry")
    print("  4. Check Application Status")
    
    print("\n⚠️  IMPORTANT: Before running these examples:")
    print("  1. Install dependencies: pip install -r requirements.txt")
    print("  2. Install Playwright: playwright install chromium")
    print("  3. Configure your email credentials")
    print("  4. Customize university configurations")
    print("  5. Test with dummy data first!")
    
    print("\n💡 To run a specific example:")
    print("  python examples.py")
    
    # Uncomment to run examples:
    # example_single_application()
    # example_batch_applications()
    # example_manual_student_entry()
    # example_status_check()


if __name__ == "__main__":
    main()
