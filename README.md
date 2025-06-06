# ⚽ RBS-MatchPredictor-XGBoost

A comprehensive platform for analyzing referee bias in soccer matches and generating sophisticated match predictions using **XGBoost Machine Learning** with **Poisson Distribution Simulation** for advanced analytics.

## 🌟 Features

### 🏛️ Referee Bias Analysis
- **RBS (Referee Bias Score)** calculation for team-referee combinations
- Statistical analysis of referee favoritism patterns  
- Bias detection across multiple competitions and seasons
- Referee assignment optimization tools

### 🚀 XGBoost + Poisson ML Prediction Engine
- **5 trained XGBoost models** using gradient boosting algorithms
- **Enhanced Classification model** for Win/Draw/Loss probability prediction
- **4 XGBoost Regression models** for Home/Away goals and xG prediction
- **60+ engineered features** including team differentials, form trends, referee bias analysis
- **Poisson Distribution Simulation** for detailed scoreline probabilities (0-0, 1-0, 1-1, etc.)
- **Statistical match outcome modeling** using predicted goals as lambda parameters
- Real-time prediction with enhanced model confidence metrics and feature importance

### 📊 Team Performance Analytics
- Comprehensive team statistics aggregation
- Home vs away performance analysis
- Shot conversion rates, penalty efficiency, and xG metrics
- Historical trend analysis and form tracking

### 🔄 RBS Optimization
- Find optimal referee assignments to minimize total bias
- Multi-constraint optimization for fair match officiating
- Scenario analysis and "what-if" modeling

### 🧠 XGBoost Model Management
- **Automated XGBoost model training** on historical match data
- **Model persistence** with joblib for fast prediction serving
- **Enhanced feature engineering** with 60+ features including differentials
- **Continuous learning** capability with retraining on new data
- **Feature scaling** and preprocessing for optimal performance
- **Performance metrics** including log loss and classification reports

## 🏗️ Technical Architecture

- **Frontend**: React with Tailwind CSS
- **Backend**: FastAPI (Python)
- **Database**: MongoDB
- **Machine Learning**: XGBoost gradient boosting, Scikit-learn, joblib model persistence
- **Statistics**: SciPy for Poisson distribution simulation
- **Analytics**: NumPy, Pandas for enhanced feature engineering
- **Deployment**: Docker with Supervisor

## 📚 Documentation

- **[Startup Guide](STARTUP_GUIDE.md)** - Complete setup and usage instructions
- **[RBS Algorithm Guide](RBS_ALGORITHM_GUIDE.md)** - Detailed referee bias calculation methodology  
- **[XGBoost Match Prediction Guide](MATCH_PREDICTION_ALGORITHM_GUIDE.md)** - XGBoost + Poisson ML model architecture and training

## 🛠️ Quick Start Scripts

- **`quick_start.sh`** - Complete system status check and startup guide
- **`train_models.sh`** - Interactive XGBoost model training script

## 🚀 Quick Start

### Using the Startup Script (Recommended)
```bash
# Run the quick start script
./quick_start.sh
```

### Manual Steps
1. **Check services are running:**
   ```bash
   sudo supervisorctl status
   ```

2. **Access the platform:**
   - Frontend: http://localhost:3000
   - API Documentation: http://localhost:8001/docs

3. **Upload your data:**
   - Player statistics CSV
   - Team statistics CSV  
   - Match results CSV

4. **Train XGBoost models (first time only):**
   ```bash
   # Use training script
   ./train_models.sh
   
   # Or train via frontend
   # Navigate to XGBoost + Poisson tab → Click "🚀 Train XGBoost Models"
   ```

5. **Start analyzing:**
   - Calculate comprehensive team stats
   - Analyze referee bias patterns
   - Generate XGBoost + Poisson predictions

## 📈 Key Algorithms

### Referee Bias Score (RBS)
```
RBS = tanh(Σ weighted_statistical_differences)
Normalized score between -1 (negative bias) and +1 (positive bias)
```

