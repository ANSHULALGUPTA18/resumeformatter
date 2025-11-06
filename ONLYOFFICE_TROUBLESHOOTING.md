# 🔧 OnlyOffice Connection Issues - Troubleshooting

## ✅ **Latest Update - November 3, 2025 12:36 PM**

**Status:** OnlyOffice container restarted with proper configuration.
**Action Required:** Wait 60-90 seconds for full initialization, then try again.

---

## 🚨 **Current Errors (Before Fix)**

1. **"The document could not be saved"** - OnlyOffice can't reach Flask to save
2. **"Download failed"** - OnlyOffice can't download the document from Flask
3. **WebSocket 502 errors** - Internal services not fully initialized

**Root causes identified:**
1. OnlyOffice internal services (port 8000) not fully started
2. WebSocket connections failing before services ready
3. Document service needs 60-90 seconds to initialize

---

## ✅ **Fixes Applied**

1. **Network Configuration** - Changed to `host.docker.internal` ✅
2. **Docker Host Mapping** - Added `extra_hosts` in docker-compose.yml ✅
3. **Container Restart** - Fresh start with proper configuration ✅
4. **Verified Connectivity** - Backend is accessible from Docker ✅

---

## ⏳ **Current Status**

OnlyOffice is starting up. Services initialize in this order:
1. **0-30s:** Container starts, nginx loads
2. **30-60s:** Document service starts (port 8000)
3. **60-90s:** WebSocket services ready
4. **90s+:** Fully operational

**What to do now:**
1. ⏰ Wait 90 seconds (grab a coffee ☕)
2. 🔄 Refresh the browser page
3. 📝 Try clicking "Click to edit" again
4. ✅ Document should load successfully

---

## 🔍 **Step 1: Check Network Configuration**

Run this diagnostic script:

```powershell
python check_network.py
```

This will show:
- Your local IP addresses
- Flask backend status
- OnlyOffice status
- Network accessibility
- Recommended configuration

---

## 🛠️ **Step 2: Fix Based on Results**

### **Option A: Windows Firewall is Blocking (Most Common)**

**Symptom**: `check_network.py` shows Flask is NOT accessible from network IP

**Fix**:

1. **Open Windows Firewall Settings**
   - Press `Win + R`
   - Type: `wf.msc`
   - Press Enter

2. **Create Inbound Rule**
   - Click "Inbound Rules" → "New Rule"
   - Select "Port" → Next
   - Select "TCP" → Specific local ports: `5000`
   - Select "Allow the connection"
   - Check all profiles (Domain, Private, Public)
   - Name: "Flask Backend - Port 5000"
   - Finish

3. **Restart Flask**
   ```powershell
   # Stop Flask (Ctrl+C)
   python app.py
   ```

4. **Test Again**
   ```powershell
   python check_network.py
   ```

---

### **Option B: Use Different Docker Network Mode**

If firewall fix doesn't work, restart OnlyOffice with host network mode:

```powershell
# Stop current container
docker stop onlyoffice-documentserver
docker rm onlyoffice-documentserver

# Start with network=host mode (Linux) or port mapping (Windows)
docker run -i -t -d -p 8080:80 -p 443:443 ^
  -e JWT_ENABLED=false ^
  --add-host=host.docker.internal:host-gateway ^
  --name onlyoffice-documentserver ^
  onlyoffice/documentserver
```

---

### **Option C: Manual IP Configuration**

If automatic IP detection fails, manually set your IP:

1. **Find your IP**:
   ```powershell
   ipconfig
   ```
   Look for "IPv4 Address" (e.g., `192.168.1.100`)

2. **Edit `onlyoffice_routes.py`**:
   
   Find this line (around line 54):
   ```python
   backend_url = f"http://{local_ip}:5000"
   ```
   
   Replace with your actual IP:
   ```python
   backend_url = "http://192.168.1.100:5000"  # Use YOUR IP!
   ```

3. **Restart Flask**

---

## 🧪 **Step 3: Test the Fix**

### **Test 1: Check Flask is accessible**

