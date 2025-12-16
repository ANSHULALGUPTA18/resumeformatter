# Azure Deployment Guide

## Pre-Deployment Cleanup ✅

The project has been cleaned up and is ready for Azure deployment:

### Removed Files
- ✅ All unnecessary markdown documentation (kept only README.md and this file)
- ✅ Test files (test_*.py)
- ✅ Development scripts (.bat, .ps1, .sh files)
- ✅ Temporary files and cache (__pycache__, .venv, venv)
- ✅ Old output files (formatted resumes)
- ✅ Database files (will be recreated on deployment)

### History Storage Removed ✅

The application no longer stores resume history:
- **Auto-cleanup after download**: Files are automatically deleted after being downloaded
- **Startup cleanup**: Old files are removed when the server starts
- **Manual cleanup endpoint**: `/api/cleanup` endpoint to remove files older than 1 hour
- **No persistent storage**: Output files are temporary and not stored long-term

## Azure Deployment Steps

### Option 1: Azure App Service (Recommended)

#### Prerequisites
1. Azure account with active subscription
2. Azure CLI installed: `az --version`
3. Git installed

#### Backend Deployment

```bash
# Login to Azure
az login

# Create resource group
az group create --name resume-formatter-rg --location eastus

# Create App Service plan (Linux)
az appservice plan create --name resume-formatter-plan --resource-group resume-formatter-rg --sku B1 --is-linux

# Create web app for backend
az webapp create --resource-group resume-formatter-rg --plan resume-formatter-plan --name resume-formatter-backend --runtime "PYTHON:3.11"

# Configure deployment from local git
cd Backend
az webapp deployment source config-local-git --name resume-formatter-backend --resource-group resume-formatter-rg

# Get deployment credentials
az webapp deployment list-publishing-credentials --name resume-formatter-backend --resource-group resume-formatter-rg

# Deploy
git init
git add .
git commit -m "Initial deployment"
git remote add azure <deployment-git-url>
git push azure main

# Configure startup command
az webapp config set --resource-group resume-formatter-rg --name resume-formatter-backend --startup-file "gunicorn --bind=0.0.0.0 --timeout 600 app:app"
```

#### Frontend Deployment (Static Web App)

```bash
# Create static web app
az staticwebapp create --name resume-formatter-frontend --resource-group resume-formatter-rg --source https://github.com/<your-repo> --location eastus --branch main --app-location "/frontend" --output-location "build"

# Or deploy using Azure Static Web Apps CLI
cd frontend
npm install
npm run build
az staticwebapp deploy --app-name resume-formatter-frontend --resource-group resume-formatter-rg --app-location "build"
```

### Option 2: Azure Container Instances

```bash
# Build and push Docker image
docker build -t resume-formatter-backend ./Backend
docker tag resume-formatter-backend <your-registry>.azurecr.io/resume-formatter-backend
docker push <your-registry>.azurecr.io/resume-formatter-backend

# Create container instance
az container create --resource-group resume-formatter-rg --name resume-formatter-backend --image <your-registry>.azurecr.io/resume-formatter-backend --dns-name-label resume-formatter --ports 5000
```

### Option 3: Azure Kubernetes Service (AKS)

For production-scale deployments with auto-scaling and high availability.

## Environment Variables

Set these in Azure App Service Configuration:

```
FLASK_ENV=production
FLASK_DEBUG=False
CORS_ORIGINS=https://your-frontend-url.azurestaticapps.net
MAX_CONTENT_LENGTH=16777216
UPLOAD_FOLDER=/tmp/uploads
OUTPUT_FOLDER=/tmp/output
TEMPLATE_FOLDER=/tmp/templates
```

## Post-Deployment Configuration

### 1. Configure CORS
Update `app.py` CORS settings with your Azure frontend URL:
```python
CORS(app, resources={r"/api/*": {"origins": ["https://your-frontend.azurestaticapps.net"]}})
```

