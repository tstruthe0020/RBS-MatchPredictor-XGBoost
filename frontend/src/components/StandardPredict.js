import React from 'react';
import { formatPercentage, formatScore, getConfidenceColor } from '../analysis-components';

const StandardPredict = ({ 
  teams, 
  referees, 
  configs,
  predictionForm, 
  setPredictionForm,
  configName,
  setConfigName,
  predictionResult, 
  predicting, 
  predictMatch,
  resetPrediction,
  exportPDF,
  exportingPDF
}) => {
  
  const handlePredictionFormChange = (field, value) => {
    setPredictionForm(prev => ({
      ...prev,
      [field]: value
    }));
  };

  const isFormValid = () => {
    return predictionForm.home_team && 
           predictionForm.away_team && 
           predictionForm.referee_name;
  };

  return (
    <div className="space-y-6">
      <div className="bg-white p-6 rounded-lg shadow-lg border border-gray-200">
        <h2 className="text-xl font-bold mb-4" style={{color: '#002629'}}>🎯 Standard Match Prediction</h2>
        <p className="mb-6" style={{color: '#002629', opacity: 0.8}}>
          Get match predictions using our trained XGBoost models with team statistics, historical data, and referee bias scores.
        </p>

        {/* Prediction Form */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mb-6">
          <div>
            <label className="block text-sm font-medium mb-2" style={{color: '#002629'}}>Home Team</label>
            <select
              value={predictionForm.home_team}
              onChange={(e) => handlePredictionFormChange('home_team', e.target.value)}
              className="form-select w-full"
            >
              <option value="">Select Home Team</option>
              {teams.map(team => (
                <option key={team} value={team}>{team}</option>
              ))}
            </select>
          </div>

          <div>
            <label className="block text-sm font-medium mb-2" style={{color: '#002629'}}>Away Team</label>
            <select
              value={predictionForm.away_team}
              onChange={(e) => handlePredictionFormChange('away_team', e.target.value)}
              className="form-select w-full"
            >
              <option value="">Select Away Team</option>
              {teams.filter(team => team !== predictionForm.home_team).map(team => (
                <option key={team} value={team}>{team}</option>
              ))}
            </select>
          </div>

          <div>
            <label className="block text-sm font-medium mb-2" style={{color: '#002629'}}>Referee</label>
            <select
              value={predictionForm.referee_name}
              onChange={(e) => handlePredictionFormChange('referee_name', e.target.value)}
              className="form-select w-full"
            >
              <option value="">Select Referee</option>
              {referees.map(referee => (
                <option key={referee} value={referee}>{referee}</option>
              ))}
            </select>
          </div>

          <div>
            <label className="block text-sm font-medium mb-2" style={{color: '#002629'}}>Match Date (Optional)</label>
            <input
              type="date"
              value={predictionForm.match_date}
              onChange={(e) => handlePredictionFormChange('match_date', e.target.value)}
              className="form-input w-full"
            />
          </div>
        </div>

        {/* Configuration Selection */}
        <div className="mb-6">
          <label className="block text-sm font-medium mb-2" style={{color: '#002629'}}>Prediction Configuration</label>
          <select
            value={configName}
            onChange={(e) => setConfigName(e.target.value)}
            className="form-select w-full max-w-sm"
          >
            <option value="default">Default Configuration</option>
            {configs.map(config => (
              <option key={config.config_name} value={config.config_name}>{config.config_name}</option>
            ))}
          </select>
        </div>

        {/* Prediction Button */}
        <div className="flex space-x-4 mb-6">
          <button
            onClick={predictMatch}
            disabled={!isFormValid() || predicting}
            className="px-6 py-3 text-white font-medium rounded-lg hover:opacity-90 disabled:opacity-50 disabled:cursor-not-allowed flex items-center space-x-2 transition-opacity"
            style={{backgroundColor: '#1C5D99'}}
            title={!isFormValid() ? 'Please select home team, away team, and referee' : ''}
          >
            {predicting ? (
              <>
                <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-white"></div>
                <span>Predicting...</span>
              </>
            ) : (
              <>
                <span>🎯</span>
                <span>Predict Match</span>
              </>
            )}
          </button>

          {predictionResult && (
            <button
              onClick={resetPrediction}
              className="px-6 py-3 text-white font-medium rounded-lg hover:opacity-90 transition-opacity"
              style={{backgroundColor: '#12664F'}}
            >
              🔄 New Prediction
            </button>
          )}
        </div>

        {/* Prediction Results */}
        {predictionResult && (
          <div className="bg-white border-2 rounded-lg p-6" style={{borderColor: '#1C5D99'}}>
            <div className="text-center mb-6">
              <h3 className="text-2xl font-bold mb-2" style={{color: '#002629'}}>
                {predictionResult.home_team} vs {predictionResult.away_team}
              </h3>
              <div className="text-lg mb-2" style={{color: '#002629'}}>
                Predicted Score: <span className="font-bold" style={{color: '#1C5D99'}}>{predictionResult.predicted_home_goals}</span>
                {' - '}
                <span className="font-bold" style={{color: '#12664F'}}>{predictionResult.predicted_away_goals}</span>
              </div>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-6">
              {/* Match Outcome Probabilities */}
              <div className="bg-gray-50 p-4 rounded-lg">
                <h4 className="font-semibold mb-3" style={{color: '#002629'}}>Match Outcome</h4>
                <div className="space-y-2">
                  <div className="flex justify-between">
                    <span className="text-sm">Home Win:</span>
                    <span className="font-bold text-green-600">{formatPercentage(predictionResult.home_win_probability/100)}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-sm">Draw:</span>
                    <span className="font-bold text-yellow-600">{formatPercentage(predictionResult.draw_probability/100)}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-sm">Away Win:</span>
                    <span className="font-bold text-red-600">{formatPercentage(predictionResult.away_win_probability/100)}</span>
                  </div>
                </div>
              </div>

              {/* Expected Goals */}
              <div className="bg-gray-50 p-4 rounded-lg">
                <h4 className="font-semibold mb-3" style={{color: '#002629'}}>Expected Goals (xG)</h4>
                <div className="space-y-2">
                  <div className="flex justify-between">
                    <span className="text-gray-600">{predictionResult.home_team}:</span>
                    <span className="font-medium text-blue-600">{predictionResult.home_xg}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-gray-600">{predictionResult.away_team}:</span>
                    <span className="font-medium text-red-600">{predictionResult.away_xg}</span>
                  </div>
                </div>
              </div>

              {/* Model Confidence */}
              <div className="bg-gray-50 p-4 rounded-lg">
                <h4 className="font-semibold mb-3" style={{color: '#002629'}}>Prediction Details</h4>
                <div className="space-y-2">
                  <div className="flex justify-between">
                    <span className="text-gray-600">Model Confidence:</span>
                    <span className="font-medium" style={{color: getConfidenceColor((predictionResult.prediction_breakdown?.xgboost_confidence?.classifier_confidence || 0) * 100)}}>
                      {predictionResult.prediction_breakdown?.xgboost_confidence?.classifier_confidence 
                        ? (predictionResult.prediction_breakdown.xgboost_confidence.classifier_confidence * 100).toFixed(1)
                        : 'N/A'}%
                    </span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-gray-600">Referee:</span>
                    <span className="font-medium">{predictionResult.referee}</span>
                  </div>
                </div>
              </div>
            </div>

            {/* Export Button */}
            <div className="text-center">
              <button
                onClick={exportPDF}
                disabled={exportingPDF}
                className="px-6 py-3 text-white font-medium rounded-lg hover:opacity-90 disabled:opacity-50 disabled:cursor-not-allowed flex items-center space-x-2 mx-auto transition-opacity"
                style={{backgroundColor: '#002629'}}
              >
                {exportingPDF ? (
                  <>
                    <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-white"></div>
                    <span>Exporting...</span>
                  </>
                ) : (
                  <>
                    <span>📄</span>
                    <span>Export PDF</span>
                  </>
                )}
              </button>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default StandardPredict;