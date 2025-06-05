# ⚽ Match Prediction Algorithm Guide

## Overview
This sophisticated algorithm predicts match outcomes using xG-based calculations, team performance metrics, referee bias analysis, and Poisson probability distributions.

## 🧮 Algorithm Flow

```
Base xG → Possession → Fouls → Penalties → PPG → Referee → Final xG → Goals → Probabilities
```

## 📊 Step-by-Step Algorithm

### Step 1: Base xG Calculation
**Formula:**
```python
base_xg = team_avg_shots_per_game × team_avg_xg_per_shot
```

**Data Sources:**
- `shots_total`: Average shots per game (home/away context)
- `xg_per_shot`: Historical shooting efficiency
- Values aggregated from player stats or team stats

**Example:**
```
Arsenal Home: 14.2 shots/game × 0.18 xG/shot = 2.56 base xG
```

### Step 2: Possession Adjustment
**Formula:**
```python
possession_factor = 1 + (possession_pct - 50) × 0.01
adjusted_xg = base_xg × possession_factor
```

**Logic:**
- Teams with more possession get more attacking opportunities
- 60% possession = 1.1x multiplier
- 40% possession = 0.9x multiplier

**Example:**
```
Arsenal: 55% possession → factor = 1.05
Adjusted xG = 2.56 × 1.05 = 2.69
```

### Step 3: Fouls Drawn Adjustment
**Formula:**
```python
fouls_factor = 1 + (fouls_drawn - baseline) × fouls_multiplier
# baseline = 10 (league average)
# fouls_multiplier = 0.02 (configurable)
```

**Logic:**
- Teams that draw more fouls create more scoring opportunities
- Set pieces and penalty chances increase with fouls drawn

**Example:**
```
Arsenal: 12 fouls drawn/game → factor = 1 + (12-10) × 0.02 = 1.04
Adjusted xG = 2.69 × 1.04 = 2.80
```

### Step 4: Penalty Factor Addition
**Formula:**
```python
penalty_xg = penalties_per_game × penalty_xg_value × penalty_conversion_rate
# penalty_xg_value = 0.79 (historical average)
```

**Calculation:**
```python
penalty_xg = team_penalties_avg × 0.79 × team_penalty_conversion_rate
total_xg = adjusted_xg + penalty_xg
```

**Example:**
```
Arsenal: 0.15 penalties/game × 0.79 × 0.85 conversion = +0.10 xG
Total xG = 2.80 + 0.10 = 2.90
```

### Step 5: Team Quality (PPG) Adjustment
**Formula:**
```python
ppg_difference = home_team_ppg - away_team_ppg
ppg_adjustment = ppg_difference × 0.15
```

**Application:**
```python
home_xg += ppg_adjustment
away_xg -= ppg_adjustment
```

**Example:**
```
Arsenal PPG: 2.1, Chelsea PPG: 1.8
PPG difference: +0.3
Adjustment: 0.3 × 0.15 = +0.045 for Arsenal, -0.045 for Chelsea
```

### Step 6: Referee Bias Adjustment
**Formula:**
```python
referee_adjustment = rbs_score × 0.2
final_xg = total_xg + referee_adjustment
```

**Logic:**
- RBS (Referee Bias Score) ranges from -3 to +3
- Scaling factor of 0.2 converts to xG adjustment
- RBS of +2.5 = +0.5 xG boost

**Example:**
```
Arsenal with Referee Smith: RBS = +1.2
Referee adjustment = 1.2 × 0.2 = +0.24 xG
Final xG = 2.90 + 0.24 = 3.14
```

### Step 7: Goal Conversion
**Formula:**
```python
predicted_goals = final_xg × goals_per_xg_ratio
```

**goals_per_xg_ratio:**
- Historical efficiency: actual_goals ÷ xg_accumulated
- Accounts for clinical finishing vs. poor finishing teams

**Example:**
```
Arsenal goals/xG ratio: 1.15 (clinical finishers)
Predicted goals = 3.14 × 1.15 = 3.61 goals
```

### Step 8: Probability Calculation (Poisson Distribution)
**Formula:**
```python
# For each possible score combination (0-10 goals each)
prob_home_i_away_j = poisson(i, λ_home) × poisson(j, λ_away)

# Where λ = predicted goals for each team
home_win_prob = Σ prob(home > away)
draw_prob = Σ prob(home = away)  
away_win_prob = Σ prob(home < away)
```