Open browser:
```
http://YOUR_IP:5000/api/health
```

Should return: `{"status": "ok"}`

### **Test 2: Check OnlyOffice can reach Flask**

From inside OnlyOffice container:

```powershell
# Enter container
docker exec -it onlyoffice-documentserver bash

# Test connection
curl http://host.docker.internal:5000/api/health
# OR
curl http://YOUR_IP:5000/api/health

# Exit
exit
```

Should return: `{"status": "ok"}`

### **Test 3: Try editing a resume**

1. Restart Flask: `python app.py`
2. Refresh browser
3. Click on a resume
4. OnlyOffice should load
5. Make an edit
6. Press Ctrl+S
7. Should save successfully! ✅

---

## 📊 **Understanding the Network Flow**

```
┌─────────────────────────────────────────┐
│    Your Browser                          │
│    (localhost:3000)                      │
│                                          │
│    Loads OnlyOffice editor               │
└─────────────────────────────────────────┘
         ↓
    Connects to
         ↓
┌─────────────────────────────────────────┐
│    OnlyOffice Container                  │
│    (localhost:8080)                      │
│                                          │
│    Needs to reach Flask to:              │
│    1. Download document                  │
│    2. Save edited document               │
│                                          │
│    Uses: host.docker.internal:5000       │
│    OR: YOUR_IP:5000                      │
└─────────────────────────────────────────┘
         ↓
    Must reach
         ↓
┌─────────────────────────────────────────┐
│    Flask Backend                         │
│    (YOUR_IP:5000)                        │
│                                          │
│    Must be accessible from Docker!       │
│    ⚠️  Firewall must allow port 5000     │
└─────────────────────────────────────────┘
```

---

## ✅ **Verification Checklist**

After applying fixes, verify:

- [ ] `python check_network.py` shows all green ✅
- [ ] Flask accessible at `http://YOUR_IP:5000/api/health`
- [ ] OnlyOffice running: `docker ps`
- [ ] Windows Firewall allows port 5000
- [ ] Flask console shows: "✅ Using local IP: X.X.X.X"
- [ ] Browser loads OnlyOffice editor
- [ ] Can make edits
- [ ] Can save (Ctrl+S) without errors
- [ ] Flask console shows: "✅ Document saved successfully"

---

## 🔥 **Quick Fix Commands**

```powershell
# 1. Check network
python check_network.py

# 2. Allow Flask in firewall
# (Use GUI: wf.msc → New Rule → Port 5000)

# 3. Restart OnlyOffice
docker restart onlyoffice-documentserver

# 4. Restart Flask
cd Backend
python app.py

# 5. Refresh browser
# Press F5

# 6. Test editing
# Click resume → Edit → Ctrl+S
```

---

## 📞 **Still Not Working?**

### **Check Flask Console**

When you click on a resume, you should see:
```
✅ Using local IP: 192.168.1.100
📡 OnlyOffice will use: http://192.168.1.100:5000
📡 Callback URL: http://192.168.1.100:5000/api/onlyoffice/callback/...
```

### **Check Browser Console (F12)**

Should see:
```
✅ OnlyOffice config loaded: {...}
✅ OnlyOffice editor initialized!
```

### **Check OnlyOffice Logs**

```powershell
docker logs onlyoffice-documentserver --tail 50
```

Look for connection errors or callback failures.

---

## 🎯 **Expected Working State**

**Flask Console:**
```
✅ Using local IP: 192.168.1.100
📡 OnlyOffice will use: http://192.168.1.100:5000
📥 OnlyOffice callback received for formatted_xxx.docx: status=2
📥 Downloading edited document from: http://...
✅ Document saved successfully: formatted_xxx.docx (12345 bytes)
```

**Browser:**
- OnlyOffice editor loads
- Can type and edit
- Ctrl+S saves without errors
- No error popups

**Result:**
- ✅ Edit documents
- ✅ Save changes
- ✅ Download edited versions
- ✅ No connection errors

---

**Run `python check_network.py` first to diagnose the issue!** 🔍
