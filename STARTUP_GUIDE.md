# 🚀 RBS-MatchPredictor-XGBoost - Startup Guide

## Overview
This platform analyzes referee bias in soccer matches and provides sophisticated match predictions using **XGBoost Machine Learning with Poisson Distribution Simulation**. It consists of a React frontend, FastAPI backend, MongoDB database, and trained XGBoost models for enhanced match prediction.

## 🏗️ System Architecture

```
Frontend (React) ←→ Backend (FastAPI) ←→ Database (MongoDB)
     :3000              :8001              :27017
                          ↓
               XGBoost Models (joblib)
                 /app/backend/models/
                  (xgb_*.pkl files)
```

## 📋 Prerequisites

- Docker environment (already provided in this setup)
- Python 3.8+
- Node.js 18+
- MongoDB
- XGBoost and Scikit-learn for ML models

## 🚀 Quick Start

### 1. Check Service Status
```bash
sudo supervisorctl status
```
All services should show `RUNNING`:
- backend
- frontend  
- mongodb

### 2. Restart Services (if needed)
```bash
# Restart all services
sudo supervisorctl restart all

# Or restart individually
sudo supervisorctl restart backend
sudo supervisorctl restart frontend
sudo supervisorctl restart mongodb
```

### 3. Access the Application
- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8001
- **API Documentation**: http://localhost:8001/docs

### 4. Check Service Logs
```bash
# Backend logs
tail -f /var/log/supervisor/backend.*.log

# Frontend logs  
tail -f /var/log/supervisor/frontend.*.log

# MongoDB logs
tail -f /var/log/supervisor/mongodb.*.log
```

## 🚀 XGBoost Model Setup (First Time Only)

### 1. Check XGBoost Model Status
Navigate to the **XGBoost + Poisson** tab in the frontend to check if models are trained.

### 2. Train XGBoost Models (Required on First Run)
```bash
# Via API
curl -X POST "http://localhost:8001/api/train-ml-models"

# Or use the frontend button "🚀 Train XGBoost Models"
```

### 3. Verify Model Training
The system will train 5 XGBoost models:
- **XGBClassifier**: Win/Draw/Loss prediction with enhanced accuracy
- **4 XGBRegressors**: Home/Away goals and xG prediction

Models are saved in `/app/backend/models/` directory with `xgb_` prefix.

### 4. XGBoost Model Management Commands
```bash
# Check XGBoost model status
curl -X GET "http://localhost:8001/api/ml-models/status"

# Reload XGBoost models from disk
curl -X POST "http://localhost:8001/api/ml-models/reload"
```

## 📊 Data Upload Process

### Required Data Files

#### 1. Player Stats CSV
**Required columns:**
- `match_id`: Unique identifier for each match
- `player_name`: Player's full name
- `team_name`: Team name (must be consistent)
- `is_home`: Boolean (true/false) indicating if team is playing at home
- `goals`: Number of goals scored
- `assists`: Number of assists
- `yellow_cards`: Number of yellow cards received
- `fouls_committed`: Number of fouls committed
- `fouls_drawn`: Number of fouls drawn
- `xg`: Expected goals value
- `shots_total`: Total shots taken (optional but recommended)
- `shots_on_target`: Shots on target (optional but recommended)
- `penalty_attempts`: Number of penalty attempts (optional)
- `penalty_goals`: Number of penalty goals (optional)

#### 2. Team Stats CSV
**Required columns:**
- `match_id`: Unique identifier (must match player stats)
- `team_name`: Team name (must be consistent)
- `is_home`: Boolean indicating home/away status
- `goals`: Goals scored in the match
- `xg`: Expected goals for the match
- `shots_total`: Total shots taken
- `shots_on_target`: Shots on target
- `possession_pct`: Possession percentage (0-100)
- `fouls_committed`: Total fouls committed
- `fouls_drawn`: Total fouls drawn
- `penalties_awarded`: Number of penalties awarded
- `penalty_goals`: Goals scored from penalties
- `opponent`: Opponent team name

#### 3. Match Results CSV
**Required columns:**
- `match_id`: Unique identifier (must match other files)
- `home_team`: Home team name
- `away_team`: Away team name
- `home_score`: Final home team score
- `away_score`: Final away team score
- `referee`: Referee name
- `date`: Match date (YYYY-MM-DD format)
- `competition`: Competition/league name (optional)
- `season`: Season identifier (optional)

### Upload Steps

1. **Navigate to Data Upload Tab**
2. **Upload files in this order:**
   - Player Stats first
   - Team Stats second  
   - Match Results last
3. **Wait for processing confirmation**
4. **Calculate comprehensive team stats** (button in Team Performance tab)
5. **Train XGBoost models** (Navigate to XGBoost + Poisson tab → Click "🚀 Train XGBoost Models")

## 🔧 System Maintenance

### Recalculate Team Statistics
After uploading new data:
```bash
curl -X POST "http://localhost:8001/api/calculate-comprehensive-team-stats"
```

### Retrain XGBoost Models (After New Data)
When you have new match data, retrain the XGBoost models:
```bash
# Via API
curl -X POST "http://localhost:8001/api/train-ml-models"

# Or use the frontend button in XGBoost + Poisson tab
```

