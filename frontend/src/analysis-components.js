// Advanced Analysis Components for Football Analytics Suite

// Statistical Variables Configuration
export const VARIABLE_CATEGORIES = {
  rbs: {
    name: 'RBS Variables',
    count: 7,
    variables: [
      'yellow_cards_weight',
      'red_cards_weight', 
      'fouls_committed_weight',
      'fouls_drawn_weight',
      'penalties_awarded_weight',
      'xg_difference_weight',
      'possession_percentage_weight'
    ]
  },
  match_predictors: {
    name: 'Match Predictor Variables',
    count: 13,
    variables: [
      'team_home_wins',
      'team_away_wins',
      'team_draws',
      'recent_form_5_matches',
      'head_to_head_wins',
      'head_to_head_losses',
      'points_per_game',
      'goals_scored_per_game',
      'goals_conceded_per_game',
      'clean_sheets_percentage',
      'cards_per_game',
      'referee_bias_score',
      'home_advantage_factor'
    ]
  },
  basic_stats: {
    name: 'Basic Stats',
    count: 10,
    variables: [
      'matches_played',
      'wins',
      'draws',
      'losses',
      'goals_scored',
      'goals_conceded',
      'goal_difference',
      'yellow_cards',
      'red_cards',
      'fouls_committed'
    ]
  },
  advanced_stats: {
    name: 'Advanced Stats',
    count: 9,
    variables: [
      'xg_per_shot',
      'conversion_rate',
      'shots_on_target_percentage',
      'possession_percentage',
      'pass_completion_rate',
      'defensive_actions_per_game',
      'attacking_third_entries',
      'penalty_conversion_rate',
      'corners_per_game'
    ]
  },
  outcome_stats: {
    name: 'Outcome Stats',
    count: 1,
    variables: [
      'match_result'
    ]
  }
};

// Regression Analysis Functions
export const runRegressionAnalysis = async (selectedVariables, target, apiEndpoint) => {
  try {
    const response = await fetch(`${apiEndpoint}/api/regression-analysis`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        selected_stats: selectedVariables,
        target: target,
        test_size: 0.2,
        random_state: 42
      })
    });

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    return await response.json();
  } catch (error) {
    console.error('Regression analysis error:', error);
    throw error;
  }
};

// Configuration Management Functions
export const savePredictionConfig = async (config, apiEndpoint) => {
  try {
    // Ensure all required fields are present with correct types
    const predictionConfig = {
      config_name: config.config_name || 'default',
      xg_shot_based_weight: parseFloat(config.xg_shot_based_weight || 0.4),
      xg_historical_weight: parseFloat(config.xg_historical_weight || 0.4),
      xg_opponent_defense_weight: parseFloat(config.xg_opponent_defense_weight || 0.2),
      ppg_adjustment_factor: parseFloat(config.ppg_adjustment_factor || 0.15),
      possession_adjustment_per_percent: parseFloat(config.possession_adjustment_per_percent || 0.01),
      fouls_drawn_factor: parseFloat(config.fouls_drawn_factor || 0.02),
      fouls_drawn_baseline: parseFloat(config.fouls_drawn_baseline || 10.0),
      fouls_drawn_min_multiplier: parseFloat(config.fouls_drawn_min_multiplier || 0.8),
      fouls_drawn_max_multiplier: parseFloat(config.fouls_drawn_max_multiplier || 1.3),
      penalty_xg_value: parseFloat(config.penalty_xg_value || 0.79),
      rbs_scaling_factor: parseFloat(config.rbs_scaling_factor || 0.2),
      min_conversion_rate: parseFloat(config.min_conversion_rate || 0.5),
      max_conversion_rate: parseFloat(config.max_conversion_rate || 2.0),
      min_xg_per_match: parseFloat(config.min_xg_per_match || 0.1),
      confidence_matches_multiplier: parseFloat(config.confidence_matches_multiplier || 4),
      max_confidence: parseFloat(config.max_confidence || 90),
      min_confidence: parseFloat(config.min_confidence || 20)
    };

    const response = await fetch(`${apiEndpoint}/api/prediction-config`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(predictionConfig)
    });

    if (!response.ok) {
      const errorData = await response.text();
      throw new Error(`HTTP error! status: ${response.status}, message: ${errorData}`);
    }

    return await response.json();
  } catch (error) {
    console.error('Save prediction config error:', error);
    throw error;
  }
};

