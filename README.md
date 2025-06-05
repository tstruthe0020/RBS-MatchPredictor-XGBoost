# ⚽ Soccer Referee Bias Analysis Platform

A comprehensive platform for analyzing referee bias in soccer matches and generating sophisticated match predictions using advanced xG-based algorithms.

## 🌟 Features

### 🏛️ Referee Bias Analysis
- **RBS (Referee Bias Score)** calculation for team-referee combinations
- Statistical analysis of referee favoritism patterns  
- Bias detection across multiple competitions and seasons
- Referee assignment optimization tools

### 🎯 Match Prediction Engine
- **8-step sophisticated algorithm** using xG, possession, fouls, penalties, team quality, and referee bias
- **Poisson probability distributions** for win/draw/loss percentages
- Real-time prediction with detailed algorithmic breakdown
- Home/away context preservation throughout calculations

### 📊 Team Performance Analytics
- Comprehensive team statistics aggregation
- Home vs away performance analysis
- Shot conversion rates, penalty efficiency, and xG metrics
- Historical trend analysis and form tracking

### 🔄 RBS Optimization
- Find optimal referee assignments to minimize total bias
- Multi-constraint optimization for fair match officiating
- Scenario analysis and "what-if" modeling

## 🏗️ Technical Architecture

- **Frontend**: React with Tailwind CSS
- **Backend**: FastAPI (Python)
- **Database**: MongoDB
- **Analytics**: NumPy, SciPy, Scikit-learn
- **Deployment**: Docker with Supervisor

## 📚 Documentation

- **[Startup Guide](STARTUP_GUIDE.md)** - Complete setup and usage instructions
- **[RBS Algorithm Guide](RBS_ALGORITHM_GUIDE.md)** - Detailed referee bias calculation methodology  
- **[Match Prediction Guide](MATCH_PREDICTION_ALGORITHM_GUIDE.md)** - Step-by-step algorithm explanation

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

4. **Start analyzing:**
   - Calculate comprehensive team stats
   - Analyze referee bias patterns
   - Generate match predictions

## 📈 Key Algorithms

### Referee Bias Score (RBS)
```
RBS = Σ(Actual_Points - Expected_Points) / Total_Matches
```

### Match Prediction Pipeline
```
Base xG → Possession → Fouls → Penalties → PPG → Referee → Final xG → Goals → Probabilities
```

### Probability Calculation
```python
# Poisson distribution for match outcomes
P(home_win) = Σ P(home_goals > away_goals)
P(draw) = Σ P(home_goals = away_goals)  
P(away_win) = Σ P(home_goals < away_goals)
```

## 🎯 Use Cases

### For Leagues & Organizations
- **Fair officiating** through bias-aware referee assignments
- **Match prediction** for broadcast and betting markets
- **Performance analysis** for teams and referees

### For Analysts & Researchers
- **Quantitative bias measurement** with statistical rigor
- **Predictive modeling** using comprehensive feature sets
- **Data-driven insights** into match dynamics

### For Teams & Coaches
- **Opponent analysis** with referee-adjusted expectations
- **Performance benchmarking** against statistical models
- **Strategic planning** based on historical patterns

## 📊 Data Requirements

### Input Data
- **Player Stats**: Goals, assists, xG, shots, fouls, penalties per match
- **Team Stats**: Possession, shots, xG, defensive metrics per match  
- **Match Results**: Scores, referees, dates, competitions

### Output Analytics
- **RBS Scores**: Quantified referee bias measurements
- **Match Predictions**: Goal predictions and outcome probabilities
- **Performance Metrics**: Comprehensive team and player statistics

## 🔧 Advanced Configuration

The platform supports extensive customization through configuration parameters:

- **Possession impact factors**
- **Fouls drawn multipliers**  
- **Penalty xG values**
- **Team quality adjustments**
- **Referee bias scaling**

## 📞 Support & Development

For detailed setup instructions, algorithm explanations, and troubleshooting guides, refer to the comprehensive documentation in this repository.

---

**Built for accuracy, transparency, and fairness in soccer analytics.**
