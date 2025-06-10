import React from 'react';
import PlayerSearchInput from '../PlayerSearchInput';
import { formatPercentage, formatScore, getConfidenceColor } from '../analysis-components';

const EnhancedXGBoost = ({ 
  teams, 
  referees,
  predictionForm, 
  setPredictionForm,
  predictionResult, 
  predicting,
  showStartingXI,
  setShowStartingXI,
  selectedFormation,
  setSelectedFormation,
  availableFormations,
  homeStartingXI,
  awayStartingXI,
  setHomeStartingXI,
  setAwayStartingXI,
  useTimeDecay,
  setUseTimeDecay,
  decayPreset,
  setDecayPreset,
  decayPresets,
  mlStatus,
  checkMLStatus,
  trainMLModels,
  trainingModels,
  reloadMLModels,
  predictMatchEnhanced,
  resetPrediction,
  exportPDF,
  exportingPDF,
  fetchTeamPlayers,
  loadingPlayers,
  playerSearchTerms,
  searchResults,
  handlePlayerSearch,
  selectPlayerFromSearch,
  validateStartingXI,
  getButtonTooltip,
  handleFormationChange
}) => {
  
  const handlePredictionFormChange = (field, value) => {
    setPredictionForm(prev => ({
      ...prev,
      [field]: value
    }));
    
    // Fetch players when teams are selected and Starting XI is enabled
    if ((field === 'home_team' || field === 'away_team') && showStartingXI && value) {
      fetchTeamPlayers(value, field === 'home_team');
    }
  };

  const isFormValid = () => {
    const basicValid = predictionForm.home_team && 
                      predictionForm.away_team && 
                      predictionForm.referee_name;
    
    if (!basicValid) return false;
    
    // If Starting XI is enabled, validate lineups
    if (showStartingXI) {
      return validateStartingXI(homeStartingXI) && validateStartingXI(awayStartingXI);
    }
    
    return true;
  };

  const renderStartingXIGrid = (startingXI, isHomeTeam, teamName) => {
    if (!startingXI || !startingXI.positions) return null;

    const positionsByType = startingXI.positions.reduce((acc, position) => {
      if (!acc[position.position_type]) {
        acc[position.position_type] = [];
      }
      acc[position.position_type].push(position);
      return acc;
    }, {});

    return (
      <div className={`${isHomeTeam ? 'bg-green-50' : 'bg-blue-50'} p-6 rounded-lg border border-${isHomeTeam ? 'green' : 'blue'}-200`}>
        <div className="flex items-center justify-between mb-4">
          <h4 className={`font-semibold text-${isHomeTeam ? 'green' : 'blue'}-900 text-lg`}>
            {isHomeTeam ? '🏠' : '✈️'} {teamName}
          </h4>
          <span className={`px-3 py-1 rounded-full text-sm font-medium ${
            validateStartingXI(startingXI) 
              ? 'bg-green-100 text-green-800' 
              : 'bg-red-100 text-red-800'
          }`}>
            {validateStartingXI(startingXI) ? '✅ Complete' : '⚠️ Incomplete'}
          </span>
        </div>

        <div className="space-y-4">
          {Object.entries(positionsByType).map(([posType, positions]) => {
            return (
              <div key={posType} className="space-y-2">
                <div className={`text-sm font-medium text-${isHomeTeam ? 'green' : 'blue'}-800 uppercase`}>{posType}</div>
                {positions.map(position => (
                  <div key={position.position_id} className="flex items-center space-x-3">
                    <div className={`w-16 text-xs font-medium text-${isHomeTeam ? 'green' : 'blue'}-700`}>
                      {position.position_name}
                    </div>
                    <div className="flex-1">
                      <PlayerSearchInput
                        positionId={position.position_id}
                        positionType={position.position_type}
                        isHomeTeam={isHomeTeam}
                        currentPlayer={position.player}
                        searchTerm={playerSearchTerms[`${isHomeTeam ? 'home' : 'away'}_${position.position_id}`] || ''}
                        searchResults={searchResults[`${isHomeTeam ? 'home' : 'away'}_${position.position_id}`] || []}
                        onSearch={(term) => handlePlayerSearch(term, isHomeTeam, position.position_type, position.position_id)}
                        onSelect={(player) => selectPlayerFromSearch(player, isHomeTeam, position.position_id)}
                        placeholder={`Search ${position.position_type} players...`}
                      />
                    </div>
                  </div>
                ))}
              </div>
            );
          })}
        </div>
      </div>
    );
  };

  return (
    <div className="space-y-6">
      <div className="bg-white p-6 rounded-lg shadow-lg border border-gray-200">
        <h2 className="text-xl font-bold mb-4" style={{color: '#002629'}}>🚀 Enhanced XGBoost Predictions</h2>
        <p className="mb-6" style={{color: '#002629', opacity: 0.8}}>
          Advanced predictions with Starting XI analysis and Time Decay weighting for more accurate results.
        </p>

        {/* ML Model Status */}
        <div className="mb-6 p-4 rounded-lg" style={{backgroundColor: '#A3D9FF'}}>
          <div className="flex items-center justify-between">
            <div>
              <h3 className="text-lg font-semibold" style={{color: '#002629'}}>🧠 XGBoost Models</h3>
              <div className="flex items-center space-x-2 mt-2">
                <span className={`inline-block w-3 h-3 rounded-full ${mlStatus?.models_loaded ? 'bg-green-500' : 'bg-red-500'}`}></span>
                <span className="text-sm font-medium" style={{color: '#002629'}}>
                  {mlStatus?.models_loaded ? 'Ready' : 'Training Required'}
                </span>
                <span className="text-xs" style={{color: '#002629', opacity: 0.7}}>
                  ({mlStatus?.feature_columns_count || 0} features)
                </span>
              </div>
            </div>
            <div className="flex space-x-2">
              <button
                onClick={checkMLStatus}
                className="px-3 py-1 text-sm text-white rounded hover:opacity-90 transition-opacity"
                style={{backgroundColor: '#1C5D99'}}
              >
                🔄 Refresh Status
              </button>
              <button
                onClick={trainMLModels}
                disabled={trainingModels}
                className="px-4 py-2 text-white font-medium rounded hover:opacity-90 disabled:opacity-50 disabled:cursor-not-allowed flex items-center space-x-2 transition-opacity"
                style={{backgroundColor: '#12664F'}}
              >
                {trainingModels ? (
                  <>
                    <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white"></div>
                    <span>Training...</span>
                  </>
                ) : (
                  <>
                    <span>🏋️</span>
                    <span>Train Models</span>
                  </>
                )}
              </button>
            </div>
          </div>
        </div>

        {/* Enhanced Features Controls */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-6">
          {/* Starting XI Controls */}
          <div className="p-4 rounded-lg border-2" style={{backgroundColor: '#F2E9E4', borderColor: '#1C5D99'}}>
            <div className="flex items-center justify-between mb-4">
              <h4 className="font-semibold" style={{color: '#002629'}}>⚽ Starting XI Analysis</h4>
              <label className="flex items-center">
                <input
                  type="checkbox"
                  checked={showStartingXI}
                  onChange={(e) => setShowStartingXI(e.target.checked)}
                  className="mr-2"
                />
                <span className="text-sm" style={{color: '#002629'}}>Enable</span>
              </label>
            </div>
            
            {showStartingXI && (
              <div className="space-y-3">
                <div>
                  <label className="block text-sm font-medium mb-2" style={{color: '#002629'}}>Formation</label>
                  <select
                    value={selectedFormation}
                    onChange={(e) => handleFormationChange(e.target.value)}
                    className="form-select w-full"
                  >
                    {availableFormations.map(formation => (
                      <option key={formation} value={formation}>{formation}</option>
                    ))}
                  </select>
                </div>
              </div>
            )}
          </div>

          {/* Time Decay Controls */}
          <div className="p-4 rounded-lg border-2" style={{backgroundColor: '#F2E9E4', borderColor: '#12664F'}}>
            <div className="flex items-center justify-between mb-4">
              <h4 className="font-semibold" style={{color: '#002629'}}>⏰ Time Decay Weighting</h4>
              <label className="flex items-center">
                <input
                  type="checkbox"
                  checked={useTimeDecay}
                  onChange={(e) => setUseTimeDecay(e.target.checked)}
                  className="mr-2"
                />
                <span className="text-sm" style={{color: '#002629'}}>Enable</span>
              </label>
            </div>
            
            <div>
              <label className="block text-sm font-medium mb-2" style={{color: '#002629'}}>Decay Preset</label>
              <select
                value={decayPreset}
                onChange={(e) => setDecayPreset(e.target.value)}
                disabled={!useTimeDecay}
                className="form-select w-full"
              >
                {decayPresets.map(preset => (
                  <option key={preset.name} value={preset.name}>
                    {preset.display_name} - {preset.description}
                  </option>
                ))}
              </select>
            </div>
          </div>
        </div>

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

        {/* Starting XI Selection */}
        {showStartingXI && predictionForm.home_team && predictionForm.away_team && (
          <div className="mb-6">
            <h3 className="text-lg font-semibold mb-4" style={{color: '#002629'}}>Starting XI Selection</h3>
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              {homeStartingXI && renderStartingXIGrid(homeStartingXI, true, predictionForm.home_team)}
              {awayStartingXI && renderStartingXIGrid(awayStartingXI, false, predictionForm.away_team)}
            </div>
            
            {(homeStartingXI || awayStartingXI) && (
              <div className="mt-4 text-center">
                <button
                  onClick={() => {
                    setHomeStartingXI(null);
                    setAwayStartingXI(null);
                    if (predictionForm.home_team) fetchTeamPlayers(predictionForm.home_team, true);
                    if (predictionForm.away_team) fetchTeamPlayers(predictionForm.away_team, false);
                  }}
                  className="px-4 py-2 text-white font-medium rounded hover:opacity-90 transition-opacity"
                  style={{backgroundColor: '#002629'}}
                >
                  🔄 Reset to Default XI
                </button>
              </div>
            )}
          </div>
        )}

        {/* Prediction Button */}
        <div className="flex space-x-4 mb-6">
          <button
            onClick={predictMatchEnhanced}
            disabled={!isFormValid() || predicting}
            className="px-6 py-3 text-white font-medium rounded-lg hover:opacity-90 disabled:opacity-50 disabled:cursor-not-allowed flex items-center space-x-2 transition-opacity"
            style={{backgroundColor: '#1C5D99'}}
            title={getButtonTooltip()}
          >
            {predicting ? (
              <>
                <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-white"></div>
                <span>Predicting...</span>
              </>
            ) : (
              <>
                <span>🚀</span>
                <span>{showStartingXI ? 'Enhanced Predict with XI' : 'Standard XGBoost Predict'}</span>
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

        {/* Algorithm Explanation */}
        <div className="mb-6 p-4 rounded-lg border-2" style={{backgroundColor: '#A3D9FF', borderColor: '#1C5D99'}}>
          <h4 className="font-semibold mb-2" style={{color: '#002629'}}>🧮 Enhanced Algorithm</h4>
          <p className="text-sm" style={{color: '#002629', opacity: 0.8}}>
            {showStartingXI 
              ? "Using advanced XGBoost with Starting XI player analysis and Time Decay weighting. Player-specific statistics are aggregated based on formation positions to provide more accurate team strength calculations."
              : "Using standard XGBoost prediction with team statistics, historical data, and referee bias scores. Enable Starting XI for player-level analysis."
            }
          </p>
        </div>

        {/* Prediction Results */}
        {predictionResult && (
          <div className="bg-white border-2 rounded-lg p-6" style={{borderColor: '#1C5D99'}}>
            <div className="text-center mb-6">
              <h3 className="text-2xl font-bold mb-2" style={{color: '#002629'}}>
                {predictionResult.home_team} vs {predictionResult.away_team}
              </h3>
              <div className="text-lg text-gray-600 mb-4">
                Predicted Score: <span className="font-bold text-blue-600">{predictionResult.predicted_home_goals}</span>
                {' - '}
                <span className="font-bold text-red-600">{predictionResult.predicted_away_goals}</span>
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

              {/* Enhanced Information */}
              <div className="bg-gray-50 p-4 rounded-lg">
                <h4 className="font-semibold mb-3" style={{color: '#002629'}}>Enhanced Details</h4>
                <div className="space-y-2">
                  <div className="flex justify-between">
                    <span className="text-gray-600">Prediction Method:</span>
                    <span className="font-medium">{predictionResult.prediction_breakdown?.prediction_method || 'Enhanced ML'}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-gray-600">Features Used:</span>
                    <span className="font-medium">{predictionResult.prediction_breakdown?.model_confidence?.features_used || 'N/A'}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-gray-600">Time Decay:</span>
                    <span className="font-medium">{useTimeDecay ? decayPreset : 'Disabled'}</span>
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
                    <span>Export Enhanced PDF</span>
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

export default EnhancedXGBoost;