**Implementation:**
```python
from scipy.stats import poisson

for home_goals in range(11):
    for away_goals in range(11):
        prob = poisson.pmf(home_goals, pred_home) * poisson.pmf(away_goals, pred_away)
        if home_goals > away_goals:
            home_win_prob += prob
        elif home_goals == away_goals:
            draw_prob += prob
        else:
            away_win_prob += prob
```

## 🎯 Complete Example Calculation

### Match: Arsenal (Home) vs Chelsea (Away)
**Referee:** Michael Oliver

#### Arsenal Calculation:
```
1. Base xG: 14.2 shots × 0.18 xG/shot = 2.56
2. Possession: 55% → ×1.05 = 2.69
3. Fouls: 12/game → ×1.04 = 2.80  
4. Penalties: 0.15 × 0.79 × 0.85 = +0.10 → 2.90
5. PPG: +0.045 → 2.945
6. Referee: RBS +1.2 → +0.24 → 3.185
7. Conversion: ×1.15 = 3.66 predicted goals
```

#### Chelsea Calculation:
```
1. Base xG: 12.8 shots × 0.16 xG/shot = 2.05
2. Possession: 45% → ×0.95 = 1.95
3. Fouls: 9/game → ×0.96 = 1.87
4. Penalties: 0.08 × 0.79 × 0.75 = +0.05 → 1.92
5. PPG: -0.045 → 1.875  
6. Referee: RBS -0.8 → -0.16 → 1.715
7. Conversion: ×0.98 = 1.68 predicted goals
```

#### Probability Calculation:
```python
Arsenal: 3.66 predicted goals
Chelsea: 1.68 predicted goals

Using Poisson distribution:
- Arsenal win: 74.2%
- Draw: 18.1%  
- Chelsea win: 7.7%
```

## ⚙️ Configuration Parameters

### Adjustable Factors
```python
class PredictionConfig:
    possession_factor = 0.01        # Possession impact
    fouls_drawn_baseline = 10       # League average fouls
    fouls_drawn_factor = 0.02       # Fouls impact multiplier
    penalty_xg_value = 0.79         # xG value of penalties
    ppg_factor = 0.15               # Team quality impact
    referee_bias_factor = 0.2       # RBS scaling factor
```

### Home/Away Context
- All statistics calculated separately for home and away performance
- Home advantage built into historical data
- Venue-specific team performance patterns preserved

## 📈 Advanced Features

### Confidence Factors
```python
confidence = (home_matches + away_matches) / 2 × confidence_multiplier
```

### Quality Checks
- Minimum match requirements for reliable predictions
- Data freshness validation
- Statistical significance testing

### Edge Case Handling
```python
# Zero predicted goals
if predicted_goals <= 0:
    if home_goals <= 0 and away_goals <= 0:
        return [33.33, 33.33, 33.34]  # Equal probability
    # Adjust probabilities based on which team has zero
```

## 🔍 Data Requirements

### Team Statistics (per team, per venue)
- `shots_total`: Total shots per game
- `xg_per_shot`: Expected goals per shot
- `possession_pct`: Average possession percentage
- `fouls_drawn`: Fouls drawn per game
- `penalties_awarded`: Penalties per game
- `penalty_conversion_rate`: Penalty success rate
- `goals_per_xg`: Finishing efficiency ratio
- `ppg`: Points per game

### Match Context
- Home/away status
- Referee assignment
- Team form and recent performance

## 🎲 Probability Interpretation

### Match Outcome Probabilities
- **High Confidence**: Difference > 50% between outcomes
- **Medium Confidence**: Clear favorite (60-70% probability)
- **Low Confidence**: Even match (40-60% range)

### Typical Probability Ranges
- **Dominant vs Weak**: 80%+ / 15% / 5%
- **Strong vs Average**: 65% / 25% / 10%
- **Even Match**: 40% / 30% / 30%
- **Upset Likely**: 25% / 30% / 45%

## 🔄 Algorithm Validation

### Backtesting Methods
1. **Historical Validation**: Test on past matches
2. **Cross-Validation**: Split data into training/testing sets
3. **Rolling Validation**: Predict future matches as they occur

### Performance Metrics
- **Prediction Accuracy**: Correct outcome percentage
- **Probability Calibration**: Reliability of probability estimates
- **Log Loss**: Measure of probability prediction quality
- **Brier Score**: Accuracy of probabilistic predictions

---

This algorithm combines multiple statistical approaches to provide comprehensive, data-driven match predictions with full transparency and mathematical rigor.
