import React, { useState, useEffect } from 'react';
import axios from 'axios';
import PlayerSearchInput from './PlayerSearchInput';
import './App.css';

const API = (process.env.REACT_APP_BACKEND_URL || 'http://localhost:8001') + '/api';

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

  // Player search states
  const [playerSearchTerms, setPlayerSearchTerms] = useState({});
  const [searchResults, setSearchResults] = useState({});

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

  // Database management states
  const [wipingDatabase, setWipingDatabase] = useState(false);
  const [databaseStats, setDatabaseStats] = useState(null);

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
        checkMLStatus(),
        fetchDatabaseStats()
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
      const response = await axios.get(`${API}/prediction-configs`);
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
      const response = await axios.get(`${API}/ml-models/status`);
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

    // Clear search term after selection
    const searchKey = `${isHomeTeam ? 'home' : 'away'}_${positionId}`;
    setPlayerSearchTerms(prev => ({
      ...prev,
      [searchKey]: selectedPlayer ? selectedPlayer.player_name : ''
    }));
    setSearchResults(prev => ({
      ...prev,
      [searchKey]: []
    }));
  };

  // Player search functionality
  const searchPlayers = (searchTerm, isHomeTeam, positionType, positionId) => {
    const teamPlayers = isHomeTeam ? homeTeamPlayers : awayTeamPlayers;
    const currentXI = isHomeTeam ? homeStartingXI : awayStartingXI;
    const searchKey = `${isHomeTeam ? 'home' : 'away'}_${positionId}`;
    
    if (!searchTerm.trim()) {
      setSearchResults(prev => ({
        ...prev,
        [searchKey]: []
      }));
      return;
    }

    const filtered = teamPlayers
      .filter(player => {
        // Filter by search term
        const nameMatch = player.player_name.toLowerCase().includes(searchTerm.toLowerCase());
        // Prefer players of same position, but allow others
        const positionMatch = player.position === positionType;
        // Exclude already selected players
        const notSelected = !currentXI?.positions.some(pos => pos.player?.player_name === player.player_name);
        
        return nameMatch && notSelected;
      })
      .sort((a, b) => {
        // Sort by position match first, then by matches played
        if (a.position === positionType && b.position !== positionType) return -1;
        if (b.position === positionType && a.position !== positionType) return 1;
        return (b.matches_played || 0) - (a.matches_played || 0);
      })
      .slice(0, 8); // Limit to 8 results

    setSearchResults(prev => ({
      ...prev,
      [searchKey]: filtered
    }));
  };

  const handlePlayerSearch = (searchTerm, isHomeTeam, positionType, positionId) => {
    const searchKey = `${isHomeTeam ? 'home' : 'away'}_${positionId}`;
    setPlayerSearchTerms(prev => ({
      ...prev,
      [searchKey]: searchTerm
    }));
    searchPlayers(searchTerm, isHomeTeam, positionType, positionId);
  };

  const selectPlayerFromSearch = (player, isHomeTeam, positionId) => {
    updateStartingXIPlayer(isHomeTeam, positionId, player);
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
      await axios.post(`${API}/ml-models/reload`);
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

  // Database Management Functions
  const fetchDatabaseStats = async () => {
    try {
      const response = await axios.get(`${API}/database/stats`);
      setDatabaseStats(response.data);
    } catch (error) {
      console.error('Error fetching database stats:', error);
    }
  };

  const wipeDatabase = async () => {
    // Double confirmation for safety
    const firstConfirm = window.confirm(
      '⚠️ WARNING: This will permanently delete ALL data from the database!\n\n' +
      'This includes:\n' +
      '• All match data\n' +
      '• All team statistics\n' +
      '• All player statistics\n' +
      '• All referee bias scores\n' +
      '• All configurations\n\n' +
      'Are you sure you want to continue?'
    );
    
    if (!firstConfirm) return;
    
    const secondConfirm = window.confirm(
      '🚨 FINAL WARNING: This action cannot be undone!\n\n' +
      'Type "DELETE" in the next prompt to confirm database wipe.'
    );
    
    if (!secondConfirm) return;
    
    const finalConfirm = window.prompt(
      'Type "DELETE" (in capital letters) to confirm:'
    );
    
    if (finalConfirm !== 'DELETE') {
      alert('❌ Database wipe cancelled - confirmation text did not match.');
      return;
    }
    
    setWipingDatabase(true);
    try {
      const response = await axios.delete(`${API}/database/wipe`);
      
      if (response.data.success) {
        alert(`✅ ${response.data.message}`);
        // Refresh all data after wipe
        await fetchInitialData();
      }
    } catch (error) {
      alert(`❌ Database Wipe Error: ${error.response?.data?.detail || error.message}`);
    }
    setWipingDatabase(false);
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
      const response = await axios.post(`${API}/upload/${datasetType}`, formData, {
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

              {/* Database Management */}
              <div className="mt-8 p-4 bg-gradient-to-r from-red-50 to-orange-50 rounded-lg border border-red-200">
                <div className="flex items-center justify-between mb-4">
                  <div>
                    <h3 className="text-lg font-semibold text-red-900">🗄️ Database Management</h3>
                    <p className="text-sm text-red-700 mt-1">Development tools for managing database content</p>
                  </div>
                  <button
                    onClick={fetchDatabaseStats}
                    className="px-3 py-1 text-sm bg-red-600 text-white rounded hover:bg-red-700"
                  >
                    🔄 Refresh Stats
                  </button>
                </div>

                {/* Database Statistics */}
                {databaseStats && (
                  <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-4">
                    <div className="bg-white p-3 rounded border border-red-200">
                      <div className="text-lg font-bold text-red-600">{databaseStats.total_documents || 0}</div>
                      <div className="text-xs text-red-700">Total Records</div>
                    </div>
                    <div className="bg-white p-3 rounded border border-red-200">
                      <div className="text-lg font-bold text-red-600">{databaseStats.collections?.matches || 0}</div>
                      <div className="text-xs text-red-700">Matches</div>
                    </div>
                    <div className="bg-white p-3 rounded border border-red-200">
                      <div className="text-lg font-bold text-red-600">{databaseStats.collections?.team_stats || 0}</div>
                      <div className="text-xs text-red-700">Team Stats</div>
                    </div>
                    <div className="bg-white p-3 rounded border border-red-200">
                      <div className="text-lg font-bold text-red-600">{databaseStats.collections?.player_stats || 0}</div>
                      <div className="text-xs text-red-700">Player Stats</div>
                    </div>
                  </div>
                )}

                {/* Danger Zone */}
                <div className="bg-red-100 p-4 rounded border border-red-300">
                  <div className="flex items-center justify-between">
                    <div>
                      <h4 className="font-semibold text-red-900">⚠️ Danger Zone</h4>
                      <p className="text-sm text-red-700 mt-1">
                        Permanently delete all data from the database. This action cannot be undone.
                      </p>
                    </div>
                    <button
                      onClick={wipeDatabase}
                      disabled={wipingDatabase}
                      className="px-4 py-2 bg-red-600 text-white font-medium rounded-lg hover:bg-red-700 disabled:bg-gray-400 disabled:cursor-not-allowed flex items-center space-x-2"
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
        )}        {/* Enhanced XGBoost Tab with Starting XI */}
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
                                            <div className="flex-1">
                                              <PlayerSearchInput
                                                positionId={position.position_id}
                                                positionType={position.position_type}
                                                isHomeTeam={true}
                                                currentPlayer={position.player}
                                                searchTerm={playerSearchTerms[`home_${position.position_id}`] || ''}
                                                searchResults={searchResults[`home_${position.position_id}`] || []}
                                                onSearch={(term) => handlePlayerSearch(term, true, position.position_type, position.position_id)}
                                                onSelect={(player) => selectPlayerFromSearch(player, true, position.position_id)}
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
                                            <div className="flex-1">
                                              <PlayerSearchInput
                                                positionId={position.position_id}
                                                positionType={position.position_type}
                                                isHomeTeam={false}
                                                currentPlayer={position.player}
                                                searchTerm={playerSearchTerms[`away_${position.position_id}`] || ''}
                                                searchResults={searchResults[`away_${position.position_id}`] || []}
                                                onSearch={(term) => handlePlayerSearch(term, false, position.position_type, position.position_id)}
                                                onSelect={(player) => selectPlayerFromSearch(player, false, position.position_id)}
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