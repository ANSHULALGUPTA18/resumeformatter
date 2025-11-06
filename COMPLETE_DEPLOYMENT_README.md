# 📘 Resume Formatter - Complete Deployment Guide

## 🎯 Table of Contents
1. [Project Overview](#project-overview)
2. [Project Structure](#project-structure)
3. [Prerequisites](#prerequisites)
4. [Local Development Setup](#local-development-setup)
5. [Docker & OnlyOffice Setup](#docker--onlyoffice-setup)
6. [Azure Deployment](#azure-deployment)
7. [Testing](#testing)
8. [Troubleshooting](#troubleshooting)

---

## 📦 Project Overview

**Resume Formatter** is a full-stack web application that automatically formats resumes using custom templates with AI-powered section detection.

### Features
- ✅ Upload custom resume templates (DOCX/PDF)
- ✅ Batch process multiple resumes
- ✅ AI-powered section detection and mapping
- ✅ Preserve template formatting (fonts, colors, styles)
- ✅ Real-time preview with OnlyOffice integration
- ✅ Download formatted resumes

### Tech Stack
- **Backend:** Python 3.10, Flask
- **Frontend:** React 18
- **Document Processing:** python-docx, pdfplumber, PyMuPDF
- **AI/ML:** Sentence Transformers, spaCy, Transformers
- **Document Editor:** OnlyOffice Document Server (Docker)
- **Deployment:** Microsoft Azure

---

## 📁 Project Structure

```
resumeformatter.onlyoffice/
│
├── Backend/                              # Python Flask API
│   ├── app.py                            # Main application entry point
│   ├── config.py                         # Configuration settings
│   ├── requirements.txt                  # Python dependencies (COMPLETE)
│   ├── startup.sh                        # Azure startup script
│   ├── .deployment                       # Azure deployment config
│   │
│   ├── models/                           # Database models
│   │   └── database.py                   # Template database
│   │
│   ├── routes/                           # API routes
│   │   ├── onlyoffice_routes.py          # OnlyOffice editor endpoints
│   │   └── cai_contact_routes.py         # Contact management
│   │
│   ├── utils/                            # Utility modules
│   │   ├── advanced_resume_parser.py     # Resume parsing with ML
│   │   ├── advanced_template_analyzer.py # Template analysis
│   │   ├── enhanced_formatter_integration.py  # Main formatter
│   │   ├── enhanced_section_classifier.py     # AI section detection
│   │   ├── intelligent_formatter.py      # Intelligent formatting
│   │   ├── smart_section_mapper.py       # Section mapping
│   │   └── ... (other utilities)
│   │
│   ├── static/uploads/                   # Uploaded files
│   │   ├── templates/                    # Template files
│   │   └── resumes/                      # Resume files
│   │
│   └── output/                           # Generated formatted resumes
│
├── frontend/                             # React Web App
│   ├── public/                           # Static assets
│   ├── src/                              # React source code
│   │   ├── App.js                        # Main component
│   │   ├── components/                   # React components
│   │   └── ...
│   ├── package.json                      # Node dependencies
│   ├── .env.production                   # Production environment vars
│   └── staticwebapp.config.json          # Azure Static Web App config
│
├── Deployment Guides/                    # Deployment documentation
│   ├── START_HERE.md                     # Entry point
│   ├── PRE_DEPLOYMENT_CHECKLIST.md       # Pre-deployment checks
│   ├── AZURE_DEPLOYMENT_STEP_BY_STEP.md  # Main deployment guide
│   ├── AZURE_QUICK_COMMANDS.md           # Quick command reference
│   └── DEPLOYMENT_FLOWCHART.md           # Visual guides
│
├── docker-compose.yml                    # OnlyOffice Docker setup
├── start-onlyoffice.bat                  # Start OnlyOffice (Windows)
└── COMPLETE_DEPLOYMENT_README.md         # This file
```

---

## ✅ Prerequisites

### 1. Software Requirements

#### For Local Development
- **Python 3.10** or higher
  - Download: https://www.python.org/downloads/
  - Verify: `python --version`

- **Node.js 16+** and npm
  - Download: https://nodejs.org/
  - Verify: `node --version` and `npm --version`

- **Git**
  - Download: https://git-scm.com/
  - Verify: `git --version`

- **Docker Desktop** (for OnlyOffice)
  - Download: https://www.docker.com/products/docker-desktop/
  - Verify: `docker --version`

#### For Azure Deployment
- **Azure CLI**
  - Download: https://aka.ms/installazurecliwindows
  - Verify: `az --version`

- **Azure Account**
  - Sign up: https://azure.microsoft.com/free/
  - Get $200 free credits

### 2. System Requirements
- **RAM:** 8GB minimum (16GB recommended with ML models)
- **Storage:** 5GB free space
- **OS:** Windows 10/11, macOS, or Linux

---

## 🚀 Local Development Setup

### PHASE 1: Backend Setup

#### Step 1: Navigate to Backend Folder
```powershell
cd "c:\Users\Sahithi\Desktop\resumeformatter.onlyoffice\Backend"
```

#### Step 2: Create Virtual Environment
```powershell
# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
.\venv\Scripts\activate

# On macOS/Linux:
source venv/bin/activate
```

You should see `(venv)` in your terminal prompt.

#### Step 3: Install Dependencies
```powershell
# Install all dependencies
pip install -r requirements.txt

# This will install:
# - Flask and web framework
# - Document processing libraries
# - ML/AI libraries (2GB+ download)
# - All utilities

# Installation time: 5-15 minutes
```

#### Step 4: Download spaCy Language Model
```powershell
# Required for NLP features
python -m spacy download en_core_web_sm
```

#### Step 5: Create Required Folders
```powershell
# These folders are created automatically, but you can verify:
mkdir -p static/uploads/templates
mkdir -p static/uploads/resumes
mkdir -p output
```

#### Step 6: Start Backend Server
```powershell
# Make sure you're in Backend folder with venv activated
python app.py
```

**Expected Output:**
```
================================================================================
🎯 RESUME FORMATTER - BACKEND SERVER
================================================================================
✅ API running on http://127.0.0.1:5000
✅ Network access: http://192.168.x.x:5000
✅ React frontend: http://localhost:3000
✅ OnlyOffice Document Server: http://localhost:8080
================================================================================
```

**Test Backend:**
Open browser: http://localhost:5000/api/health

**Expected Response:** `{"status": "ok"}`

---

### PHASE 2: Frontend Setup

#### Step 1: Navigate to Frontend Folder
```powershell
# Open new terminal (keep backend running)
cd "c:\Users\Sahithi\Desktop\resumeformatter.onlyoffice\frontend"
```

#### Step 2: Install Dependencies
```powershell
npm install

# This installs:
# - React and React DOM
# - Axios (HTTP client)
# - PDF.js (PDF preview)
# - TinyMCE (rich text editor)
# - Other UI libraries

# Installation time: 2-5 minutes
```

#### Step 3: Create Environment File
Create `.env.local` file in frontend folder:
```env
REACT_APP_API_URL=http://localhost:5000
```

#### Step 4: Start Frontend Server
```powershell
npm start
```

**Expected Output:**
```
Compiled successfully!

You can now view resume-formatter-frontend in the browser.

  Local:            http://localhost:3000
  On Your Network:  http://192.168.x.x:3000
```

**Test Frontend:**
Browser will automatically open: http://localhost:3000

---

## 🐳 Docker & OnlyOffice Setup

OnlyOffice Document Server provides real-time document editing capabilities.

### Step 1: Install Docker Desktop
1. Download: https://www.docker.com/products/docker-desktop/
2. Install and restart computer
3. Start Docker Desktop
4. Verify: `docker --version`

### Step 2: Pull OnlyOffice Image
```powershell
# This downloads ~2GB
docker pull onlyoffice/documentserver
```

### Step 3: Start OnlyOffice Container

**Option A: Using Docker Compose (Recommended)**
```powershell
# Navigate to project root
cd "c:\Users\Sahithi\Desktop\resumeformatter.onlyoffice"

# Start OnlyOffice
docker-compose up -d
```

**Option B: Using Docker Command**
```powershell
docker run -d -p 8080:80 `
  --name onlyoffice-documentserver `
  --restart always `
  -v ${PWD}/onlyoffice-data:/var/www/onlyoffice/Data `
  onlyoffice/documentserver
```

**Option C: Using Batch Script (Windows)**
```powershell
# Simply double-click:
start-onlyoffice.bat
```

### Step 4: Verify OnlyOffice is Running
```powershell
# Check container status
docker ps

# You should see:
# CONTAINER ID   IMAGE                        STATUS
# xxxxxxxxxxxx   onlyoffice/documentserver    Up X minutes
```

**Test OnlyOffice:**
Open browser: http://localhost:8080/welcome/

### Step 5: OnlyOffice Management Commands

```powershell
# Stop OnlyOffice
docker stop onlyoffice-documentserver

# Start OnlyOffice
docker start onlyoffice-documentserver

# Restart OnlyOffice
docker restart onlyoffice-documentserver

# View logs
docker logs onlyoffice-documentserver

# Remove container (if needed)
docker rm -f onlyoffice-documentserver
```

### Docker Compose File Reference
```yaml
version: '3'
services:
  onlyoffice-documentserver:
    image: onlyoffice/documentserver
    container_name: onlyoffice-documentserver
    ports:
      - "8080:80"
    volumes:
      - ./onlyoffice-data:/var/www/onlyoffice/Data
    restart: always
```

---

## ☁️ Azure Deployment

### Quick Deployment Overview

```
┌─────────────────────────────────────────────────────────────┐
│                    DEPLOYMENT PROCESS                        │
└─────────────────────────────────────────────────────────────┘

1. Prepare Files        (30 min)
2. Deploy Backend       (45 min)
3. Setup Storage        (15 min)
4. Deploy Frontend      (30 min)
5. Test Everything      (30 min)
─────────────────────────────────────────────────────────────
TOTAL TIME              2-3 hours (first time)
```

### Files to Create Before Deployment

#### 1. Backend/startup.sh
```bash
#!/bin/bash
gunicorn --bind=0.0.0.0:8000 --timeout 600 --workers 2 app:app
```

#### 2. Backend/.deployment
```ini
[config]
SCM_DO_BUILD_DURING_DEPLOYMENT=true
```

#### 3. frontend/.env.production
```env
REACT_APP_API_URL=https://YOUR_BACKEND_NAME.azurewebsites.net
```

#### 4. frontend/staticwebapp.config.json
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

### Deployment Steps (Summary)

**For detailed step-by-step instructions, see:**
- `AZURE_DEPLOYMENT_STEP_BY_STEP.md` - Complete guide
- `AZURE_QUICK_COMMANDS.md` - Quick command reference

#### Quick Deployment Commands

```powershell
# 1. Login to Azure
az login

# 2. Set variables
$RESOURCE_GROUP = "resume-formatter-rg"
$LOCATION = "eastus"
$APP_NAME = "resume-formatter-api-$(Get-Random -Maximum 9999)"

# 3. Create resource group
az group create --name $RESOURCE_GROUP --location $LOCATION

# 4. Create App Service Plan (Basic tier)
az appservice plan create `
  --name resume-formatter-plan `
  --resource-group $RESOURCE_GROUP `
  --sku B1 `
  --is-linux

# 5. Create Web App
az webapp create `
  --resource-group $RESOURCE_GROUP `
  --plan resume-formatter-plan `
  --name $APP_NAME `
  --runtime "PYTHON:3.10"

# 6. Configure settings
az webapp config set `
  --resource-group $RESOURCE_GROUP `
  --name $APP_NAME `
  --startup-file "startup.sh"

az webapp config appsettings set `
  --resource-group $RESOURCE_GROUP `
  --name $APP_NAME `
  --settings `
    FLASK_ENV=production `
    PYTHONUNBUFFERED=1 `
    SCM_DO_BUILD_DURING_DEPLOYMENT=true `
    WEBSITES_PORT=8000

# 7. Deploy backend
cd Backend
Get-ChildItem -Exclude venv,__pycache__,.git,node_modules | Compress-Archive -DestinationPath deploy.zip -Force
az webapp deployment source config-zip `
  --resource-group $RESOURCE_GROUP `
  --name $APP_NAME `
  --src deploy.zip

# 8. Build and deploy frontend
cd ../frontend
npm install
npm run build

# Deploy to Azure Static Web Apps or Storage
# See AZURE_DEPLOYMENT_STEP_BY_STEP.md for details
```

---

## 🧪 Testing

### Local Testing

#### Test Backend API
```powershell
# Health check
curl http://localhost:5000/api/health

# Get templates
curl http://localhost:5000/api/templates

# OnlyOffice status
curl http://localhost:5000/api/onlyoffice/status
```

#### Test Frontend
1. Open http://localhost:3000
2. Upload a template (DOCX file)
3. Upload a resume (PDF or DOCX)
4. Click "Format Resumes"
5. Preview and download result

### Azure Testing

#### Test Backend
```powershell
# Replace with your app name
curl https://YOUR_APP_NAME.azurewebsites.net/api/health
```

#### Test Frontend
1. Open your frontend URL
2. Test all features
3. Check browser console for errors

### End-to-End Testing Checklist
- [ ] Backend health check works
- [ ] Frontend loads without errors
- [ ] Can upload template
- [ ] Can upload resume
- [ ] Formatting completes successfully
- [ ] Can preview formatted resume
- [ ] Can download formatted resume
- [ ] OnlyOffice editor opens (local only)
- [ ] No CORS errors in console

---

## 🐛 Troubleshooting

### Common Issues & Solutions

#### Issue 1: Backend Won't Start
**Symptoms:** Import errors, module not found

**Solution:**
```powershell
# Ensure virtual environment is activated
.\venv\Scripts\activate

# Reinstall dependencies
pip install -r requirements.txt

# Download spaCy model
python -m spacy download en_core_web_sm
```

#### Issue 2: Frontend Can't Connect to Backend
**Symptoms:** CORS errors, network errors

**Solution:**
1. Check backend is running on port 5000
2. Verify `.env.local` has correct API URL
3. Check CORS settings in `Backend/app.py`

#### Issue 3: OnlyOffice Not Working
**Symptoms:** Editor doesn't load, connection refused

**Solution:**
```powershell
# Check Docker is running
docker ps

# Restart OnlyOffice
docker restart onlyoffice-documentserver

# Check logs
docker logs onlyoffice-documentserver

# If not running, start it
docker start onlyoffice-documentserver
```

#### Issue 4: Out of Memory During Installation
**Symptoms:** Installation fails, pip crashes

**Solution:**
```powershell
# Install without ML packages first
pip install Flask Flask-CORS python-docx pdfplumber PyPDF2 reportlab gunicorn mammoth

# Then install ML packages one by one
pip install sentence-transformers
pip install transformers
pip install torch
pip install spacy
```

#### Issue 5: Azure Deployment Fails
**Symptoms:** Application Error, 500 errors

**Solution:**
```powershell
# Check logs
az webapp log tail --name YOUR_APP_NAME --resource-group resume-formatter-rg

# Common fixes:
# 1. Ensure startup.sh has Unix line endings (LF not CRLF)
# 2. Remove Windows-specific packages (docx2pdf, pywin32)
# 3. Check Python version is 3.10
# 4. Verify all environment variables are set
```

### Getting Help

#### Log Files
```powershell
# Backend logs (local)
# Check terminal where app.py is running

# Azure logs
az webapp log tail --name YOUR_APP_NAME --resource-group resume-formatter-rg

# Docker logs
docker logs onlyoffice-documentserver
```

#### Support Resources
- **Azure Documentation:** https://docs.microsoft.com/azure
- **Flask Documentation:** https://flask.palletsprojects.com/
- **React Documentation:** https://react.dev/
- **OnlyOffice Docs:** https://helpcenter.onlyoffice.com/

---

## 📊 Performance Optimization

### Backend Optimization
```python
# In config.py
USE_ML_PARSER = True      # Better accuracy but slower
USE_ML_PARSER = False     # Faster but less accurate

PARALLEL_WORKERS = 4      # Adjust based on CPU cores
```

### Frontend Optimization
```bash
# Production build
npm run build

# Optimize bundle size
npm install --production
```

### Docker Optimization
```yaml
# Allocate more resources in Docker Desktop
# Settings → Resources → Advanced
# - CPUs: 4
# - Memory: 4GB
```

---

## 💰 Cost Estimates

### Local Development
- **Cost:** $0 (free)
- **Requirements:** Your computer

### Azure Deployment

#### FREE Tier (Testing)
- App Service (F1): $0
- Static Web App: $0
- Storage (10GB): $0.18/month
- **Total: ~$0.18/month**

#### BASIC Tier (Production)
- App Service (B1): $13.14/month
- Static Web App: $0
- Storage (10GB): $0.18/month
- **Total: ~$13.32/month**

---

## 🎓 Learning Resources

### Tutorials
1. **Flask:** https://flask.palletsprojects.com/tutorial/
2. **React:** https://react.dev/learn
3. **Azure:** https://docs.microsoft.com/learn/azure/
4. **Docker:** https://docs.docker.com/get-started/

### Video Courses
- Flask Mega-Tutorial (free)
- React Official Tutorial
- Azure Fundamentals (free certification)

---

## 📝 Quick Reference Commands

### Development
```powershell
# Start backend
cd Backend
.\venv\Scripts\activate
python app.py

# Start frontend
cd frontend
npm start

# Start OnlyOffice
docker start onlyoffice-documentserver
```

### Deployment
```powershell
# Deploy backend
cd Backend
Get-ChildItem -Exclude venv,__pycache__ | Compress-Archive -DestinationPath deploy.zip -Force
az webapp deployment source config-zip --resource-group resume-formatter-rg --name YOUR_APP_NAME --src deploy.zip

# Build frontend
cd frontend
npm run build
```

### Docker
```powershell
# Start OnlyOffice
docker start onlyoffice-documentserver

# Stop OnlyOffice
docker stop onlyoffice-documentserver

# View logs
docker logs onlyoffice-documentserver
```

---

## ✅ Deployment Checklist

### Before Deployment
- [ ] All dependencies in requirements.txt
- [ ] startup.sh created
- [ ] .deployment created
- [ ] .env.production created
- [ ] staticwebapp.config.json created
- [ ] Tested locally
- [ ] Azure account ready

### During Deployment
- [ ] Backend deployed
- [ ] Backend health check works
- [ ] Storage configured
- [ ] Frontend built
- [ ] Frontend deployed
- [ ] Environment variables set

### After Deployment
- [ ] End-to-end testing complete
- [ ] No errors in logs
- [ ] Performance acceptable
- [ ] Costs monitored

---

## 🎉 Success!

If you've followed this guide, you should now have:
- ✅ Local development environment running
- ✅ OnlyOffice Document Server integrated
- ✅ Application deployed to Azure
- ✅ All features working correctly

**Next Steps:**
1. Customize the UI
2. Add more features
3. Optimize performance
4. Monitor costs
5. Share with users!

---

**Created:** November 2024  
**Version:** 1.0  
**Status:** Production Ready ✅  
**Difficulty:** Beginner-Friendly ⭐⭐⭐

**Good luck with your deployment! 🚀**
