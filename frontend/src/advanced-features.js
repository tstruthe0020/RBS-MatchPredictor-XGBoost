// Advanced features for the Football Analytics Suite
import axios from 'axios';

const API = (process.env.REACT_APP_BACKEND_URL || 'http://localhost:8001') + '/api';

// Enhanced RBS Analysis Functions
export const fetchEnhancedRBSAnalysis = async (teamName, refereeName) => {
  try {
    const response = await axios.get(`${API}/enhanced-rbs-analysis/${encodeURIComponent(teamName)}/${encodeURIComponent(refereeName)}`);
    return response.data;
  } catch (error) {
    console.error('Error fetching enhanced RBS analysis:', error);
    throw error;
  }
};

// Team Performance Analysis Functions
export const fetchTeamPerformance = async (teamName) => {
  try {
    const response = await axios.get(`${API}/team-performance/${encodeURIComponent(teamName)}`);
    return response.data;
  } catch (error) {
    console.error('Error fetching team performance:', error);
    throw error;
  }
};

// Configuration Management Functions
export const fetchAllPredictionConfigs = async () => {
  try {
    const response = await axios.get(`${API}/prediction-configs`);
    return response.data.configs || [];
  } catch (error) {
    console.error('Error fetching prediction configs:', error);
    return [];
  }
};

export const fetchAllRBSConfigs = async () => {
  try {
    const response = await axios.get(`${API}/rbs-configs`);
    return response.data.configs || [];
  } catch (error) {
    console.error('Error fetching RBS configs:', error);
    return [];
  }
};

export const deletePredictionConfig = async (configName) => {
  try {
    const response = await axios.delete(`${API}/prediction-config/${encodeURIComponent(configName)}`);
    return response.data;
  } catch (error) {
    console.error('Error deleting prediction config:', error);
    throw error;
  }
};

export const deleteRBSConfig = async (configName) => {
  try {
    const response = await axios.delete(`${API}/rbs-config/${encodeURIComponent(configName)}`);
    return response.data;
  } catch (error) {
    console.error('Error deleting RBS config:', error);
    throw error;
  }
};

// AI Optimization Functions
export const suggestPredictionConfig = async () => {
  try {
    const response = await axios.post(`${API}/suggest-prediction-config`);
    return response.data;
  } catch (error) {
    console.error('Error getting prediction config suggestions:', error);
    throw error;
  }
};

export const analyzeRBSOptimization = async () => {
  try {
    const response = await axios.post(`${API}/analyze-rbs-optimization`);
    return response.data;
  } catch (error) {
    console.error('Error analyzing RBS optimization:', error);
    throw error;
  }
};

export const analyzePredictorOptimization = async () => {
  try {
    const response = await axios.post(`${API}/analyze-predictor-optimization`);
    return response.data;
  } catch (error) {
    console.error('Error analyzing predictor optimization:', error);
    throw error;
  }
};

export const analyzeComprehensiveRegression = async () => {
  try {
    const response = await axios.post(`${API}/analyze-comprehensive-regression`);
    return response.data;
  } catch (error) {
    console.error('Error analyzing comprehensive regression:', error);
    throw error;
  }
};

// Advanced optimization with parameters
export const runAdvancedOptimization = async (optimizationType, parameters = {}) => {
  try {
    let endpoint;
    let requestData = parameters;
    
    switch (optimizationType) {
      case 'prediction-suggestion':
        endpoint = `${API}/suggest-prediction-config`;
        break;
      case 'rbs-optimization':
        endpoint = `${API}/analyze-rbs-optimization`;
        break;
      case 'predictor-optimization':
        endpoint = `${API}/analyze-predictor-optimization`;
        break;
      case 'comprehensive-regression':
        endpoint = `${API}/analyze-comprehensive-regression`;
        break;
      default:
        throw new Error(`Unknown optimization type: ${optimizationType}`);
    }
    
    const response = await axios.post(endpoint, requestData);
    return response.data;
  } catch (error) {
    console.error(`Error running ${optimizationType} optimization:`, error);
    throw error;
  }
};

// Utility functions for formatting and display
export const formatOptimizationResults = (results, optimizationType) => {
  if (!results) return null;
  
  return {
    type: optimizationType,
    timestamp: new Date().toISOString(),
    success: results.success || false,
    data: results,
    summary: generateOptimizationSummary(results, optimizationType)
  };
};

