# 🚀 Azure Deployment - Quick Commands Cheat Sheet

## ⚡ Copy-Paste Commands (In Order)

### 1️⃣ Setup Variables
```powershell
# Set these first
$RESOURCE_GROUP = "resume-formatter-rg"
$LOCATION = "eastus"
$APP_NAME = "resume-formatter-api-$(Get-Random -Maximum 9999)"
$STORAGE_NAME = "resumefiles$(Get-Random -Maximum 9999)"
```

### 2️⃣ Login to Azure
```powershell
az login
```

### 3️⃣ Create Resource Group
```powershell
az group create --name $RESOURCE_GROUP --location $LOCATION
```

### 4️⃣ Create App Service Plan (Choose One)

**FREE Tier (Testing):**
```powershell
az appservice plan create --name resume-formatter-plan --resource-group $RESOURCE_GROUP --sku F1 --is-linux
```

**BASIC Tier (Recommended - $13/month):**
```powershell
az appservice plan create --name resume-formatter-plan --resource-group $RESOURCE_GROUP --sku B1 --is-linux
```

### 5️⃣ Create Backend Web App
```powershell
az webapp create --resource-group $RESOURCE_GROUP --plan resume-formatter-plan --name $APP_NAME --runtime "PYTHON:3.10"
```

### 6️⃣ Configure Backend
```powershell
az webapp config set --resource-group $RESOURCE_GROUP --name $APP_NAME --startup-file "startup.sh"

az webapp config appsettings set --resource-group $RESOURCE_GROUP --name $APP_NAME --settings FLASK_ENV=production PYTHONUNBUFFERED=1 SCM_DO_BUILD_DURING_DEPLOYMENT=true WEBSITES_PORT=8000
```

### 7️⃣ Deploy Backend
```powershell
cd "c:\Users\Sahithi\Desktop\resumeformatter.onlyoffice\Backend"

# Create ZIP (exclude unnecessary files)
Get-ChildItem -Exclude venv,__pycache__,.git,node_modules | Compress-Archive -DestinationPath deploy.zip -Force

# Deploy
az webapp deployment source config-zip --resource-group $RESOURCE_GROUP --name $APP_NAME --src deploy.zip
```

### 8️⃣ Create Storage Account
```powershell
az storage account create --name $STORAGE_NAME --resource-group $RESOURCE_GROUP --location $LOCATION --sku Standard_LRS

$CONNECTION_STRING = az storage account show-connection-string --name $STORAGE_NAME --resource-group $RESOURCE_GROUP --query connectionString -o tsv

az storage container create --name resumes --connection-string $CONNECTION_STRING
az storage container create --name templates --connection-string $CONNECTION_STRING
az storage container create --name output --connection-string $CONNECTION_STRING

az webapp config appsettings set --resource-group $RESOURCE_GROUP --name $APP_NAME --settings AZURE_STORAGE_CONNECTION_STRING="$CONNECTION_STRING"
```

### 9️⃣ Build and Deploy Frontend
```powershell
cd "c:\Users\Sahithi\Desktop\resumeformatter.onlyoffice\frontend"

# Install dependencies
npm install

# Build
npm run build

# Create storage for static website
$FRONTEND_STORAGE = "resumeweb$(Get-Random -Maximum 9999)"

az storage account create --name $FRONTEND_STORAGE --resource-group $RESOURCE_GROUP --location $LOCATION --sku Standard_LRS --kind StorageV2

az storage blob service-properties update --account-name $FRONTEND_STORAGE --static-website --index-document index.html --404-document index.html

az storage blob upload-batch --account-name $FRONTEND_STORAGE --source ./build --destination '$web'

# Get frontend URL
az storage account show --name $FRONTEND_STORAGE --resource-group $RESOURCE_GROUP --query "primaryEndpoints.web" -o tsv
```

---

## 🔍 Useful Commands

### Check Backend Status
```powershell
az webapp browse --name $APP_NAME --resource-group $RESOURCE_GROUP
```

### View Backend Logs
```powershell
az webapp log tail --name $APP_NAME --resource-group $RESOURCE_GROUP
```

### Restart Backend
```powershell
az webapp restart --name $APP_NAME --resource-group $RESOURCE_GROUP
```

### List All Resources
```powershell
az resource list --resource-group $RESOURCE_GROUP --output table
```

### Get Backend URL
```powershell
az webapp show --name $APP_NAME --resource-group $RESOURCE_GROUP --query "defaultHostName" -o tsv
```

### Get Frontend URL
```powershell
az storage account show --name $FRONTEND_STORAGE --resource-group $RESOURCE_GROUP --query "primaryEndpoints.web" -o tsv
```

---

## 🗑️ Delete Everything (Start Over)
```powershell
az group delete --name $RESOURCE_GROUP --yes --no-wait
```

---

## 📊 Check Costs
```powershell
az consumption usage list --output table
```

Or visit: https://portal.azure.com → Cost Management

---

## 🔧 Troubleshooting Commands

### Enable Detailed Logging
```powershell
az webapp log config --name $APP_NAME --resource-group $RESOURCE_GROUP --application-logging filesystem --level information --docker-container-logging filesystem
```

### Download All Logs
```powershell
az webapp log download --name $APP_NAME --resource-group $RESOURCE_GROUP --log-file logs.zip
```

### Check Deployment Status
```powershell
az webapp deployment list --name $APP_NAME --resource-group $RESOURCE_GROUP --output table
```

---

## 📝 Important URLs

After deployment, save these URLs:

**Backend API:**
```
https://<your-app-name>.azurewebsites.net
```

**Frontend Website:**
```
https://<your-storage-account>.z13.web.core.windows.net
```

**Azure Portal:**
```
https://portal.azure.com
```

---

## ⚠️ Common Issues & Quick Fixes

### Issue: "Application Error"
```powershell
az webapp log tail --name $APP_NAME --resource-group $RESOURCE_GROUP
```

### Issue: Frontend Can't Connect
Update CORS in `Backend/app.py` and redeploy:
```python
CORS(app, resources={r"/api/*": {"origins": "*"}})
```

### Issue: Out of Memory
```powershell
az appservice plan update --name resume-formatter-plan --resource-group $RESOURCE_GROUP --sku B2
```

---

## 💡 Pro Tips

1. **Save your URLs** - Write down backend and frontend URLs
2. **Check logs first** - Most issues show up in logs
3. **Use Free tier for testing** - Switch to paid when ready
4. **Monitor costs daily** - Check Azure portal
5. **Keep credentials safe** - Never commit connection strings to Git

---

## 📞 Need Help?

**Azure Support:**
- Portal: https://portal.azure.com
- Docs: https://docs.microsoft.com/azure
- Free tier: Community support only

**Quick Test:**
```powershell
# Test backend
curl https://<your-app-name>.azurewebsites.net/api/health

# Expected: {"status": "ok"}
```

---

**Last Updated:** November 2024
**Difficulty:** Beginner ⭐⭐⭐
**Time Required:** 2-3 hours
**Cost:** $0-15/month
