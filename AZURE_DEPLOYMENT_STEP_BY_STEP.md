# 🚀 Azure Deployment Guide - Step by Step for Beginners

## 📋 Table of Contents
1. [What You Need Before Starting](#what-you-need-before-starting)
2. [Understanding Your Project](#understanding-your-project)
3. [Step-by-Step Deployment Process](#step-by-step-deployment-process)
4. [Testing Your Deployment](#testing-your-deployment)
5. [Troubleshooting](#troubleshooting)

---

## 🎯 What You Need Before Starting

### 1. Create Azure Account (FREE)
- Go to: https://azure.microsoft.com/free/
- Sign up with your email
- You get **$200 FREE credits** for 30 days
- No charges until you upgrade to paid account

### 2. Install Required Software

#### A. Install Azure CLI (Command Line Tool)
**For Windows:**
1. Download: https://aka.ms/installazurecliwindows
2. Run the installer (AzureCLI.msi)
3. Follow the installation wizard
4. Restart your computer

**Verify Installation:**
Open PowerShell and type:
```powershell
az --version
```
You should see version information.

#### B. Install Git (if not already installed)
1. Download: https://git-scm.com/download/win
2. Install with default settings

#### C. Install Node.js (for frontend)
1. Download: https://nodejs.org/ (LTS version)
2. Install with default settings

---

## 🏗️ Understanding Your Project

Your project has **TWO parts**:

### 1. **Backend** (Flask/Python API)
- Location: `Backend/` folder
- Language: Python
- Framework: Flask
- Purpose: Processes resumes, formats documents

### 2. **Frontend** (React Web App)
- Location: `frontend/` folder
- Language: JavaScript/React
- Purpose: User interface where users upload resumes

---

## 📝 Step-by-Step Deployment Process

### PHASE 1: Prepare Your Computer

#### Step 1: Login to Azure
Open PowerShell and run:
```powershell
az login
```
- A browser window will open
- Login with your Azure account
- Close browser after successful login

#### Step 2: Set Your Location
Choose a region close to you:
- **US East**: `eastus`
- **US West**: `westus2`
- **Europe**: `westeurope`
- **Asia**: `southeastasia`

```powershell
# Set variables (change location if needed)
$RESOURCE_GROUP = "resume-formatter-rg"
$LOCATION = "eastus"
$APP_NAME = "resume-formatter-api-$(Get-Random -Maximum 9999)"
$FRONTEND_NAME = "resume-formatter-web-$(Get-Random -Maximum 9999)"
```

---

### PHASE 2: Deploy Backend (Python Flask API)

#### Step 3: Create Resource Group
Think of this as a folder that holds all your Azure resources.

```powershell
az group create --name $RESOURCE_GROUP --location $LOCATION
```

**Expected Output:** ✅ "Succeeded"

#### Step 4: Create App Service Plan
This is like renting a server.

```powershell
# FREE tier (for testing) - F1
az appservice plan create `
  --name resume-formatter-plan `
  --resource-group $RESOURCE_GROUP `
  --sku F1 `
  --is-linux

# OR Basic tier (recommended) - B1 ($13/month)
az appservice plan create `
  --name resume-formatter-plan `
  --resource-group $RESOURCE_GROUP `
  --sku B1 `
  --is-linux
```

**Note:** Free tier (F1) has limitations:
- 60 minutes CPU time per day
- 1GB storage
- Good for testing only

#### Step 5: Create Web App for Backend
```powershell
az webapp create `
  --resource-group $RESOURCE_GROUP `
  --plan resume-formatter-plan `
  --name $APP_NAME `
  --runtime "PYTHON:3.10"
```

**Expected Output:** You'll see your app URL: `https://<your-app-name>.azurewebsites.net`

#### Step 6: Prepare Backend Files

**A. Update requirements.txt**
Navigate to your Backend folder and update `requirements.txt`:

```powershell
cd "c:\Users\Sahithi\Desktop\resumeformatter.onlyoffice\Backend"
```

Create/Update `requirements.txt`:
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

**B. Create startup.sh** (tells Azure how to start your app)
Create file `startup.sh` in Backend folder:
```bash
#!/bin/bash
gunicorn --bind=0.0.0.0:8000 --timeout 600 --workers 2 app:app
```

**C. Create .deployment** (tells Azure what to do)
Create file `.deployment` in Backend folder:
```ini
[config]
SCM_DO_BUILD_DURING_DEPLOYMENT=true
```

#### Step 7: Configure Backend Settings
```powershell
# Set startup command
az webapp config set `
  --resource-group $RESOURCE_GROUP `
  --name $APP_NAME `
  --startup-file "startup.sh"

# Set environment variables
az webapp config appsettings set `
  --resource-group $RESOURCE_GROUP `
  --name $APP_NAME `
  --settings `
    FLASK_ENV=production `
    PYTHONUNBUFFERED=1 `
    SCM_DO_BUILD_DURING_DEPLOYMENT=true `
    WEBSITES_PORT=8000
```

#### Step 8: Deploy Backend Code

**Option A: Using ZIP Deploy (Easiest)**
```powershell
# Make sure you're in Backend folder
cd "c:\Users\Sahithi\Desktop\resumeformatter.onlyoffice\Backend"

# Create ZIP file (exclude venv and unnecessary files)
$exclude = @('venv', '__pycache__', '*.pyc', '.git', 'node_modules')
Get-ChildItem -Exclude $exclude | Compress-Archive -DestinationPath deploy.zip -Force

# Deploy to Azure
az webapp deployment source config-zip `
  --resource-group $RESOURCE_GROUP `
  --name $APP_NAME `
  --src deploy.zip
```

**Wait 5-10 minutes** for deployment to complete.

#### Step 9: Verify Backend is Running
```powershell
# Check if app is running
az webapp browse --name $APP_NAME --resource-group $RESOURCE_GROUP
```

Or visit: `https://<your-app-name>.azurewebsites.net/api/health`

**Expected Response:** `{"status": "ok"}`

---

### PHASE 3: Deploy Frontend (React App)

#### Step 10: Prepare Frontend

Navigate to frontend folder:
```powershell
cd "c:\Users\Sahithi\Desktop\resumeformatter.onlyoffice\frontend"
```

#### Step 11: Update API URL

Create `.env.production` file in frontend folder:
```env
REACT_APP_API_URL=https://<your-backend-app-name>.azurewebsites.net
```

Replace `<your-backend-app-name>` with your actual backend app name.

#### Step 12: Create Static Web App Configuration

Create `staticwebapp.config.json` in frontend folder:
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

#### Step 13: Build Frontend
```powershell
# Install dependencies
npm install

# Build for production
npm run build
```

This creates a `build/` folder with optimized files.

#### Step 14: Deploy Frontend to Azure Static Web Apps

**Option 1: Using Azure Portal (Easiest for beginners)**

1. Go to: https://portal.azure.com
2. Click "Create a resource"
3. Search for "Static Web App"
4. Click "Create"
5. Fill in:
   - **Resource Group:** resume-formatter-rg
   - **Name:** resume-formatter-web
   - **Plan type:** Free
   - **Region:** Same as backend
   - **Deployment source:** Other (we'll upload manually)
6. Click "Review + Create" → "Create"
7. After creation, go to your Static Web App
8. Click "Browse" to get your URL
9. Use Azure CLI to deploy:

```powershell
# Get deployment token
$token = az staticwebapp secrets list `
  --name resume-formatter-web `
  --resource-group $RESOURCE_GROUP `
  --query "properties.apiKey" -o tsv

# Deploy using SWA CLI
npm install -g @azure/static-web-apps-cli

# Deploy the build folder
cd "c:\Users\Sahithi\Desktop\resumeformatter.onlyoffice\frontend"
swa deploy ./build --deployment-token $token
```

**Option 2: Using Azure Storage (Alternative)**

If Static Web Apps is complex, use Azure Storage for static hosting:

```powershell
# Create storage account
$STORAGE_NAME = "resumeformatter$(Get-Random -Maximum 9999)"

az storage account create `
  --name $STORAGE_NAME `
  --resource-group $RESOURCE_GROUP `
  --location $LOCATION `
  --sku Standard_LRS `
  --kind StorageV2

# Enable static website
az storage blob service-properties update `
  --account-name $STORAGE_NAME `
  --static-website `
  --index-document index.html `
  --404-document index.html

# Upload build files
az storage blob upload-batch `
  --account-name $STORAGE_NAME `
  --source ./build `
  --destination '$web'

# Get website URL
az storage account show `
  --name $STORAGE_NAME `
  --resource-group $RESOURCE_GROUP `
  --query "primaryEndpoints.web" -o tsv
```

---

### PHASE 4: Configure Storage (Optional but Recommended)

#### Step 15: Create Azure Blob Storage for Files

```powershell
# Create storage account
$STORAGE_NAME = "resumefiles$(Get-Random -Maximum 9999)"

az storage account create `
  --name $STORAGE_NAME `
  --resource-group $RESOURCE_GROUP `
  --location $LOCATION `
  --sku Standard_LRS

# Get connection string
$CONNECTION_STRING = az storage account show-connection-string `
  --name $STORAGE_NAME `
  --resource-group $RESOURCE_GROUP `
  --query connectionString -o tsv

# Create containers
az storage container create --name resumes --connection-string $CONNECTION_STRING
az storage container create --name templates --connection-string $CONNECTION_STRING
az storage container create --name output --connection-string $CONNECTION_STRING

# Add connection string to backend
az webapp config appsettings set `
  --resource-group $RESOURCE_GROUP `
  --name $APP_NAME `
  --settings AZURE_STORAGE_CONNECTION_STRING="$CONNECTION_STRING"
```

---

## ✅ Testing Your Deployment

### Test Backend
```powershell
# Test health endpoint
curl https://<your-backend-app>.azurewebsites.net/api/health

# Expected: {"status": "ok"}
```

### Test Frontend
1. Open your frontend URL in browser
2. Try uploading a template
3. Try uploading a resume
4. Check if formatting works

---

## 🐛 Troubleshooting

### Issue 1: Backend Shows "Application Error"

**Solution:**
```powershell
# Check logs
az webapp log tail --name $APP_NAME --resource-group $RESOURCE_GROUP

# Enable logging
az webapp log config `
  --name $APP_NAME `
  --resource-group $RESOURCE_GROUP `
  --application-logging filesystem `
  --level information
```

### Issue 2: Frontend Can't Connect to Backend

**Check:**
1. CORS settings in `app.py`
2. API URL in `.env.production`
3. Backend is running

**Fix CORS:**
Update `app.py`:
```python
CORS(app, resources={
    r"/api/*": {
        "origins": [
            "https://your-frontend-url.azurestaticapps.net",
            "https://your-storage-account.z13.web.core.windows.net"
        ]
    }
})
```

### Issue 3: Deployment Takes Too Long

**Solution:**
- Free tier has limited resources
- Upgrade to B1 tier ($13/month)
- Or wait patiently (can take 10-15 minutes)

### Issue 4: Out of Memory

**Solution:**
```powershell
# Upgrade to higher tier
az appservice plan update `
  --name resume-formatter-plan `
  --resource-group $RESOURCE_GROUP `
  --sku B2
```

---

## 💰 Cost Summary

### Free Tier (Testing Only)
- **App Service:** F1 Free (limited)
- **Static Web App:** Free
- **Storage:** Pay-as-you-go (~$0.18/month for 10GB)
- **Total:** ~$0-2/month

### Basic Tier (Recommended)
- **App Service:** B1 ($13.14/month)
- **Static Web App:** Free
- **Storage:** ~$0.18/month
- **Total:** ~$13-15/month

### How to Monitor Costs
1. Go to: https://portal.azure.com
2. Click "Cost Management + Billing"
3. View your spending

---

## 🎉 Success Checklist

- [ ] Azure account created
- [ ] Azure CLI installed
- [ ] Resource group created
- [ ] Backend deployed and running
- [ ] Frontend deployed and accessible
- [ ] Storage configured (optional)
- [ ] CORS configured correctly
- [ ] Application tested end-to-end

---

## 📞 Getting Help

### Azure Support
- Free tier: Community support only
- Paid tier: 24/7 support

### Useful Commands

```powershell
# View all resources
az resource list --resource-group $RESOURCE_GROUP --output table

# Delete everything (if you want to start over)
az group delete --name $RESOURCE_GROUP --yes

# Restart backend
az webapp restart --name $APP_NAME --resource-group $RESOURCE_GROUP

# View backend logs
az webapp log tail --name $APP_NAME --resource-group $RESOURCE_GROUP
```

---

## 🚀 Next Steps After Deployment

1. **Custom Domain** (Optional)
   - Buy a domain (e.g., from GoDaddy, Namecheap)
   - Configure DNS
   - Add to Azure

2. **SSL Certificate** (Free with Azure)
   - Automatic with custom domain
   - Or use Azure's default HTTPS

3. **Monitoring**
   - Enable Application Insights
   - Set up alerts

4. **CI/CD** (Automatic Deployment)
   - Connect to GitHub
   - Auto-deploy on code push

---

## 📚 Additional Resources

- **Azure Documentation:** https://docs.microsoft.com/azure
- **Azure Free Account:** https://azure.microsoft.com/free/
- **Azure Portal:** https://portal.azure.com
- **Azure Pricing Calculator:** https://azure.microsoft.com/pricing/calculator/

---

**Estimated Time to Complete:** 2-3 hours (first time)

**Difficulty Level:** Beginner-Friendly ⭐⭐⭐

**Cost:** $0-15/month

---

**Good Luck! 🎉**

If you get stuck, check the logs and error messages. Most issues are related to:
1. CORS configuration
2. Environment variables
3. File paths
4. Missing dependencies

**Remember:** You have $200 free credits, so don't worry about costs while learning!