export const generateOptimizationSummary = (results, optimizationType) => {
  switch (optimizationType) {
    case 'prediction-suggestion':
      return `AI-suggested configuration with ${Object.keys(results.suggested_config || {}).length} optimized parameters`;
    case 'rbs-optimization':
      return `RBS analysis completed with ${results.teams_analyzed || 0} teams and ${results.referees_analyzed || 0} referees`;
    case 'predictor-optimization':
      return `Predictor optimization analyzed ${results.features_analyzed || 0} features`;
    case 'comprehensive-regression':
      return `Comprehensive analysis of ${results.variables_analyzed || 0} variables`;
    default:
      return 'Optimization completed successfully';
  }
};

// Enhanced RBS Analysis Components
export const RBSVarianceAnalysis = ({ varianceData }) => {
  if (!varianceData || !varianceData.variance_ratios) return null;
  
  return (
    <div className="mt-4 p-4 bg-gray-50 rounded-lg">
      <h4 className="font-semibold text-gray-800 mb-3">📊 Decision Variance Analysis</h4>
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {Object.entries(varianceData.variance_ratios).map(([category, ratio]) => (
          <div key={category} className="bg-white p-3 rounded border">
            <div className="flex justify-between items-center">
              <span className="text-sm font-medium text-gray-700">
                {category.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase())}
              </span>
              <span className={`text-sm font-bold ${
                ratio === null ? 'text-gray-500' :
                ratio > 1.5 ? 'text-red-600' :
                ratio < 0.5 ? 'text-blue-600' :
                'text-green-600'
              }`}>
                {ratio === null ? 'N/A' : ratio.toFixed(3)}
              </span>
            </div>
            {varianceData.interpretation && varianceData.interpretation[category] && (
              <p className="text-xs text-gray-600 mt-1">
                {varianceData.interpretation[category]}
              </p>
            )}
          </div>
        ))}
      </div>
      <div className="mt-3 text-xs text-gray-600">
        <strong>Confidence:</strong> {varianceData.confidence} | 
        <strong> Team Matches:</strong> {varianceData.team_matches_with_referee} | 
        <strong> Referee Total:</strong> {varianceData.referee_total_matches}
      </div>
    </div>
  );
};

