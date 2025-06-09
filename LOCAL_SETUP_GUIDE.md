# Local Development Setup Guide

## ✅ Configuration Updated for Local Development

The Football Analytics Suite is now configured to run locally on your PC.

## 📋 Prerequisites

1. **Node.js** (v14 or higher)
2. **Python** (v3.8 or higher) 
3. **MongoDB** (v4.4 or higher)
4. **Yarn** package manager

## 🔧 Configuration Details

### Frontend Configuration
- **File**: `/app/frontend/.env`
- **Backend URL**: `http://localhost:8001`
- **Frontend Port**: `3000` (default)

### Backend Configuration  
- **File**: `/app/backend/.env`
- **MongoDB URL**: `mongodb://localhost:27017`
- **Backend Port**: `8001`
- **Database**: `test_database`

## 🚀 Running the Application Locally

### 1. Start MongoDB
```bash
# On Windows (if MongoDB is installed as service)
net start MongoDB

# On macOS/Linux
sudo systemctl start mongod
# OR
mongod --dbpath /path/to/your/db
```

### 2. Start Backend (FastAPI)
```bash
cd /app/backend
pip install -r requirements.txt
python server.py
```
**Expected output**: `Uvicorn running on http://0.0.0.0:8001`

### 3. Start Frontend (React)
```bash
cd /app/frontend  
yarn install
yarn start
```
**Expected output**: `webpack compiled successfully`

## 🌐 Access Points

- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8001/api
- **Backend Docs**: http://localhost:8001/docs (Swagger UI)

## 🔍 Verification Steps

### 1. Test Backend Connectivity
```bash
curl http://localhost:8001/api/stats
```
**Expected**: JSON response with database statistics

### 2. Test Frontend-Backend Communication
1. Open browser to http://localhost:3000
2. Open browser console (F12)
3. Look for successful API calls in Network tab
4. Check Dashboard tab loads correctly

## 📊 Features Available

### ✅ Core Features
- Dashboard with statistics
- Upload Data (CSV files)
- Standard Match Prediction  
- Enhanced XGBoost Prediction with Starting XI
- Regression Analysis
- Configuration Management

### 🚀 Advanced Features (New)
- **PDF Export** for predictions
- **Enhanced RBS Analysis** (team-referee combinations)
- **Team Performance Analysis** (comprehensive metrics)
- **Configuration Management** (prediction & RBS configs)
- **Advanced AI Optimization** (4 specialized algorithms)

## 🛠️ Troubleshooting

### Backend Issues
- **Port 8001 in use**: Change port in `server.py`
- **MongoDB connection failed**: Ensure MongoDB is running
- **Module not found**: Run `pip install -r requirements.txt`

### Frontend Issues  
- **Port 3000 in use**: React will prompt to use different port
- **API connection failed**: Verify `REACT_APP_BACKEND_URL` in `.env`
- **Dependencies missing**: Run `yarn install`

### Database Issues
- **Empty data**: Upload sample data via Upload Data tab
- **Connection timeout**: Check MongoDB service status

## 📁 Important Files

### Configuration Files
- `/app/frontend/.env` - Frontend environment variables
- `/app/backend/.env` - Backend environment variables

### Key Source Files
- `/app/frontend/src/App.js` - Main React application
- `/app/frontend/src/advanced-features.js` - Advanced features module
- `/app/backend/server.py` - FastAPI backend server

## 🎯 Ready for Development

The application is now fully configured for local development with:
- ✅ Localhost URLs configured
- ✅ All advanced features implemented  
- ✅ Backend-frontend communication verified
- ✅ All dependencies properly set up

You can now run the Football Analytics Suite locally on your PC!