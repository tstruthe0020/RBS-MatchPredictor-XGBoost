import React from 'react';
import { TeamPerformanceMetrics } from '../advanced-features';

const Dashboard = ({ 
  teams, 
  referees, 
  stats, 
  mlStatus, 
  rbsStatus, 
  databaseStats,
  teamPerformanceData,
  selectedTeamForAnalysis,
  setSelectedTeamForAnalysis,
  loadingTeamPerformance,
  fetchTeamPerformanceData,
  modelPerformanceData,
  optimizationHistory,
  accuracyTrends,
  loadingModelPerformance,
  setLoadingModelPerformance,
  performanceDays,
  setPerformanceDays,
  fetchModelPerformance,
  fetchOptimizationHistory,
  fetchPredictionAccuracyTrends,
  setModelPerformanceData,
  setOptimizationHistory,
  setAccuracyTrends,
  checkMLStatus,
  checkRBSStatus,
  calculateRBS,
  calculatingRBS,
  fetchDatabaseStats,
  wipeDatabase,
  wipingDatabase
}) => {
  return (
    <div className="space-y-6">
      <div className="bg-white p-6 rounded-lg shadow-lg border border-gray-200">
        <h2 className="text-xl font-bold mb-4" style={{color: '#002629'}}>📊 Football Analytics Dashboard</h2>
        <p className="mb-6" style={{color: '#002629', opacity: 0.8}}>
          Advanced football match prediction system with Enhanced XGBoost models, Starting XI analysis, and Time Decay algorithms.
        </p>

        {/* Statistics Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          <div className="p-4 rounded-lg border-2" style={{backgroundColor: '#A3D9FF', borderColor: '#1C5D99'}}>
            <div className="text-2xl font-bold" style={{color: '#002629'}}>{teams.length}</div>
            <div style={{color: '#002629'}}>Teams</div>
          </div>
          <div className="p-4 rounded-lg border-2" style={{backgroundColor: '#A3D9FF', borderColor: '#12664F'}}>
            <div className="text-2xl font-bold" style={{color: '#002629'}}>{referees.length}</div>
            <div style={{color: '#002629'}}>Referees</div>
          </div>
          <div className="p-4 rounded-lg border-2" style={{backgroundColor: '#A3D9FF', borderColor: '#1C5D99'}}>
            <div className="text-2xl font-bold" style={{color: '#002629'}}>{stats.matches || 0}</div>
            <div style={{color: '#002629'}}>Matches</div>
          </div>
          <div className="p-4 rounded-lg border-2" style={{backgroundColor: '#A3D9FF', borderColor: '#12664F'}}>
            <div className="text-2xl font-bold" style={{color: '#002629'}}>{stats.player_stats || 0}</div>
            <div style={{color: '#002629'}}>Player Records</div>
          </div>
        </div>

        {/* Enhanced Features */}
        <div className="mt-8">
          <h3 className="text-lg font-semibold mb-4" style={{color: '#002629'}}>🚀 Enhanced Features</h3>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div className="p-4 rounded-lg border-2" style={{backgroundColor: '#F2E9E4', borderColor: '#1C5D99'}}>
              <h4 className="font-semibold" style={{color: '#002629'}}>⚽ Starting XI Analysis</h4>
              <p className="text-sm mt-1" style={{color: '#002629', opacity: 0.8}}>Select specific players for each team to get predictions based on actual lineups</p>
              <div className="mt-2 text-xs" style={{color: '#1C5D99'}}>
                • Formation-based selection (4-4-2, 4-3-3, etc.)
                • Player stats aggregation
                • Position-aware analysis
              </div>
            </div>
            <div className="p-4 rounded-lg border-2" style={{backgroundColor: '#F2E9E4', borderColor: '#12664F'}}>
              <h4 className="font-semibold" style={{color: '#002629'}}>⏰ Time Decay Weighting</h4>
              <p className="text-sm mt-1" style={{color: '#002629', opacity: 0.8}}>Recent matches have higher impact than historical data</p>
              <div className="mt-2 text-xs" style={{color: '#12664F'}}>
                • Configurable decay presets
                • Exponential/Linear decay options
                • Season-aware weighting
              </div>
            </div>
          </div>
        </div>

        {/* ML Model Status */}
        <div className="mt-8 p-4 rounded-lg" style={{backgroundColor: '#A3D9FF'}}>
          <div className="flex items-center justify-between">
            <div>
              <h3 className="text-lg font-semibold" style={{color: '#002629'}}>🧠 XGBoost Models Status</h3>
              <div className="flex items-center space-x-2 mt-2">
                <span className={`inline-block w-3 h-3 rounded-full ${mlStatus?.models_loaded ? 'bg-green-500' : 'bg-red-500'}`}></span>
                <span className="text-sm font-medium" style={{color: '#002629'}}>
                  {mlStatus?.models_loaded ? '✅ Models Ready' : '❌ Models Need Training'}
                </span>
                <span className="text-xs" style={{color: '#002629', opacity: 0.7}}>
                  ({mlStatus?.feature_columns_count || 0} features)
                </span>
              </div>
            </div>
            <button
              onClick={checkMLStatus}
              className="px-3 py-1 text-sm text-white rounded hover:opacity-90 transition-opacity"
              style={{backgroundColor: '#1C5D99'}}
            >
              🔄 Refresh
            </button>
          </div>
        </div>

        {/* RBS Calculation Status */}
        <div className="mt-8 p-4 rounded-lg border-2" style={{backgroundColor: '#F2E9E4', borderColor: '#12664F'}}>
          <div className="flex items-center justify-between">
            <div>
              <h3 className="text-lg font-semibold" style={{color: '#002629'}}>⚖️ Referee Bias Score (RBS) Status</h3>
              <div className="flex items-center space-x-2 mt-2">
                <span className={`inline-block w-3 h-3 rounded-full ${rbsStatus?.calculated ? 'bg-green-500' : 'bg-red-500'}`}></span>
                <span className="text-sm font-medium" style={{color: '#002629'}}>
                  {rbsStatus?.calculated ? '✅ RBS Calculations Available' : '❌ RBS Not Calculated'}
                </span>
                {rbsStatus?.last_calculated && (
                  <span className="text-xs" style={{color: '#002629', opacity: 0.7}}>
                    (Last calculated: {new Date(rbsStatus.last_calculated).toLocaleDateString()})
                  </span>
                )}
              </div>
              {rbsStatus?.calculated && (
                <div className="mt-2 text-sm" style={{color: '#002629', opacity: 0.8}}>
                  {rbsStatus.referees_analyzed} referees analyzed • {rbsStatus.teams_covered} teams covered • {rbsStatus.total_calculations} bias scores
                </div>
              )}
            </div>
            <div className="flex space-x-2">
              <button
                onClick={checkRBSStatus}
                className="px-3 py-1 text-sm text-white rounded hover:opacity-90 transition-opacity"
                style={{backgroundColor: '#1C5D99'}}
              >
                🔄 Check Status
              </button>
              <button
                onClick={calculateRBS}
                disabled={calculatingRBS}
                className="px-4 py-2 text-white font-medium rounded hover:opacity-90 disabled:opacity-50 disabled:cursor-not-allowed flex items-center space-x-2 transition-opacity"
                style={{backgroundColor: '#12664F'}}
              >
                {calculatingRBS ? (
                  <>
                    <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white"></div>
                    <span>Calculating...</span>
                  </>
                ) : (
                  <>
                    <span>⚖️</span>
                    <span>Calculate RBS</span>
                  </>
                )}
              </button>
            </div>
          </div>
        </div>

        {/* Database Management */}
        <div className="mt-8 p-4 rounded-lg border-2" style={{backgroundColor: '#F2E9E4', borderColor: '#002629'}}>
          <div className="flex items-center justify-between mb-4">
            <div>
              <h3 className="text-lg font-semibold" style={{color: '#002629'}}>🗄️ Database Management</h3>
              <p className="text-sm mt-1" style={{color: '#002629', opacity: 0.8}}>Development tools for managing database content</p>
            </div>
            <button
              onClick={fetchDatabaseStats}
              className="px-3 py-1 text-sm text-white rounded hover:opacity-90 transition-opacity"
              style={{backgroundColor: '#002629'}}
            >
              🔄 Refresh Stats
            </button>
          </div>

          {/* Database Statistics */}
          {databaseStats && (
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-4">
              <div className="bg-white p-3 rounded border-2" style={{borderColor: '#002629'}}>
                <div className="text-lg font-bold" style={{color: '#002629'}}>{databaseStats.total_documents || 0}</div>
                <div className="text-xs" style={{color: '#002629', opacity: 0.8}}>Total Records</div>
              </div>
              <div className="bg-white p-3 rounded border-2" style={{borderColor: '#002629'}}>
                <div className="text-lg font-bold" style={{color: '#002629'}}>{databaseStats.collections?.matches || 0}</div>
                <div className="text-xs" style={{color: '#002629', opacity: 0.8}}>Matches</div>
              </div>
              <div className="bg-white p-3 rounded border-2" style={{borderColor: '#002629'}}>
                <div className="text-lg font-bold" style={{color: '#002629'}}>{databaseStats.collections?.team_stats || 0}</div>
                <div className="text-xs" style={{color: '#002629', opacity: 0.8}}>Team Stats</div>
              </div>
              <div className="bg-white p-3 rounded border-2" style={{borderColor: '#002629'}}>
                <div className="text-lg font-bold" style={{color: '#002629'}}>{databaseStats.collections?.player_stats || 0}</div>
                <div className="text-xs" style={{color: '#002629', opacity: 0.8}}>Player Stats</div>
              </div>
            </div>
          )}

          {/* Danger Zone */}
          <div className="p-4 rounded border-2" style={{backgroundColor: '#A3D9FF', borderColor: '#002629'}}>
            <div className="flex items-center justify-between">
              <div>
                <h4 className="font-semibold" style={{color: '#002629'}}>⚠️ Danger Zone</h4>
                <p className="text-sm mt-1" style={{color: '#002629', opacity: 0.8}}>
                  Permanently delete all data from the database. This action cannot be undone.
                </p>
              </div>
              <button
                onClick={wipeDatabase}
                disabled={wipingDatabase}
                className="px-4 py-2 text-white font-medium rounded-lg hover:opacity-90 disabled:opacity-50 disabled:cursor-not-allowed flex items-center space-x-2 transition-opacity"
                style={{backgroundColor: '#002629'}}
              >
                {wipingDatabase ? (
                  <>
                    <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white"></div>
                    <span>Wiping...</span>
                  </>
                ) : (
                  <>
                    <span>🗑️</span>
                    <span>Wipe Database</span>
                  </>
                )}
              </button>
            </div>
          </div>
        </div>

        {/* Team Performance Analysis */}
        <div className="mt-8 p-4 rounded-lg border-2" style={{backgroundColor: '#F2E9E4', borderColor: '#1C5D99'}}>
          <div className="flex items-center justify-between mb-4">
            <div>
              <h3 className="text-lg font-semibold" style={{color: '#002629'}}>📊 Team Performance Analysis</h3>
              <p className="text-sm mt-1" style={{color: '#002629', opacity: 0.8}}>Detailed performance metrics for any team</p>
            </div>
          </div>

          <div className="flex items-center space-x-3 mb-4">
            <select
              value={selectedTeamForAnalysis}
              onChange={(e) => setSelectedTeamForAnalysis(e.target.value)}
              className="form-select"
              style={{minWidth: '200px'}}
            >
              <option value="">Select Team for Analysis</option>
              {teams.map(team => (
                <option key={team} value={team}>{team}</option>
              ))}
            </select>
            <button
              onClick={() => fetchTeamPerformanceData(selectedTeamForAnalysis)}
              disabled={!selectedTeamForAnalysis || loadingTeamPerformance}
              className="px-4 py-2 text-white font-medium rounded hover:opacity-90 disabled:opacity-50 disabled:cursor-not-allowed flex items-center space-x-2"
              style={{backgroundColor: '#1C5D99'}}
            >
              {loadingTeamPerformance ? (
                <>
                  <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white"></div>
                  <span>Loading...</span>
                </>
              ) : (
                <>
                  <span>📈</span>
                  <span>Analyze Performance</span>
                </>
              )}
            </button>
          </div>

          {teamPerformanceData && (
            <TeamPerformanceMetrics performanceData={teamPerformanceData} />
          )}
        </div>

        {/* Model Performance Dashboard */}
        <div className="mt-8 p-4 rounded-lg border-2" style={{backgroundColor: '#F2E9E4', borderColor: '#1C5D99'}}>
          <div className="flex items-center justify-between mb-4">
            <div>
              <h3 className="text-lg font-semibold" style={{color: '#002629'}}>📈 Model Performance Dashboard</h3>
              <p className="text-sm mt-1" style={{color: '#002629', opacity: 0.8}}>Track prediction accuracy and model performance over time</p>
            </div>
            <div className="flex items-center space-x-3">
              <select
                value={performanceDays}
                onChange={(e) => setPerformanceDays(parseInt(e.target.value))}
                className="form-select text-sm"
                style={{minWidth: '120px'}}
              >
                <option value={7}>Last 7 days</option>
                <option value={30}>Last 30 days</option>
                <option value={90}>Last 90 days</option>
                <option value={365}>Last year</option>
              </select>
              <button
                onClick={async () => {
                  setLoadingModelPerformance(true);
                  try {
                    const [performance, history, trends] = await Promise.all([
                      fetchModelPerformance(performanceDays),
                      fetchOptimizationHistory(),
                      fetchPredictionAccuracyTrends()
                    ]);
                    setModelPerformanceData(performance);
                    setOptimizationHistory(history);
                    setAccuracyTrends(trends);
                  } catch (error) {
                    console.error('Error fetching model performance:', error);
                  } finally {
                    setLoadingModelPerformance(false);
                  }
                }}
                disabled={loadingModelPerformance}
                className="px-4 py-2 text-white font-medium rounded hover:opacity-90 disabled:opacity-50 disabled:cursor-not-allowed flex items-center space-x-2"
                style={{backgroundColor: '#1C5D99'}}
              >
                {loadingModelPerformance ? (
                  <>
                    <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white"></div>
                    <span>Loading...</span>
                  </>
                ) : (
                  <>
                    <span>📊</span>
                    <span>Load Performance</span>
                  </>
                )}
              </button>
            </div>
          </div>

          {modelPerformanceData && (
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-6">
              <div className="bg-white p-4 rounded border-2" style={{borderColor: '#1C5D99'}}>
                <div className="text-2xl font-bold" style={{color: '#002629'}}>{modelPerformanceData.outcome_accuracy || 0}%</div>
                <div className="text-sm" style={{color: '#002629', opacity: 0.8}}>Outcome Accuracy</div>
                <div className="text-xs mt-1" style={{color: '#1C5D99'}}>
                  {modelPerformanceData.total_predictions || 0} predictions analyzed
                </div>
              </div>
              <div className="bg-white p-4 rounded border-2" style={{borderColor: '#12664F'}}>
                <div className="text-2xl font-bold" style={{color: '#002629'}}>{modelPerformanceData.goals_r2_score ? (modelPerformanceData.goals_r2_score * 100).toFixed(1) : 0}%</div>
                <div className="text-sm" style={{color: '#002629', opacity: 0.8}}>Goals R² Score</div>
                <div className="text-xs mt-1" style={{color: '#12664F'}}>
                  MAE: {modelPerformanceData.home_goals_mae ? modelPerformanceData.home_goals_mae.toFixed(2) : 'N/A'}
                </div>
              </div>
              <div className="bg-white p-4 rounded border-2" style={{borderColor: '#002629'}}>
                <div className="text-2xl font-bold" style={{color: '#002629'}}>{modelPerformanceData.log_loss ? modelPerformanceData.log_loss.toFixed(3) : 'N/A'}</div>
                <div className="text-sm" style={{color: '#002629', opacity: 0.8}}>Log Loss</div>
                <div className="text-xs mt-1" style={{color: '#002629', opacity: 0.6}}>
                  Lower is better
                </div>
              </div>
            </div>
          )}

          {accuracyTrends && (
            <div className="bg-white p-4 rounded border-2" style={{borderColor: '#1C5D99'}}>
              <h4 className="font-semibold mb-3" style={{color: '#002629'}}>📈 Accuracy Trends</h4>
              <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                {Object.entries(accuracyTrends).map(([period, accuracy]) => (
                  <div key={period} className="text-center">
                    <div className="text-lg font-bold" style={{color: '#1C5D99'}}>{accuracy}%</div>
                    <div className="text-xs" style={{color: '#002629', opacity: 0.8}}>{period}</div>
                  </div>
                ))}
              </div>
            </div>
          )}

          {optimizationHistory && (
            <div className="mt-4 bg-white p-4 rounded border-2" style={{borderColor: '#12664F'}}>
              <h4 className="font-semibold mb-3" style={{color: '#002629'}}>🔧 Recent Optimizations</h4>
              <div className="space-y-2">
                {optimizationHistory.slice(0, 5).map((opt, index) => (
                  <div key={index} className="flex justify-between items-center py-2 border-b border-gray-200">
                    <div>
                      <div className="font-medium" style={{color: '#002629'}}>{opt.optimization_type}</div>
                      <div className="text-xs" style={{color: '#002629', opacity: 0.6}}>{opt.timestamp}</div>
                    </div>
                    <div className="text-right">
                      <div className="font-medium" style={{color: opt.improvement > 0 ? '#12664F' : '#002629'}}>
                        {opt.improvement > 0 ? '+' : ''}{opt.improvement}%
                      </div>
                      <div className="text-xs" style={{color: '#002629', opacity: 0.6}}>improvement</div>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}

          {!modelPerformanceData && !loadingModelPerformance && (
            <div className="text-center py-8" style={{color: '#002629', opacity: 0.6}}>
              Click "Load Performance" to view model performance metrics
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default Dashboard;