### 2. Set up Application Insights (Optional)
```bash
az monitor app-insights component create --app resume-formatter-insights --location eastus --resource-group resume-formatter-rg --application-type web
```

### 3. Configure Custom Domain (Optional)
```bash
az webapp config hostname add --webapp-name resume-formatter-backend --resource-group resume-formatter-rg --hostname www.yourdomain.com
```

## File Structure for Deployment

```
resumeformatter.onlyoffice/
├── Backend/
│   ├── app.py                 # Main Flask application
│   ├── config.py              # Configuration
│   ├── requirements.txt       # Python dependencies
│   ├── requirements_ml.txt    # ML dependencies (optional)
│   ├── startup.sh            # Startup script
│   ├── models/               # Database models
│   ├── routes/               # API routes
│   ├── utils/                # Utility functions
│   ├── database/             # Database files
│   ├── Static/               # Static files (templates)
│   └── Output/               # Temporary output (auto-cleaned)
├── frontend/
│   ├── src/                  # React source
│   ├── public/               # Public assets
│   ├── package.json          # Node dependencies
│   └── build/                # Production build
├── .gitignore                # Git ignore rules
├── README.md                 # Project documentation
└── DEPLOYMENT.md             # This file
```

## Storage Considerations

### Temporary Storage
- Output files are stored in `/tmp` on Azure App Service
- Files are automatically cleaned up after download
- Startup cleanup removes old files
- Manual cleanup endpoint: `POST /api/cleanup`

### Persistent Storage (If Needed)
If you need to store templates or other files persistently:

```bash
# Create storage account
az storage account create --name resumeformatterstorage --resource-group resume-formatter-rg --location eastus --sku Standard_LRS

# Create file share
az storage share create --name templates --account-name resumeformatterstorage

# Mount to App Service
az webapp config storage-account add --resource-group resume-formatter-rg --name resume-formatter-backend --custom-id templates --storage-type AzureFiles --share-name templates --account-name resumeformatterstorage --mount-path /mnt/templates
```

## Monitoring and Logs

```bash
# View logs
az webapp log tail --name resume-formatter-backend --resource-group resume-formatter-rg

# Enable application logging
az webapp log config --name resume-formatter-backend --resource-group resume-formatter-rg --application-logging filesystem --level information
```

## Scaling

```bash
# Scale up (vertical)
az appservice plan update --name resume-formatter-plan --resource-group resume-formatter-rg --sku P1V2

# Scale out (horizontal)
az webapp scale --name resume-formatter-backend --resource-group resume-formatter-rg --instance-count 3
```

## Cost Optimization

1. **Use B1 tier for development**: ~$13/month
2. **Use P1V2 for production**: ~$85/month with better performance
3. **Enable auto-scaling**: Scale based on CPU/memory usage
4. **Use Azure CDN**: Cache static assets
5. **Implement cleanup**: Auto-delete old files (already implemented)

## Troubleshooting

### Issue: Application won't start
- Check startup logs: `az webapp log tail`
- Verify Python version: Should be 3.11
- Check requirements.txt is present

### Issue: File upload fails
- Increase `MAX_CONTENT_LENGTH` in config
- Check disk space in `/tmp`
- Verify CORS settings

### Issue: Slow performance
- Enable Application Insights
- Scale up to higher tier
- Optimize ML model loading (already implemented with caching)

## Security Checklist

- ✅ CORS configured for specific origins
- ✅ File upload validation
- ✅ Secure filename handling
- ✅ Auto-cleanup of temporary files
- ✅ No sensitive data in logs
- ⚠️ Add authentication if needed
- ⚠️ Use Azure Key Vault for secrets
- ⚠️ Enable HTTPS only

## Next Steps

1. Deploy backend to Azure App Service
2. Deploy frontend to Azure Static Web Apps
3. Configure environment variables
4. Test the deployment
5. Set up monitoring and alerts
6. Configure custom domain (optional)
7. Enable auto-scaling (optional)

## Support

For issues or questions:
- Check Azure App Service logs
- Review application logs
- Contact Azure support
