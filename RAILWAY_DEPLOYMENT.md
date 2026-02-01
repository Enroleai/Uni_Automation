# Deploying Student Application Automation to Railway

Complete guide for deploying the automation system to Railway.app

## 📋 Prerequisites

1. **Railway Account**: Sign up at https://railway.app
2. **GitHub Account**: To connect your repository
3. **Project Files**: The complete automation system

---

## 🚀 Deployment Steps

### Step 1: Prepare Your Project

#### 1.1 Create a Web API Wrapper

Since Railway requires a web service, we'll create an API wrapper around the automation system.

Create `railway_app.py` (main entry point):

```python
from flask import Flask, request, jsonify
from orchestrator import ApplicationOrchestrator
from models import init_db, Student
import os
import json
from datetime import date

app = Flask(__name__)

# Initialize database
db_path = os.environ.get('DATABASE_URL', 'student_data.db')
engine, SessionMaker = init_db(db_path)

@app.route('/')
def home():
    return jsonify({
        'status': 'running',
        'service': 'Student Application Automation API',
        'version': '1.0',
        'endpoints': {
            'health': '/health',
            'extract': '/api/extract (POST)',
            'store': '/api/store (POST)',
            'submit': '/api/submit (POST)',
            'status': '/api/status/<student_id> (GET)'
        }
    })

@app.route('/health')
def health():
    return jsonify({'status': 'healthy', 'database': 'connected'})

@app.route('/api/extract', methods=['POST'])
def extract_data():
    """Extract student data from text"""
    from document_extractor import DocumentExtractor
    
    try:
        data = request.json
        text = data.get('text', '')
        
        extractor = DocumentExtractor()
        extracted = extractor.extract_structured_data(text)
        
        return jsonify({
            'success': True,
            'data': extracted
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/store', methods=['POST'])
def store_student():
    """Store student data in database"""
    try:
        data = request.json
        
        session = SessionMaker()
        student = Student(**data)
        session.add(student)
        session.commit()
        student_id = student.id
        session.close()
        
        return jsonify({
            'success': True,
            'student_id': student_id,
            'message': 'Student data stored successfully'
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/submit', methods=['POST'])
def submit_application():
    """Submit application to university"""
    try:
        data = request.json
        student_id = data.get('student_id')
        university_config = data.get('university_config')
        password = data.get('password')
        
        email_config = {
            'address': os.environ.get('EMAIL_ADDRESS'),
            'password': os.environ.get('EMAIL_PASSWORD')
        }
        
        orchestrator = ApplicationOrchestrator(email_config=email_config)
        
        success = orchestrator.submit_application(
            student_id=student_id,
            university_config=university_config,
            password=password
        )
        
        return jsonify({
            'success': success,
            'message': 'Application submitted' if success else 'Application failed'
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/status/<int:student_id>', methods=['GET'])
def get_status(student_id):
    """Get application status"""
    try:
        orchestrator = ApplicationOrchestrator()
        status = orchestrator.get_application_status(student_id)
        
        return jsonify({
            'success': True,
            'data': status
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port)
```

#### 1.2 Update requirements.txt

Make sure all dependencies are listed:

```txt
flask==3.0.0
playwright==1.40.0
pypdf2==3.0.1
pillow==10.1.0
pytesseract==0.3.10
python-dotenv==1.0.0
sqlalchemy==2.0.23
imap-tools==1.5.0
beautifulsoup4==4.12.2
requests==2.31.0
pandas==2.1.3
pydantic[email]==2.5.0
gunicorn==21.2.0
psycopg2-binary==2.9.9
```

#### 1.3 Create Procfile

Railway uses this to know how to start your app:

```
web: gunicorn railway_app:app
```

#### 1.4 Create railway.json

Railway configuration file:

```json
{
  "$schema": "https://railway.app/railway.schema.json",
  "build": {
    "builder": "NIXPACKS",
    "buildCommand": "pip install -r requirements.txt && playwright install chromium"
  },
  "deploy": {
    "startCommand": "gunicorn railway_app:app --bind 0.0.0.0:$PORT --workers 2 --timeout 120",
    "restartPolicyType": "ON_FAILURE",
    "restartPolicyMaxRetries": 10
  }
}
```

#### 1.5 Create .env.example

Template for environment variables:

```bash
# Email Configuration
EMAIL_ADDRESS=your-email@gmail.com
EMAIL_PASSWORD=your-app-password

# Database (Railway will provide this)
DATABASE_URL=sqlite:///student_data.db

# Flask Configuration
FLASK_ENV=production
SECRET_KEY=your-secret-key-here

# Optional: For production security
ALLOWED_ORIGINS=https://yourdomain.com
API_KEY=your-api-key-for-authentication
```

