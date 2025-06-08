        {activeTab === 'xgboost' && (
          <div className="space-y-6">
            <div className="bg-white p-6 rounded-lg shadow-sm border">
              <h2 className="text-xl font-bold text-gray-900 mb-4">🚀 Enhanced XGBoost Prediction with Starting XI</h2>
              <p className="text-gray-600 mb-6">
                Advanced match prediction using XGBoost with Starting XI player selection and time decay. 
                Select specific players for each team to get more accurate predictions based on actual lineups.
              </p>

              {/* Enhanced Features Toggle */}
              <div className="mb-6 p-4 bg-gradient-to-r from-blue-50 to-indigo-50 rounded-lg border border-blue-200">
                <div className="flex items-center justify-between mb-4">
                  <h3 className="text-lg font-semibold text-blue-900">🎯 Enhanced Prediction Features</h3>
                  <button
                    onClick={() => setShowStartingXI(!showStartingXI)}
                    className={`px-4 py-2 rounded-lg font-medium ${
                      showStartingXI 
                        ? 'bg-blue-600 text-white' 
                        : 'bg-gray-200 text-gray-700 hover:bg-gray-300'
                    }`}
                  >
                    {showStartingXI ? '✅ Using Starting XI' : '📋 Enable Starting XI'}
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
                    <p className="text-xs text-blue-700 mt-1">Recent matches have higher impact than older ones</p>
                  </div>
                  
                  <div>
                    <label className="block text-sm font-medium text-blue-900 mb-1">Decay Preset</label>
                    <select
                      value={decayPreset}
                      onChange={(e) => setDecayPreset(e.target.value)}
                      disabled={!useTimeDecay}
                      className="w-full px-3 py-2 border border-blue-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 disabled:bg-gray-100"
                    >
                      {decayPresets.map(preset => (
                        <option key={preset.preset_name} value={preset.preset_name}>
                          {preset.preset_name.charAt(0).toUpperCase() + preset.preset_name.slice(1)} - {preset.description}
                        </option>
                      ))}
                    </select>
                  </div>
                </div>

                {/* ML Status */}
                <div className="flex items-center space-x-2">
                  <span className={`inline-block w-3 h-3 rounded-full ${mlStatus?.models_loaded ? 'bg-green-500' : 'bg-red-500'}`}></span>
                  <span className="text-sm font-medium text-blue-900">
                    XGBoost Models: {mlStatus?.models_loaded ? '✅ Ready' : '❌ Need Training'}
                  </span>
                  <button
                    onClick={checkMLStatus}
                    className="ml-auto px-3 py-1 text-sm bg-blue-600 text-white rounded hover:bg-blue-700"
                  >
                    Refresh
                  </button>
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
                        className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 disabled:bg-gray-100"
                      >
                        {availableFormations.map(formation => (
                          <option key={formation} value={formation}>{formation}</option>
                        ))}
                      </select>
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

                  {/* Starting XI Selection */}
                  {showStartingXI && (predictionForm.home_team || predictionForm.away_team) && (
                    <div className="space-y-6">
                      <div className="border-t pt-6">
                        <h3 className="text-lg font-semibold text-gray-900 mb-4">⚽ Starting XI Selection ({selectedFormation})</h3>
                        
                        {loadingPlayers && (
                          <div className="flex items-center justify-center py-8">
                            <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
                            <span className="ml-3 text-gray-600">Loading players...</span>
                          </div>
                        )}

                        {!loadingPlayers && (
                          <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
                            {/* Home Team Starting XI */}
                            {predictionForm.home_team && homeStartingXI && (
                              <div className="bg-green-50 p-4 rounded-lg border border-green-200">
                                <div className="flex items-center justify-between mb-4">
                                  <h4 className="font-semibold text-green-900">🏠 {predictionForm.home_team}</h4>
                                  <span className={`px-2 py-1 rounded text-xs font-medium ${
                                    validateStartingXI(homeStartingXI) 
                                      ? 'bg-green-100 text-green-800' 
                                      : 'bg-yellow-100 text-yellow-800'
                                  }`}>
                                    {homeStartingXI.positions.filter(pos => pos.player).length}/11 selected
                                  </span>
                                </div>
                                
                                <div className="space-y-3">
                                  {homeStartingXI.positions.map(position => (
                                    <div key={position.position_id} className="flex items-center space-x-3">
                                      <div className="w-16 text-xs font-medium text-green-700">
                                        {position.position_type}
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
                                            // Only show players of same position or unassigned players
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
                              </div>
                            )}

                            {/* Away Team Starting XI */}
                            {predictionForm.away_team && awayStartingXI && (
                              <div className="bg-blue-50 p-4 rounded-lg border border-blue-200">
                                <div className="flex items-center justify-between mb-4">
                                  <h4 className="font-semibold text-blue-900">✈️ {predictionForm.away_team}</h4>
                                  <span className={`px-2 py-1 rounded text-xs font-medium ${
                                    validateStartingXI(awayStartingXI) 
                                      ? 'bg-blue-100 text-blue-800' 
                                      : 'bg-yellow-100 text-yellow-800'
                                  }`}>
                                    {awayStartingXI.positions.filter(pos => pos.player).length}/11 selected
                                  </span>
                                </div>
                                
                                <div className="space-y-3">
                                  {awayStartingXI.positions.map(position => (
                                    <div key={position.position_id} className="flex items-center space-x-3">
                                      <div className="w-16 text-xs font-medium text-blue-700">
                                        {position.position_type}
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
                                            // Only show players of same position or unassigned players
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
                              </div>
                            )}
                          </div>
                        )}
                      </div>
                    </div>
                  )}

                  {/* Prediction Button */}
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
                      className="px-6 py-3 bg-blue-600 text-white font-medium rounded-lg hover:bg-blue-700 disabled:bg-gray-400 disabled:cursor-not-allowed flex items-center space-x-2"
                    >
                      {predicting ? (
                        <>
                          <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white"></div>
                          <span>Calculating...</span>
                        </>
                      ) : (
                        <>
                          <span>🚀</span>
                          <span>{showStartingXI ? 'Enhanced Predict with XI' : 'Standard Predict'}</span>
                        </>
                      )}
                    </button>

                    {showStartingXI && (
                      <button
                        onClick={() => {
                          if (predictionForm.home_team) fetchTeamPlayers(predictionForm.home_team, true);
                          if (predictionForm.away_team) fetchTeamPlayers(predictionForm.away_team, false);
                        }}
                        disabled={loadingPlayers || !predictionForm.home_team || !predictionForm.away_team}
                        className="px-4 py-3 bg-gray-600 text-white font-medium rounded-lg hover:bg-gray-700 disabled:bg-gray-400 disabled:cursor-not-allowed"
                      >
                        🔄 Reset to Default XI
                      </button>
                    )}
                  </div>

                  {/* Algorithm Explanation */}
                  <div className="bg-gray-50 p-4 rounded-lg">
                    <h3 className="text-md font-semibold text-gray-900 mb-2">
                      {showStartingXI ? '🎯 Enhanced XGBoost Algorithm' : '🚀 Standard XGBoost Algorithm'}
                    </h3>
                    <div className="text-sm text-gray-700 space-y-1">
                      {showStartingXI ? (
                        <>
                          <p><strong>1. Player-Specific Analysis:</strong> Uses stats only from selected starting XI players</p>
                          <p><strong>2. Time Decay Weighting:</strong> Recent matches weighted higher than historical data</p>
                          <p><strong>3. Enhanced Features:</strong> 45+ features including player combinations and form</p>
                          <p><strong>4. Formation-Aware:</strong> Considers tactical setup and player positions</p>
                          <p><strong>5. XGBoost ML:</strong> Gradient boosting with enhanced feature engineering</p>
                          <p><strong>6. Poisson Simulation:</strong> Detailed scoreline probability distribution</p>
                        </>
                      ) : (
                        <>
                          <p><strong>1. Team Aggregation:</strong> Uses all available player data aggregated to team level</p>
                          <p><strong>2. Historical Analysis:</strong> Equal weighting of all historical matches</p>
                          <p><strong>3. Standard Features:</strong> 45+ team-level features (form, referee bias, head-to-head)</p>
                          <p><strong>4. XGBoost ML:</strong> Gradient boosting for Win/Draw/Loss and goal predictions</p>
                          <p><strong>5. Poisson Distribution:</strong> Scoreline probabilities based on expected goals</p>
                        </>
                      )}
                    </div>
                  </div>
                </div>
              ) : (
                /* Enhanced Prediction Results */
                <div className="space-y-6">
                  {/* Header with enhanced features used */}
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
                          <span className="px-2 py-1 bg-green-100 text-green-800 rounded-full">✅ Home XI</span>
                        )}
                        {predictionResult.prediction_breakdown?.starting_xi_used?.away_team && (
                          <span className="px-2 py-1 bg-blue-100 text-blue-800 rounded-full">✅ Away XI</span>
                        )}
                        {predictionResult.prediction_breakdown?.time_decay_applied && (
                          <span className="px-2 py-1 bg-purple-100 text-purple-800 rounded-full">
                            ⏰ {predictionResult.prediction_breakdown?.decay_preset}
                          </span>
                        )}
                      </div>
                    </div>
                  </div>

                  {/* Enhanced prediction results display would continue here... */}
                  {/* For now, show standard results but with enhanced indicators */}
                  <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                    <div className="bg-white p-4 border rounded-lg text-center">
                      <div className="text-3xl font-bold text-green-600">{predictionResult.home_win_probability}%</div>
                      <div className="text-gray-600">Home Win</div>
                    </div>
                    <div className="bg-white p-4 border rounded-lg text-center">
                      <div className="text-3xl font-bold text-gray-600">{predictionResult.draw_probability}%</div>
                      <div className="text-gray-600">Draw</div>
                    </div>
                    <div className="bg-white p-4 border rounded-lg text-center">
                      <div className="text-3xl font-bold text-red-600">{predictionResult.away_win_probability}%</div>
                      <div className="text-gray-600">Away Win</div>
                    </div>
                  </div>

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