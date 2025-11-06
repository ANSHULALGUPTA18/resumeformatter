# Resume Formatter - Quick Start Guide 🚀

## Prerequisites

Before starting, ensure you have:
- ✅ **Docker Desktop** installed and running
- ✅ **Python 3.8+** installed
- ✅ **Node.js 14+** installed

---

## Step 1: Start OnlyOffice Document Server (Required for Editing)

### Option A: Using the Startup Script (Recommended)
```bash
# Double-click or run:
start-onlyoffice.bat
```

### Option B: Manual Docker Command
```bash
docker run -d -p 8080:80 --name onlyoffice-documentserver onlyoffice/documentserver:latest
```

### Option C: Using Docker Compose
```bash
docker-compose up -d
```

**Wait for OnlyOffice to start** (30-60 seconds). Check status:
```bash
curl http://localhost:8080/healthcheck
```

---

## Step 2: Start Backend Server

### Windows:
```bash
cd Backend
venv\Scripts\activate
python app.py
```

### macOS/Linux:
```bash
cd Backend
source venv/bin/activate
python app.py
```

**Expected Output:**
```
======================================================================
🎯 RESUME FORMATTER - BACKEND SERVER
======================================================================
✅ API running on http://127.0.0.1:5000
✅ Network access: http://192.168.0.104:5000
✅ React frontend: http://localhost:3000
✅ OnlyOffice Document Server: http://localhost:8080
======================================================================
```

---

## Step 3: Start Frontend

Open a **new terminal**:

```bash
cd frontend
npm start
```

**Expected Output:**
```
Compiled successfully!

Local:            http://localhost:3000
On Your Network:  http://192.168.x.x:3000
```

---

## Step 4: Access the Application

Open your browser and go to:
```
http://localhost:3000
```

---

## Common Issues & Solutions

### Issue 1: "list index out of range" Error ✅ FIXED

**Status:** This has been fixed in the latest version.

**What was the problem:**
- The code was trying to access list elements without checking if they exist
- Happened when parsing resume data with unexpected formats

**Solution Applied:**
- Added safety checks before accessing list elements
- Files fixed: `word_formatter.py`, `advanced_resume_parser.py`

---

### Issue 2: Docker Not Running

**Error:** "Docker is not running"

**Solution:**
1. Open Docker Desktop
2. Wait for it to fully start (green icon in system tray)
3. Run the startup script again

---

### Issue 3: Port 8080 Already in Use

**Error:** "Port 8080 is already allocated"

**Solution:**
```bash
# Stop the existing container
docker stop onlyoffice-documentserver
docker rm onlyoffice-documentserver

# Start fresh
start-onlyoffice.bat
```

---

### Issue 4: OnlyOffice Not Accessible

**Error:** Cannot access http://localhost:8080

**Check:**
```bash
# Check if container is running
docker ps

# Check container logs
docker logs onlyoffice-documentserver

# Restart container
docker restart onlyoffice-documentserver
```

---

### Issue 5: Backend Port 5000 Conflict

**Error:** "Port 5000 already in use"

**Solution (Windows):**
```bash
# Find process using port 5000
netstat -ano | findstr :5000

# Kill the process (replace <PID> with actual process ID)
taskkill /PID <PID> /F
```

---

## Testing the Application

### 1. Upload a Template
- Click "Upload Template"
- Select a DOCX file with placeholder sections
- Give it a name (e.g., "Georgia Template")

### 2. Upload Resumes
- Click "Upload Resumes"
- Select one or more PDF/DOCX resume files
- Click "Format"

### 3. Download Results
- Wait for processing to complete
- Click "Download" for each formatted resume
- Or click "Download All" for batch download

---

## Stopping the Application

### Stop Backend
Press `Ctrl+C` in the backend terminal

### Stop Frontend
Press `Ctrl+C` in the frontend terminal

### Stop OnlyOffice
```bash
docker stop onlyoffice-documentserver
```

### Stop Everything
```bash
# Stop all containers
docker-compose down

# Or stop just OnlyOffice
docker stop onlyoffice-documentserver
```

---

## Performance Tips

1. **First Run is Slower**
   - OnlyOffice takes 30-60 seconds to start initially
   - ML models download on first use (~90MB)

2. **Batch Processing**
   - Upload multiple resumes at once for faster processing
   - System processes them in parallel

3. **Keep Docker Running**
   - Leave OnlyOffice container running between sessions
   - Restart is much faster than initial start

---

## Architecture Overview

```
┌─────────────────┐
│   Browser       │
│  localhost:3000 │
└────────┬────────┘
         │
         ▼
┌─────────────────┐      ┌──────────────────┐
│  React Frontend │─────▶│  Flask Backend   │
│  (Port 3000)    │      │  (Port 5000)     │
└─────────────────┘      └────────┬─────────┘
                                  │
                                  ▼
                         ┌──────────────────┐
                         │  OnlyOffice      │
                         │  Document Server │
                         │  (Port 8080)     │
                         └──────────────────┘
```

---

## Need Help?

- **Check logs:** Backend terminal shows detailed processing logs
- **Check Docker:** `docker logs onlyoffice-documentserver`
- **Check browser console:** F12 → Console tab
- **Read full README:** See `README.md` for detailed documentation

---

**Last Updated:** November 3, 2025
**Version:** 2.1.0
**Status:** ✅ All Issues Fixed
