        {/* Enhanced XGBoost Tab with Starting XI */}
        {activeTab === 'xgboost' && (
          <div className="space-y-6">
            <div className="bg-white p-6 rounded-lg shadow-sm border">
              <h2 className="text-xl font-bold text-gray-900 mb-4">🚀 Enhanced XGBoost with Starting XI</h2>
              <p className="text-gray-600 mb-6">
                Advanced match prediction using XGBoost with Starting XI player selection and time decay weighting. 
                Select specific players for each team to get more accurate predictions based on actual lineups.
              </p>

              {/* Enhanced Features Control Panel */}
              <div className="mb-6 p-4 bg-gradient-to-r from-blue-50 to-indigo-50 rounded-lg border border-blue-200">
                <div className="flex items-center justify-between mb-4">
                  <h3 className="text-lg font-semibold text-blue-900">🎯 Enhanced Prediction Features</h3>
                  <button
                    onClick={() => setShowStartingXI(!showStartingXI)}
                    className={`px-4 py-2 rounded-lg font-medium transition-colors ${
                      showStartingXI 
                        ? 'bg-blue-600 text-white shadow-md' 
                        : 'bg-white text-blue-700 border border-blue-300 hover:bg-blue-50'
                    }`}
                  >
                    {showStartingXI ? '✅ Starting XI Active' : '📋 Enable Starting XI'}
                  </button>
                </div>

                {/* Time Decay Settings */}
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-4">
                  <div>
                    <label className="flex items-center space-x-2">
                      <input
                        type="checkbox"
                        checked={useTimeDecay}
                        onChange={(e) => setUseTimeDecay(e.target.checked)}
                        className="rounded border-gray-300 text-blue-600 focus:ring-blue-500"
                      />
                      <span className="text-sm font-medium text-blue-900">Apply Time Decay</span>
                    </label>
                    <p className="text-xs text-blue-700 mt-1">Recent matches weighted higher than historical data</p>
                  </div>
                  
                  <div>
                    <label className="block text-sm font-medium text-blue-900 mb-1">Decay Preset</label>
                    <select
                      value={decayPreset}
                      onChange={(e) => setDecayPreset(e.target.value)}
                      disabled={!useTimeDecay}
                      className="w-full px-3 py-2 border border-blue-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 disabled:bg-gray-100 disabled:text-gray-500"
                    >
                      {decayPresets.map(preset => (
                        <option key={preset.preset_name} value={preset.preset_name}>
                          {preset.preset_name.charAt(0).toUpperCase() + preset.preset_name.slice(1)} - {preset.description}
                        </option>
                      ))}
                    </select>
                  </div>
                </div>

                {/* ML Model Status */}
                <div className="flex items-center justify-between p-3 bg-white rounded-lg border border-blue-200">
                  <div className="flex items-center space-x-3">
                    <span className={`inline-block w-3 h-3 rounded-full ${mlStatus?.models_loaded ? 'bg-green-500' : 'bg-red-500'}`}></span>
                    <div>
                      <span className="text-sm font-medium text-blue-900">
                        XGBoost Models: {mlStatus?.models_loaded ? '✅ Ready' : '❌ Need Training'}
                      </span>
                      <div className="text-xs text-blue-700">
                        {mlStatus?.feature_columns_count || 0} features • Enhanced Engineering
                      </div>
                    </div>
                  </div>
                  <div className="flex space-x-2">
                    <button
                      onClick={checkMLStatus}
                      className="px-3 py-1 text-sm bg-blue-600 text-white rounded hover:bg-blue-700"
                    >
                      🔄 Refresh
                    </button>
                    {!mlStatus?.models_loaded && (
                      <button
                        onClick={trainMLModels}
                        disabled={trainingModels}
                        className="px-3 py-1 text-sm bg-orange-600 text-white rounded hover:bg-orange-700 disabled:bg-gray-400"
                      >
                        {trainingModels ? '⏳ Training...' : '🧠 Train'}
                      </button>
                    )}
                  </div>
                </div>
              </div>

              {!predictionResult ? (
                /* Enhanced Prediction Form */
                <div className="space-y-6">
                  {/* Basic Match Setup */}
                  <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-2">Home Team *</label>
                      <select
                        value={predictionForm.home_team}
                        onChange={(e) => {
                          handlePredictionFormChange('home_team', e.target.value);
                          if (e.target.value && showStartingXI) {
                            fetchTeamPlayers(e.target.value, true);
                          }
                        }}
                        className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                      >
                        <option value="">Select Home Team</option>
                        {teams.map(team => (
                          <option key={team} value={team}>{team}</option>
                        ))}
                      </select>
                    </div>

                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-2">Away Team *</label>
                      <select
                        value={predictionForm.away_team}
                        onChange={(e) => {
                          handlePredictionFormChange('away_team', e.target.value);
                          if (e.target.value && showStartingXI) {
                            fetchTeamPlayers(e.target.value, false);
                          }
                        }}
                        className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                      >
                        <option value="">Select Away Team</option>
                        {teams.filter(team => team !== predictionForm.home_team).map(team => (
                          <option key={team} value={team}>{team}</option>
                        ))}
                      </select>
                    </div>

                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-2">Referee *</label>
                      <select
                        value={predictionForm.referee_name}
                        onChange={(e) => handlePredictionFormChange('referee_name', e.target.value)}
                        className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                      >
                        <option value="">Select Referee</option>
                        {referees.map(referee => (
                          <option key={referee} value={referee}>{referee}</option>
                        ))}
                      </select>
                    </div>
                  </div>

                  {/* Formation and Date */}
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-2">Formation</label>
                      <select
                        value={selectedFormation}
                        onChange={(e) => handleFormationChange(e.target.value)}
                        disabled={!showStartingXI}
                        className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 disabled:bg-gray-100 disabled:text-gray-500"
                      >
                        {availableFormations.map(formation => (
                          <option key={formation} value={formation}>{formation}</option>
                        ))}
                      </select>
                      {!showStartingXI && (
                        <p className="text-xs text-gray-500 mt-1">Enable Starting XI to change formation</p>
                      )}
                    </div>

                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-2">Match Date (Optional)</label>
                      <input
                        type="date"
                        value={predictionForm.match_date}
                        onChange={(e) => handlePredictionFormChange('match_date', e.target.value)}
                        className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                      />
                    </div>
                  </div>

                  {/* Starting XI Selection Interface */}
                  {showStartingXI && (predictionForm.home_team || predictionForm.away_team) && (
                    <div className="space-y-6">
                      <div className="border-t pt-6">
                        <h3 className="text-lg font-semibold text-gray-900 mb-4">⚽ Starting XI Selection ({selectedFormation})</h3>
                        
                        {loadingPlayers && (
                          <div className="flex items-center justify-center py-8">
                            <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
                            <span className="ml-3 text-gray-600">Loading players and generating default lineups...</span>
                          </div>
                        )}

                        {!loadingPlayers && (
                          <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
                            {/* Home Team Starting XI */}
                            {predictionForm.home_team && homeStartingXI && (
                              <div className="bg-green-50 p-6 rounded-lg border border-green-200">
                                <div className="flex items-center justify-between mb-4">
                                  <h4 className="font-semibold text-green-900 text-lg">🏠 {predictionForm.home_team}</h4>
                                  <span className={`px-3 py-1 rounded-full text-sm font-medium ${
                                    validateStartingXI(homeStartingXI) 
                                      ? 'bg-green-100 text-green-800' 
                                      : 'bg-yellow-100 text-yellow-800'
                                  }`}>
                                    {homeStartingXI.positions.filter(pos => pos.player).length}/11 selected
                                  </span>
                                </div>
                                
                                <div className="space-y-3">
                                  {['GK', 'DEF', 'MID', 'FWD'].map(posType => {
                                    const positions = homeStartingXI.positions.filter(pos => pos.position_type === posType);
                                    return (
                                      <div key={posType} className="space-y-2">
                                        <div className="text-sm font-medium text-green-800 uppercase">{posType}</div>
                                        {positions.map(position => (
                                          <div key={position.position_id} className="flex items-center space-x-3">
                                            <div className="w-12 text-xs font-medium text-green-700">
                                              {position.position_id}
                                            </div>
                                            <select
                                              value={position.player?.player_name || ''}
                                              onChange={(e) => {
                                                const selectedPlayer = homeTeamPlayers.find(p => p.player_name === e.target.value);
                                                updateStartingXIPlayer(true, position.position_id, selectedPlayer);
                                              }}
                                              className="flex-1 px-3 py-2 border border-green-300 rounded-lg focus:ring-2 focus:ring-green-500 focus:border-green-500 text-sm"
                                            >
                                              <option value="">Select Player</option>
                                              {homeTeamPlayers
                                                .filter(player => 
                                                  player.position === position.position_type || 
                                                  !homeStartingXI.positions.some(pos => pos.player?.player_name === player.player_name)
                                                )
                                                .map(player => (
                                                  <option key={player.player_name} value={player.player_name}>
                                                    {player.player_name} ({player.matches_played} matches)
                                                  </option>
                                                ))
                                              }
                                            </select>
                                          </div>
                                        ))}
                                      </div>
                                    );
                                  })}
                                </div>
                              </div>
                            )}

                            {/* Away Team Starting XI */}
                            {predictionForm.away_team && awayStartingXI && (
                              <div className="bg-blue-50 p-6 rounded-lg border border-blue-200">
                                <div className="flex items-center justify-between mb-4">
                                  <h4 className="font-semibold text-blue-900 text-lg">✈️ {predictionForm.away_team}</h4>
                                  <span className={`px-3 py-1 rounded-full text-sm font-medium ${
                                    validateStartingXI(awayStartingXI) 
                                      ? 'bg-blue-100 text-blue-800' 
                                      : 'bg-yellow-100 text-yellow-800'
                                  }`}>
                                    {awayStartingXI.positions.filter(pos => pos.player).length}/11 selected
                                  </span>
                                </div>
                                
                                <div className="space-y-3">
                                  {['GK', 'DEF', 'MID', 'FWD'].map(posType => {
                                    const positions = awayStartingXI.positions.filter(pos => pos.position_type === posType);
                                    return (
                                      <div key={posType} className="space-y-2">
                                        <div className="text-sm font-medium text-blue-800 uppercase">{posType}</div>
                                        {positions.map(position => (
                                          <div key={position.position_id} className="flex items-center space-x-3">
                                            <div className="w-12 text-xs font-medium text-blue-700">
                                              {position.position_id}
                                            </div>
                                            <select
                                              value={position.player?.player_name || ''}
                                              onChange={(e) => {
                                                const selectedPlayer = awayTeamPlayers.find(p => p.player_name === e.target.value);
                                                updateStartingXIPlayer(false, position.position_id, selectedPlayer);
                                              }}
                                              className="flex-1 px-3 py-2 border border-blue-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 text-sm"
                                            >
                                              <option value="">Select Player</option>
                                              {awayTeamPlayers
                                                .filter(player => 
                                                  player.position === position.position_type || 
                                                  !awayStartingXI.positions.some(pos => pos.player?.player_name === player.player_name)
                                                )
                                                .map(player => (
                                                  <option key={player.player_name} value={player.player_name}>
                                                    {player.player_name} ({player.matches_played} matches)
                                                  </option>
                                                ))
                                              }
                                            </select>
                                          </div>
                                        ))}
                                      </div>
                                    );
                                  })}
                                </div>
                              </div>
                            )}
                          </div>
                        )}
                      </div>
                    </div>
                  )}

                  {/* Prediction Buttons */}
                  <div className="flex space-x-4">
                    <button
                      onClick={showStartingXI ? predictMatchEnhanced : predictMatch}
                      disabled={
                        predicting || 
                        !predictionForm.home_team || 
                        !predictionForm.away_team || 
                        !predictionForm.referee_name ||
                        (showStartingXI && (!validateStartingXI(homeStartingXI) || !validateStartingXI(awayStartingXI)))
                      }
                      className="px-6 py-3 bg-gradient-to-r from-blue-600 to-indigo-600 text-white font-medium rounded-lg hover:from-blue-700 hover:to-indigo-700 disabled:bg-gray-400 disabled:cursor-not-allowed flex items-center space-x-2 shadow-md"
                    >
                      {predicting ? (
                        <>
                          <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white"></div>
                          <span>Calculating...</span>
                        </>
                      ) : (
                        <>
                          <span>🚀</span>
                          <span>{showStartingXI ? 'Enhanced Predict with XI' : 'Standard XGBoost Predict'}</span>
                        </>
                      )}
                    </button>

                    {showStartingXI && (predictionForm.home_team || predictionForm.away_team) && (
                      <button
                        onClick={() => {
                          if (predictionForm.home_team) fetchTeamPlayers(predictionForm.home_team, true);
                          if (predictionForm.away_team) fetchTeamPlayers(predictionForm.away_team, false);
                        }}
                        disabled={loadingPlayers}
                        className="px-4 py-3 bg-gray-600 text-white font-medium rounded-lg hover:bg-gray-700 disabled:bg-gray-400 disabled:cursor-not-allowed"
                      >
                        🔄 Reset to Default XI
                      </button>
                    )}
                  </div>

                  {/* Algorithm Explanation */}
                  <div className="bg-gradient-to-r from-gray-50 to-blue-50 p-6 rounded-lg border border-gray-200">
                    <h3 className="text-md font-semibold text-gray-900 mb-3">
                      {showStartingXI ? '🎯 Enhanced XGBoost Algorithm' : '🚀 Standard XGBoost Algorithm'}
                    </h3>
                    <div className="text-sm text-gray-700 space-y-2">
                      {showStartingXI ? (
                        <>
                          <div className="flex items-start space-x-2">
                            <span className="text-blue-600 font-semibold">1.</span>
                            <span><strong>Player-Specific Analysis:</strong> Uses stats only from selected starting XI players</span>
                          </div>
                          <div className="flex items-start space-x-2">
                            <span className="text-blue-600 font-semibold">2.</span>
                            <span><strong>Time Decay Weighting:</strong> Recent matches weighted higher ({decayPreset} preset)</span>
                          </div>
                          <div className="flex items-start space-x-2">
                            <span className="text-blue-600 font-semibold">3.</span>
                            <span><strong>Formation-Aware Features:</strong> Considers tactical setup and player positions</span>
                          </div>
                          <div className="flex items-start space-x-2">
                            <span className="text-blue-600 font-semibold">4.</span>
                            <span><strong>Enhanced Features:</strong> 45+ features including player combinations</span>
                          </div>
                          <div className="flex items-start space-x-2">
                            <span className="text-blue-600 font-semibold">5.</span>
                            <span><strong>XGBoost ML:</strong> Gradient boosting with enhanced feature engineering</span>
                          </div>
                        </>
                      ) : (
                        <>
                          <div className="flex items-start space-x-2">
                            <span className="text-orange-600 font-semibold">1.</span>
                            <span><strong>Team Aggregation:</strong> Uses all available player data aggregated to team level</span>
                          </div>
                          <div className="flex items-start space-x-2">
                            <span className="text-orange-600 font-semibold">2.</span>
                            <span><strong>Standard Features:</strong> 45+ team-level features (form, referee bias, head-to-head)</span>
                          </div>
                          <div className="flex items-start space-x-2">
                            <span className="text-orange-600 font-semibold">3.</span>
                            <span><strong>XGBoost ML:</strong> Gradient boosting for Win/Draw/Loss and goal predictions</span>
                          </div>
                          <div className="flex items-start space-x-2">
                            <span className="text-orange-600 font-semibold">4.</span>
                            <span><strong>Poisson Distribution:</strong> Scoreline probabilities based on expected goals</span>
                          </div>
                        </>
                      )}
                    </div>
                  </div>
                </div>
              ) : (
                /* Enhanced Prediction Results */
                <div className="space-y-6">
                  {/* Header with enhanced features indicators */}
                  <div className="bg-gradient-to-r from-green-50 to-blue-50 p-6 rounded-lg border border-green-200">
                    <div className="text-center">
                      <h3 className="text-2xl font-bold text-gray-900 mb-2">
                        {predictionResult.home_team} vs {predictionResult.away_team}
                      </h3>
                      <div className="text-lg text-gray-600 mb-4">
                        Predicted Score: <span className="font-bold text-blue-600">{predictionResult.predicted_home_goals}</span>
                        {' - '}
                        <span className="font-bold text-red-600">{predictionResult.predicted_away_goals}</span>
                      </div>
                      
                      {/* Enhancement indicators */}
                      <div className="flex items-center justify-center space-x-4 text-sm">
                        {predictionResult.prediction_breakdown?.starting_xi_used?.home_team && (
                          <span className="px-3 py-1 bg-green-100 text-green-800 rounded-full">✅ Home XI</span>
                        )}
                        {predictionResult.prediction_breakdown?.starting_xi_used?.away_team && (
                          <span className="px-3 py-1 bg-blue-100 text-blue-800 rounded-full">✅ Away XI</span>
                        )}
                        {predictionResult.prediction_breakdown?.time_decay_applied && (
                          <span className="px-3 py-1 bg-purple-100 text-purple-800 rounded-full">
                            ⏰ {predictionResult.prediction_breakdown?.decay_preset}
                          </span>
                        )}
                        <span className="px-3 py-1 bg-orange-100 text-orange-800 rounded-full">
                          🚀 Enhanced XGBoost
                        </span>
                      </div>
                    </div>
                  </div>

                  {/* Win/Draw/Loss Probabilities */}
                  <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                    <div className="bg-white p-6 border rounded-lg text-center shadow-sm">
                      <div className="text-4xl font-bold text-green-600 mb-2">{predictionResult.home_win_probability}%</div>
                      <div className="text-gray-600 mb-3">Home Win</div>
                      <div className="w-full bg-gray-200 rounded-full h-3">
                        <div 
                          className="bg-green-600 h-3 rounded-full transition-all duration-1000" 
                          style={{width: `${predictionResult.home_win_probability}%`}}
                        ></div>
                      </div>
                    </div>
                    <div className="bg-white p-6 border rounded-lg text-center shadow-sm">
                      <div className="text-4xl font-bold text-gray-600 mb-2">{predictionResult.draw_probability}%</div>
                      <div className="text-gray-600 mb-3">Draw</div>
                      <div className="w-full bg-gray-200 rounded-full h-3">
                        <div 
                          className="bg-gray-600 h-3 rounded-full transition-all duration-1000" 
                          style={{width: `${predictionResult.draw_probability}%`}}
                        ></div>
                      </div>
                    </div>
                    <div className="bg-white p-6 border rounded-lg text-center shadow-sm">
                      <div className="text-4xl font-bold text-red-600 mb-2">{predictionResult.away_win_probability}%</div>
                      <div className="text-gray-600 mb-3">Away Win</div>
                      <div className="w-full bg-gray-200 rounded-full h-3">
                        <div 
                          className="bg-red-600 h-3 rounded-full transition-all duration-1000" 
                          style={{width: `${predictionResult.away_win_probability}%`}}
                        ></div>
                      </div>
                    </div>
                  </div>

                  {/* Additional Stats */}
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                    <div className="bg-white p-6 rounded-lg border shadow-sm">
                      <h4 className="font-semibold text-gray-900 mb-3">⚽ Expected Goals</h4>
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
                    
                    <div className="bg-white p-6 rounded-lg border shadow-sm">
                      <h4 className="font-semibold text-gray-900 mb-3">🎯 Model Confidence</h4>
                      <div className="space-y-2">
                        <div className="flex justify-between">
                          <span className="text-gray-600">Prediction Method:</span>
                          <span className="font-medium">{predictionResult.prediction_breakdown?.prediction_method || 'Enhanced ML'}</span>
                        </div>
                        <div className="flex justify-between">
                          <span className="text-gray-600">Features Used:</span>
                          <span className="font-medium">{predictionResult.prediction_breakdown?.model_confidence?.features_used || 'N/A'}</span>
                        </div>
                      </div>
                    </div>
                  </div>

                  {/* Action Buttons */}
                  <div className="flex space-x-4">
                    <button
                      onClick={resetPrediction}
                      className="px-6 py-3 bg-gray-600 text-white font-medium rounded-lg hover:bg-gray-700"
                    >
                      🔄 New Prediction
                    </button>
                    
                    <button
                      onClick={exportPDF}
                      disabled={exportingPDF}
                      className="px-6 py-3 bg-green-600 text-white font-medium rounded-lg hover:bg-green-700 disabled:bg-gray-400 flex items-center space-x-2"
                    >
                      {exportingPDF ? (
                        <>
                          <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white"></div>
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
        )}

        {/* Analysis Tab */}
        {activeTab === 'analysis' && (
          <div className="space-y-6">
            <div className="bg-white p-6 rounded-lg shadow-sm border">
              <h2 className="text-xl font-bold text-gray-900 mb-4">📈 Analytics Dashboard</h2>
              <p className="text-gray-600 mb-6">
                Comprehensive analysis tools for football data including regression analysis, 
                referee bias studies, and predictive model optimization.
              </p>

              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                <div className="bg-blue-50 p-6 rounded-lg border border-blue-200">
                  <h3 className="font-semibold text-blue-900 mb-3">📊 Regression Analysis</h3>
                  <p className="text-blue-700 text-sm mb-4">
                    Analyze statistical correlations between team performance metrics and match outcomes.
                  </p>
                  <button className="w-full px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700">
                    Run Analysis
                  </button>
                </div>

                <div className="bg-green-50 p-6 rounded-lg border border-green-200">
                  <h3 className="font-semibold text-green-900 mb-3">⚖️ Referee Bias Study</h3>
                  <p className="text-green-700 text-sm mb-4">
                    Calculate and analyze referee bias scores across different teams and competitions.
                  </p>
                  <button className="w-full px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700">
                    Calculate RBS
                  </button>
                </div>

                <div className="bg-purple-50 p-6 rounded-lg border border-purple-200">
                  <h3 className="font-semibold text-purple-900 mb-3">🎯 Model Optimization</h3>
                  <p className="text-purple-700 text-sm mb-4">
                    Optimize prediction algorithms and analyze feature importance for better accuracy.
                  </p>
                  <button className="w-full px-4 py-2 bg-purple-600 text-white rounded-lg hover:bg-purple-700">
                    Optimize Models
                  </button>
                </div>
              </div>
            </div>
          </div>
        )}

        {/* Configuration Tab */}
        {activeTab === 'config' && (
          <div className="space-y-6">
            <div className="bg-white p-6 rounded-lg shadow-sm border">
              <h2 className="text-xl font-bold text-gray-900 mb-4">⚙️ System Configuration</h2>
              <p className="text-gray-600 mb-6">
                Configure prediction algorithms, time decay settings, and system parameters.
              </p>

              <div className="space-y-8">
                {/* Time Decay Configuration */}
                <div className="border-b pb-6">
                  <h3 className="text-lg font-semibold text-gray-900 mb-4">⏰ Time Decay Settings</h3>
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-2">Default Decay Preset</label>
                      <select
                        value={decayPreset}
                        onChange={(e) => setDecayPreset(e.target.value)}
                        className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                      >
                        {decayPresets.map(preset => (
                          <option key={preset.preset_name} value={preset.preset_name}>
                            {preset.preset_name.charAt(0).toUpperCase() + preset.preset_name.slice(1)}
                          </option>
                        ))}
                      </select>
                    </div>
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-2">Apply by Default</label>
                      <label className="flex items-center space-x-2">
                        <input
                          type="checkbox"
                          checked={useTimeDecay}
                          onChange={(e) => setUseTimeDecay(e.target.checked)}
                          className="rounded border-gray-300 text-blue-600 focus:ring-blue-500"
                        />
                        <span className="text-sm text-gray-600">Enable time decay by default</span>
                      </label>
                    </div>
                  </div>
                </div>

                {/* Formation Settings */}
                <div className="border-b pb-6">
                  <h3 className="text-lg font-semibold text-gray-900 mb-4">⚽ Formation Settings</h3>
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-2">Default Formation</label>
                      <select
                        value={selectedFormation}
                        onChange={(e) => setSelectedFormation(e.target.value)}
                        className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                      >
                        {availableFormations.map(formation => (
                          <option key={formation} value={formation}>{formation}</option>
                        ))}
                      </select>
                    </div>
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-2">Available Formations</label>
                      <div className="text-sm text-gray-600">
                        {availableFormations.join(', ')}
                      </div>
                    </div>
                  </div>
                </div>

                {/* System Status */}
                <div>
                  <h3 className="text-lg font-semibold text-gray-900 mb-4">🔧 System Status</h3>
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                    <div className="bg-gray-50 p-4 rounded-lg">
                      <h4 className="font-medium text-gray-900 mb-2">XGBoost Models</h4>
                      <div className="flex items-center space-x-2">
                        <span className={`inline-block w-3 h-3 rounded-full ${mlStatus?.models_loaded ? 'bg-green-500' : 'bg-red-500'}`}></span>
                        <span className="text-sm">{mlStatus?.models_loaded ? 'Loaded' : 'Not Loaded'}</span>
                      </div>
                    </div>
                    <div className="bg-gray-50 p-4 rounded-lg">
                      <h4 className="font-medium text-gray-900 mb-2">Data Status</h4>
                      <div className="text-sm text-gray-600">
                        {teams.length} teams, {referees.length} referees
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        )}

      </div>
    </div>
  );
}

export default App;