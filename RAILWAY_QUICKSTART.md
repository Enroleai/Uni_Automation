# Railway Deployment - Quick Reference

## 🚀 3-Minute Quick Deploy

### Step 1: Push to GitHub (2 minutes)

```bash
# In your project directory
git init
git add .
git commit -m "Initial commit"

# Create repo on github.com, then:
git remote add origin https://github.com/YOUR_USERNAME/REPO_NAME.git
git branch -M main
git push -u origin main
```

### Step 2: Deploy on Railway (1 minute)

1. Go to https://railway.app
2. Click "New Project"
3. Select "Deploy from GitHub repo"
4. Choose your repository
5. Railway will auto-detect and deploy!

### Step 3: Set Environment Variables

In Railway dashboard → Variables tab:

```
EMAIL_ADDRESS=your-email@gmail.com
EMAIL_PASSWORD=your-app-password
SECRET_KEY=<generate-random-string>
FLASK_ENV=production
```

**Done!** Your API will be live at: `https://your-app.up.railway.app`

---

## 📝 Generate SECRET_KEY

```python
import secrets
print(secrets.token_hex(32))
```

Or:

```bash
python3 -c "import secrets; print(secrets.token_hex(32))"
```

---

## 🔧 Add PostgreSQL Database (Optional)

1. In Railway dashboard, click "New"
2. Select "Database" → "PostgreSQL"
3. Railway automatically sets `DATABASE_URL`
4. Your app will use PostgreSQL instead of SQLite

---

## 🧪 Test Your Deployment

```bash
# Health check
curl https://your-app.up.railway.app/health

# Extract data
curl -X POST https://your-app.up.railway.app/api/extract \
  -H "Content-Type: application/json" \
  -d '{"text": "Name: John Smith\nEmail: john@email.com\nGPA: 3.8"}'

# Store student
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

## 🐛 Troubleshooting

### Issue: Build fails

**Solution**: Check Railway build logs. Usually missing dependencies.

```bash
# Test locally first:
pip install -r requirements.txt
python railway_app.py
```

### Issue: Playwright not working

**Solution**: Use Docker deployment method

In Railway dashboard:
- Settings → Builder → Select "Dockerfile"

### Issue: Database errors

**Solution**: Check DATABASE_URL in environment variables

```python
# Add debug logging in railway_app.py:
print(f"Database URL: {os.environ.get('DATABASE_URL')}")
```

### Issue: Email verification fails

**Solution**: Verify EMAIL_ADDRESS and EMAIL_PASSWORD are set correctly

For Gmail, use App Password: https://myaccount.google.com/apppasswords

---

## 📊 Monitor Your App

### View Logs
1. Railway dashboard → Your project
2. Click on "Deployments"
3. Select latest deployment
4. View real-time logs

### Set up Metrics
Railway automatically tracks:
- CPU usage
- Memory usage
- Request count
- Response time

---

## 💰 Cost Estimation

**Railway Pricing:**
- Free tier: $5 credit/month
- Hobby: $5/month + $0.000231/GB-hr
- Pro: $20/month + lower rates

**Typical costs for this app:**
- Low traffic (< 100 requests/day): ~$0-5/month
- Medium traffic (< 1000 requests/day): ~$5-15/month
- High traffic (< 10k requests/day): ~$15-30/month

---

## 🔐 Production Security Checklist

Before going live:

- [ ] Set strong SECRET_KEY
- [ ] Enable HTTPS (Railway does this automatically)
- [ ] Add API authentication
- [ ] Set up rate limiting
- [ ] Configure CORS properly
- [ ] Use PostgreSQL (not SQLite)
- [ ] Enable error monitoring
- [ ] Set up backups
- [ ] Review logs regularly
- [ ] Use environment variables for all secrets

---

## 📞 Get Help

- **Railway Discord**: https://discord.gg/railway
- **Railway Docs**: https://docs.railway.app
- **GitHub Issues**: Create issue in your repo

---

## 🎯 What's Deployed

When you deploy to Railway, you get:

✅ **API Service** running on Railway
✅ **Database** (SQLite or PostgreSQL)
✅ **Automatic HTTPS** with Railway domain
✅ **Auto-scaling** based on traffic
✅ **Monitoring** and logs built-in
✅ **CI/CD** - auto-deploys on git push

---

## 🔄 Update Your Deployment

```bash
# Make changes to your code
git add .
git commit -m "Update: description of changes"
git push

# Railway automatically redeploys!
```

---

## ⚡ Performance Tips

1. **Use PostgreSQL** instead of SQLite for better performance
2. **Optimize workers**: Adjust in Procfile based on traffic
3. **Add caching**: Use Redis for frequently accessed data
4. **Monitor metrics**: Check Railway dashboard regularly
5. **Set timeouts**: Adjust gunicorn timeout for long operations

---

**That's it! You're ready to deploy to Railway! 🚀**
