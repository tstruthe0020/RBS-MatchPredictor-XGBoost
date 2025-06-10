import React from 'react';
import { RBSVarianceAnalysis } from '../advanced-features';
import { getRBSScoreColor } from '../analysis-components';

const Results = ({
  refereeAnalysis,
  setRefereeAnalysis,
  selectedRefereeForDetails,
  setSelectedRefereeForDetails,
  detailedRefereeAnalysis,
  setDetailedRefereeAnalysis,
  enhancedRefereeAnalysis,
  setEnhancedRefereeAnalysis,
  selectedTeamForRefereeAnalysis,
  setSelectedTeamForRefereeAnalysis,
  loadingRefereeAnalysis,
  setLoadingRefereeAnalysis,
  loadingDetailedAnalysis,
  setLoadingDetailedAnalysis,
  loadingEnhancedAnalysis,
  setLoadingEnhancedAnalysis,
  teams,
  referees,
  fetchRefereeAnalysis,
  fetchDetailedRefereeAnalysis,
  fetchEnhancedRBSAnalysis,
  defaultDecayPreset,
  setDefaultDecayPreset,
  decayPresets,
  saveSystemConfig
}) => {

  const handleFetchRefereeAnalysis = async () => {
    setLoadingRefereeAnalysis(true);
    try {
      const data = await fetchRefereeAnalysis();
      setRefereeAnalysis(data);
    } catch (error) {
      console.error('Error fetching referee analysis:', error);
      alert(`❌ Error loading referee analysis: ${error.response?.data?.detail || error.message}`);
    } finally {
      setLoadingRefereeAnalysis(false);
    }
  };

  const handleRefereeClick = async (refereeName) => {
    setSelectedRefereeForDetails(refereeName);
    setLoadingDetailedAnalysis(true);
    try {
      const data = await fetchDetailedRefereeAnalysis(refereeName);
      setDetailedRefereeAnalysis(data);
    } catch (error) {
      console.error('Error fetching detailed referee analysis:', error);
      alert(`❌ Error loading detailed analysis: ${error.response?.data?.detail || error.message}`);
    } finally {
      setLoadingDetailedAnalysis(false);
    }
  };

  const handleEnhancedRefereeAnalysis = async () => {
    if (!selectedTeamForRefereeAnalysis || !selectedRefereeForDetails) {
      alert('Please select both a team and a referee for enhanced analysis');
      return;
    }

    setLoadingEnhancedAnalysis(true);
    try {
      const data = await fetchEnhancedRBSAnalysis(selectedTeamForRefereeAnalysis, selectedRefereeForDetails);
      setEnhancedRefereeAnalysis(data);
    } catch (error) {
      console.error('Error fetching enhanced referee analysis:', error);
      alert(`❌ Error loading enhanced analysis: ${error.response?.data?.detail || error.message}`);
    } finally {
      setLoadingEnhancedAnalysis(false);
    }
  };

  const closeDetailedAnalysis = () => {
    setSelectedRefereeForDetails(null);
    setDetailedRefereeAnalysis(null);
    setEnhancedRefereeAnalysis(null);
  };

  const handleSaveSystemConfig = async () => {
    try {
      await saveSystemConfig({
        default_decay_preset: defaultDecayPreset
      });
      alert('✅ System configuration saved successfully!');
    } catch (error) {
      console.error('Error saving system config:', error);
      alert(`❌ Error saving configuration: ${error.response?.data?.detail || error.message}`);
    }
  };

  return (
    <div className="space-y-6">
      <div className="bg-white p-6 rounded-lg shadow-lg border border-gray-200">
        <h2 className="text-xl font-bold mb-4" style={{color: '#002629'}}>📋 Results & Referee Analysis</h2>
        <p className="mb-6" style={{color: '#002629', opacity: 0.8}}>
          Comprehensive analysis of referee decisions, bias patterns, and team-specific statistics.
        </p>

        {/* Time Decay Configuration */}
        <div className="mb-6 p-4 rounded-lg border-2" style={{backgroundColor: '#F2E9E4', borderColor: '#12664F'}}>
          <div className="flex items-center justify-between mb-4">
            <div>
              <h3 className="font-semibold" style={{color: '#002629'}}>⏰ Time Decay Configuration</h3>
              <p className="text-sm mt-1" style={{color: '#002629', opacity: 0.8}}>
                Set the default time decay preset for match predictions
              </p>
            </div>
            <button
              onClick={handleSaveSystemConfig}
              className="px-4 py-2 text-white font-medium rounded hover:opacity-90 transition-opacity"
              style={{backgroundColor: '#12664F'}}
            >
              💾 Save Config
            </button>
          </div>
          
          <div className="flex items-center space-x-4">
            <label className="text-sm font-medium" style={{color: '#002629'}}>Default Preset:</label>
            <select
              value={defaultDecayPreset}
              onChange={(e) => setDefaultDecayPreset(e.target.value)}
              className="form-select"
              style={{minWidth: '200px'}}
            >
              {decayPresets.map(preset => (
                <option key={preset.name} value={preset.name}>
                  {preset.display_name} - {preset.description}
                </option>
              ))}
            </select>
          </div>
        </div>

        {/* Overall Referee Analysis */}
        <div className="mb-6">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-lg font-semibold" style={{color: '#002629'}}>⚖️ Overall Referee Analysis</h3>
            <button
              onClick={handleFetchRefereeAnalysis}
              disabled={loadingRefereeAnalysis}
              className="px-4 py-2 text-white font-medium rounded hover:opacity-90 disabled:opacity-50 disabled:cursor-not-allowed flex items-center space-x-2"
              style={{backgroundColor: '#1C5D99'}}
            >
              {loadingRefereeAnalysis ? (
                <>
                  <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white"></div>
                  <span>Loading...</span>
                </>
              ) : (
                <>
                  <span>📊</span>
                  <span>Load Analysis</span>
                </>
              )}
            </button>
          </div>

          {refereeAnalysis && (
            <div className="grid grid-cols-1 lg:grid-cols-2 xl:grid-cols-3 gap-4">
              {refereeAnalysis.map((referee, index) => (
                <div 
                  key={index}
                  onClick={() => handleRefereeClick(referee.name)}
                  className="p-4 rounded-lg border-2 cursor-pointer hover:shadow-lg transition-all"
                  style={{
                    borderColor: '#1C5D99',
                    backgroundColor: selectedRefereeForDetails === referee.name ? '#A3D9FF' : 'white'
                  }}
                >
                  <div className="font-medium mb-2" style={{color: '#002629'}}>{referee.name}</div>
                  <div className="grid grid-cols-2 gap-2 text-sm">
                    <div>
                      <div className="text-xs" style={{color: '#002629', opacity: 0.7}}>Matches</div>
                      <div className="font-bold" style={{color: '#002629'}}>{referee.matches}</div>
                    </div>
                    <div>
                      <div className="text-xs" style={{color: '#002629', opacity: 0.7}}>Avg RBS</div>
                      <div className="font-bold" style={{color: getRBSScoreColor(referee.avg_bias_score)}}>
                        {referee.avg_bias_score?.toFixed(3) || 'N/A'}
                      </div>
                    </div>
                    <div>
                      <div className="text-xs" style={{color: '#002629', opacity: 0.7}}>Confidence</div>
                      <div className="font-bold" style={{color: '#002629'}}>
                        {referee.confidence || 0}%
                      </div>
                    </div>
                    <div>
                      <div className="text-xs" style={{color: '#002629', opacity: 0.7}}>Teams</div>
                      <div className="font-bold" style={{color: '#002629'}}>{referee.teams}</div>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>

        {/* Detailed Referee Analysis */}
        {selectedRefereeForDetails && (
          <div className="mb-6 p-4 rounded-lg border-2" style={{backgroundColor: '#A3D9FF', borderColor: '#1C5D99'}}>
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-lg font-semibold" style={{color: '#002629'}}>
                🔍 Detailed Analysis: {selectedRefereeForDetails}
              </h3>
              <button
                onClick={closeDetailedAnalysis}
                className="px-3 py-1 text-white rounded hover:opacity-90 transition-opacity"
                style={{backgroundColor: '#002629'}}
              >
                ✖️ Close
              </button>
            </div>

            {loadingDetailedAnalysis ? (
              <div className="text-center py-8">
                <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600 mx-auto"></div>
                <div className="mt-2" style={{color: '#002629'}}>Loading detailed analysis...</div>
              </div>
            ) : detailedRefereeAnalysis ? (
              <div className="space-y-6">
                {/* Summary Statistics */}
                <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                  <div className="stat-card">
                    <div className="stat-card-number">{detailedRefereeAnalysis.total_matches}</div>
                    <div className="stat-card-label">Total Matches</div>
                  </div>
                  <div className="stat-card">
                    <div className="stat-card-number">{detailedRefereeAnalysis.teams_officiated}</div>
                    <div className="stat-card-label">Teams Officiated</div>
                  </div>
                  <div className="stat-card">
                    <div className="stat-card-number" style={{color: getRBSScoreColor(detailedRefereeAnalysis.average_rbs_score)}}>
                      {detailedRefereeAnalysis.average_rbs_score?.toFixed(2) || 'N/A'}
                    </div>
                    <div className="stat-card-label">Avg Bias Score</div>
                  </div>
                  <div className="stat-card">
                    <div className="stat-card-number">{detailedRefereeAnalysis.rbs_calculations || 0}</div>
                    <div className="stat-card-label">RBS Calculations</div>
                  </div>
                </div>

                {/* Match Outcomes */}
                <div>
                  <h4 className="font-semibold mb-3" style={{color: '#002629'}}>📊 Match Outcomes</h4>
                  <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                    <div className="bg-white p-3 rounded border">
                      <div className="text-lg font-bold text-green-600">{detailedRefereeAnalysis.home_wins}</div>
                      <div className="text-sm" style={{color: '#002629'}}>Home Wins</div>
                    </div>
                    <div className="bg-white p-3 rounded border">
                      <div className="text-lg font-bold text-yellow-600">{detailedRefereeAnalysis.draws}</div>
                      <div className="text-sm" style={{color: '#002629'}}>Draws</div>
                    </div>
                    <div className="bg-white p-3 rounded border">
                      <div className="text-lg font-bold text-red-600">{detailedRefereeAnalysis.away_wins}</div>
                      <div className="text-sm" style={{color: '#002629'}}>Away Wins</div>
                    </div>
                    <div className="bg-white p-3 rounded border">
                      <div className="text-lg font-bold" style={{color: '#1C5D99'}}>
                        {detailedRefereeAnalysis.home_win_percentage?.toFixed(1) || 0}%
                      </div>
                      <div className="text-sm" style={{color: '#002629'}}>Home Win %</div>
                    </div>
                  </div>
                </div>

                {/* Enhanced RBS Analysis */}
                <div>
                  <div className="flex items-center justify-between mb-4">
                    <h4 className="font-semibold" style={{color: '#002629'}}>🎯 Enhanced RBS Analysis</h4>
                    <div className="flex items-center space-x-3">
                      <select
                        value={selectedTeamForRefereeAnalysis}
                        onChange={(e) => setSelectedTeamForRefereeAnalysis(e.target.value)}
                        className="form-select text-sm"
                        style={{minWidth: '150px'}}
                      >
                        <option value="">Select Team</option>
                        {teams.map(team => (
                          <option key={team} value={team}>{team}</option>
                        ))}
                      </select>
                      <button
                        onClick={handleEnhancedRefereeAnalysis}
                        disabled={!selectedTeamForRefereeAnalysis || loadingEnhancedAnalysis}
                        className="px-3 py-2 text-white text-sm font-medium rounded hover:opacity-90 disabled:opacity-50 disabled:cursor-not-allowed flex items-center space-x-1"
                        style={{backgroundColor: '#12664F'}}
                      >
                        {loadingEnhancedAnalysis ? (
                          <>
                            <div className="animate-spin rounded-full h-3 w-3 border-b-2 border-white"></div>
                            <span>Loading...</span>
                          </>
                        ) : (
                          <>
                            <span>🔬</span>
                            <span>Analyze</span>
                          </>
                        )}
                      </button>
                    </div>
                  </div>

                  {enhancedRefereeAnalysis && (
                    <RBSVarianceAnalysis analysis={enhancedRefereeAnalysis} />
                  )}
                </div>

                {/* Team-Specific RBS Scores */}
                {detailedRefereeAnalysis.team_rbs_scores && Object.keys(detailedRefereeAnalysis.team_rbs_scores).length > 0 && (
                  <div>
                    <h4 className="font-semibold mb-3" style={{color: '#002629'}}>🏆 Team-Specific RBS Scores</h4>
                    <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-3">
                      {Object.entries(detailedRefereeAnalysis.team_rbs_scores)
                        .sort(([,a], [,b]) => (b.rbs_score || 0) - (a.rbs_score || 0))
                        .map(([team, data]) => (
                          <div key={team} className="bg-white p-3 rounded border">
                            <div className="font-medium text-sm" style={{color: '#002629'}}>{team}</div>
                            <div className="text-lg font-bold" style={{color: getRBSScoreColor(data.rbs_score)}}>
                              {data.rbs_score?.toFixed(2) || 'N/A'}
                            </div>
                            <div className="text-xs" style={{color: '#002629', opacity: 0.7}}>
                              {data.matches} matches
                            </div>
                          </div>
                        ))}
                    </div>
                  </div>
                )}
              </div>
            ) : (
              <div className="text-center py-4" style={{color: '#002629', opacity: 0.6}}>
                No detailed analysis available for this referee
              </div>
            )}
          </div>
        )}

        {!refereeAnalysis && !loadingRefereeAnalysis && (
          <div className="text-center py-8" style={{color: '#002629', opacity: 0.6}}>
            Click "Load Analysis" to view referee statistics and analysis
          </div>
        )}
      </div>
    </div>
  );
};

export default Results;