# Soccer Referee Bias Analysis Platform - Startup Scripts

This directory contains several Windows batch files to help you easily start and manage the application.

## 📁 Available Scripts

### 🚀 **initial_start.bat** - First Time Setup
**Use this for your very first run**
- Checks Python and Node.js installation
- Installs all backend dependencies (pip install -r requirements.txt)
- Installs all frontend dependencies (yarn install)
- Checks environment configuration
- Starts both backend and frontend servers
- Provides setup completion confirmation

### ⚡ **quick_start.bat** - Regular Startup
**Use this for all subsequent runs**
- Quickly starts both backend and frontend servers
- Checks for existing running services
- No dependency installation (assumes already done)
- Faster startup time
- Includes helpful usage tips

### 🏭 **supervisor_start.bat** - Production Startup
**Use this if supervisor is available**
- Uses supervisor to manage services
- More robust service management
- Better for production environments
- Falls back to quick_start.bat if supervisor unavailable

### 🛑 **stop_services.bat** - Stop All Services
**Use this to cleanly shut down the application**
- Stops supervisor services if available
- Finds and stops processes on ports 3000 and 8001
- Provides process cleanup
- Helps prevent port conflicts

## 🚀 Getting Started

### First Time Setup:
1. **Double-click `initial_start.bat`**
2. Wait for dependency installation
3. Both servers will start automatically
4. Application opens at http://localhost:3000

### Regular Use:
1. **Double-click `quick_start.bat`**
2. Servers start quickly
3. Application opens at http://localhost:3000

### Stopping the Application:
1. **Double-click `stop_services.bat`**
2. All services will be stopped cleanly

## 📋 Prerequisites

Before running these scripts, ensure you have:

- **Python 3.8+** installed and in PATH
- **Node.js 16+** installed and in PATH  
- **Yarn** package manager installed (`npm install -g yarn`)
- **Git** (if cloning from repository)

## 🔧 Configuration

The scripts expect these files to exist:
- `backend/requirements.txt` - Python dependencies
- `backend/.env` - Backend environment variables
- `frontend/package.json` - Node.js dependencies  
- `frontend/.env` - Frontend environment variables

## 🌐 Default URLs

- **Backend API:** http://localhost:8001
- **Frontend:** http://localhost:3000
- **API Documentation:** http://localhost:8001/docs

## 🚨 Troubleshooting

### Port Already in Use:
```bash
# Run stop_services.bat first
# Then try starting again
```

### Dependencies Failed to Install:
```bash
# Check Python/Node.js installation
python --version
node --version
yarn --version

# Run initial_start.bat again
```

### Services Won't Start:
```bash
# Check if ports are free
netstat -an | find ":3000"
netstat -an | find ":8001"

# Stop any conflicting processes
# Run stop_services.bat
```

## 📊 Application Features

Once started, you can:
- **📤 Upload Data:** Multi-dataset CSV upload
- **📈 Analyze:** Comprehensive regression analysis
- **⚙️ Optimize:** Formula optimization with statistical insights
- **🎯 Predict:** Match outcome predictions
- **📋 Configure:** Algorithm parameter tuning

## 🔄 Updates

After pulling updates from the repository:
1. Run `initial_start.bat` to install any new dependencies
2. Use `quick_start.bat` for subsequent runs

---

**Need Help?** Check the application logs in the command windows that open, or review the console output for error messages.