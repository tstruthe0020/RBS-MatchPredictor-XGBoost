# 🏛️ Referee Bias Score (RBS) Algorithm Guide

## Overview
The Referee Bias Score (RBS) measures referee bias through two statistical approaches:
1. **Performance Differential**: How differently a team performs with vs without a specific referee
2. **Decision Variance**: How consistently/inconsistently a referee makes decisions for a specific team vs their overall patterns

## 🧮 Current Implementation (Performance Differential Method)

### Core Concept
The algorithm compares a team's average performance statistics when a specific referee officiates vs when other referees officiate.

### Formula
```python
# For each team statistic (goals, shots, fouls_drawn, penalties, etc.)
with_referee_avg = mean(team_stats_when_referee_X_officiates)
without_referee_avg = mean(team_stats_when_other_referees_officiate)

performance_differential = with_referee_avg - without_referee_avg
```

### Key Statistics Analyzed
- **Yellow Cards**: Disciplinary actions against the team (negative impact)
- **Red Cards**: Serious disciplinary actions (negative impact)
- **Fouls Committed**: Fouls called against the team (negative impact)
- **Fouls Drawn**: Fouls awarded to the team (positive impact)
- **Penalties Awarded**: Penalties given to the team (positive impact)
- **xG Difference**: Goal-creating advantage (positive impact)
- **Possession Percentage**: Ball control advantage (positive impact)

### Weighted RBS Calculation
```python
# Each component weighted by importance
rbs_components = {
    'yellow_cards': -yellow_diff * weight_yellow,
    'red_cards': -red_diff * weight_red,
    'fouls_committed': -fouls_comm_diff * weight_fouls_comm,
    'fouls_drawn': fouls_drawn_diff * weight_fouls_drawn,
    'penalties_awarded': penalties_diff * weight_penalties,
    'xg_difference': xg_diff * weight_xg,
    'possession_percentage': possession_diff * weight_possession
}

# Sum weighted components
rbs_raw = sum(rbs_components.values())

# Normalize using tanh function to (-1, +1) range
rbs_score = tanh(rbs_raw)
```

## 📊 Enhanced Variance Analysis

### Additional Analysis: Referee Decision Consistency
Beyond performance differential, the system analyzes how consistently a referee makes decisions for a specific team compared to their overall patterns.

#### Variance Ratio Calculation
```python
# Referee's decision variance for specific team
team_variance = variance(referee_decisions_for_team_Y)

# Referee's overall decision variance across all teams  
overall_variance = variance(referee_decisions_all_teams)

# Variance ratio (higher = more inconsistent for this team)
variance_ratio = team_variance / overall_variance
```

#### Decision Categories Analyzed
- **Yellow Cards**: Consistency in disciplinary decisions
- **Red Cards**: Consistency in serious disciplinary actions
- **Fouls Called**: Variance in foul decisions
- **Penalties Awarded**: Consistency in penalty decisions
- **Possession %**: Consistency in game flow management

## 🔍 Detailed Example

### Scenario: Arsenal with Referee Michael Oliver

#### Performance Differential Analysis:
```python
# Arsenal matches WITH Michael Oliver (11 matches)
with_oliver_avg = {
    'yellow_cards': 1.8,      # vs 2.3 with other refs
    'fouls_drawn': 12.7,      # vs 8.9 with other refs  
    'penalties_awarded': 0.18, # vs 0.08 with other refs
    'xg_difference': +0.8,    # vs +0.3 with other refs
    'possession_pct': 61.2    # vs 58.4 with other refs
}

# Calculate differentials
differentials = {
    'yellow_cards': 1.8 - 2.3 = -0.5,        # Fewer cards (positive for team)
    'fouls_drawn': 12.7 - 8.9 = +3.8,        # More fouls drawn (positive)
    'penalties_awarded': 0.18 - 0.08 = +0.10, # More penalties (positive)
    'xg_difference': 0.8 - 0.3 = +0.5,       # Better xG advantage (positive)  
    'possession_pct': 61.2 - 58.4 = +2.8     # More possession (positive)
}

# Apply weights and sum
rbs_raw = (-0.5 * -1.0) + (3.8 * 0.3) + (0.10 * 2.0) + (0.5 * 1.5) + (2.8 * 0.1)
rbs_raw = 0.5 + 1.14 + 0.2 + 0.75 + 0.28 = 2.87

# Normalize  
rbs_score = tanh(2.87) = +0.995 ≈ +1.0
```