// Team Performance Components
export const TeamPerformanceMetrics = ({ performanceData }) => {
  if (!performanceData) return null;
  
  return (
    <div className="space-y-4">
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        {/* Offensive Metrics */}
        <div className="bg-green-50 p-4 rounded-lg border border-green-200">
          <h4 className="font-semibold text-green-800 mb-3">⚽ Offensive</h4>
          <div className="space-y-2">
            <div className="flex justify-between">
              <span className="text-sm text-green-700">Goals/Game</span>
              <span className="font-medium text-green-900">{performanceData.goals_per_game?.toFixed(2) || 'N/A'}</span>
            </div>
            <div className="flex justify-between">
              <span className="text-sm text-green-700">xG/Game</span>
              <span className="font-medium text-green-900">{performanceData.xg_per_game?.toFixed(2) || 'N/A'}</span>
            </div>
            <div className="flex justify-between">
              <span className="text-sm text-green-700">Conversion Rate</span>
              <span className="font-medium text-green-900">{performanceData.conversion_rate?.toFixed(3) || 'N/A'}</span>
            </div>
          </div>
        </div>
        
        {/* Defensive Metrics */}
        <div className="bg-red-50 p-4 rounded-lg border border-red-200">
          <h4 className="font-semibold text-red-800 mb-3">🛡️ Defensive</h4>
          <div className="space-y-2">
            <div className="flex justify-between">
              <span className="text-sm text-red-700">Goals Conceded/Game</span>
              <span className="font-medium text-red-900">{performanceData.goals_conceded_per_game?.toFixed(2) || 'N/A'}</span>
            </div>
            <div className="flex justify-between">
              <span className="text-sm text-red-700">xG Conceded/Game</span>
              <span className="font-medium text-red-900">{performanceData.xg_conceded_per_game?.toFixed(2) || 'N/A'}</span>
            </div>
            <div className="flex justify-between">
              <span className="text-sm text-red-700">Clean Sheets %</span>
              <span className="font-medium text-red-900">{performanceData.clean_sheet_percentage?.toFixed(1) || 'N/A'}%</span>
            </div>
          </div>
        </div>
        
        {/* Overall Metrics */}
        <div className="bg-blue-50 p-4 rounded-lg border border-blue-200">
          <h4 className="font-semibold text-blue-800 mb-3">📊 Overall</h4>
          <div className="space-y-2">
            <div className="flex justify-between">
              <span className="text-sm text-blue-700">Points/Game</span>
              <span className="font-medium text-blue-900">{performanceData.points_per_game?.toFixed(2) || 'N/A'}</span>
            </div>
            <div className="flex justify-between">
              <span className="text-sm text-blue-700">Win Rate</span>
              <span className="font-medium text-blue-900">{performanceData.win_rate?.toFixed(1) || 'N/A'}%</span>
            </div>
            <div className="flex justify-between">
              <span className="text-sm text-blue-700">Matches Played</span>
              <span className="font-medium text-blue-900">{performanceData.matches_played || 'N/A'}</span>
            </div>
          </div>
        </div>
      </div>
      
      {/* Additional detailed metrics if available */}
      {performanceData.detailed_stats && (
        <div className="bg-white p-4 rounded-lg border border-gray-200">
          <h4 className="font-semibold text-gray-800 mb-3">📈 Detailed Statistics</h4>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            {Object.entries(performanceData.detailed_stats).map(([key, value]) => (
              <div key={key} className="text-center">
                <div className="text-2xl font-bold text-gray-800">
                  {typeof value === 'number' ? value.toFixed(2) : value}
                </div>
                <div className="text-xs text-gray-600 uppercase">
                  {key.replace(/_/g, ' ')}
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
};

// Configuration Management Components
export const ConfigurationList = ({ configs, type, onEdit, onDelete, onSelect }) => {
  if (!configs || configs.length === 0) {
    return (
      <div className="text-center py-8 text-gray-500">
        <p>No {type} configurations found.</p>
        <p className="text-sm">Create a new configuration to get started.</p>
      </div>
    );
  }
  
  return (
    <div className="space-y-3">
      {configs.map((config) => (
        <div key={config.config_name} className="flex items-center justify-between p-4 bg-white border border-gray-200 rounded-lg hover:shadow-md transition-shadow">
          <div className="flex-1">
            <div className="flex items-center space-x-3">
              <h4 className="font-medium text-gray-800">{config.config_name}</h4>
              {config.config_name === 'default' && (
                <span className="px-2 py-1 text-xs bg-blue-100 text-blue-800 rounded-full">Default</span>
              )}
            </div>
            <div className="text-sm text-gray-600 mt-1">
              Created: {new Date(config.created_at).toLocaleDateString()}
              {config.updated_at !== config.created_at && (
                <span> • Updated: {new Date(config.updated_at).toLocaleDateString()}</span>
              )}
            </div>
            {type === 'Prediction' && (
              <div className="text-xs text-gray-500 mt-1">
                xG Weights: Shot-based {config.xg_shot_based_weight}, Historical {config.xg_historical_weight}, Defense {config.xg_opponent_defense_weight}
              </div>
            )}
            {type === 'RBS' && (
              <div className="text-xs text-gray-500 mt-1">
                Key Weights: Yellow {config.yellow_cards_weight}, Red {config.red_cards_weight}, Penalties {config.penalties_awarded_weight}
              </div>
            )}
          </div>
          <div className="flex items-center space-x-2">
            <button
              onClick={() => onSelect && onSelect(config)}
              className="px-3 py-1 text-sm text-blue-600 hover:text-blue-800 hover:bg-blue-50 rounded transition-colors"
            >
              Select
            </button>
            <button
              onClick={() => onEdit(config)}
              className="px-3 py-1 text-sm text-green-600 hover:text-green-800 hover:bg-green-50 rounded transition-colors"
            >
              Edit
            </button>
            {config.config_name !== 'default' && (
              <button
                onClick={() => {
                  if (window.confirm(`Are you sure you want to delete the "${config.config_name}" configuration? This action cannot be undone.`)) {
                    onDelete(config.config_name);
                  }
                }}
                className="px-3 py-1 text-sm text-red-600 hover:text-red-800 hover:bg-red-50 rounded transition-colors"
              >
                Delete
              </button>
            )}
          </div>
        </div>
      ))}
    </div>
  );
};

// Advanced Optimization Components
export const OptimizationResults = ({ results, type }) => {
  if (!results) return null;
  
  return (
    <div className="mt-6 space-y-4">
      <div className="bg-white p-6 rounded-lg border border-gray-200">
        <div className="flex items-center justify-between mb-4">
          <h3 className="text-lg font-semibold text-gray-800">
            🤖 {type.replace(/-/g, ' ').replace(/\b\w/g, l => l.toUpperCase())} Results
          </h3>
          <span className="text-xs text-gray-500">
            {new Date(results.timestamp).toLocaleString()}
          </span>
        </div>
        
        {results.summary && (
          <div className="mb-4 p-3 bg-blue-50 rounded-lg">
            <p className="text-blue-800">{results.summary}</p>
          </div>
        )}
        
        {/* Type-specific result rendering */}
        {type === 'prediction-suggestion' && results.data.suggested_config && (
          <div className="space-y-3">
            <h4 className="font-medium text-gray-700">Suggested Configuration:</h4>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {Object.entries(results.data.suggested_config).map(([key, value]) => (
                <div key={key} className="flex justify-between p-2 bg-gray-50 rounded">
                  <span className="text-sm text-gray-600">{key.replace(/_/g, ' ')}</span>
                  <span className="text-sm font-medium text-gray-800">
                    {typeof value === 'number' ? value.toFixed(3) : value}
                  </span>
                </div>
              ))}
            </div>
            {results.data.confidence_score && (
              <div className="mt-3 p-2 bg-green-50 rounded">
                <span className="text-sm text-green-700">Confidence Score: </span>
                <span className="text-sm font-medium text-green-800">
                  {(results.data.confidence_score * 100).toFixed(1)}%
                </span>
              </div>
            )}
          </div>
        )}
        
        {type === 'rbs-optimization' && (
          <div className="space-y-3">
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <div className="text-center p-3 bg-gray-50 rounded">
                <div className="text-2xl font-bold text-gray-800">{results.data.teams_analyzed || 0}</div>
                <div className="text-xs text-gray-600">Teams Analyzed</div>
              </div>
              <div className="text-center p-3 bg-gray-50 rounded">
                <div className="text-2xl font-bold text-gray-800">{results.data.referees_analyzed || 0}</div>
                <div className="text-xs text-gray-600">Referees Analyzed</div>
              </div>
              <div className="text-center p-3 bg-gray-50 rounded">
                <div className="text-2xl font-bold text-gray-800">{results.data.optimization_score?.toFixed(3) || 'N/A'}</div>
                <div className="text-xs text-gray-600">Optimization Score</div>
              </div>
            </div>
            {results.data.recommendations && (
              <div className="mt-4">
                <h4 className="font-medium text-gray-700 mb-2">Recommendations:</h4>
                <ul className="space-y-1">
                  {results.data.recommendations.map((rec, index) => (
                    <li key={index} className="text-sm text-gray-700 flex items-start">
                      <span className="text-blue-500 mr-2">•</span>
                      {rec}
                    </li>
                  ))}
                </ul>
              </div>
            )}
          </div>
        )}
        
        {(type === 'predictor-optimization' || type === 'comprehensive-regression') && (
          <div className="space-y-3">
            {results.data.feature_importance && (
              <div>
                <h4 className="font-medium text-gray-700 mb-2">Top Features:</h4>
                <div className="space-y-2">
                  {Object.entries(results.data.feature_importance).slice(0, 10).map(([feature, importance]) => (
                    <div key={feature} className="flex items-center">
                      <span className="text-sm text-gray-600 flex-1">{feature.replace(/_/g, ' ')}</span>
                      <div className="w-24 bg-gray-200 rounded-full h-2 ml-2">
                        <div 
                          className="bg-blue-500 h-2 rounded-full" 
                          style={{width: `${(importance * 100)}%`}}
                        ></div>
                      </div>
                      <span className="text-sm font-medium text-gray-800 ml-2 w-12 text-right">
                        {(importance * 100).toFixed(1)}%
                      </span>
                    </div>
                  ))}
                </div>
              </div>
            )}
            {results.data.model_performance && (
              <div className="mt-4 grid grid-cols-1 md:grid-cols-3 gap-4">
                {Object.entries(results.data.model_performance).map(([metric, value]) => (
                  <div key={metric} className="text-center p-3 bg-gray-50 rounded">
                    <div className="text-lg font-bold text-gray-800">
                      {typeof value === 'number' ? value.toFixed(3) : value}
                    </div>
                    <div className="text-xs text-gray-600">{metric.replace(/_/g, ' ').toUpperCase()}</div>
                  </div>
                ))}
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
};

export default {
  fetchEnhancedRBSAnalysis,
  fetchTeamPerformance,
  fetchAllPredictionConfigs,
  fetchAllRBSConfigs,
  deletePredictionConfig,
  deleteRBSConfig,
  suggestPredictionConfig,
  analyzeRBSOptimization,
  analyzePredictorOptimization,
  analyzeComprehensiveRegression,
  runAdvancedOptimization,
  formatOptimizationResults,
  generateOptimizationSummary,
  RBSVarianceAnalysis,
  TeamPerformanceMetrics,
  ConfigurationList,
  OptimizationResults
};