### Reset Database (if needed)
```bash
# Access MongoDB
mongo
use soccer_analysis
db.dropDatabase()
```

### Update Dependencies
```bash
# Backend (includes ML libraries)
cd /app/backend
pip install -r requirements.txt

# Frontend  
cd /app/frontend
yarn install
```

## 🧠 Understanding the Platform

### Core Features
1. **Referee Bias Analysis**: Calculate RBS scores for team-referee combinations
2. **XGBoost + Poisson Match Prediction**: Predict match outcomes using trained XGBoost models with Poisson simulation
3. **Team Performance Analysis**: Detailed team statistics and trends
4. **RBS Optimization**: Find optimal referee assignments to minimize bias
5. **XGBoost Model Management**: Train, reload, and monitor enhanced prediction models

### Key Metrics
- **RBS (Referee Bias Score)**: Measures referee favoritism toward specific teams (normalized -1 to +1)
- **xG (Expected Goals)**: Statistical measure of shot quality
- **PPG (Points Per Game)**: Team quality indicator
- **XGBoost Confidence**: Enhanced model prediction confidence and feature importance
- **Enhanced Feature Engineering**: 60+ features including differentials, form, h2h, referee bias
- **Poisson Parameters**: Lambda values used for detailed scoreline probability calculations

### XGBoost + Poisson Machine Learning Models
- **XGBClassifier**: Predicts Win/Draw/Loss with enhanced accuracy and probability percentages
- **Home Goals XGBRegressor**: Predicts expected goals for home team using gradient boosting
- **Away Goals XGBRegressor**: Predicts expected goals for away team using gradient boosting
- **Home xG XGBRegressor**: Predicts expected xG for home team with enhanced features
- **Away xG XGBRegressor**: Predicts expected xG for away team with enhanced features
- **Poisson Simulation**: Converts XGBoost predictions into detailed scoreline probabilities

## 🔍 Troubleshooting

### Common Issues

#### Backend Won't Start
```bash
# Check logs
tail -n 50 /var/log/supervisor/backend.*.log

# Common fixes
sudo supervisorctl restart backend
pip install -r /app/backend/requirements.txt

# Check XGBoost model directory
ls -la /app/backend/models/xgb_*.pkl
```

#### XGBoost Models Not Working
```bash
# Check XGBoost model status
curl -X GET "http://localhost:8001/api/ml-models/status"

# Retrain XGBoost models if needed
curl -X POST "http://localhost:8001/api/train-ml-models"

# Check XGBoost model files exist
ls -la /app/backend/models/xgb_*.pkl
```

#### Frontend Build Errors
```bash
# Check logs
tail -n 50 /var/log/supervisor/frontend.*.log

# Common fixes
cd /app/frontend
yarn install
sudo supervisorctl restart frontend
```

#### Database Connection Issues
```bash
# Check MongoDB status
sudo supervisorctl status mongodb

# Restart if needed
sudo supervisorctl restart mongodb
```

#### Data Upload Fails
- Verify CSV format matches required columns exactly
- Check for special characters in team/player names
- Ensure match_id consistency across files
- Upload files in correct order (Player → Team → Match)

#### XGBoost Prediction Errors
- Ensure XGBoost models are trained (check XGBoost + Poisson tab)
- Verify teams and referees exist in database
- Check that sufficient historical data is available
- Retrain XGBoost models if dataset has changed significantly

### Performance Optimization

#### For Large Datasets
- Upload data in smaller batches
- Monitor memory usage during XGBoost training
- Consider training XGBoost models overnight for large datasets
- Use model reload instead of retraining for temporary issues

#### XGBoost Model Performance
- Retrain XGBoost models when adding significant new data
- Monitor enhanced accuracy metrics in training results
- Consider feature selection for improved XGBoost performance
- Review Poisson simulation parameters for optimal scoreline predictions

## 📚 Next Steps

1. **Upload your data** following the CSV format guidelines
2. **Train XGBoost models** for enhanced match prediction (first time setup)
3. **Explore team performance** to understand your dataset
4. **Calculate RBS scores** for referee bias analysis
5. **Make XGBoost + Poisson predictions** using the trained models
6. **Analyze detailed scoreline probabilities** from Poisson simulation
7. **Optimize referee assignments** using the RBS optimization tool
8. **Monitor XGBoost model performance** and retrain as needed

## 🆘 Support

For technical issues:
1. Check the logs first
2. Verify XGBoost models are trained (XGBoost + Poisson tab)
3. Verify data format requirements
4. Ensure all services are running
5. Review this startup guide

### XGBoost-Specific Support
- **Model Training Issues**: Check system memory and available data
- **Prediction Errors**: Verify XGBoost model status and feature availability
- **Performance Problems**: Consider XGBoost model retraining or feature selection
- **Poisson Simulation Issues**: Check lambda parameter calculations and model outputs

---

**Important**: Always backup your data before making significant changes to the system. XGBoost model training may take several minutes depending on dataset size and provides enhanced accuracy over traditional Random Forest approaches.
