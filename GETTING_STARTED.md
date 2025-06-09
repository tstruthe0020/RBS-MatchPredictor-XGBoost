# Getting Started - First Time Setup

## ✅ **Current Status: Backend Started Successfully!**

The messages you saw are completely normal:

### 1. "XGBoost models not found - will need to train first" ✅
- **This is expected** on first run
- Models need to be trained with your data before predictions work
- **Solution**: Upload data and train models (steps below)

### 2. Deprecation Warning ✅  
- **Fixed!** Updated to use modern FastAPI lifespan handlers
- This was just a warning and didn't affect functionality

## 🚀 **Next Steps to Get Everything Working:**

### Step 1: Verify Backend is Running
Your backend should now be running on: **http://localhost:8001**

Test it:
```bash
# Open this URL in your browser:
http://localhost:8001/docs
```
You should see the FastAPI documentation interface.

### Step 2: Start Frontend (New Terminal)
```bash
cd C:\Users\theos\RBS-MatchPredictor-XGBoost\frontend
yarn install
yarn start
```

**Expected Output:**
```
webpack compiled successfully!
Local: http://localhost:3000
```

### Step 3: Access the Application
Open your browser to: **http://localhost:3000**

You should see the Football Analytics Suite dashboard.

### Step 4: Upload Data and Train Models

1. **Go to Upload Data Tab**
   - Click "📁 Upload Data" in the navigation
   
2. **Upload CSV Files** (if you have them):
   - Match Data (match results with teams, scores, referees)
   - Team Stats (team-level statistics)  
   - Player Stats (individual player statistics)

3. **Train ML Models**:
   - Go to "🚀 Enhanced XGBoost" tab
   - Click "🧠 Train" button in the model status section
   - Wait for training to complete

## 📊 **Sample Data (If You Don't Have Data Yet)**

If you don't have data files yet, you can:

1. **Use the Application Without Data**: 
   - Most features will work but show empty results
   - You can explore the interface and configuration options

2. **Create Sample Data**:
   - The app has debug endpoints to generate sample data
   - Go to: http://localhost:8001/docs
   - Look for endpoints starting with `/debug/`

## 🔍 **Troubleshooting:**

### Backend Issues:
- **"Address already in use"**: Kill any process on port 8001
- **MongoDB errors**: Make sure MongoDB is running on localhost:27017
- **Import errors**: Run `pip install -r requirements.txt` again

### Frontend Issues:
- **Port 3000 busy**: Kill process on port 3000 or choose different port
- **"Connection refused"**: Make sure backend is running on port 8001
- **Yarn not found**: Install with `npm install -g yarn`

### MongoDB Not Running:
```bash
# Windows (if installed as service):
net start MongoDB

# Windows (manual):
mongod --dbpath C:\data\db

# Check if running:
mongo --eval "db.adminCommand('ismaster')"
```

## ✅ **Success Checklist:**

- [ ] Backend running on http://localhost:8001 (✅ Done!)
- [ ] Frontend running on http://localhost:3000
- [ ] MongoDB running on localhost:27017
- [ ] Can access application in browser
- [ ] No "connection refused" errors in browser console

## 🎯 **What You Can Do Now:**

### Without Data:
- ✅ Explore all 10 tabs and UI features
- ✅ Test configuration management
- ✅ View API documentation
- ✅ Try advanced features (they'll show empty results)

### With Data:
- ✅ Upload your CSV files
- ✅ Train XGBoost models
- ✅ Generate match predictions
- ✅ Analyze referee bias
- ✅ Export PDF reports
- ✅ Use all advanced features

## 📖 **Next Steps:**

1. **Get Frontend Running**: Follow Step 2 above
2. **Upload Some Data**: Use the Upload Data tab
3. **Train Models**: Use the Enhanced XGBoost tab
4. **Start Analyzing**: Try predictions and analysis features

You're doing great! The backend is running successfully. Now just get the frontend started and you'll have the full application running locally.