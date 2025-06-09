import React, { useState, useEffect } from 'react';
import axios from 'axios';
import './App.css';

const API = process.env.REACT_APP_BACKEND_URL || 'http://localhost:8001/api';

function App() {
  // Navigation state
  const [activeTab, setActiveTab] = useState('dashboard');

  // Data states
  const [teams, setTeams] = useState([]);
  const [referees, setReferees] = useState([]);
  const [configs, setConfigs] = useState([]);
  const [rbsConfigs, setRbsConfigs] = useState([]);
  const [datasets, setDatasets] = useState([]);
  const [stats, setStats] = useState({});

  // Upload states
  const [uploadStatus, setUploadStatus] = useState({});
  const [uploadingDataset, setUploadingDataset] = useState(false);

  // Prediction states
  const [predictionForm, setPredictionForm] = useState({
    home_team: '',
    away_team: '',
    referee_name: '',
    match_date: ''
  });
  const [predictionResult, setPredictionResult] = useState(null);
  const [predicting, setPredicting] = useState(false);
  const [configName, setConfigName] = useState('default');

  // Enhanced XGBoost states
  const [showStartingXI, setShowStartingXI] = useState(false);
  const [selectedFormation, setSelectedFormation] = useState('4-4-2');
  const [availableFormations, setAvailableFormations] = useState(['4-4-2', '4-3-3', '3-5-2', '4-5-1', '3-4-3']);
  const [homeTeamPlayers, setHomeTeamPlayers] = useState([]);
  const [awayTeamPlayers, setAwayTeamPlayers] = useState([]);
  const [homeStartingXI, setHomeStartingXI] = useState(null);
  const [awayStartingXI, setAwayStartingXI] = useState(null);
  const [loadingPlayers, setLoadingPlayers] = useState(false);

  // Time decay states
  const [useTimeDecay, setUseTimeDecay] = useState(true);
  const [decayPreset, setDecayPreset] = useState('moderate');
  const [decayPresets, setDecayPresets] = useState([]);

  // ML states
  const [mlStatus, setMlStatus] = useState(null);
  const [trainingModels, setTrainingModels] = useState(false);
  const [trainingResults, setTrainingResults] = useState(null);

  // Export states
  const [exportingPDF, setExportingPDF] = useState(false);

  // Initialize data on component mount
  useEffect(() => {
    fetchInitialData();
  }, []);

  const fetchInitialData = async () => {
    try {
      await Promise.all([
        fetchTeams(),
        fetchReferees(),
        fetchConfigs(),
        fetchDatasets(),
        fetchStats(),
        fetchFormations(),
        fetchDecayPresets(),
        checkMLStatus()
      ]);
    } catch (error) {
      console.error('Error fetching initial data:', error);
    }
  };

  // API Functions
  const fetchTeams = async () => {
    try {
      const response = await axios.get(`${API}/teams`);
      setTeams(response.data.teams || []);
    } catch (error) {
      console.error('Error fetching teams:', error);
    }
  };

  const fetchReferees = async () => {
    try {
      const response = await axios.get(`${API}/referees`);
      setReferees(response.data.referees || []);
    } catch (error) {
      console.error('Error fetching referees:', error);
    }
  };

  const fetchConfigs = async () => {
    try {
      const response = await axios.get(`${API}/configs`);
      setConfigs(response.data.configs || []);
    } catch (error) {
      console.error('Error fetching configs:', error);
    }
  };

  const fetchDatasets = async () => {
    try {
      const response = await axios.get(`${API}/datasets`);
      setDatasets(response.data.datasets || []);
    } catch (error) {
      console.error('Error fetching datasets:', error);
    }
  };

  const fetchStats = async () => {
    try {
      const response = await axios.get(`${API}/stats`);
      setStats(response.data || {});
    } catch (error) {
      console.error('Error fetching stats:', error);
    }
  };

  const fetchFormations = async () => {
    try {
      const response = await axios.get(`${API}/formations`);
      if (response.data.success) {
        setAvailableFormations(response.data.formations.map(f => f.name));
      }
    } catch (error) {
      console.error('Error fetching formations:', error);
    }
  };

  const fetchDecayPresets = async () => {
    try {
      const response = await axios.get(`${API}/time-decay/presets`);
      if (response.data.success) {
        setDecayPresets(response.data.presets);
      }
    } catch (error) {
      console.error('Error fetching decay presets:', error);
    }
  };

  const checkMLStatus = async () => {
    try {
      const response = await axios.get(`${API}/ml-status`);
      setMlStatus(response.data);
    } catch (error) {
      console.error('Error checking ML status:', error);
    }
  };

  // Starting XI Functions
  const fetchTeamPlayers = async (teamName, isHomeTeam = true) => {
    try {
      setLoadingPlayers(true);
      const response = await axios.get(`${API}/teams/${encodeURIComponent(teamName)}/players?formation=${selectedFormation}`);
      
      if (response.data.success) {
        const players = response.data.players || [];
        const defaultXI = response.data.default_starting_xi;
        
        if (isHomeTeam) {
          setHomeTeamPlayers(players);
          setHomeStartingXI(defaultXI);
        } else {
          setAwayTeamPlayers(players);
          setAwayStartingXI(defaultXI);
        }
      }
    } catch (error) {
      console.error('Error fetching team players:', error);
      alert(`Error loading players for ${teamName}: ${error.response?.data?.detail || error.message}`);
    } finally {
      setLoadingPlayers(false);
    }
  };

  const handleFormationChange = async (newFormation) => {
    setSelectedFormation(newFormation);
    
    // Regenerate starting XIs for both teams with new formation
    if (predictionForm.home_team) {
      await fetchTeamPlayers(predictionForm.home_team, true);
    }
    if (predictionForm.away_team) {
      await fetchTeamPlayers(predictionForm.away_team, false);
    }
  };

  const updateStartingXIPlayer = (isHomeTeam, positionId, selectedPlayer) => {
    const setStartingXI = isHomeTeam ? setHomeStartingXI : setAwayStartingXI;
    const currentXI = isHomeTeam ? homeStartingXI : awayStartingXI;
    
    if (!currentXI) return;
    
    const updatedPositions = currentXI.positions.map(pos => {
      if (pos.position_id === positionId) {
        return { ...pos, player: selectedPlayer };
      }
      return pos;
    });
    
    setStartingXI({
      ...currentXI,
      positions: updatedPositions
    });
  };

  const validateStartingXI = (startingXI) => {
    if (!startingXI || !startingXI.positions) return false;
    return startingXI.positions.filter(pos => pos.player).length === 11;
  };

  // Prediction Functions
  const handlePredictionFormChange = (field, value) => {
    setPredictionForm(prev => ({
      ...prev,
      [field]: value
    }));
  };

  const predictMatch = async () => {
    if (!predictionForm.home_team || !predictionForm.away_team || !predictionForm.referee_name) {
      alert('Please fill in all required fields');
      return;
    }

    setPredicting(true);
    try {
      const requestData = {
        ...predictionForm,
        config_name: configName
      };
      const response = await axios.post(`${API}/predict-match`, requestData);
      setPredictionResult(response.data);
    } catch (error) {
      alert(`❌ Prediction Error: ${error.response?.data?.detail || error.message}`);
    }
    setPredicting(false);
  };

  const predictMatchEnhanced = async () => {
    if (!predictionForm.home_team || !predictionForm.away_team || !predictionForm.referee_name) {
      alert('Please fill in all required fields');
      return;
    }

    setPredicting(true);
    try {
      const requestData = {
        home_team: predictionForm.home_team,
        away_team: predictionForm.away_team,
        referee_name: predictionForm.referee_name,
        match_date: predictionForm.match_date,
        config_name: configName,
        home_starting_xi: homeStartingXI,
        away_starting_xi: awayStartingXI,
        use_time_decay: useTimeDecay,
        decay_preset: decayPreset
      };
      
      const response = await axios.post(`${API}/predict-match-enhanced`, requestData);
      setPredictionResult(response.data);
    } catch (error) {
      alert(`❌ Enhanced Prediction Error: ${error.response?.data?.detail || error.message}`);
    }
    setPredicting(false);
  };

  const resetPrediction = () => {
    setPredictionForm({
      home_team: '',
      away_team: '',
      referee_name: '',
      match_date: ''
    });
    setPredictionResult(null);
    setHomeStartingXI(null);
    setAwayStartingXI(null);
  };

  // ML Functions
  const trainMLModels = async () => {
    setTrainingModels(true);
    try {
      const response = await axios.post(`${API}/train-ml-models`);
      setTrainingResults(response.data);
      await checkMLStatus(); // Refresh status after training
    } catch (error) {
      alert(`❌ Training Error: ${error.response?.data?.detail || error.message}`);
    }
    setTrainingModels(false);
  };

  const reloadMLModels = async () => {
    try {
      await axios.post(`${API}/reload-ml-models`);
      await checkMLStatus();
      alert('✅ Models reloaded successfully!');
    } catch (error) {
      alert(`❌ Reload Error: ${error.response?.data?.detail || error.message}`);
    }
  };

  // Export Functions
  const exportPDF = async () => {
    if (!predictionResult) return;
    
    setExportingPDF(true);
    try {
      const response = await axios.post(`${API}/export-pdf`, {
        prediction_data: predictionResult
      }, {
        responseType: 'blob'
      });
      
      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', `match_prediction_${predictionResult.home_team}_vs_${predictionResult.away_team}.pdf`);
      document.body.appendChild(link);
      link.click();
      link.remove();
    } catch (error) {
      alert(`❌ Export Error: ${error.response?.data?.detail || error.message}`);
    }
    setExportingPDF(false);
  };

  // File Upload Function
  const handleFileUpload = async (event, datasetType) => {
    const file = event.target.files[0];
    if (!file) return;

    setUploadingDataset(true);
    setUploadStatus(prev => ({
      ...prev,
      [datasetType]: '⏳ Uploading...'
    }));

    const formData = new FormData();
    formData.append('file', file);

    try {
      const response = await axios.post(`${API}/upload-${datasetType}`, formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      });

      setUploadStatus(prev => ({
        ...prev,
        [datasetType]: `✅ ${response.data.message}`
      }));

      // Refresh data after upload
      await fetchInitialData();
    } catch (error) {
      setUploadStatus(prev => ({
        ...prev,
        [datasetType]: `❌ Upload failed: ${error.response?.data?.detail || error.message}`
      }));
    }
    setUploadingDataset(false);
  };

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <div className="bg-white shadow-sm border-b">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center py-4">
            <div className="flex items-center space-x-4">
              <h1 className="text-2xl font-bold text-gray-900">⚽ Football Analytics Suite</h1>
              <span className="text-sm text-gray-500">Enhanced with Starting XI & Time Decay</span>
            </div>
          </div>
        </div>
      </div>

      {/* Navigation */}
      <div className="bg-white shadow-sm">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <nav className="flex space-x-8 overflow-x-auto">
            {[
              { id: 'dashboard', name: '📊 Dashboard', icon: '📊' },
              { id: 'upload', name: '📁 Upload Data', icon: '📁' },
              { id: 'predict', name: '🎯 Standard Predict', icon: '🎯' },
              { id: 'xgboost', name: '🚀 Enhanced XGBoost', icon: '🚀' },
              { id: 'analysis', name: '📈 Analysis', icon: '📈' },
              { id: 'config', name: '⚙️ Config', icon: '⚙️' }
            ].map(tab => (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id)}
                className={`py-4 px-6 text-sm font-medium border-b-2 whitespace-nowrap ${
                  activeTab === tab.id
                    ? 'border-blue-500 text-blue-600'
                    : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                }`}
              >
                <span className="mr-2">{tab.icon}</span>
                {tab.name}
              </button>
            ))}
          </nav>
        </div>
      </div>

      {/* Main Content */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        
        {/* Dashboard Tab */}
        {activeTab === 'dashboard' && (
          <div className="space-y-6">
            <div className="bg-white p-6 rounded-lg shadow-sm border">
              <h2 className="text-xl font-bold text-gray-900 mb-4">📊 Football Analytics Dashboard</h2>
              <p className="text-gray-600 mb-6">
                Advanced football match prediction system with Enhanced XGBoost models, Starting XI analysis, and Time Decay algorithms.
              </p>

              {/* Statistics Grid */}
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
                <div className="bg-blue-50 p-4 rounded-lg border border-blue-200">
                  <div className="text-2xl font-bold text-blue-600">{teams.length}</div>
                  <div className="text-blue-700">Teams</div>
                </div>
                <div className="bg-green-50 p-4 rounded-lg border border-green-200">
                  <div className="text-2xl font-bold text-green-600">{referees.length}</div>
                  <div className="text-green-700">Referees</div>
                </div>
                <div className="bg-purple-50 p-4 rounded-lg border border-purple-200">
                  <div className="text-2xl font-bold text-purple-600">{stats.matches || 0}</div>
                  <div className="text-purple-700">Matches</div>
                </div>
                <div className="bg-orange-50 p-4 rounded-lg border border-orange-200">
                  <div className="text-2xl font-bold text-orange-600">{stats.player_stats || 0}</div>
                  <div className="text-orange-700">Player Records</div>
                </div>
              </div>

              {/* Enhanced Features */}
              <div className="mt-8">
                <h3 className="text-lg font-semibold text-gray-900 mb-4">🚀 Enhanced Features</h3>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                  <div className="bg-gradient-to-r from-blue-50 to-indigo-50 p-4 rounded-lg border border-blue-200">
                    <h4 className="font-semibold text-blue-900">⚽ Starting XI Analysis</h4>
                    <p className="text-blue-700 text-sm mt-1">Select specific players for each team to get predictions based on actual lineups</p>
                    <div className="mt-2 text-xs text-blue-600">
                      • Formation-based selection (4-4-2, 4-3-3, etc.)
                      • Player stats aggregation
                      • Position-aware analysis
                    </div>
                  </div>
                  <div className="bg-gradient-to-r from-green-50 to-emerald-50 p-4 rounded-lg border border-green-200">
                    <h4 className="font-semibold text-green-900">⏰ Time Decay Weighting</h4>
                    <p className="text-green-700 text-sm mt-1">Recent matches have higher impact than historical data</p>
                    <div className="mt-2 text-xs text-green-600">
                      • Configurable decay presets
                      • Exponential/Linear decay options
                      • Season-aware weighting
                    </div>
                  </div>
                </div>
              </div>

              {/* ML Model Status */}
              <div className="mt-8 p-4 bg-gray-50 rounded-lg">
                <div className="flex items-center justify-between">
                  <div>
                    <h3 className="text-lg font-semibold text-gray-900">🧠 XGBoost Models Status</h3>
                    <div className="flex items-center space-x-2 mt-2">
                      <span className={`inline-block w-3 h-3 rounded-full ${mlStatus?.models_loaded ? 'bg-green-500' : 'bg-red-500'}`}></span>
                      <span className="text-sm font-medium">
                        {mlStatus?.models_loaded ? '✅ Models Ready' : '❌ Models Need Training'}
                      </span>
                      <span className="text-xs text-gray-500">
                        ({mlStatus?.feature_columns_count || 0} features)
                      </span>
                    </div>
                  </div>
                  <button
                    onClick={checkMLStatus}
                    className="px-3 py-1 text-sm bg-gray-600 text-white rounded hover:bg-gray-700"
                  >
                    🔄 Refresh
                  </button>
                </div>
              </div>
            </div>
          </div>
        )}

        {/* Upload Data Tab */}
        {activeTab === 'upload' && (
          <div className="space-y-6">
            <div className="bg-white p-6 rounded-lg shadow-sm border">
              <h2 className="text-xl font-bold text-gray-900 mb-4">📁 Upload Football Data</h2>
              <p className="text-gray-600 mb-6">
                Upload your football datasets to enable predictions and analysis.
              </p>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                {[
                  { id: 'matches', name: 'Match Data', desc: 'Upload match results and statistics' },
                  { id: 'team-stats', name: 'Team Stats', desc: 'Upload team-level statistics' },
                  { id: 'player-stats', name: 'Player Stats', desc: 'Upload individual player statistics' }
                ].map(dataset => (
                  <div key={dataset.id} className="border border-gray-200 rounded-lg p-4">
                    <h3 className="font-semibold text-gray-900 mb-2">{dataset.name}</h3>
                    <p className="text-sm text-gray-600 mb-4">{dataset.desc}</p>
                    
                    <input
                      type="file"
                      accept=".csv"
                      onChange={(e) => handleFileUpload(e, dataset.id)}
                      disabled={uploadingDataset}
                      className="w-full text-sm text-gray-500 file:mr-4 file:py-2 file:px-4 file:rounded-lg file:border-0 file:text-sm file:font-medium file:bg-blue-50 file:text-blue-700 hover:file:bg-blue-100"
                    />
                    
                    {uploadStatus[dataset.id] && (
                      <div className="mt-2 text-sm">
                        {uploadStatus[dataset.id]}
                      </div>
                    )}
                  </div>
                ))}
              </div>

              {/* Uploaded Datasets */}
              {datasets.length > 0 && (
                <div className="mt-8">
                  <h3 className="text-lg font-semibold text-gray-900 mb-4">📊 Uploaded Datasets</h3>
                  <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                    {datasets.map(dataset => (
                      <div key={dataset.name} className="bg-green-50 p-4 rounded-lg border border-green-200">
                        <div className="font-medium text-green-900">{dataset.name}</div>
                        <div className="text-sm text-green-700">{dataset.records} records</div>
                        <div className="text-xs text-green-600">Uploaded: {new Date(dataset.uploaded_at).toLocaleDateString()}</div>
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </div>
          </div>
        )}

        {/* Standard Prediction Tab */}
        {activeTab === 'predict' && (
          <div className="space-y-6">
            <div className="bg-white p-6 rounded-lg shadow-sm border">
              <h2 className="text-xl font-bold text-gray-900 mb-4">🎯 Standard Match Prediction</h2>
              <p className="text-gray-600 mb-6">
                Standard prediction using team-level statistics and historical data.
              </p>

              {!predictionResult ? (
                <div className="space-y-6">
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-2">Home Team *</label>
                      <select
                        value={predictionForm.home_team}
                        onChange={(e) => handlePredictionFormChange('home_team', e.target.value)}
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
                        onChange={(e) => handlePredictionFormChange('away_team', e.target.value)}
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

                  <button
                    onClick={predictMatch}
                    disabled={predicting || !predictionForm.home_team || !predictionForm.away_team || !predictionForm.referee_name}
                    className="px-6 py-3 bg-blue-600 text-white font-medium rounded-lg hover:bg-blue-700 disabled:bg-gray-400 disabled:cursor-not-allowed flex items-center space-x-2"
                  >
                    {predicting ? (
                      <>
                        <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white"></div>
                        <span>Predicting...</span>
                      </>
                    ) : (
                      <>
                        <span>🎯</span>
                        <span>Predict Match</span>
                      </>
                    )}
                  </button>
                </div>
              ) : (
                <div className="space-y-6">
                  <div className="bg-gradient-to-r from-blue-50 to-indigo-50 p-6 rounded-lg border border-blue-200">
                    <div className="text-center">
                      <h3 className="text-2xl font-bold text-gray-900 mb-2">
                        {predictionResult.home_team} vs {predictionResult.away_team}
                      </h3>
                      <div className="text-lg text-gray-600 mb-2">
                        Predicted Score: <span className="font-bold text-blue-600">{predictionResult.predicted_home_goals}</span>
                        {' - '}
                        <span className="font-bold text-red-600">{predictionResult.predicted_away_goals}</span>
                      </div>
                    </div>
                  </div>

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
                          <span>Export PDF</span>
                        </>
                      )}
                    </button>
                  </div>
                </div>
              )}
            </div>
          </div>
        )}