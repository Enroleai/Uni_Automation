# Student Application Automation - Railway Deployment

API service for automated university application submissions.

## Quick Deploy to Railway

[![Deploy on Railway](https://railway.app/button.svg)](https://railway.app/new/template?template=https://github.com/yourusername/student-app-automation)

## API Endpoints

### Health Check
```
GET /health
```

### Extract Student Data
```
POST /api/extract
Content-Type: application/json

{
  "text": "Student information text..."
}
```

### Store Student
```
POST /api/store
Content-Type: application/json

{
  "first_name": "John",
  "last_name": "Smith",
  "email": "john@email.com",
  "phone": "(555) 123-4567",
  "gpa": "3.85",
  "sat_score": 1450
}
```

### Submit Application
```
POST /api/submit
Content-Type: application/json

{
  "student_id": 1,
  "university_config": {
    "name": "Sample University",
    "signup_url": "https://...",
    "login_url": "https://...",
    "application_url": "https://...",
    "field_mapping": {...}
  },
  "password": "SecurePass123!"
}
```

### Get Application Status
```
GET /api/status/<student_id>
```

### Batch Submit
```
POST /api/batch
Content-Type: application/json

{
  "student_ids": [1, 2, 3],
  "university_configs": [{...}, {...}],
  "password": "SecurePass123!"
}
```

## Environment Variables

Required:
- `EMAIL_ADDRESS` - Email for verification
- `EMAIL_PASSWORD` - Email app password
- `DATABASE_URL` - Database connection (auto-set by Railway for PostgreSQL)

Optional:
- `SECRET_KEY` - Flask secret key
- `API_KEY` - For API authentication
- `ALLOWED_ORIGINS` - CORS origins
- `BROWSERLESS_API_KEY` - For remote browser service

## Local Development

```bash
# Install dependencies
pip install -r requirements.txt
playwright install chromium

# Set environment variables
cp .env.example .env
# Edit .env with your credentials

# Run locally
python railway_app.py
```

## Documentation

See `RAILWAY_DEPLOYMENT.md` for complete deployment guide.

## License

MIT
