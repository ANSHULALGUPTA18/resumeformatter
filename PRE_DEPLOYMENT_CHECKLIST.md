# ✅ Pre-Deployment Checklist - Resume Formatter

## 📋 Before You Start Deployment

### 1. Account Setup
- [ ] Azure account created (https://azure.microsoft.com/free/)
- [ ] Email verified
- [ ] Free $200 credits activated
- [ ] Credit card added (won't be charged on free tier)

### 2. Software Installation
- [ ] Azure CLI installed and working (`az --version`)
- [ ] Git installed (`git --version`)
- [ ] Node.js installed (`node --version`)
- [ ] Python 3.10 installed (`python --version`)
- [ ] PowerShell available (comes with Windows)

### 3. Project Files Ready
- [ ] Backend folder exists with all files
- [ ] Frontend folder exists with all files
- [ ] No errors when running locally
- [ ] All dependencies listed in requirements.txt
- [ ] All dependencies listed in package.json

---

## 🔧 Backend Preparation

### Files to Create/Update

#### 1. Update `Backend/requirements.txt`
```txt
Flask==3.0.0
Flask-CORS==4.0.0
python-docx==1.1.0
pdfplumber==0.10.3
PyPDF2==3.0.1
reportlab==4.0.7
Werkzeug==3.0.1
pypdf==3.17.0
Pillow==10.1.0
PyMuPDF==1.23.8
gunicorn==20.1.0
mammoth==1.6.0
```

**Checklist:**
- [ ] File exists at `Backend/requirements.txt`
- [ ] All packages listed
- [ ] No version conflicts

#### 2. Create `Backend/startup.sh`
```bash
#!/bin/bash
gunicorn --bind=0.0.0.0:8000 --timeout 600 --workers 2 app:app
```

**Checklist:**
- [ ] File created
- [ ] Correct syntax
- [ ] File saved with Unix line endings (LF, not CRLF)

#### 3. Create `Backend/.deployment`
```ini
[config]
SCM_DO_BUILD_DURING_DEPLOYMENT=true
```

**Checklist:**
- [ ] File created
- [ ] Correct syntax

#### 4. Update `Backend/app.py` CORS Settings
Find the CORS section and update:
```python
CORS(app, resources={
    r"/api/*": {
        "origins": [
            "http://localhost:3000",
            "https://*.azurestaticapps.net",
            "https://*.azurewebsites.net",
            "*"  # Remove this in production
        ]
    }
})
```

**Checklist:**
- [ ] CORS configured
- [ ] Allows Azure domains
- [ ] No syntax errors

#### 5. Remove Windows-Specific Dependencies
In `requirements.txt`, comment out or remove:
```txt
# docx2pdf  # Windows only - remove for Azure
# pywin32   # Windows only - remove for Azure
```

**Checklist:**
- [ ] Windows-only packages removed
- [ ] Code doesn't depend on these packages
- [ ] Alternative solutions implemented if needed

---

## 🎨 Frontend Preparation

### Files to Create/Update

#### 1. Create `frontend/.env.production`
```env
REACT_APP_API_URL=https://YOUR_BACKEND_APP_NAME.azurewebsites.net
```

**Note:** You'll update `YOUR_BACKEND_APP_NAME` after deploying backend

**Checklist:**
- [ ] File created
- [ ] Correct syntax
- [ ] Will update after backend deployment

#### 2. Create `frontend/staticwebapp.config.json`
```json
{
  "navigationFallback": {
    "rewrite": "/index.html"
  },
  "routes": [
    {
      "route": "/api/*",
      "allowedRoles": ["anonymous"]
    }
  ],
  "responseOverrides": {
    "404": {
      "rewrite": "/index.html"
    }
  }
}
```

**Checklist:**
- [ ] File created
- [ ] Valid JSON syntax
- [ ] No trailing commas

#### 3. Test Frontend Build
```powershell
cd frontend
npm install
npm run build
```

**Checklist:**
- [ ] `npm install` completes without errors
- [ ] `npm run build` completes successfully
- [ ] `build/` folder created
- [ ] No console errors

---

## 🗂️ File Structure Check

Your project should look like this:

```
resumeformatter.onlyoffice/
│
├── Backend/
│   ├── app.py                    ✅
│   ├── config.py                 ✅
│   ├── requirements.txt          ✅ (updated)
│   ├── startup.sh                ✅ (new)
│   ├── .deployment               ✅ (new)
│   ├── models/                   ✅
│   ├── routes/                   ✅
│   ├── utils/                    ✅
│   └── venv/                     ⚠️  (don't deploy this)
│
├── frontend/
│   ├── public/                   ✅
│   ├── src/                      ✅
│   ├── package.json              ✅
│   ├── .env.production           ✅ (new)
│   ├── staticwebapp.config.json  ✅ (new)
│   └── node_modules/             ⚠️  (don't deploy this)
│
└── Documentation files...
```

**Checklist:**
- [ ] All required files present
- [ ] New files created
- [ ] No missing dependencies

---

## 💻 Local Testing

### Test Backend Locally
```powershell
cd Backend
python app.py
```

**Visit:** http://localhost:5000/api/health

**Expected:** `{"status": "ok"}`

**Checklist:**
- [ ] Backend starts without errors
- [ ] Health endpoint works
- [ ] No import errors
- [ ] No missing files

### Test Frontend Locally
```powershell
cd frontend
npm start
```

**Visit:** http://localhost:3000

**Checklist:**
- [ ] Frontend loads
- [ ] No console errors
- [ ] Can navigate pages
- [ ] UI looks correct

---

## 🔐 Security Check

### Backend Security
- [ ] No hardcoded passwords
- [ ] No API keys in code
- [ ] No sensitive data in Git
- [ ] `.gitignore` includes:
  - `venv/`
  - `__pycache__/`
  - `*.pyc`
  - `.env`
  - `*.log`

### Frontend Security
- [ ] No API keys in code
- [ ] Environment variables used correctly
- [ ] `.gitignore` includes:
  - `node_modules/`
  - `build/`
  - `.env.local`

---

## 📊 Azure Prerequisites

### Azure Account
- [ ] Account created
- [ ] Logged in to portal (https://portal.azure.com)
- [ ] Free credits available
- [ ] Payment method added (for verification)

### Azure CLI
```powershell
# Test Azure CLI
az --version
az login
az account show
```

**Checklist:**
- [ ] Azure CLI installed
- [ ] Can login successfully
- [ ] Correct subscription selected

---

## 💰 Cost Planning

### Choose Your Tier

**FREE Tier (F1) - Testing Only**
- Cost: $0/month
- Limitations: 60 min CPU/day, 1GB storage
- Good for: Learning, testing
- [ ] I understand the limitations

**BASIC Tier (B1) - Recommended**
- Cost: $13.14/month
- Features: Always on, 1.75GB RAM
- Good for: Small business, real users
- [ ] I'm ready to pay $13/month

**Decision:**
- [ ] I will start with FREE tier
- [ ] I will start with BASIC tier

---

## 📝 Information to Collect

During deployment, you'll need to save these:

### Backend Information
- [ ] Resource Group Name: `_______________________`
- [ ] App Service Plan Name: `_______________________`
- [ ] Backend App Name: `_______________________`
- [ ] Backend URL: `https://________________.azurewebsites.net`

### Storage Information
- [ ] Storage Account Name: `_______________________`
- [ ] Connection String: `_______________________` (save securely)

### Frontend Information
- [ ] Static Web App Name: `_______________________`
- [ ] Frontend URL: `https://________________.azurestaticapps.net`

---

## 🎯 Deployment Strategy

### Recommended Order
1. ✅ Deploy Backend first
2. ✅ Test Backend health endpoint
3. ✅ Create Storage
4. ✅ Update Frontend with Backend URL
5. ✅ Deploy Frontend
6. ✅ Test end-to-end

**Checklist:**
- [ ] I understand the order
- [ ] I will follow step-by-step
- [ ] I will test after each step

---

## ⏰ Time Allocation

### Estimated Time Breakdown
- Setup & Prerequisites: 30 minutes
- Backend Deployment: 45 minutes
- Storage Setup: 15 minutes
- Frontend Deployment: 30 minutes
- Testing & Fixes: 30 minutes
- **Total: 2-3 hours**

**Checklist:**
- [ ] I have 2-3 hours available
- [ ] I won't rush through steps
- [ ] I will read error messages carefully

---

## 📚 Resources Ready

### Documentation
- [ ] AZURE_DEPLOYMENT_STEP_BY_STEP.md (main guide)
- [ ] AZURE_QUICK_COMMANDS.md (command reference)
- [ ] DEPLOYMENT_FLOWCHART.md (visual guide)
- [ ] This checklist

### Bookmarks
- [ ] Azure Portal: https://portal.azure.com
- [ ] Azure Docs: https://docs.microsoft.com/azure
- [ ] Azure Pricing: https://azure.microsoft.com/pricing/calculator/

---

## 🆘 Support Plan

### If Something Goes Wrong
1. **Check logs first**
   ```powershell
   az webapp log tail --name YOUR_APP_NAME --resource-group YOUR_RESOURCE_GROUP
   ```

2. **Common issues documented**
   - See AZURE_DEPLOYMENT_STEP_BY_STEP.md → Troubleshooting section

3. **Azure Support**
   - Free tier: Community forums only
   - Paid tier: 24/7 support

**Checklist:**
- [ ] I know how to check logs
- [ ] I have troubleshooting guide ready
- [ ] I won't panic if errors occur

---

## ✅ Final Pre-Deployment Check

### All Systems Go?
- [ ] Azure account ready
- [ ] Software installed
- [ ] Project files prepared
- [ ] Local testing passed
- [ ] Security checked
- [ ] Cost plan decided
- [ ] Time allocated
- [ ] Documentation ready
- [ ] Support plan in place

---

## 🚀 Ready to Deploy!

If all checkboxes above are checked, you're ready to start deployment!

**Next Step:** Open `AZURE_DEPLOYMENT_STEP_BY_STEP.md` and follow Phase 1.

---

## 📞 Emergency Contacts

### If You Get Stuck
1. **Check logs** (most issues show up here)
2. **Read error messages carefully**
3. **Search Azure documentation**
4. **Ask in Azure community forums**
5. **Review this checklist again**

### Azure Support
- Portal: https://portal.azure.com → Support
- Docs: https://docs.microsoft.com/azure
- Community: https://docs.microsoft.com/answers/

---

## 💡 Pro Tips

1. **Start with FREE tier** - Learn without cost
2. **Save all URLs** - You'll need them
3. **Check logs often** - Catch issues early
4. **Test after each step** - Don't wait until end
5. **Monitor costs daily** - Avoid surprises
6. **Keep credentials safe** - Never commit to Git
7. **Take breaks** - Don't rush
8. **Document your changes** - For future reference

---

## 🎉 Motivation

**Remember:**
- Everyone starts as a beginner
- Errors are learning opportunities
- Azure has great documentation
- You have $200 free credits
- This checklist has your back
- You can do this! 💪

---

**Good Luck! 🚀**

**Estimated Success Rate:** 95% if you follow this checklist

**Time to Complete:** 2-3 hours

**Cost:** $0-15/month

**Difficulty:** Beginner-Friendly ⭐⭐⭐

---

**Last Updated:** November 2024
**Version:** 1.0
**Status:** Ready for Deployment ✅
