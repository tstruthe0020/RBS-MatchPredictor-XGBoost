# 🏛️ Referee Bias Score (RBS) Algorithm Guide

## Overview
The Referee Bias Score (RBS) measures referee bias through two statistical approaches:
1. **Performance Differential**: How differently a team performs with vs without a specific referee
2. **Decision Variance**: How consistently/inconsistently a referee makes decisions for a specific team vs their overall patterns

## 🧮 RBS Calculation Methodology

### Approach 1: Team Performance Differential

#### Core Concept
Compare team's average performance statistics when a specific referee officiates vs when other referees officiate.

#### Formula
```python
# For each team statistic (goals, shots, fouls_drawn, penalties, etc.)
with_referee_avg = mean(team_stats_when_referee_X_officiates)
without_referee_avg = mean(team_stats_when_other_referees_officiate)

performance_differential = (with_referee_avg - without_referee_avg) / without_referee_avg * 100
```

#### Key Statistics Analyzed
- **Offensive Stats**: Goals, shots, xG, penalties awarded
- **Disciplinary Stats**: Yellow cards, red cards, fouls called against
- **Possession Stats**: Possession percentage, pass completion
- **Defensive Stats**: Fouls drawn, opponent yellow cards

### Approach 2: Referee Decision Variance Analysis

#### Core Concept
Compare how consistently a referee makes decisions for a specific team vs their overall decision patterns.

#### Formula
```python
# Referee's overall decision variance across all teams
overall_variance = variance(referee_decisions_all_teams)

# Referee's decision variance for specific team
team_specific_variance = variance(referee_decisions_for_team_Y)

# Variance ratio (higher = more inconsistent for this team)
variance_ratio = team_specific_variance / overall_variance
```

#### Decision Categories
- **Fouls Called**: Per game variance in foul decisions
- **Cards Issued**: Variance in disciplinary actions
- **Penalties Awarded**: Consistency in penalty decisions
- **Advantage Played**: How often play continues vs stops

## 📊 Detailed Implementation

### Step 1: Data Segmentation
```python
def segment_team_matches(team_name, referee_name):
    # Matches with specific referee
    with_referee = matches.filter(
        (home_team == team_name OR away_team == team_name) AND 
        referee == referee_name
    )
    
    # Matches with other referees
    without_referee = matches.filter(
        (home_team == team_name OR away_team == team_name) AND 
        referee != referee_name
    )
    
    return with_referee, without_referee
```

### Step 2: Performance Differential Calculation
```python
def calculate_performance_differential(team_name, referee_name):
    with_ref, without_ref = segment_team_matches(team_name, referee_name)
    
    differentials = {}
    stats_to_analyze = [
        'goals', 'shots_total', 'xg', 'penalties_awarded', 
        'fouls_drawn', 'yellow_cards_against', 'possession_pct'
    ]
    
    for stat in stats_to_analyze:
        with_avg = mean(with_ref[stat])
        without_avg = mean(without_ref[stat])
        
        if without_avg > 0:
            differential = (with_avg - without_avg) / without_avg * 100
        else:
            differential = 0
            
        differentials[stat] = differential
    
    return differentials
```

### Step 3: Variance Analysis
```python
def calculate_referee_variance_bias(team_name, referee_name):
    # Get referee's decisions for specific team
    team_decisions = get_referee_decisions_for_team(referee_name, team_name)
    
    # Get referee's decisions for all other teams
    overall_decisions = get_referee_decisions_overall(referee_name)
    
    variance_ratios = {}
    decision_types = ['fouls_called', 'yellow_cards', 'penalties_awarded']
    
    for decision in decision_types:
        team_variance = variance(team_decisions[decision])
        overall_variance = variance(overall_decisions[decision])
        
        if overall_variance > 0:
            variance_ratios[decision] = team_variance / overall_variance
        else:
            variance_ratios[decision] = 1.0
    
    return variance_ratios
```

### Step 4: Combined RBS Score
```python
def calculate_comprehensive_rbs(team_name, referee_name):
    # Performance differential component
    performance_diff = calculate_performance_differential(team_name, referee_name)
    
    # Variance analysis component  
    variance_ratios = calculate_referee_variance_bias(team_name, referee_name)
    
    # Weight and combine components
    performance_score = weighted_average(performance_diff.values(), weights=[...])
    variance_score = weighted_average(variance_ratios.values(), weights=[...])
    
    # Final RBS (normalized to -5 to +5 scale)
    rbs_score = (performance_score * 0.7 + variance_score * 0.3) / 20
    
    return {
        'rbs_score': rbs_score,
        'performance_differential': performance_diff,
        'variance_analysis': variance_ratios,
        'sample_size_with_ref': len(with_referee_matches),
        'sample_size_without_ref': len(without_referee_matches)
    }
```

## 🔍 Detailed Example

### Scenario: Arsenal with Referee Michael Oliver