#### 1.6 Create nixpacks.toml

For better Playwright support on Railway:

```toml
[phases.setup]
nixPkgs = ["...", "chromium", "nss", "freetype", "harfbuzz", "ca-certificates", "ttf-freefont"]

[phases.install]
cmds = [
    "pip install -r requirements.txt",
    "playwright install chromium",
    "playwright install-deps"
]

[start]
cmd = "gunicorn railway_app:app --bind 0.0.0.0:$PORT --workers 2 --timeout 120"
```

---

### Step 2: Push to GitHub

```bash
# Initialize git repository
git init

# Create .gitignore
cat > .gitignore << EOF
__pycache__/
*.pyc
*.db
.env
.venv/
venv/
screenshots/
*.log
.DS_Store
EOF

# Add all files
git add .

# Commit
git commit -m "Initial commit - Student Application Automation"

# Create GitHub repository (on github.com)
# Then push:
git remote add origin https://github.com/yourusername/student-app-automation.git
git branch -M main
git push -u origin main
```

---

### Step 3: Deploy on Railway

#### 3.1 Create New Project

1. Go to https://railway.app
2. Click "New Project"
3. Select "Deploy from GitHub repo"
4. Choose your repository

#### 3.2 Configure Environment Variables

In Railway dashboard:

1. Go to your project
2. Click on "Variables" tab
3. Add the following variables:

```
EMAIL_ADDRESS=your-email@gmail.com
EMAIL_PASSWORD=your-app-password
FLASK_ENV=production
SECRET_KEY=generate-a-random-secret-key
```

To generate a secret key:
```python
import secrets
print(secrets.token_hex(32))
```

#### 3.3 Add PostgreSQL Database (Optional)

For production, use PostgreSQL instead of SQLite:

1. In Railway dashboard, click "New"
2. Select "Database" → "PostgreSQL"
3. Railway will automatically set `DATABASE_URL` environment variable
4. Update your code to use PostgreSQL:

```python
# In models.py, change init_db function:
def init_db(db_url: str = None):
    if db_url is None:
        db_url = os.environ.get('DATABASE_URL', 'sqlite:///student_data.db')
    
    # Railway PostgreSQL URLs start with 'postgres://', need to change to 'postgresql://'
    if db_url.startswith('postgres://'):
        db_url = db_url.replace('postgres://', 'postgresql://', 1)
    
    engine = create_engine(db_url)
    Base.metadata.create_all(engine)
    return engine, sessionmaker(bind=engine)
```

#### 3.4 Configure Custom Domain (Optional)

1. In Railway dashboard, go to "Settings"
2. Under "Domains", click "Generate Domain"
3. Or add your custom domain

---

### Step 4: Handle Playwright in Railway

#### Option A: Use Playwright in Docker (Recommended)

Create `Dockerfile`:

```dockerfile
FROM python:3.11-slim

# Install system dependencies for Playwright
RUN apt-get update && apt-get install -y \
    wget \
    gnupg \
    ca-certificates \
    fonts-liberation \
    libasound2 \
    libatk-bridge2.0-0 \
    libatk1.0-0 \
    libc6 \
    libcairo2 \
    libcups2 \
    libdbus-1-3 \
    libexpat1 \
    libfontconfig1 \
    libgbm1 \
    libgcc1 \
    libglib2.0-0 \
    libgtk-3-0 \
    libnspr4 \
    libnss3 \
    libpango-1.0-0 \
    libpangocairo-1.0-0 \
    libstdc++6 \
    libx11-6 \
    libx11-xcb1 \
    libxcb1 \
    libxcomposite1 \
    libxcursor1 \
    libxdamage1 \
    libxext6 \
    libxfixes3 \
    libxi6 \
    libxrandr2 \
    libxrender1 \
    libxss1 \
    libxtst6 \
    lsb-release \
    xdg-utils \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy requirements
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Install Playwright browsers
RUN playwright install chromium
RUN playwright install-deps

# Copy application code
COPY . .

# Expose port
EXPOSE 8080

# Start command
CMD ["gunicorn", "railway_app:app", "--bind", "0.0.0.0:8080", "--workers", "2", "--timeout", "120"]
```

Then update `railway.json`:

```json
{
  "$schema": "https://railway.app/railway.schema.json",
  "build": {
    "builder": "DOCKERFILE",
    "dockerfilePath": "Dockerfile"
  },
  "deploy": {
    "restartPolicyType": "ON_FAILURE",
    "restartPolicyMaxRetries": 10
  }
}
```

#### Option B: Use Remote Browser (Browserless)

If Playwright doesn't work on Railway, use a remote browser service:

