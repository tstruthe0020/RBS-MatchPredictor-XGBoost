# ⚽ Soccer Referee Bias Analysis Platform

A comprehensive platform for analyzing referee bias in soccer matches and generating sophisticated match predictions using **Machine Learning algorithms** and advanced analytics.

## 🌟 Features

### 🏛️ Referee Bias Analysis
- **RBS (Referee Bias Score)** calculation for team-referee combinations
- Statistical analysis of referee favoritism patterns  
- Bias detection across multiple competitions and seasons
- Referee assignment optimization tools

### 🤖 ML-Based Match Prediction Engine
- **5 trained Machine Learning models** using Random Forest algorithms
- **Classification model** for Win/Draw/Loss probability prediction
- **4 Regression models** for Home/Away goals and xG prediction
- **45+ engineered features** including team stats, form, referee bias, and historical data
- Real-time prediction with model confidence metrics and feature importance

### 📊 Team Performance Analytics
- Comprehensive team statistics aggregation
- Home vs away performance analysis
- Shot conversion rates, penalty efficiency, and xG metrics
- Historical trend analysis and form tracking

### 🔄 RBS Optimization
- Find optimal referee assignments to minimize total bias
- Multi-constraint optimization for fair match officiating
- Scenario analysis and "what-if" modeling

### 🧠 ML Model Management
- **Automated model training** on historical match data
- **Model persistence** with joblib for fast prediction serving
- **Continuous learning** capability with retraining on new data
- **Feature scaling** and preprocessing for optimal performance

## 🏗️ Technical Architecture

- **Frontend**: React with Tailwind CSS
- **Backend**: FastAPI (Python)
- **Database**: MongoDB
- **Machine Learning**: Scikit-learn (Random Forest), joblib model persistence
- **Analytics**: NumPy, SciPy, Pandas for feature engineering
- **Deployment**: Docker with Supervisor

## 📚 Documentation

- **[Startup Guide](STARTUP_GUIDE.md)** - Complete setup and usage instructions
- **[RBS Algorithm Guide](RBS_ALGORITHM_GUIDE.md)** - Detailed referee bias calculation methodology  
- **[ML Match Prediction Guide](MATCH_PREDICTION_ALGORITHM_GUIDE.md)** - Machine Learning model architecture and training

## 🚀 Quick Start

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

4. **Train ML models (first time only):**
   - Navigate to Match Prediction tab
   - Click "🧠 Train ML Models"
   - Wait for training completion

5. **Start analyzing:**
   - Calculate comprehensive team stats
   - Analyze referee bias patterns
   - Generate ML-powered match predictions

## 📈 Key Algorithms

### Referee Bias Score (RBS)
```
RBS = tanh(Σ weighted_statistical_differences)
Normalized score between -1 (negative bias) and +1 (positive bias)
```

### ML Match Prediction Pipeline
```
Feature Engineering (45+ features) → 
Standard Scaling → 
Random Forest Models → 
Predictions + Probabilities
```

### Model Architecture
```python
# 5 trained models working together:
- Classification: Win/Draw/Loss probabilities
- Regression: Home goals prediction  
- Regression: Away goals prediction
- Regression: Home xG prediction
- Regression: Away xG prediction
```

## 🎯 Use Cases

### For Leagues & Organizations
- **Fair officiating** through bias-aware referee assignments
- **ML-powered match prediction** for broadcast and betting markets
- **Performance analysis** for teams and referees
- **Data-driven decision making** with statistical confidence

### For Analysts & Researchers
- **Quantitative bias measurement** with statistical rigor
- **Machine Learning insights** into match outcome patterns
- **Feature importance analysis** showing key prediction factors
- **Model retraining** capabilities for evolving datasets

### For Teams & Coaches
- **Opponent analysis** with ML-enhanced predictions
- **Performance benchmarking** against trained models
- **Strategic planning** based on historical patterns and ML insights

## 📊 Data Requirements

### Input Data
- **Player Stats**: Goals, assists, xG, shots, fouls, penalties per match
- **Team Stats**: Possession, shots, xG, defensive metrics per match  
- **Match Results**: Scores, referees, dates, competitions

### Output Analytics
- **RBS Scores**: Quantified referee bias measurements
- **ML Predictions**: Goal and xG predictions with confidence metrics
- **Win/Draw/Loss Probabilities**: Calculated using trained classification models
- **Feature Importance**: Analysis of which factors most influence predictions

## 🔧 Advanced Configuration

The platform supports extensive customization:

### ML Model Parameters
- **Training data scope** (all data vs specific seasons)
- **Feature selection** (45+ available features)
- **Model retraining** schedules
- **Prediction confidence thresholds**

### RBS Configuration  
- **Statistical weight adjustments**
- **Confidence calculation parameters**
- **Bias detection sensitivity**

## 🤖 ML Model Management

### Training Process
1. **Feature Engineering**: Extract 45+ features from historical data
2. **Data Preprocessing**: Standard scaling and validation
3. **Model Training**: Random Forest algorithms with cross-validation
4. **Model Persistence**: Save trained models using joblib
5. **Performance Evaluation**: Accuracy metrics and feature importance

### Available Models
- **Classification Model**: ~75% accuracy for match outcomes
- **Regression Models**: R² scores 0.28-1.0 for goals and xG prediction
- **Feature Count**: 45+ engineered features
- **Training Data**: All available historical matches

### API Endpoints
- `POST /api/train-ml-models` - Train all models
- `GET /api/ml-models/status` - Check model status
- `POST /api/ml-models/reload` - Reload saved models
- `POST /api/predict-match` - Generate ML predictions

## 📞 Support & Development

For detailed setup instructions, algorithm explanations, and troubleshooting guides, refer to the comprehensive documentation in this repository.

---

**Built for accuracy, transparency, and fairness in soccer analytics powered by Machine Learning.**
