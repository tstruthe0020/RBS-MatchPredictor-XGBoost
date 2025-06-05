# 🏛️ Referee Bias Score (RBS) Algorithm Guide

## Overview
The Referee Bias Score (RBS) quantifies the statistical bias a referee shows toward specific teams based on historical match outcomes compared to expected performance.

## 🧮 RBS Calculation Formula

### Core Formula
```
RBS = Σ(Actual_Points - Expected_Points) / Total_Matches
```

### Detailed Calculation Steps

#### Step 1: Expected Points Calculation
For each match between Team A and Referee R:

```python
# Team quality difference
quality_diff = team_ppg - opponent_ppg

# Expected points based on team quality
if quality_diff > 0.5:
    expected_points = 2.1  # Strong team expected to win
elif quality_diff > 0.2:
    expected_points = 1.8  # Moderate favorite
elif quality_diff > -0.2:
    expected_points = 1.5  # Even match
elif quality_diff > -0.5:
    expected_points = 1.2  # Slight underdog
else:
    expected_points = 0.9  # Strong underdog
```

#### Step 2: Actual Points
Standard soccer points system:
- **Win**: 3 points
- **Draw**: 1 point  
- **Loss**: 0 points

#### Step 3: RBS Calculation
```python
rbs_sum = 0
total_matches = 0

for match in team_referee_matches:
    actual_points = get_match_points(match)
    expected_points = calculate_expected_points(match)
    rbs_sum += (actual_points - expected_points)
    total_matches += 1

rbs_score = rbs_sum / total_matches if total_matches > 0 else 0
```

## 📊 RBS Score Interpretation

### Scale and Meaning
- **RBS > +1.0**: Strong positive bias (referee favors this team)
- **RBS +0.5 to +1.0**: Moderate positive bias
- **RBS -0.5 to +0.5**: Neutral (no significant bias)
- **RBS -0.5 to -1.0**: Moderate negative bias  
- **RBS < -1.0**: Strong negative bias (referee disfavors this team)

### Statistical Significance
- **Minimum 5 matches** required for meaningful RBS calculation
- **10+ matches** recommended for statistical reliability
- **Confidence increases** with more historical data

## 🔍 Detailed Example

### Scenario: Team Arsenal with Referee John Smith

**Historical Matches:**

| Match | Arsenal PPG | Opponent PPG | Quality Diff | Expected Points | Actual Result | Actual Points | Difference |
|-------|-------------|--------------|--------------|-----------------|---------------|---------------|------------|
| 1     | 2.1         | 1.3          | +0.8         | 2.1             | Win (3-1)     | 3             | +0.9       |
| 2     | 2.1         | 2.0          | +0.1         | 1.5             | Draw (1-1)    | 1             | -0.5       |
| 3     | 2.1         | 1.8          | +0.3         | 1.8             | Win (2-0)     | 3             | +1.2       |
| 4     | 2.1         | 2.2          | -0.1         | 1.5             | Loss (0-2)    | 0             | -1.5       |
| 5     | 2.1         | 1.5          | +0.6         | 2.1             | Win (4-1)     | 3             | +0.9       |

**RBS Calculation:**
```
RBS = (0.9 + (-0.5) + 1.2 + (-1.5) + 0.9) / 5
RBS = 1.0 / 5 = +0.2
```

**Interpretation:** Slight positive bias - Arsenal performs marginally better than expected with this referee.

## 🛠️ Technical Implementation

### Database Queries
```python
# Get team-referee match history
matches = db.matches.find({
    "$or": [
        {"home_team": team_name, "referee": referee_name},
        {"away_team": team_name, "referee": referee_name}
    ]
})

# Calculate team PPG at time of each match
team_ppg = calculate_historical_ppg(team_name, match_date)
opponent_ppg = calculate_historical_ppg(opponent_name, match_date)
```

### Quality Difference Thresholds
```python
def calculate_expected_points(quality_diff):
    if quality_diff > 0.5:
        return 2.1      # 70% win probability
    elif quality_diff > 0.2:
        return 1.8      # 60% win probability  
    elif quality_diff > -0.2:
        return 1.5      # 50% win probability (even)
    elif quality_diff > -0.5:
        return 1.2      # 40% win probability
    else:
        return 0.9      # 30% win probability
```

## 📈 RBS Applications

### 1. Referee Assignment Optimization
```python
# Find referee with minimal bias for matchup
optimal_referee = min(available_referees, 
                     key=lambda r: abs(get_rbs(home_team, r) + get_rbs(away_team, r)))
```

### 2. Match Prediction Enhancement
```python
# Apply RBS bias to xG predictions
home_bias = get_rbs(home_team, referee) * 0.2
away_bias = get_rbs(away_team, referee) * 0.2

adjusted_home_xg = base_home_xg + home_bias
adjusted_away_xg = base_away_xg + away_bias
```

### 3. Fair Play Analysis
- Identify referees with consistently high absolute RBS values
- Monitor referee performance across different team types
- Detect unusual patterns in match outcomes

## 🎯 RBS Confidence Factors

### Factors Affecting Reliability
1. **Sample Size**: More matches = higher confidence
2. **Recency**: Recent matches weighted more heavily
3. **Competition Level**: Different leagues may have different patterns
4. **Match Importance**: Cup finals vs. regular season matches

### Confidence Calculation
```python
def calculate_rbs_confidence(matches_count, avg_match_age_days):
    sample_confidence = min(matches_count / 10.0, 1.0)
    recency_confidence = max(0.5, 1.0 - (avg_match_age_days / 365.0))
    return sample_confidence * recency_confidence
```

## 🔄 RBS Updates and Maintenance

### When to Recalculate
- After each match day
- When new historical data is added
- Seasonally for comprehensive review

### Data Quality Considerations
- Ensure consistent team naming
- Verify referee name standardization
- Handle team relocations/renamings
- Account for referee career changes

## 📊 Advanced RBS Metrics

### RBS Variance
Measures consistency of referee bias:
```python
rbs_variance = sum((match_diff - rbs_mean)² for match_diff in match_differences) / matches_count
```

### Weighted RBS
Gives more weight to recent matches:
```python
weighted_rbs = sum(match_diff * weight for match_diff, weight in zip(differences, weights)) / sum(weights)
```

### RBS Trend
Tracks how referee bias changes over time:
```python
recent_rbs = calculate_rbs(last_10_matches)
overall_rbs = calculate_rbs(all_matches)
rbs_trend = recent_rbs - overall_rbs
```

---

The RBS system provides a quantitative foundation for understanding and mitigating referee bias in soccer, contributing to fairer match outcomes and more accurate predictions.