#### Variance Analysis:
```python
# Oliver's penalty decisions for Arsenal: [0, 1, 0, 1, 0, 0, 1, 0, 0, 1, 0]
arsenal_penalty_variance = variance([0,1,0,1,0,0,1,0,0,1,0]) = 0.24

# Oliver's penalty decisions across all teams
overall_penalty_variance = variance(all_decisions) = 0.18

penalty_variance_ratio = 0.24 / 0.18 = 1.33

# Interpretation: 33% more variable penalty decisions for Arsenal
```

## 📈 RBS Score Interpretation

### Current Scale (Normalized)
- **RBS > +0.7**: Very strong positive bias (much better performance with referee)
- **RBS +0.3 to +0.7**: Strong positive bias  
- **RBS +0.1 to +0.3**: Moderate positive bias
- **RBS -0.1 to +0.1**: Neutral (no significant bias)
- **RBS -0.1 to -0.3**: Moderate negative bias
- **RBS -0.3 to -0.7**: Strong negative bias
- **RBS < -0.7**: Very strong negative bias (much worse performance with referee)

### Variance Ratio Interpretation
- **Ratio > 2.0**: Much more variable treatment (inconsistent)
- **Ratio 1.5-2.0**: More variable than usual
- **Ratio 0.5-1.5**: Normal variance range
- **Ratio < 0.5**: Much less variable (very consistent treatment)

## 🛠️ Technical Implementation

### Data Segmentation
```python
def segment_team_matches(team_name, referee_name):
    # Get all team matches
    all_team_matches = get_team_matches(team_name)
    
    # Split by referee
    with_referee = [m for m in all_team_matches if m['referee'] == referee_name]
    without_referee = [m for m in all_team_matches if m['referee'] != referee_name]
    
    return with_referee, without_referee
```

### Statistical Significance
```python
def calculate_confidence(matches_with_ref, matches_without_ref):
    if matches_with_ref >= 12 and matches_without_ref >= 20:
        return "Very High"
    elif matches_with_ref >= 8 and matches_without_ref >= 15:
        return "High"  
    elif matches_with_ref >= 5 and matches_without_ref >= 10:
        return "Medium"
    else:
        return "Low"
```

## 🎯 API Access

### Enhanced RBS Analysis Endpoint
```http
GET /api/enhanced-rbs-analysis/{team_name}/{referee_name}
```

**Response:**
```json
{
    "success": true,
    "team_name": "Arsenal",
    "referee_name": "Michael Oliver",
    "standard_rbs": {
        "rbs_score": 0.995,
        "matches_with_ref": 11,
        "matches_without_ref": 47,
        "confidence_level": 85.5,
        "stats_breakdown": {
            "yellow_cards": 0.5,
            "fouls_drawn": 1.14,
            "penalties_awarded": 0.2,
            "xg_difference": 0.75,
            "possession_percentage": 0.28
        }
    },
    "variance_analysis": {
        "variance_ratios": {
            "yellow_cards": 1.12,
            "penalties_awarded": 1.33,
            "fouls_committed": 0.89
        },
        "confidence": "High",
        "interpretation": {
            "yellow_cards": "Normal variance",
            "penalties_awarded": "More variable than usual"
        }
    }
}
```

## 🔄 Usage in Match Prediction

### RBS Application
The RBS score is applied to match predictions as a referee bias adjustment:

```python
def apply_rbs_to_prediction(base_xg, team_name, referee_name):
    rbs_score = get_rbs(team_name, referee_name)
    
    # Conservative scaling (RBS score * 0.2)
    rbs_adjustment = rbs_score * 0.2
    
    return base_xg + rbs_adjustment
```

**Example:**
- Arsenal base xG: 2.5
- RBS with Oliver: +1.0  
- Adjustment: +1.0 × 0.2 = +0.2
- Final xG: 2.5 + 0.2 = 2.7

This methodology provides a robust, statistically grounded measure of referee bias based on actual performance differentials and decision pattern analysis.