#### Data Collection:
```python
# Arsenal matches WITH Michael Oliver (last 2 seasons)
with_oliver = [
    {goals: 2.1, shots: 16, xg: 2.3, penalties: 0.2, fouls_drawn: 12},
    {goals: 1.8, shots: 14, xg: 1.9, penalties: 0.1, fouls_drawn: 15},
    {goals: 2.5, shots: 18, xg: 2.8, penalties: 0.3, fouls_drawn: 11},
    # ... 8 more matches
]

# Arsenal matches WITHOUT Michael Oliver
without_oliver = [
    {goals: 1.6, shots: 13, xg: 1.8, penalties: 0.1, fouls_drawn: 9},
    {goals: 1.9, shots: 15, xg: 2.1, penalties: 0.1, fouls_drawn: 8},
    # ... 45 more matches
]
```

#### Performance Differential Calculation:
```python
with_oliver_avg = {
    'goals': 2.13,
    'shots': 16.2, 
    'xg': 2.33,
    'penalties': 0.18,
    'fouls_drawn': 12.7
}

without_oliver_avg = {
    'goals': 1.74,
    'shots': 13.8,
    'xg': 1.95, 
    'penalties': 0.08,
    'fouls_drawn': 8.9
}

differentials = {
    'goals': (2.13 - 1.74) / 1.74 * 100 = +22.4%,
    'shots': (16.2 - 13.8) / 13.8 * 100 = +17.4%,
    'xg': (2.33 - 1.95) / 1.95 * 100 = +19.5%,
    'penalties': (0.18 - 0.08) / 0.08 * 100 = +125%,
    'fouls_drawn': (12.7 - 8.9) / 8.9 * 100 = +42.7%
}
```

#### Variance Analysis:
```python
# Oliver's penalty decisions for Arsenal: [0, 1, 0, 1, 0, 0, 1, 0, 0, 1]
arsenal_penalty_variance = variance([0,1,0,1,0,0,1,0,0,1]) = 0.24

# Oliver's penalty decisions across all teams: [0,0,1,0,1,0,0,1,0,1,0,0,...]  
overall_penalty_variance = variance(all_decisions) = 0.18

penalty_variance_ratio = 0.24 / 0.18 = 1.33 (33% more variable)
```

#### Final RBS Calculation:
```python
performance_component = weighted_avg([22.4, 17.4, 19.5, 125, 42.7]) = +35.2%
variance_component = weighted_avg([1.33, 1.12, 0.95]) = +13.3%

rbs_score = (35.2 * 0.7 + 13.3 * 0.3) / 20 = +1.43
```

**Interpretation**: Strong positive bias - Arsenal performs significantly better with Oliver (+1.43 RBS)

## 📈 Statistical Significance Testing

### Minimum Sample Requirements
```python
def is_statistically_significant(with_ref_matches, without_ref_matches):
    return (
        len(with_ref_matches) >= 5 AND 
        len(without_ref_matches) >= 10 AND
        total_matches >= 15
    )
```

### Confidence Intervals
```python
def calculate_confidence_interval(differential, sample_size):
    std_error = standard_deviation / sqrt(sample_size)
    margin_error = 1.96 * std_error  # 95% confidence
    
    return {
        'lower_bound': differential - margin_error,
        'upper_bound': differential + margin_error
    }
```

## 🎯 RBS Score Interpretation

### Scale and Meaning
- **RBS > +2.0**: Very strong positive bias (team performs much better with this referee)
- **RBS +1.0 to +2.0**: Strong positive bias
- **RBS +0.5 to +1.0**: Moderate positive bias
- **RBS -0.5 to +0.5**: Neutral (no significant bias detected)
- **RBS -0.5 to -1.0**: Moderate negative bias
- **RBS -1.0 to -2.0**: Strong negative bias
- **RBS < -2.0**: Very strong negative bias (team performs much worse with this referee)

### Component Breakdown
```python
{
    'rbs_score': 1.43,
    'performance_differential': {
        'goals': +22.4%,
        'shots': +17.4%, 
        'penalties': +125%,
        'fouls_drawn': +42.7%
    },
    'variance_analysis': {
        'penalty_decisions': 1.33,  # More variable than usual
        'foul_calls': 1.12,         # Slightly more variable
        'card_decisions': 0.95      # About average variance
    },
    'confidence': 'High',  # Based on sample size
    'sample_size': {'with_ref': 11, 'without_ref': 47}
}
```

## 🔄 Implementation in Match Prediction

### RBS Application
```python
def apply_rbs_to_prediction(base_xg, team_name, referee_name):
    rbs_data = calculate_comprehensive_rbs(team_name, referee_name)
    
    # Apply only the performance differential component
    performance_factor = rbs_data['performance_differential']['xg'] / 100
    
    # Conservative scaling (don't over-adjust)
    rbs_adjustment = base_xg * performance_factor * 0.1
    
    return base_xg + rbs_adjustment
```

This approach provides a much more robust, statistically grounded measure of referee bias based on actual performance differentials and decision pattern analysis.
