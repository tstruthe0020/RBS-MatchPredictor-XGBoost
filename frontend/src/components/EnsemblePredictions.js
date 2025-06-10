import React from 'react';
import { formatPercentage, formatScore, getConfidenceColor } from '../analysis-components';

const EnsemblePredictions = ({ 
  teams, 
  referees,
  ensembleModelStatus,
  setEnsembleModelStatus,
  ensemblePredictionData,
  setEnsemblePredictionData,
  ensembleComparison,
  setEnsembleComparison,
  selectedEnsembleTeams,
  setSelectedEnsembleTeams,
  loadingEnsemblePrediction,
  setLoadingEnsemblePrediction,
  loadingEnsembleTraining,
  setLoadingEnsembleTraining,
  loadingComparison,
  setLoadingComparison,
  getEnsembleModelStatus,
  trainEnsembleModels,
  makeEnsemblePrediction,
  comparePredictionMethods
}) => {

  const handleEnsembleTeamChange = (field, value) => {
    setSelectedEnsembleTeams(prev => ({
      ...prev,
      [field]: value
    }));
  };

  const isEnsembleFormValid = () => {
    return selectedEnsembleTeams.home && 
           selectedEnsembleTeams.away && 
           selectedEnsembleTeams.referee;
  };

  const handleCheckEnsembleStatus = async () => {
    setLoadingEnsembleTraining(true);
    try {
      const status = await getEnsembleModelStatus();
      setEnsembleModelStatus(status);
    } catch (error) {
      console.error('Error checking ensemble status:', error);
      alert(`❌ Error checking ensemble status: ${error.response?.data?.detail || error.message}`);
    } finally {
      setLoadingEnsembleTraining(false);
    }
  };

  const handleTrainEnsembleModels = async () => {
    if (!window.confirm('🤖 Train Ensemble Models?\n\nThis will train multiple ML models including Random Forest, Gradient Boosting, Neural Networks, and Logistic Regression. This process may take several minutes.')) {
      return;
    }

    setLoadingEnsembleTraining(true);
    try {
      const result = await trainEnsembleModels();
      await handleCheckEnsembleStatus(); // Refresh status
      if (result?.success) {
        alert('✅ Ensemble models trained successfully!');
      } else {
        alert('⚠️ Training completed but some models may need more data for optimal performance.');
      }
    } catch (error) {
      console.error('Error training ensemble models:', error);
      alert(`❌ Error training ensemble models: ${error.response?.data?.detail || error.message}`);
    } finally {
      setLoadingEnsembleTraining(false);
    }
  };

  const handleMakeEnsemblePrediction = async () => {
    if (!isEnsembleFormValid()) {
      alert('Please select home team, away team, and referee');
      return;
    }

    setLoadingEnsemblePrediction(true);
    try {
      const result = await makeEnsemblePrediction(
        selectedEnsembleTeams.home,
        selectedEnsembleTeams.away,
        selectedEnsembleTeams.referee
      );
      setEnsemblePredictionData(result);
    } catch (error) {
      console.error('Error making ensemble prediction:', error);
      alert(`❌ Error making ensemble prediction: ${error.response?.data?.detail || error.message}`);
    } finally {
      setLoadingEnsemblePrediction(false);
    }
  };

  const handleCompareVsXGBoost = async () => {
    if (!isEnsembleFormValid()) {
      alert('Please select home team, away team, and referee');
      return;
    }

    setLoadingComparison(true);
    try {
      const result = await comparePredictionMethods(
        selectedEnsembleTeams.home,
        selectedEnsembleTeams.away,
        selectedEnsembleTeams.referee
      );
      setEnsembleComparison(result);
    } catch (error) {
      console.error('Error comparing prediction methods:', error);
      alert(`❌ Error comparing prediction methods: ${error.response?.data?.detail || error.message}`);
    } finally {
      setLoadingComparison(false);
    }
  };

  return (
    <div className="space-y-6">
      <div className="bg-white p-6 rounded-lg shadow-lg border border-gray-200">
        <div className="flex items-center justify-between mb-6">
          <div>
            <h2 className="text-xl font-bold mb-2" style={{color: '#002629'}}>🤖 Ensemble Prediction System</h2>
            <p className="text-sm" style={{color: '#002629', opacity: 0.8}}>
              Advanced prediction system combining multiple machine learning models for improved accuracy and reliability.
              Uses XGBoost, Random Forest, Gradient Boosting, Neural Networks, and Logistic Regression.
            </p>
          </div>
          <button
            onClick={handleCheckEnsembleStatus}
            disabled={loadingEnsembleTraining}
            className="px-4 py-2 text-white font-medium rounded hover:opacity-90 disabled:opacity-50 disabled:cursor-not-allowed flex items-center space-x-2"
            style={{backgroundColor: '#1C5D99'}}
          >
            {loadingEnsembleTraining ? (
              <>
                <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white"></div>
                <span>Checking...</span>
              </>
            ) : (
              <>
                <span>📊</span>
                <span>Check Status</span>
              </>
            )}
          </button>
        </div>

        {/* Model Status Display */}
        {ensembleModelStatus && (
          <div className="mb-6 p-4 rounded-lg border-2" style={{backgroundColor: '#A3D9FF', borderColor: '#1C5D99'}}>
            <h3 className="font-semibold mb-3" style={{color: '#002629'}}>🔍 Ensemble Model Status</h3>
            <div className="grid grid-cols-2 md:grid-cols-5 gap-4">
              {Object.entries(ensembleModelStatus.models_available || {}).map(([modelType, status]) => (
                <div key={modelType} 
                     className="p-3 rounded border-2"
                     style={{
                       borderColor: status.available ? '#12664F' : '#002629',
                       backgroundColor: status.available ? '#A3D9FF' : 'white'
                     }}>
                  <div className="text-center">
                    <div className="text-lg mb-1">
                      {status.available ? '✅' : '❌'}
                    </div>
                    <div className="text-xs font-medium" style={{color: '#002629'}}>
                      {modelType.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase())}
                    </div>
                  </div>
                </div>
              ))}
            </div>

            {ensembleModelStatus.model_weights && Object.keys(ensembleModelStatus.model_weights).length > 0 && (
              <div className="mt-4">
                <h4 className="font-medium mb-2" style={{color: '#002629'}}>Model Weights</h4>
                <div className="grid grid-cols-2 md:grid-cols-5 gap-2">
                  {Object.entries(ensembleModelStatus.model_weights).map(([model, weight]) => (
                    <div key={model} className="text-xs text-center">
                      <div style={{color: '#002629'}}>{model}</div>
                      <div className="font-bold" style={{color: '#1C5D99'}}>{(weight * 100).toFixed(1)}%</div>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>
        )}

        {/* Train Ensemble Models */}
        <div className="mb-6 p-4 rounded-lg border-2" style={{backgroundColor: '#F2E9E4', borderColor: '#12664F'}}>
          <div className="flex items-center justify-between">
            <div>
              <h3 className="font-semibold" style={{color: '#002629'}}>🏋️ Train Ensemble Models</h3>
              <p className="text-sm mt-1" style={{color: '#002629', opacity: 0.8}}>
                Train multiple ML models for ensemble predictions
              </p>
            </div>
            <button
              onClick={handleTrainEnsembleModels}
              disabled={loadingEnsembleTraining}
              className="px-4 py-2 text-white font-medium rounded hover:opacity-90 disabled:opacity-50 disabled:cursor-not-allowed flex items-center space-x-2"
              style={{backgroundColor: '#12664F'}}
            >
              {loadingEnsembleTraining ? (
                <>
                  <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white"></div>
                  <span>Training Models...</span>
                </>
              ) : (
                <>
                  <span>🤖</span>
                  <span>Train Models</span>
                </>
              )}
            </button>
          </div>
        </div>

        {/* Prediction Form */}
        <div className="mb-6">
          <h3 className="font-semibold mb-4" style={{color: '#002629'}}>🎯 Make Ensemble Prediction</h3>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div>
              <label className="block text-sm font-medium mb-2" style={{color: '#002629'}}>Home Team</label>
              <select
                value={selectedEnsembleTeams.home}
                onChange={(e) => handleEnsembleTeamChange('home', e.target.value)}
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
                value={selectedEnsembleTeams.away}
                onChange={(e) => handleEnsembleTeamChange('away', e.target.value)}
                className="form-select w-full"
              >
                <option value="">Select Away Team</option>
                {teams.map(team => (
                  <option key={team} value={team}>{team}</option>
                ))}
              </select>
            </div>

            <div>
              <label className="block text-sm font-medium mb-2" style={{color: '#002629'}}>Referee</label>
              <select
                value={selectedEnsembleTeams.referee}
                onChange={(e) => handleEnsembleTeamChange('referee', e.target.value)}
                className="form-select w-full"
              >
                <option value="">Select Referee</option>
                {referees.map(ref => (
                  <option key={ref} value={ref}>{ref}</option>
                ))}
              </select>
            </div>
          </div>

          <div className="flex space-x-4 mt-4">
            <button
              onClick={handleMakeEnsemblePrediction}
              disabled={!isEnsembleFormValid() || loadingEnsemblePrediction}
              className="px-6 py-3 text-white font-medium rounded-lg hover:opacity-90 disabled:opacity-50 disabled:cursor-not-allowed flex items-center space-x-2"
              style={{backgroundColor: '#1C5D99'}}
            >
              {loadingEnsemblePrediction ? (
                <>
                  <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-white"></div>
                  <span>Predicting...</span>
                </>
              ) : (
                <>
                  <span>🤖</span>
                  <span>Make Ensemble Prediction</span>
                </>
              )}
            </button>

            <button
              onClick={handleCompareVsXGBoost}
              disabled={!isEnsembleFormValid() || loadingComparison}
              className="px-6 py-3 text-white font-medium rounded-lg hover:opacity-90 disabled:opacity-50 disabled:cursor-not-allowed flex items-center space-x-2"
              style={{backgroundColor: '#12664F'}}
            >
              {loadingComparison ? (
                <>
                  <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-white"></div>
                  <span>Comparing...</span>
                </>
              ) : (
                <>
                  <span>⚖️</span>
                  <span>Compare vs XGBoost</span>
                </>
              )}
            </button>
          </div>
        </div>

        {/* Ensemble Prediction Results */}
        {ensemblePredictionData && (
          <div className="mb-6 bg-white border-2 rounded-lg p-6" style={{borderColor: '#1C5D99'}}>
            <div className="text-center mb-6">
              <h3 className="text-2xl font-bold mb-2" style={{color: '#002629'}}>
                🤖 Ensemble Prediction Results
              </h3>
              <div className="text-lg font-semibold" style={{color: '#002629'}}>
                {selectedEnsembleTeams.home} vs {selectedEnsembleTeams.away}
              </div>
            </div>

            <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
              <div className="stat-card text-center">
                <div className="stat-card-number">{ensemblePredictionData.predicted_home_goals}</div>
                <div className="stat-card-label">Home Goals</div>
              </div>
              <div className="stat-card text-center">
                <div className="stat-card-number">{ensemblePredictionData.predicted_away_goals}</div>
                <div className="stat-card-label">Away Goals</div>
              </div>
              <div className="stat-card text-center">
                <div className="stat-card-number">{ensemblePredictionData.home_xg}</div>
                <div className="stat-card-label">Home xG</div>
              </div>
              <div className="stat-card text-center">
                <div className="stat-card-number">{ensemblePredictionData.away_xg}</div>
                <div className="stat-card-label">Away xG</div>
              </div>
            </div>

            {/* Match Outcome Probabilities */}
            <div className="mt-6 grid grid-cols-1 md:grid-cols-3 gap-4">
              <div className="bg-gray-50 p-4 rounded-lg">
                <h4 className="font-semibold mb-3" style={{color: '#002629'}}>Match Outcome</h4>
                <div className="space-y-2">
                  <div className="flex justify-between">
                    <span className="text-sm">Home Win:</span>
                    <span className="font-bold text-green-600">{ensemblePredictionData.home_win_probability}%</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-sm">Draw:</span>
                    <span className="font-bold text-yellow-600">{ensemblePredictionData.draw_probability}%</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-sm">Away Win:</span>
                    <span className="font-bold text-red-600">{ensemblePredictionData.away_win_probability}%</span>
                  </div>
                </div>
              </div>

              {/* Confidence Metrics */}
              <div className="bg-gray-50 p-4 rounded-lg">
                <h4 className="font-semibold mb-3" style={{color: '#002629'}}>Confidence Metrics</h4>
                <div className="space-y-2">
                  <div className="flex justify-between">
                    <span className="text-sm">Overall Confidence:</span>
                    <span className="font-bold" style={{color: getConfidenceColor(ensemblePredictionData.confidence_metrics?.overall_confidence || 0)}}>
                      {ensemblePredictionData.confidence_metrics?.overall_confidence || 'N/A'}%
                    </span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-sm">Model Agreement:</span>
                    <span className="font-bold text-blue-600">
                      {ensemblePredictionData.confidence_metrics?.model_agreement || 'N/A'}%
                    </span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-sm">Prediction Stability:</span>
                    <span className="font-bold text-purple-600">
                      {ensemblePredictionData.confidence_metrics?.prediction_stability || 'N/A'}%
                    </span>
                  </div>
                </div>
              </div>

              {/* Individual Model Predictions */}
              <div className="bg-gray-50 p-4 rounded-lg">
                <h4 className="font-semibold mb-3" style={{color: '#002629'}}>Model Breakdown</h4>
                {ensemblePredictionData.individual_predictions && Object.keys(ensemblePredictionData.individual_predictions).length > 0 ? (
                  <div className="space-y-2">
                    {Object.entries(ensemblePredictionData.individual_predictions).slice(0, 3).map(([model, predictions]) => (
                      <div key={model} className="flex justify-between text-xs">
                        <span>{model}:</span>
                        <span>{predictions.home_goals} - {predictions.away_goals}</span>
                      </div>
                    ))}
                  </div>
                ) : (
                  <p className="text-xs text-gray-500">Individual model data not available</p>
                )}
              </div>
            </div>
          </div>
        )}

        {/* Comparison Results */}
        {ensembleComparison && (
          <div className="bg-white border-2 rounded-lg p-6" style={{borderColor: '#12664F'}}>
            <h3 className="text-xl font-bold mb-4" style={{color: '#002629'}}>⚖️ XGBoost vs Ensemble Comparison</h3>
            
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              {/* XGBoost Results */}
              <div className="p-3 rounded border-2" style={{borderColor: '#1C5D99', backgroundColor: 'white'}}>
                <h5 className="font-medium mb-3" style={{color: '#002629'}}>🚀 XGBoost</h5>
                <div className="space-y-2 text-sm">
                  <div className="flex justify-between">
                    <span>Home Win:</span>
                    <span className="font-bold">{ensembleComparison.xgboost_prediction.home_win_probability}%</span>
                  </div>
                  <div className="flex justify-between">
                    <span>Draw:</span>
                    <span className="font-bold">{ensembleComparison.xgboost_prediction.draw_probability}%</span>
                  </div>
                  <div className="flex justify-between">
                    <span>Away Win:</span>
                    <span className="font-bold">{ensembleComparison.xgboost_prediction.away_win_probability}%</span>
                  </div>
                  <div className="flex justify-between">
                    <span>Goals:</span>
                    <span className="font-bold">
                      {ensembleComparison.xgboost_prediction.predicted_home_goals} - {ensembleComparison.xgboost_prediction.predicted_away_goals}
                    </span>
                  </div>
                </div>
              </div>

              {/* Ensemble Results */}
              <div className="p-3 rounded border-2" style={{borderColor: '#12664F', backgroundColor: 'white'}}>
                <h5 className="font-medium mb-3" style={{color: '#002629'}}>🤖 Ensemble</h5>
                <div className="space-y-2 text-sm">
                  <div className="flex justify-between">
                    <span>Home Win:</span>
                    <span className="font-bold">{ensembleComparison.ensemble_prediction.home_win_probability}%</span>
                  </div>
                  <div className="flex justify-between">
                    <span>Draw:</span>
                    <span className="font-bold">{ensembleComparison.ensemble_prediction.draw_probability}%</span>
                  </div>
                  <div className="flex justify-between">
                    <span>Away Win:</span>
                    <span className="font-bold">{ensembleComparison.ensemble_prediction.away_win_probability}%</span>
                  </div>
                  <div className="flex justify-between">
                    <span>Goals:</span>
                    <span className="font-bold">
                      {ensembleComparison.ensemble_prediction.predicted_home_goals} - {ensembleComparison.ensemble_prediction.predicted_away_goals}
                    </span>
                  </div>
                </div>
              </div>
            </div>

            {/* Comparison Metrics */}
            <div className="mt-4 p-3 rounded" style={{backgroundColor: '#A3D9FF'}}>
              <h6 className="font-medium mb-2" style={{color: '#002629'}}>📊 Comparison Metrics</h6>
              <div className="grid grid-cols-2 md:grid-cols-3 gap-4 text-sm">
                <div className="text-center">
                  <div className="font-bold" style={{color: '#002629'}}>
                    {ensembleComparison.confidence_comparison?.more_confident_method}
                  </div>
                  <div style={{color: '#002629', opacity: 0.7}}>More Confident</div>
                </div>
                <div className="text-center">
                  <div className="font-bold" style={{color: '#002629'}}>
                    {ensembleComparison.recommendation?.ensemble_agreement}%
                  </div>
                  <div style={{color: '#002629', opacity: 0.7}}>Model Agreement</div>
                </div>
                <div className="text-center">
                  <div className="font-bold" style={{color: '#002629'}}>
                    {ensembleComparison.recommendation?.suggested_method}
                  </div>
                  <div style={{color: '#002629', opacity: 0.7}}>Recommended</div>
                </div>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default EnsemblePredictions;