# 🗺️ Azure Deployment Flowchart - Visual Guide

## 📊 Complete Deployment Flow

```
┌─────────────────────────────────────────────────────────────┐
│                    START: YOUR COMPUTER                      │
│                                                              │
│  Project Folder:                                            │
│  ├── Backend/  (Python Flask API)                          │
│  └── frontend/ (React Web App)                             │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│              STEP 1: Install Prerequisites                   │
│                                                              │
│  ✓ Azure CLI                                                │
│  ✓ Git                                                      │
│  ✓ Node.js                                                  │
│  ✓ Python 3.10                                              │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│              STEP 2: Login to Azure                          │
│                                                              │
│  Command: az login                                          │
│  → Opens browser → Login → Success                          │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│         STEP 3: Create Resource Group (Container)            │
│                                                              │
│  Think of it as: A folder in Azure                          │
│  Command: az group create                                   │
│  Result: ✓ resume-formatter-rg created                      │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│         STEP 4: Create App Service Plan (Server)             │
│                                                              │
│  Think of it as: Renting a computer in cloud               │
│  Options:                                                   │
│    • F1 (Free) - Testing only                              │
│    • B1 ($13/month) - Recommended                          │
│  Command: az appservice plan create                         │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│           STEP 5: Deploy Backend (Flask API)                 │
│                                                              │
│  1. Create Web App                                          │
│  2. Configure settings                                      │
│  3. ZIP your Backend folder                                 │
│  4. Upload to Azure                                         │
│  5. Wait 5-10 minutes                                       │
│                                                              │
│  Result: https://your-app.azurewebsites.net                │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│         STEP 6: Create Storage (File Storage)                │
│                                                              │
│  Purpose: Store uploaded resumes & templates                │
│  Creates 3 containers:                                      │
│    • resumes/                                               │
│    • templates/                                             │
│    • output/                                                │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│         STEP 7: Deploy Frontend (React App)                  │
│                                                              │
│  1. Build React app (npm run build)                         │
│  2. Create Static Web App OR Storage Account                │
│  3. Upload build files                                      │
│                                                              │
│  Result: https://your-frontend.azurestaticapps.net         │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│              STEP 8: Connect Frontend to Backend             │
│                                                              │
│  Update .env.production with backend URL                    │
│  Configure CORS in backend                                  │
│  Redeploy if needed                                         │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│                   STEP 9: Test Everything                    │
│                                                              │
│  ✓ Backend health check                                    │
│  ✓ Frontend loads                                           │
│  ✓ Upload template works                                    │
│  ✓ Upload resume works                                      │
│  ✓ Formatting works                                         │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│                    🎉 SUCCESS! 🎉                           │
│                                                              │
│  Your app is now live on Azure!                            │
│  Users can access it from anywhere                          │
└─────────────────────────────────────────────────────────────┘
```

---

## 🏗️ Architecture Diagram

```
                    ┌─────────────────┐
                    │     USERS       │
                    │  (Web Browser)  │
                    └────────┬────────┘
                             │
                             │ HTTPS
                             │
            ┌────────────────┴────────────────┐
            │                                 │
            ▼                                 ▼
    ┌──────────────┐                 ┌──────────────┐
    │   FRONTEND   │                 │   BACKEND    │
    │              │                 │              │
    │  React App   │◄───── API ─────┤  Flask API   │
    │              │      Calls      │              │
    │  Static Web  │                 │  App Service │
    │     App      │                 │              │
    └──────────────┘                 └──────┬───────┘
                                            │
                                            │
                                            ▼
                                    ┌──────────────┐
                                    │   STORAGE    │
                                    │              │
                                    │  • Resumes   │
                                    │  • Templates │
                                    │  • Output    │
                                    └──────────────┘
```

---

## 📋 Deployment Checklist

### Before You Start
- [ ] Azure account created (free $200 credits)
- [ ] Azure CLI installed
- [ ] Git installed
- [ ] Node.js installed
- [ ] Python 3.10 installed

### Backend Deployment
- [ ] Resource group created
- [ ] App Service Plan created
- [ ] Web App created
- [ ] requirements.txt updated
- [ ] startup.sh created
- [ ] Backend code deployed
- [ ] Environment variables set
- [ ] Backend URL accessible
- [ ] Health check returns {"status": "ok"}

### Storage Setup
- [ ] Storage account created
- [ ] Containers created (resumes, templates, output)
- [ ] Connection string added to backend
- [ ] CORS configured

### Frontend Deployment
- [ ] .env.production created with backend URL
- [ ] npm install completed
- [ ] npm run build completed
- [ ] Static Web App created OR Storage static website enabled
- [ ] Build files uploaded
- [ ] Frontend URL accessible

### Final Testing
- [ ] Frontend loads in browser
- [ ] Can upload template
- [ ] Can upload resume
- [ ] Formatting works
- [ ] Can download formatted resume
- [ ] No CORS errors in console

---

## 🎯 Decision Tree: Which Tier to Choose?

```
Are you just testing/learning?
│
├─ YES → Use FREE Tier (F1)
│         • $0/month
│         • 60 min CPU/day
│         • Good for learning
│
└─ NO → Do you expect < 100 users/day?
        │
        ├─ YES → Use BASIC Tier (B1)
        │         • $13/month
        │         • Always on
        │         • Good for small business
        │
        └─ NO → Use STANDARD Tier (S1)
                  • $69/month
                  • Auto-scaling
                  • Good for production
```

