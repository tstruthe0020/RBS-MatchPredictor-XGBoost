# 🚀 Soccer Referee Bias Analysis Platform - Startup Guide

## Overview
This platform analyzes referee bias in soccer matches and provides sophisticated match predictions using **Machine Learning algorithms**. It consists of a React frontend, FastAPI backend, MongoDB database, and trained ML models for match prediction.

## 🏗️ System Architecture

```
Frontend (React) ←→ Backend (FastAPI) ←→ Database (MongoDB)
     :3000              :8001              :27017
                          ↓
                   ML Models (joblib)
                 /app/backend/models/
```

## 📋 Prerequisites

- Docker environment (already provided in this setup)
- Python 3.8+
- Node.js 18+
- MongoDB
- Scikit-learn for ML models

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

## 🤖 ML Model Setup (First Time Only)

### 1. Check ML Model Status
Navigate to the **Match Prediction** tab in the frontend to check if models are trained.

### 2. Train ML Models (Required on First Run)
```bash
# Via API
curl -X POST "http://localhost:8001/api/train-ml-models"

# Or use the frontend button "🧠 Train ML Models"
```

### 3. Verify Model Training
The system will train 5 models:
- **Classification**: Win/Draw/Loss prediction (~75% accuracy)
- **4 Regression models**: Home/Away goals and xG prediction

Models are saved in `/app/backend/models/` directory.

### 4. Model Management Commands
```bash
# Check model status
curl -X GET "http://localhost:8001/api/ml-models/status"

# Reload models from disk
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
5. **Train ML models** (Navigate to Match Prediction tab → Click "🧠 Train ML Models")

## 🔧 System Maintenance

### Recalculate Team Statistics
After uploading new data:
```bash
curl -X POST "http://localhost:8001/api/calculate-comprehensive-team-stats"
```

### Retrain ML Models (After New Data)
When you have new match data, retrain the models:
```bash
# Via API
curl -X POST "http://localhost:8001/api/train-ml-models"

# Or use the frontend button in Match Prediction tab
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
2. **ML Match Prediction**: Predict match outcomes using trained Random Forest models
3. **Team Performance Analysis**: Detailed team statistics and trends
4. **RBS Optimization**: Find optimal referee assignments to minimize bias
5. **ML Model Management**: Train, reload, and monitor prediction models

### Key Metrics
- **RBS (Referee Bias Score)**: Measures referee favoritism toward specific teams (normalized -1 to +1)
- **xG (Expected Goals)**: Statistical measure of shot quality
- **PPG (Points Per Game)**: Team quality indicator
- **ML Confidence**: Model prediction confidence and feature importance
- **Feature Engineering**: 45+ features including form, h2h, referee bias, team stats

### Machine Learning Models
- **Classification Model**: Predicts Win/Draw/Loss with probability percentages
- **Home Goals Regression**: Predicts expected goals for home team
- **Away Goals Regression**: Predicts expected goals for away team  
- **Home xG Regression**: Predicts expected xG for home team
- **Away xG Regression**: Predicts expected xG for away team

## 🔍 Troubleshooting

### Common Issues

#### Backend Won't Start
```bash
# Check logs
tail -n 50 /var/log/supervisor/backend.*.log

# Common fixes
sudo supervisorctl restart backend
pip install -r /app/backend/requirements.txt

# Check ML model directory
ls -la /app/backend/models/
```

#### ML Models Not Working
```bash
# Check model status
curl -X GET "http://localhost:8001/api/ml-models/status"

# Retrain models if needed
curl -X POST "http://localhost:8001/api/train-ml-models"

# Check model files exist
ls -la /app/backend/models/*.pkl
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

#### Prediction Errors
- Ensure ML models are trained (check Match Prediction tab)
- Verify teams and referees exist in database
- Check that sufficient historical data is available
- Retrain models if dataset has changed significantly

### Performance Optimization

#### For Large Datasets
- Upload data in smaller batches
- Monitor memory usage during ML training
- Consider training models overnight for large datasets
- Use model reload instead of retraining for temporary issues

#### ML Model Performance
- Retrain models when adding significant new data
- Monitor model accuracy metrics in training results
- Consider feature selection for improved performance

## 📚 Next Steps

1. **Upload your data** following the CSV format guidelines
2. **Train ML models** for match prediction (first time setup)
3. **Explore team performance** to understand your dataset
4. **Calculate RBS scores** for referee bias analysis
5. **Make ML predictions** using the trained models
6. **Optimize referee assignments** using the RBS optimization tool
7. **Monitor model performance** and retrain as needed

## 🆘 Support

For technical issues:
1. Check the logs first
2. Verify ML models are trained (Match Prediction tab)
3. Verify data format requirements
4. Ensure all services are running
5. Review this startup guide

### ML-Specific Support
- **Model Training Issues**: Check system memory and available data
- **Prediction Errors**: Verify model status and feature availability
- **Performance Problems**: Consider model retraining or feature selection

---

**Important**: Always backup your data before making significant changes to the system. ML model training may take several minutes depending on dataset size.