export const saveRBSConfig = async (config, apiEndpoint) => {
  try {
    // Ensure all required fields are present with correct types
    const rbsConfig = {
      config_name: config.config_name || 'default',
      yellow_cards_weight: parseFloat(config.yellow_cards_weight || 0.3),
      red_cards_weight: parseFloat(config.red_cards_weight || 0.5),
      fouls_committed_weight: parseFloat(config.fouls_committed_weight || 0.1),
      fouls_drawn_weight: parseFloat(config.fouls_drawn_weight || 0.1),
      penalties_awarded_weight: parseFloat(config.penalties_awarded_weight || 0.5),
      xg_difference_weight: parseFloat(config.xg_difference_weight || 0.4),
      possession_percentage_weight: parseFloat(config.possession_percentage_weight || 0.2),
      confidence_matches_multiplier: parseFloat(config.confidence_matches_multiplier || 4),
      max_confidence: parseFloat(config.max_confidence || 95),
      min_confidence: parseFloat(config.min_confidence || 10),
      confidence_threshold_low: parseInt(config.confidence_threshold_low || 2),
      confidence_threshold_medium: parseInt(config.confidence_threshold_medium || 5),
      confidence_threshold_high: parseInt(config.confidence_threshold_high || 10)
    };

    const response = await fetch(`${apiEndpoint}/api/rbs-config`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(rbsConfig)
    });

    if (!response.ok) {
      const errorData = await response.text();
      throw new Error(`HTTP error! status: ${response.status}, message: ${errorData}`);
    }

    return await response.json();
  } catch (error) {
    console.error('Save RBS config error:', error);
    throw error;
  }
};

// Formula Optimization Functions
export const runFormulaOptimization = async (optimizationType, apiEndpoint) => {
  try {
    const response = await fetch(`${apiEndpoint}/api/optimize-formula`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        optimization_type: optimizationType
      })
    });

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    return await response.json();
  } catch (error) {
    console.error('Formula optimization error:', error);
    throw error;
  }
};

// Results Analysis Functions
export const fetchRefereeAnalysis = async (apiEndpoint) => {
  try {
    const response = await fetch(`${apiEndpoint}/api/referee-analysis`);
    
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    return await response.json();
  } catch (error) {
    console.error('Referee analysis error:', error);
    throw error;
  }
};

export const fetchDetailedRefereeAnalysis = async (refereeName, apiEndpoint) => {
  try {
    const response = await fetch(`${apiEndpoint}/api/referee-analysis/${encodeURIComponent(refereeName)}`);
    
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    return await response.json();
  } catch (error) {
    console.error('Detailed referee analysis error:', error);
    throw error;
  }
};

// Default Configurations
export const DEFAULT_PREDICTION_CONFIG = {
  config_name: 'default',
  xg_shot_based_weight: 0.4,
  xg_historical_weight: 0.4,
  xg_opponent_defense_weight: 0.2,
  ppg_adjustment_factor: 0.15,
  possession_adjustment_per_percent: 0.01,
  fouls_drawn_factor: 0.02,
  fouls_drawn_baseline: 10.0,
  fouls_drawn_min_multiplier: 0.8,
  fouls_drawn_max_multiplier: 1.3,
  penalty_xg_value: 0.79,
  rbs_scaling_factor: 0.2,
  min_conversion_rate: 0.5,
  max_conversion_rate: 2.0,
  min_xg_per_match: 0.1,
  confidence_matches_multiplier: 4,
  max_confidence: 90,
  min_confidence: 20
};

export const DEFAULT_RBS_CONFIG = {
  config_name: 'default',
  yellow_cards_weight: 0.3,
  red_cards_weight: 0.5,
  fouls_committed_weight: 0.1,
  fouls_drawn_weight: 0.1,
  penalties_awarded_weight: 0.5,
  xg_difference_weight: 0.4,
  possession_percentage_weight: 0.2,
  confidence_matches_multiplier: 4,
  max_confidence: 95,
  min_confidence: 10,
  confidence_threshold_low: 2,
  confidence_threshold_medium: 5,
  confidence_threshold_high: 10
};

// Utility Functions
export const formatPercentage = (value) => {
  return `${(value * 100).toFixed(1)}%`;
};

export const formatScore = (value) => {
  return value.toFixed(3);
};

export const getConfidenceColor = (confidence) => {
  if (confidence >= 80) return '#12664F'; // High confidence - Castleton Green
  if (confidence >= 60) return '#1C5D99'; // Medium confidence - Lapis Lazuli  
  if (confidence >= 40) return '#A3D9FF'; // Low confidence - Uranian Blue
  return '#002629'; // Very low confidence - Gunmetal
};

export const getRBSScoreColor = (score) => {
  if (score > 0.3) return '#12664F'; // Positive bias - Castleton Green
  if (score > 0.1) return '#A3D9FF'; // Slight positive - Uranian Blue
  if (score > -0.1) return '#F2E9E4'; // Neutral - Isabelline
  if (score > -0.3) return '#A3D9FF'; // Slight negative - Uranian Blue
  return '#002629'; // Negative bias - Gunmetal
};