```python
# Install browserless SDK
# pip install browserless

from playwright.sync_api import sync_playwright

def get_browser():
    browserless_api = os.environ.get('BROWSERLESS_API_KEY')
    
    if browserless_api:
        # Use Browserless cloud
        playwright = sync_playwright().start()
        browser = playwright.chromium.connect(
            f'wss://chrome.browserless.io?token={browserless_api}'
        )
    else:
        # Use local browser
        playwright = sync_playwright().start()
        browser = playwright.chromium.launch()
    
    return browser
```

Sign up for Browserless: https://browserless.io (free tier available)

---

### Step 5: Test Your Deployment

#### 5.1 Get Your Railway URL

After deployment, Railway will provide a URL like:
`https://student-app-automation-production.up.railway.app`

#### 5.2 Test Endpoints

```bash
# Health check
curl https://your-app.up.railway.app/health

# Test extraction
curl -X POST https://your-app.up.railway.app/api/extract \
  -H "Content-Type: application/json" \
  -d '{"text": "Name: John Smith\nEmail: john@email.com\nGPA: 3.8"}'

# Test store
curl -X POST https://your-app.up.railway.app/api/store \
  -H "Content-Type: application/json" \
  -d '{
    "first_name": "Jane",
    "last_name": "Doe",
    "email": "jane@email.com",
    "gpa": "3.9"
  }'
```

---

## 🔒 Security Considerations

### 1. Add API Authentication

```python
from functools import wraps

def require_api_key(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        api_key = request.headers.get('X-API-Key')
        if api_key != os.environ.get('API_KEY'):
            return jsonify({'error': 'Unauthorized'}), 401
        return f(*args, **kwargs)
    return decorated_function

@app.route('/api/submit', methods=['POST'])
@require_api_key
def submit_application():
    # ... your code
```

### 2. Add Rate Limiting

```bash
pip install flask-limiter
```

```python
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

limiter = Limiter(
    app=app,
    key_func=get_remote_address,
    default_limits=["100 per hour"]
)

@app.route('/api/submit', methods=['POST'])
@limiter.limit("10 per hour")
def submit_application():
    # ... your code
```

### 3. Enable CORS (if needed)

```bash
pip install flask-cors
```

```python
from flask_cors import CORS

CORS(app, origins=os.environ.get('ALLOWED_ORIGINS', '*').split(','))
```

---

## 📊 Monitoring & Logs

### View Logs in Railway

1. Go to your project in Railway dashboard
2. Click on "Deployments"
3. Click on latest deployment
4. View logs in real-time

### Add Logging

```python
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

@app.route('/api/submit', methods=['POST'])
def submit_application():
    logger.info(f"Received submission request for student {student_id}")
    # ... your code
    logger.info(f"Submission completed with status: {success}")
```

---

## 💰 Cost Estimation

Railway Pricing:
- **Free Tier**: $5 credit/month (good for testing)
- **Hobby Plan**: $5/month + usage
- **Pro Plan**: $20/month + usage

Additional costs:
- PostgreSQL database: Included in Railway
- Browserless (if needed): $29/month (or use free tier)

---

## 🔧 Troubleshooting

### Issue 1: Playwright Not Working

**Solution**: Use Docker deployment or Browserless remote browser

### Issue 2: Database Connection Errors

**Solution**: Check DATABASE_URL environment variable

```python
# Debug database URL
print(f"Database URL: {os.environ.get('DATABASE_URL', 'Not set')}")
```

### Issue 3: Timeout Errors

**Solution**: Increase gunicorn timeout

```
gunicorn railway_app:app --timeout 300
```

### Issue 4: Memory Issues

**Solution**: Optimize worker count and memory usage

```json
{
  "deploy": {
    "startCommand": "gunicorn railway_app:app --workers 1 --timeout 300 --max-requests 100"
  }
}
```

---

## 🎯 Production Checklist

Before going live:

- [ ] Environment variables configured
- [ ] PostgreSQL database connected
- [ ] API authentication enabled
- [ ] Rate limiting configured
- [ ] CORS configured correctly
- [ ] Logging enabled
- [ ] Error handling tested
- [ ] Custom domain configured (optional)
- [ ] Monitoring setup
- [ ] Backup strategy in place

---

## 📚 Additional Resources

- Railway Documentation: https://docs.railway.app
- Playwright Documentation: https://playwright.dev
- Flask Documentation: https://flask.palletsprojects.com
- Gunicorn Documentation: https://docs.gunicorn.org

---

## 🆘 Support

If you encounter issues:
1. Check Railway logs
2. Review environment variables
3. Test locally first with `python railway_app.py`
4. Check Railway status: https://status.railway.app

---

**Next Step**: Run through these steps and let me know if you need help with any specific part!