---

## 🔄 Deployment Process Timeline

```
┌─────────────────────────────────────────────────────────────┐
│                    ESTIMATED TIME                            │
└─────────────────────────────────────────────────────────────┘

Setup Prerequisites          ⏱️  30 minutes
├─ Install Azure CLI         ⏱️  10 min
├─ Install Git               ⏱️  5 min
├─ Install Node.js           ⏱️  10 min
└─ Login to Azure            ⏱️  5 min

Backend Deployment           ⏱️  45 minutes
├─ Create resources          ⏱️  10 min
├─ Configure settings        ⏱️  10 min
├─ Prepare files             ⏱️  10 min
└─ Deploy & wait             ⏱️  15 min

Storage Setup                ⏱️  15 minutes
├─ Create storage            ⏱️  5 min
├─ Create containers         ⏱️  5 min
└─ Configure CORS            ⏱️  5 min

Frontend Deployment          ⏱️  30 minutes
├─ Build React app           ⏱️  10 min
├─ Create Static Web App     ⏱️  10 min
└─ Deploy files              ⏱️  10 min

Testing & Troubleshooting    ⏱️  30 minutes
├─ Test backend              ⏱️  10 min
├─ Test frontend             ⏱️  10 min
└─ Fix issues                ⏱️  10 min

─────────────────────────────────────────────────────────────
TOTAL TIME (First Time)      ⏱️  2-3 hours
TOTAL TIME (Second Time)     ⏱️  30-45 minutes
```

---

## 💰 Cost Breakdown Visual

```
┌─────────────────────────────────────────────────────────────┐
│                    MONTHLY COSTS                             │
└─────────────────────────────────────────────────────────────┘

FREE TIER (Testing)
├─ App Service (F1)          $0.00
├─ Static Web App            $0.00
├─ Storage (10GB)            $0.18
└─ TOTAL                     $0.18/month ✅

BASIC TIER (Recommended)
├─ App Service (B1)          $13.14
├─ Static Web App            $0.00
├─ Storage (10GB)            $0.18
└─ TOTAL                     $13.32/month ✅

STANDARD TIER (Production)
├─ App Service (S1)          $69.35
├─ Static Web App            $9.00
├─ Storage (50GB)            $0.92
├─ App Insights              $5.75
└─ TOTAL                     $85.02/month
```

---

## 🚨 Common Issues & Solutions

```
┌─────────────────────────────────────────────────────────────┐
│                  TROUBLESHOOTING FLOW                        │
└─────────────────────────────────────────────────────────────┘

Issue: Backend shows "Application Error"
│
├─ Check logs: az webapp log tail
│
├─ Common causes:
│  ├─ Missing dependencies
│  ├─ Wrong Python version
│  ├─ Startup command incorrect
│  └─ Port configuration wrong
│
└─ Solution: Check logs and fix the specific error

─────────────────────────────────────────────────────────────

Issue: Frontend can't connect to Backend
│
├─ Check CORS settings in app.py
│
├─ Check API URL in .env.production
│
└─ Solution: Update CORS to allow frontend origin

─────────────────────────────────────────────────────────────

Issue: "Out of Memory" error
│
├─ Check App Service tier
│
└─ Solution: Upgrade to higher tier (B1 → B2 → S1)

─────────────────────────────────────────────────────────────

Issue: Deployment takes forever
│
├─ Check deployment logs
│
├─ Common causes:
│  ├─ Large dependencies (ML models)
│  ├─ Free tier limitations
│  └─ Network issues
│
└─ Solution: Be patient or upgrade tier
```

---

## 📱 Quick Reference Card

```
╔═══════════════════════════════════════════════════════════╗
║              AZURE DEPLOYMENT QUICK REFERENCE             ║
╠═══════════════════════════════════════════════════════════╣
║                                                           ║
║  LOGIN:           az login                                ║
║  CREATE GROUP:    az group create                         ║
║  CREATE APP:      az webapp create                        ║
║  DEPLOY:          az webapp deployment source config-zip  ║
║  VIEW LOGS:       az webapp log tail                      ║
║  RESTART:         az webapp restart                       ║
║  DELETE ALL:      az group delete                         ║
║                                                           ║
║  BACKEND URL:     https://<app>.azurewebsites.net        ║
║  FRONTEND URL:    https://<app>.azurestaticapps.net      ║
║  PORTAL:          https://portal.azure.com                ║
║                                                           ║
║  COST:            $0-15/month (Basic)                     ║
║  TIME:            2-3 hours (first time)                  ║
║  DIFFICULTY:      ⭐⭐⭐ (Beginner-Friendly)              ║
║                                                           ║
╚═══════════════════════════════════════════════════════════╝
```

---

## 🎓 Learning Path

```
Level 1: Beginner
├─ Deploy using FREE tier
├─ Learn Azure Portal
├─ Understand basic concepts
└─ Test with sample data

Level 2: Intermediate
├─ Upgrade to BASIC tier
├─ Configure custom domain
├─ Setup monitoring
└─ Handle real users

Level 3: Advanced
├─ Setup CI/CD pipeline
├─ Configure auto-scaling
├─ Implement caching
└─ Optimize performance
```

---

**Remember:** 
- Start with FREE tier to learn
- Upgrade when you're comfortable
- Monitor costs daily
- Check logs when issues occur
- Ask for help in Azure community

**You've got this! 🚀**
