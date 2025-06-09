# Local Development Setup (No Sudo Required)

## 🏠 Running on Your Local PC

Since you're running this on your local PC, you don't need supervisor or sudo commands. Here's how to run everything locally:

## 📋 Prerequisites

1. **Node.js** (v14 or higher) - Download from https://nodejs.org/
2. **Python** (v3.8 or higher) - Download from https://python.org/
3. **MongoDB** - Download from https://www.mongodb.com/try/download/community
4. **Yarn** - Install with: `npm install -g yarn`

## 🚀 Step-by-Step Local Setup

### 1. Start MongoDB
```bash
# Option 1: If MongoDB is installed as a service (Windows)
net start MongoDB

# Option 2: If MongoDB is installed manually
mongod --dbpath C:\data\db  # Windows
mongod --dbpath /usr/local/var/mongodb  # macOS
mongod --dbpath /var/lib/mongodb  # Linux

# Option 3: Using Docker
docker run -d -p 27017:27017 --name mongodb mongo:latest
```

### 2. Configure Environment Files

#### Frontend Environment (`frontend/.env`):
```
REACT_APP_BACKEND_URL=http://localhost:8001
WDS_SOCKET_PORT=3001
```

#### Backend Environment (`backend/.env`):
```
MONGO_URL=mongodb://localhost:27017
DB_NAME=football_analytics
```

### 3. Start Backend (Terminal 1)
```bash
cd backend
pip install -r requirements.txt
python server.py
```

**Expected Output:**
```
INFO:     Uvicorn running on http://0.0.0.0:8001 (Press CTRL+C to quit)
INFO:     Started reloader process [xxxxx] using StatReload
```

### 4. Start Frontend (Terminal 2)
```bash
cd frontend
yarn install
yarn start
```

**Expected Output:**
```
webpack compiled successfully!

You can now view frontend in the browser.
  Local:            http://localhost:3000
  On Your Network:  http://192.168.x.x:3000
```

### 5. Access the Application
- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8001/api
- **API Docs**: http://localhost:8001/docs

## 🔍 Verification Steps

### Test Backend
```bash
# Test if backend is running
curl http://localhost:8001/api/stats
# OR open in browser: http://localhost:8001/api/stats
```

### Test Frontend
1. Open http://localhost:3000 in your browser
2. Open browser console (F12)
3. Look for: `Final API URL: http://localhost:8001/api`
4. Check that no "connection refused" errors appear

## 🛠️ Common Issues & Solutions

### Issue: "Port already in use"
```bash
# Kill process on port 8001 (backend)
lsof -ti:8001 | xargs kill -9  # macOS/Linux
netstat -ano | findstr :8001   # Windows (then kill PID)

# Kill process on port 3000 (frontend)
lsof -ti:3000 | xargs kill -9  # macOS/Linux
netstat -ano | findstr :3000   # Windows (then kill PID)
```

### Issue: "MongoDB connection failed"
```bash
# Check if MongoDB is running
ps aux | grep mongod  # macOS/Linux
tasklist | findstr mongod  # Windows

# Check MongoDB status
mongo --eval "db.adminCommand('ismaster')"
```

### Issue: "Module not found" (Python)
```bash
cd backend
pip install --upgrade pip
pip install -r requirements.txt
```

### Issue: "Command not found" (Node/Yarn)
```bash
# Install Node.js from https://nodejs.org/
# Then install Yarn
npm install -g yarn

# Verify installations
node --version
npm --version
yarn --version
python --version
```

## 📁 Project Structure
```
your-project/
├── backend/
│   ├── .env
│   ├── requirements.txt
│   ├── server.py
│   └── models/
├── frontend/
│   ├── .env
│   ├── package.json
│   ├── src/
│   └── public/
└── README.md
```

## 🎯 Development Workflow

### Daily Development:
1. **Start MongoDB** (if not running as service)
2. **Terminal 1**: `cd backend && python server.py`
3. **Terminal 2**: `cd frontend && yarn start`
4. **Browser**: Open http://localhost:3000

### Making Changes:
- **Backend changes**: Server auto-reloads (FastAPI hot reload)
- **Frontend changes**: Browser auto-refreshes (React hot reload)
- **Database changes**: Use MongoDB Compass or mongo shell

### Stopping Services:
- **Ctrl+C** in each terminal to stop backend/frontend
- **MongoDB**: Stop service or Ctrl+C if running manually

## 🚀 Quick Start Script

Create this file as `start.sh` (macOS/Linux) or `start.bat` (Windows):

### start.sh (macOS/Linux):
```bash
#!/bin/bash
echo "🚀 Starting Football Analytics Suite..."

# Start MongoDB (if not running)
mongod --fork --logpath /var/log/mongodb.log --dbpath /var/lib/mongodb

# Start Backend
cd backend
python server.py &
BACKEND_PID=$!
echo "✅ Backend started on http://localhost:8001"

# Start Frontend
cd ../frontend
yarn start &
FRONTEND_PID=$!
echo "✅ Frontend started on http://localhost:3000"

echo "🎉 Application ready!"
echo "Press Ctrl+C to stop all services"

# Wait for interrupt
trap "kill $BACKEND_PID $FRONTEND_PID; exit" INT
wait
```

### start.bat (Windows):
```batch
@echo off
echo 🚀 Starting Football Analytics Suite...

echo Starting Backend...
cd backend
start "Backend" python server.py

echo Starting Frontend...
cd ..\frontend
start "Frontend" yarn start

echo 🎉 Application ready!
echo Backend: http://localhost:8001
echo Frontend: http://localhost:3000
pause
```

## ✅ Success Checklist

- [ ] MongoDB running on localhost:27017
- [ ] Backend running on localhost:8001
- [ ] Frontend running on localhost:3000
- [ ] No connection errors in browser console
- [ ] Dashboard loads with statistics
- [ ] Can navigate between tabs

You're now ready for local development without any sudo commands!