### XGBoost + Poisson Prediction Pipeline
```
Enhanced Feature Engineering (60+ features) → 
Standard Scaling → 
XGBoost Models → 
Poisson Simulation → 
Predictions + Scoreline Probabilities
```

### Model Architecture
```python
# 5 trained XGBoost models working together:
- XGBClassifier: Win/Draw/Loss probabilities
- XGBRegressor: Home goals prediction  
- XGBRegressor: Away goals prediction
- XGBRegressor: Home xG prediction
- XGBRegressor: Away xG prediction

# Enhanced with Poisson Distribution:
- Detailed scoreline probabilities (0-0, 1-0, 1-1, 2-0, etc.)
- Most likely scoreline identification
- Statistical match outcome modeling
```

## 🎯 Use Cases

### For Leagues & Organizations
- **Fair officiating** through bias-aware referee assignments
- **XGBoost + Poisson predictions** for broadcast and betting markets
- **Performance analysis** for teams and referees
- **Data-driven decision making** with statistical confidence

### For Analysts & Researchers
- **Quantitative bias measurement** with statistical rigor
- **XGBoost insights** into complex match outcome patterns
- **Enhanced feature importance analysis** showing key prediction factors
- **Poisson distribution modeling** for detailed scoreline analysis
- **Model retraining** capabilities for evolving datasets

### For Teams & Coaches
- **Opponent analysis** with XGBoost-enhanced predictions
- **Performance benchmarking** against trained models
- **Strategic planning** based on detailed scoreline probabilities
- **Tactical insights** from XGBoost feature importance analysis

## 📊 Data Requirements

### Input Data
- **Player Stats**: Goals, assists, xG, shots, fouls, penalties per match
- **Team Stats**: Possession, shots, xG, defensive metrics per match  
- **Match Results**: Scores, referees, dates, competitions

### Output Analytics
- **RBS Scores**: Quantified referee bias measurements
- **XGBoost Predictions**: Goal and xG predictions with enhanced confidence metrics
- **Win/Draw/Loss Probabilities**: Calculated using trained XGBoost classification models
- **Detailed Scoreline Probabilities**: Complete probability distribution (0-0, 1-0, etc.)
- **Enhanced Feature Importance**: Analysis of 60+ features influencing predictions
- **Poisson Parameters**: Lambda values used in statistical modeling

## 🔧 Advanced Configuration

The platform supports extensive customization:

### XGBoost Model Parameters
- **Training data scope** (all data vs specific seasons)
- **Enhanced feature selection** (60+ available features)
- **Model retraining** schedules
- **Prediction confidence thresholds**
- **Poisson simulation parameters**

### RBS Configuration  
- **Statistical weight adjustments**
- **Confidence calculation parameters**
- **Bias detection sensitivity**

## 🚀 XGBoost Model Management

### Training Process
1. **Enhanced Feature Engineering**: Extract 60+ features with differentials and trends
2. **Data Preprocessing**: Standard scaling and validation
3. **XGBoost Training**: Gradient boosting algorithms with optimal hyperparameters
4. **Model Persistence**: Save trained models using joblib
5. **Performance Evaluation**: Log loss, accuracy metrics, and feature importance
6. **Poisson Integration**: Combine XGBoost with statistical distribution modeling

### Available Models
- **XGBoost Classification Model**: Enhanced accuracy for match outcomes
- **XGBoost Regression Models**: Improved predictions for goals and xG
- **Enhanced Feature Count**: 60+ engineered features with differentials
- **Poisson Simulation**: Detailed scoreline probability modeling
- **Training Data**: All available historical matches with enhanced preprocessing

### API Endpoints
- `POST /api/train-ml-models` - Train all XGBoost models
- `GET /api/ml-models/status` - Check XGBoost model status
- `POST /api/ml-models/reload` - Reload saved XGBoost models
- `POST /api/predict-match` - Generate XGBoost + Poisson predictions

## 📞 Support & Development

For detailed setup instructions, algorithm explanations, and troubleshooting guides, refer to the comprehensive documentation in this repository.

---

**Built for accuracy, transparency, and fairness in soccer analytics powered by XGBoost Machine Learning and Poisson Distribution Simulation.**
