#!/bin/bash

# Railway Deployment Quick Start Script
# This script helps you prepare and deploy to Railway

echo "╔════════════════════════════════════════════════════════════════╗"
echo "║    Student Application Automation - Railway Deployment        ║"
echo "╚════════════════════════════════════════════════════════════════╝"
echo ""

# Step 1: Check if git is installed
echo "Step 1: Checking requirements..."
if ! command -v git &> /dev/null; then
    echo "❌ Git is not installed. Please install git first."
    exit 1
fi
echo "✅ Git is installed"

# Step 2: Initialize git repository
echo ""
echo "Step 2: Initializing Git repository..."
if [ ! -d ".git" ]; then
    git init
    echo "✅ Git repository initialized"
else
    echo "✅ Git repository already exists"
fi

# Step 3: Create .gitignore if not exists
if [ ! -f ".gitignore" ]; then
    echo "Creating .gitignore..."
    cat > .gitignore << 'EOF'
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
    echo "✅ .gitignore created"
fi

# Step 4: Generate SECRET_KEY
echo ""
echo "Step 3: Generating SECRET_KEY..."
SECRET_KEY=$(python3 -c "import secrets; print(secrets.token_hex(32))")
echo "✅ SECRET_KEY generated: $SECRET_KEY"
echo "   (Save this for Railway environment variables)"

# Step 5: Check required files
echo ""
echo "Step 4: Checking required files..."
REQUIRED_FILES=(
    "railway_app.py"
    "Procfile"
    "requirements.txt"
    "railway.json"
    "Dockerfile"
    "models.py"
    "orchestrator.py"
    "document_extractor.py"
    "email_handler.py"
    "browser_automation.py"
)

ALL_PRESENT=true
for file in "${REQUIRED_FILES[@]}"; do
    if [ -f "$file" ]; then
        echo "  ✅ $file"
    else
        echo "  ❌ $file (missing)"
        ALL_PRESENT=false
    fi
done

if [ "$ALL_PRESENT" = false ]; then
    echo ""
    echo "❌ Some required files are missing. Please ensure all files are present."
    exit 1
fi

# Step 6: Add files to git
echo ""
echo "Step 5: Adding files to git..."
git add .
echo "✅ Files added"

# Step 7: Commit
echo ""
echo "Step 6: Creating git commit..."
if git diff-index --quiet HEAD -- 2>/dev/null; then
    echo "✅ No changes to commit"
else
    git commit -m "Initial commit - Student Application Automation"
    echo "✅ Changes committed"
fi

# Step 8: Display next steps
echo ""
echo "╔════════════════════════════════════════════════════════════════╗"
echo "║                    NEXT STEPS                                  ║"
echo "╚════════════════════════════════════════════════════════════════╝"
echo ""
echo "✅ Repository prepared for Railway deployment!"
echo ""
echo "OPTION A: Deploy via GitHub"
echo "──────────────────────────────────────────────────────────────────"
echo "1. Create a new repository on GitHub"
echo "2. Run these commands:"
echo "   git remote add origin https://github.com/YOUR_USERNAME/REPO_NAME.git"
echo "   git branch -M main"
echo "   git push -u origin main"
echo ""
echo "3. Go to https://railway.app"
echo "4. Click 'New Project' → 'Deploy from GitHub repo'"
echo "5. Select your repository"
echo ""
echo "OPTION B: Deploy via Railway CLI"
echo "──────────────────────────────────────────────────────────────────"
echo "1. Install Railway CLI:"
echo "   npm install -g @railway/cli"
echo "   # or"
echo "   curl -fsSL https://railway.app/install.sh | sh"
echo ""
echo "2. Login to Railway:"
echo "   railway login"
echo ""
echo "3. Initialize and deploy:"
echo "   railway init"
echo "   railway up"
echo ""
echo "ENVIRONMENT VARIABLES TO SET IN RAILWAY:"
echo "──────────────────────────────────────────────────────────────────"
echo "EMAIL_ADDRESS=your-email@gmail.com"
echo "EMAIL_PASSWORD=your-app-password"
echo "SECRET_KEY=$SECRET_KEY"
echo "FLASK_ENV=production"
echo ""
echo "OPTIONAL (for PostgreSQL):"
echo "Add PostgreSQL database from Railway dashboard"
echo "(DATABASE_URL will be set automatically)"
echo ""
echo "OPTIONAL (for API security):"
echo "API_KEY=your-api-key"
echo "ALLOWED_ORIGINS=https://yourdomain.com"
echo ""
echo "╔════════════════════════════════════════════════════════════════╗"
echo "║                    USEFUL LINKS                                ║"
echo "╚════════════════════════════════════════════════════════════════╝"
echo ""
echo "📚 Railway Dashboard: https://railway.app/dashboard"
echo "📖 Railway Docs: https://docs.railway.app"
echo "📝 Full Guide: See RAILWAY_DEPLOYMENT.md"
echo ""
echo "🎉 Ready to deploy!"
echo ""
