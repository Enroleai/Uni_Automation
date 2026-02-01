from flask import Flask, request, jsonify
from orchestrator import ApplicationOrchestrator
from models import init_db, Student
import os
import json
from datetime import date, datetime

app = Flask(__name__)

# Initialize database
db_url = os.environ.get('DATABASE_URL')
if db_url and db_url.startswith('postgres://'):
    db_url = db_url.replace('postgres://', 'postgresql://', 1)

engine, SessionMaker = init_db(db_url or 'student_data.db')

@app.route('/')
def home():
    return jsonify({
        'status': 'running',
        'service': 'Student Application Automation API',
        'version': '1.0.0',
        'endpoints': {
            'health': 'GET /health',
            'extract': 'POST /api/extract',
            'store': 'POST /api/store',
            'submit': 'POST /api/submit',
            'status': 'GET /api/status/<student_id>',
            'batch': 'POST /api/batch'
        },
        'documentation': 'See RAILWAY_DEPLOYMENT.md for API details'
    })

@app.route('/health')
def health():
    try:
        # Test database connection
        session = SessionMaker()
        session.execute('SELECT 1')
        session.close()
        db_status = 'connected'
    except Exception as e:
        db_status = f'error: {str(e)}'
    
    return jsonify({
        'status': 'healthy',
        'database': db_status,
        'timestamp': datetime.utcnow().isoformat()
    })

@app.route('/api/extract', methods=['POST'])
def extract_data():
    """
    Extract student data from text
    
    Request body:
    {
        "text": "Student information text..."
    }
    """
    from document_extractor import DocumentExtractor
    
    try:
        data = request.json
        if not data or 'text' not in data:
            return jsonify({
                'success': False,
                'error': 'Missing "text" field in request body'
            }), 400
        
        text = data.get('text', '')
        
        extractor = DocumentExtractor()
        extracted = extractor.extract_structured_data(text)
        
        return jsonify({
            'success': True,
            'data': extracted,
            'fields_extracted': len(extracted)
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/store', methods=['POST'])
def store_student():
    """
    Store student data in database
    
    Request body:
    {
        "first_name": "John",
        "last_name": "Smith",
        "email": "john@email.com",
        ...
    }
    """
    try:
        data = request.json
        if not data:
            return jsonify({
                'success': False,
                'error': 'Empty request body'
            }), 400
        
        # Validate required fields
        required_fields = ['first_name', 'last_name', 'email']
        missing = [f for f in required_fields if f not in data]
        if missing:
            return jsonify({
                'success': False,
                'error': f'Missing required fields: {", ".join(missing)}'
            }), 400
        
        session = SessionMaker()
        try:
            student = Student(**data)
            session.add(student)
            session.commit()
            student_id = student.id
            
            return jsonify({
                'success': True,
                'student_id': student_id,
                'message': 'Student data stored successfully',
                'data': student.to_dict()
            })
        finally:
            session.close()
            
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/submit', methods=['POST'])
def submit_application():
    """
    Submit application to university
    
    Request body:
    {
        "student_id": 1,
        "university_config": {...},
        "password": "SecurePass123!"
    }
    """
    try:
        data = request.json
        if not data:
            return jsonify({
                'success': False,
                'error': 'Empty request body'
            }), 400
        
        student_id = data.get('student_id')
        university_config = data.get('university_config')
        password = data.get('password')
        
        if not all([student_id, university_config, password]):
            return jsonify({
                'success': False,
                'error': 'Missing required fields: student_id, university_config, password'
            }), 400
        
        # Get email configuration from environment
        email_config = {
            'address': os.environ.get('EMAIL_ADDRESS'),
            'password': os.environ.get('EMAIL_PASSWORD')
        }
        
        if not all(email_config.values()):
            return jsonify({
                'success': False,
                'error': 'Email configuration not set in environment variables'
            }), 500
        
        orchestrator = ApplicationOrchestrator(email_config=email_config)
        
        success = orchestrator.submit_application(
            student_id=student_id,
            university_config=university_config,
            password=password
        )
        
        return jsonify({
            'success': success,
            'message': 'Application submitted successfully' if success else 'Application submission failed',
            'student_id': student_id
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/status/<int:student_id>', methods=['GET'])
def get_status(student_id):
    """Get application status for a student"""
    try:
        orchestrator = ApplicationOrchestrator()
        status = orchestrator.get_application_status(student_id)
        
        return jsonify({
            'success': True,
            'student_id': student_id,
            'applications': status
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/batch', methods=['POST'])
def batch_submit():
    """
    Batch submit applications
    
    Request body:
    {
        "student_ids": [1, 2, 3],
        "university_configs": [{...}, {...}],
        "password": "SecurePass123!"
    }
    """
    try:
        data = request.json
        if not data:
            return jsonify({
                'success': False,
                'error': 'Empty request body'
            }), 400
        
        student_ids = data.get('student_ids', [])
        university_configs = data.get('university_configs', [])
        password = data.get('password')
        
        if not all([student_ids, university_configs, password]):
            return jsonify({
                'success': False,
                'error': 'Missing required fields'
            }), 400
        
        email_config = {
            'address': os.environ.get('EMAIL_ADDRESS'),
            'password': os.environ.get('EMAIL_PASSWORD')
        }
        
        orchestrator = ApplicationOrchestrator(email_config=email_config)
        
        results = orchestrator.batch_submit_applications(
            student_ids=student_ids,
            university_configs=university_configs,
            password=password
        )
        
        return jsonify({
            'success': True,
            'results': results
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.errorhandler(404)
def not_found(error):
    return jsonify({
        'success': False,
        'error': 'Endpoint not found',
        'available_endpoints': [
            'GET /',
            'GET /health',
            'POST /api/extract',
            'POST /api/store',
            'POST /api/submit',
            'GET /api/status/<student_id>',
            'POST /api/batch'
        ]
    }), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({
        'success': False,
        'error': 'Internal server error',
        'message': str(error)
    }), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8080))
    debug = os.environ.get('FLASK_ENV') != 'production'
    
    print("=" * 70)
    print("Student Application Automation API")
    print("=" * 70)
    print(f"Port: {port}")
    print(f"Debug: {debug}")
    print(f"Database: {db_url or 'SQLite (student_data.db)'}")
    print("=" * 70)
    
    app.run(host='0.0.0.0', port=port, debug=debug)
