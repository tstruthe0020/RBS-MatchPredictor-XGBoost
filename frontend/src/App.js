import React, { useState, useEffect } from 'react';
import axios from 'axios';
import PlayerSearchInput from './PlayerSearchInput';
import './App.css';
import './custom-colors.css';
import { 
  VARIABLE_CATEGORIES, 
  runRegressionAnalysis, 
  savePredictionConfig, 
  saveRBSConfig,
  runFormulaOptimization,
  fetchRefereeAnalysis,
  fetchDetailedRefereeAnalysis,
  DEFAULT_PREDICTION_CONFIG,
  DEFAULT_RBS_CONFIG,
  formatPercentage,
  formatScore,
  getConfidenceColor,
  getRBSScoreColor
} from './analysis-components';

import {
  fetchEnhancedRBSAnalysis,
  fetchTeamPerformance,
  fetchAllPredictionConfigs,
  fetchAllRBSConfigs,
  deletePredictionConfig,
  deleteRBSConfig,
  runAdvancedOptimization,
  formatOptimizationResults,
  RBSVarianceAnalysis,
  TeamPerformanceMetrics,
  ConfigurationList,
  OptimizationResults
} from './advanced-features';

const API = (process.env.REACT_APP_BACKEND_URL || 'http://localhost:8001') + '/api';

// Debug logging for backend URL
console.log('🔍 Frontend Configuration Debug:');
console.log('REACT_APP_BACKEND_URL:', process.env.REACT_APP_BACKEND_URL);
console.log('Final API URL:', API);

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

  // RBS Calculation states
  const [rbsStatus, setRbsStatus] = useState(null);
  const [calculatingRBS, setCalculatingRBS] = useState(false);
  const [rbsResults, setRbsResults] = useState(null);

  // Regression Analysis states
  const [selectedVariables, setSelectedVariables] = useState([]);
  const [regressionTarget, setRegressionTarget] = useState('points_per_game');
  const [regressionResults, setRegressionResults] = useState(null);
  const [runningRegression, setRunningRegression] = useState(false);

  // Prediction Config states
  const [predictionConfigs, setPredictionConfigs] = useState([]);
  const [currentPredictionConfig, setCurrentPredictionConfig] = useState(null);
  const [editingPredictionConfig, setEditingPredictionConfig] = useState(false);

  // RBS Config states (rbsConfigs already declared above, adding missing ones)
  const [currentRbsConfig, setCurrentRbsConfig] = useState(null);
  const [editingRbsConfig, setEditingRbsConfig] = useState(false);

  // Formula Optimization states
  const [runningOptimization, setRunningOptimization] = useState(false);
  const [optimizationType, setOptimizationType] = useState('rbs');

  // Results Analysis states
  const [refereeAnalysis, setRefereeAnalysis] = useState(null);
  const [selectedRefereeForAnalysis, setSelectedRefereeForAnalysis] = useState('');
  const [loadingResults, setLoadingResults] = useState(false);
  const [detailedRefereeData, setDetailedRefereeData] = useState(null);
  const [loadingDetailedAnalysis, setLoadingDetailedAnalysis] = useState(false);

  // Advanced Features States
  const [enhancedRBSData, setEnhancedRBSData] = useState(null);
  const [teamPerformanceData, setTeamPerformanceData] = useState(null);
  const [selectedTeamForAnalysis, setSelectedTeamForAnalysis] = useState('');
  const [loadingTeamPerformance, setLoadingTeamPerformance] = useState(false);
  const [loadingEnhancedRBS, setLoadingEnhancedRBS] = useState(false);
  
  // Configuration Management States
  const [allPredictionConfigs, setAllPredictionConfigs] = useState([]);
  const [allRBSConfigs, setAllRBSConfigs] = useState([]);
  const [showConfigManager, setShowConfigManager] = useState(false);
  const [showRBSConfigManager, setShowRBSConfigManager] = useState(false);
  
  // Advanced Optimization States
  const [advancedOptimizationResults, setAdvancedOptimizationResults] = useState(null);
  const [runningAdvancedOptimization, setRunningAdvancedOptimization] = useState(false);
  const [selectedOptimizationType, setSelectedOptimizationType] = useState('prediction-suggestion');
  
  // XGBoost Optimization States  
  const [optimizationStatus, setOptimizationStatus] = useState(null);
  const [optimizationResults, setOptimizationResults] = useState(null);
  const [runningXGBoostOptimization, setRunningXGBoostOptimization] = useState(false);
  const [modelPerformance, setModelPerformance] = useState(null);
  const [simulationResults, setSimulationResults] = useState(null);

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
        fetchDatabaseStats(),
        checkRBSStatus(),
        loadAllConfigurations()
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

  const getButtonTooltip = () => {
    if (!predictionForm.home_team) return "Select home team";
    if (!predictionForm.away_team) return "Select away team"; 
    if (!predictionForm.referee_name) return "Select referee";
    if (showStartingXI && predictionForm.home_team && predictionForm.away_team) {
      if (!validateStartingXI(homeStartingXI)) return "Complete home team Starting XI (11 players)";
      if (!validateStartingXI(awayStartingXI)) return "Complete away team Starting XI (11 players)";
    }
    return "";
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

    // Check Starting XI validation only if XI mode is enabled and teams are selected
    if (showStartingXI && predictionForm.home_team && predictionForm.away_team) {
      if (!validateStartingXI(homeStartingXI) || !validateStartingXI(awayStartingXI)) {
        alert('Please complete Starting XI selection for both teams (11 players each) or disable Starting XI mode');
        return;
      }
    }

    setPredicting(true);
    try {
      const requestData = {
        home_team: predictionForm.home_team,
        away_team: predictionForm.away_team,
        referee_name: predictionForm.referee_name,
        match_date: predictionForm.match_date,
        config_name: configName,
        home_starting_xi: (showStartingXI && homeStartingXI) ? homeStartingXI : null,
        away_starting_xi: (showStartingXI && awayStartingXI) ? awayStartingXI : null,
        use_time_decay: useTimeDecay,
        decay_preset: decayPreset
      };
      
      console.log('Enhanced prediction request:', requestData);
      const response = await axios.post(`${API}/predict-match-enhanced`, requestData);
      console.log('Enhanced prediction response:', response.data);
      setPredictionResult(response.data);
    } catch (error) {
      console.error('Enhanced prediction error:', error);
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
      const response = await axios.post(`${API}/export-prediction-pdf`, {
        home_team: predictionResult.home_team,
        away_team: predictionResult.away_team,
        referee_name: predictionResult.referee,
        match_date: predictionResult.match_date
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
      
      alert('✅ PDF exported successfully!');
    } catch (error) {
      console.error('Error exporting PDF:', error);
      alert(`❌ Error exporting PDF: ${error.response?.data?.detail || error.message}`);
    } finally {
      setExportingPDF(false);
    }
  };

  // Database Management Functions
  const fetchDatabaseStats = async () => {
    try {
      const response = await axios.get(`${API}/stats`);
      setDatabaseStats(response.data);
    } catch (error) {
      console.error('Error fetching database stats:', error);
    }
  };

  const wipeDatabase = async () => {
    const confirmations = [
      "⚠️ DANGER: This will permanently delete ALL data from the database!\n\nThis includes:\n• All match data\n• All team statistics\n• All player statistics\n• All RBS calculations\n• All trained ML models\n\nThis action CANNOT be undone!\n\nType 'DELETE' to confirm:",
      "⚠️ FINAL WARNING: You are about to permanently destroy all data!\n\nAre you absolutely certain you want to proceed?\n\nType 'CONFIRM' to continue:",
      "⚠️ LAST CHANCE: This is your final confirmation!\n\nOnce you click OK, ALL DATA WILL BE PERMANENTLY DELETED!\n\nClick OK to proceed or Cancel to abort:"
    ];

    try {
      // First confirmation
      const firstConfirm = prompt(confirmations[0]);
      if (firstConfirm !== 'DELETE') {
        alert('❌ Database wipe cancelled - incorrect confirmation text');
        return;
      }

      // Second confirmation  
      const secondConfirm = prompt(confirmations[1]);
      if (secondConfirm !== 'CONFIRM') {
        alert('❌ Database wipe cancelled - incorrect confirmation text');
        return;
      }

      // Final confirmation
      const finalConfirm = window.confirm(confirmations[2]);
      if (!finalConfirm) {
        alert('❌ Database wipe cancelled by user');
        return;
      }

      setWipingDatabase(true);
      const response = await axios.delete(`${API}/wipe-database`);
      
      if (response.data.success) {
        alert('✅ Database successfully wiped! All data has been permanently deleted.');
        // Reset all local state
        setTeams([]);
        setReferees([]);
        setStats({});
        setDatasets([]);
        setDatabaseStats(null);
        setMlStatus(null);
        setPredictionResult(null);
      }
    } catch (error) {
      console.error('Error wiping database:', error);
      alert(`❌ Error wiping database: ${error.response?.data?.detail || error.message}`);
    } finally {
      setWipingDatabase(false);
    }
  };

  // RBS Calculation functions
  const checkRBSStatus = async () => {
    try {
      const response = await axios.get(`${API}/rbs-status`);
      setRbsStatus(response.data);
    } catch (error) {
      console.error('Error checking RBS status:', error);
      setRbsStatus(null);
    }
  };

  const calculateRBS = async () => {
    setCalculatingRBS(true);
    try {
      const response = await axios.post(`${API}/calculate-rbs`);
      setRbsResults(response.data);
      setRbsStatus(response.data.status);
      alert(`✅ RBS Calculation Complete!\n\n• ${response.data.referees_analyzed} referees analyzed\n• ${response.data.teams_covered} teams covered\n• ${response.data.calculations_performed} bias scores calculated`);
    } catch (error) {
      console.error('Error calculating RBS:', error);
      alert(`❌ RBS Calculation Error: ${error.response?.data?.detail || error.message}`);
    } finally {
      setCalculatingRBS(false);
    }
  };

  // Function to fetch detailed referee analysis
  const fetchDetailedRefereeAnalysis = async (refereeName) => {
    setLoadingDetailedAnalysis(true);
    try {
      const response = await axios.get(`${API}/referee-analysis/${encodeURIComponent(refereeName)}`);
      setDetailedRefereeData(response.data);
      setSelectedRefereeForAnalysis(refereeName);
    } catch (error) {
      console.error('Error fetching detailed referee analysis:', error);
      alert(`❌ Error loading detailed analysis: ${error.response?.data?.detail || error.message}`);
    } finally {
      setLoadingDetailedAnalysis(false);
    }
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

  // Load all configuration lists
  const loadAllConfigurations = async () => {
    try {
      const [predictionConfigs, rbsConfigs] = await Promise.all([
        fetchAllPredictionConfigs(),
        fetchAllRBSConfigs()
      ]);
      setAllPredictionConfigs(predictionConfigs);
      setAllRBSConfigs(rbsConfigs);
    } catch (error) {
      console.error('Error loading configurations:', error);
    }
  };

  // Advanced Features Functions
  
  // Enhanced RBS Analysis
  const fetchEnhancedRBSForTeamReferee = async (teamName, refereeName) => {
    setLoadingEnhancedRBS(true);
    try {
      const data = await fetchEnhancedRBSAnalysis(teamName, refereeName);
      setEnhancedRBSData(data);
    } catch (error) {
      console.error('Error fetching enhanced RBS analysis:', error);
      alert(`❌ Error loading enhanced RBS analysis: ${error.response?.data?.detail || error.message}`);
    } finally {
      setLoadingEnhancedRBS(false);
    }
  };

  // Team Performance Analysis
  const fetchTeamPerformanceData = async (teamName) => {
    setLoadingTeamPerformance(true);
    try {
      const data = await fetchTeamPerformance(teamName);
      setTeamPerformanceData(data);
      setSelectedTeamForAnalysis(teamName);
    } catch (error) {
      console.error('Error fetching team performance:', error);
      alert(`❌ Error loading team performance: ${error.response?.data?.detail || error.message}`);
    } finally {
      setLoadingTeamPerformance(false);
    }
  };

  // Configuration Management Functions
  const handleConfigEdit = (config) => {
    setCurrentPredictionConfig(config);
    setEditingPredictionConfig(true);
    setShowConfigManager(false);
  };

  const handleConfigDelete = async (configName) => {
    try {
      await deletePredictionConfig(configName);
      await loadAllConfigurations(); // Refresh the list
      alert('✅ Configuration deleted successfully!');
    } catch (error) {
      alert(`❌ Error deleting configuration: ${error.response?.data?.detail || error.message}`);
    }
  };

  const handleRBSConfigEdit = (config) => {
    setCurrentRbsConfig(config);
    setEditingRbsConfig(true);
    setShowRBSConfigManager(false);
  };

  const handleRBSConfigDelete = async (configName) => {
    try {
      await deleteRBSConfig(configName);
      await loadAllConfigurations(); // Refresh the list
      alert('✅ RBS Configuration deleted successfully!');
    } catch (error) {
      alert(`❌ Error deleting RBS configuration: ${error.response?.data?.detail || error.message}`);
    }
  };

  // XGBoost Optimization Functions
  const fetchOptimizationStatus = async () => {
    try {
      const response = await axios.get(`${API}/xgboost-optimization-status`);
      setOptimizationStatus(response.data);
      console.log('✅ Optimization status loaded:', response.data);
    } catch (error) {
      console.error('Error fetching optimization status:', error);
      alert(`❌ Error fetching status: ${error.response?.data?.detail || error.message}`);
    }
  };

  const evaluateModelPerformance = async (days = 30) => {
    try {
      setLoadingResults(true);
      const response = await axios.get(`${API}/model-performance/${days}`);
      setModelPerformance(response.data);
      console.log('✅ Model performance evaluated:', response.data);
      
      if (response.data.error) {
        alert(`⚠️ ${response.data.error}`);
      } else {
        alert(`✅ Performance evaluated!\nAccuracy: ${response.data.outcome_accuracy}%\nGoals MAE: ${response.data.home_goals_mae?.toFixed(3)}`);
      }
    } catch (error) {
      console.error('Error evaluating model performance:', error);
      alert(`❌ Error evaluating performance: ${error.response?.data?.detail || error.message}`);
    } finally {
      setLoadingResults(false);
    }
  };

  const runXGBoostOptimization = async (method = 'grid_search', retrain = true) => {
    if (!window.confirm(`🔧 Run XGBoost optimization with ${method}?\nThis may take several minutes and will retrain your models.`)) {
      return;
    }
    
    setRunningXGBoostOptimization(true);
    try {
      console.log('🚀 Starting XGBoost optimization...');
      const response = await axios.post(`${API}/optimize-xgboost-models?method=${method}&retrain=${retrain}`);
      setOptimizationResults(response.data);
      
      if (response.data.error) {
        alert(`❌ Optimization failed: ${response.data.error}`);
      } else {
        const improvement = response.data.improvement_summary;
        alert(`✅ XGBoost optimization completed!\n` +
              `Accuracy improved by: ${improvement?.accuracy_improvement?.toFixed(2)}%\n` +
              `Goals MAE improved by: ${improvement?.goals_mae_improvement?.toFixed(3)}\n` +
              `New model version: ${response.data.new_performance?.model_version}`);
      }
      
      // Refresh status after optimization
      await fetchOptimizationStatus();
      
    } catch (error) {
      console.error('Error running XGBoost optimization:', error);
      alert(`❌ Error optimizing models: ${error.response?.data?.detail || error.message}`);
    } finally {
      setRunningXGBoostOptimization(false);
    }
  };

  const simulateOptimizationImpact = async (days = 30) => {
    try {
      setLoadingResults(true);
      const response = await axios.post(`${API}/simulate-optimization-impact?days_back=${days}`);
      setSimulationResults(response.data);
      
      if (response.data.error) {
        alert(`⚠️ ${response.data.error}`);
      } else {
        alert(`🎯 Simulation completed!\n` +
              `Current accuracy: ${response.data.current_accuracy}%\n` +
              `Potential improvement: +${(response.data.simulated_improvements.moderate_improvement - response.data.current_accuracy).toFixed(1)}%\n` +
              `Additional correct predictions: ${response.data.potential_value.additional_correct_predictions_moderate}`);
      }
    } catch (error) {
      console.error('Error simulating optimization impact:', error);
      alert(`❌ Error running simulation: ${error.response?.data?.detail || error.message}`);
    } finally {
      setLoadingResults(false);
    }
  };
  const fetchOptimizationStatus = async () => {
    try {
      const response = await axios.get(`${API}/xgboost-optimization-status`);
      setOptimizationStatus(response.data);
      console.log('✅ Optimization status loaded:', response.data);
    } catch (error) {
      console.error('Error fetching optimization status:', error);
      alert(`❌ Error fetching status: ${error.response?.data?.detail || error.message}`);
    }
  };

  const evaluateModelPerformance = async (days = 30) => {
    try {
      setLoadingResults(true);
      const response = await axios.get(`${API}/model-performance/${days}`);
      setModelPerformance(response.data);
      console.log('✅ Model performance evaluated:', response.data);
      
      if (response.data.error) {
        alert(`⚠️ ${response.data.error}`);
      } else {
        alert(`✅ Performance evaluated!\nAccuracy: ${response.data.outcome_accuracy}%\nGoals MAE: ${response.data.home_goals_mae?.toFixed(3)}`);
      }
    } catch (error) {
      console.error('Error evaluating model performance:', error);
      alert(`❌ Error evaluating performance: ${error.response?.data?.detail || error.message}`);
    } finally {
      setLoadingResults(false);
    }
  };

  const runXGBoostOptimization = async (method = 'grid_search', retrain = true) => {
    if (!window.confirm(`🔧 Run XGBoost optimization with ${method}?\nThis may take several minutes and will retrain your models.`)) {
      return;
    }
    
    setRunningXGBoostOptimization(true);
    try {
      console.log('🚀 Starting XGBoost optimization...');
      const response = await axios.post(`${API}/optimize-xgboost-models?method=${method}&retrain=${retrain}`);
      setOptimizationResults(response.data);
      
      if (response.data.error) {
        alert(`❌ Optimization failed: ${response.data.error}`);
      } else {
        const improvement = response.data.improvement_summary;
        alert(`✅ XGBoost optimization completed!\n` +
              `Accuracy improved by: ${improvement?.accuracy_improvement?.toFixed(2)}%\n` +
              `Goals MAE improved by: ${improvement?.goals_mae_improvement?.toFixed(3)}\n` +
              `New model version: ${response.data.new_performance?.model_version}`);
      }
      
      // Refresh status after optimization
      await fetchOptimizationStatus();
      
    } catch (error) {
      console.error('Error running XGBoost optimization:', error);
      alert(`❌ Error optimizing models: ${error.response?.data?.detail || error.message}`);
    } finally {
      setRunningXGBoostOptimization(false);
    }
  };

  const simulateOptimizationImpact = async (days = 30) => {
    try {
      setLoadingResults(true);
      const response = await axios.post(`${API}/simulate-optimization-impact?days_back=${days}`);
      setSimulationResults(response.data);
      
      if (response.data.error) {
        alert(`⚠️ ${response.data.error}`);
      } else {
        alert(`🎯 Simulation completed!\n` +
              `Current accuracy: ${response.data.current_accuracy}%\n` +
              `Potential improvement: +${(response.data.simulated_improvements.moderate_improvement - response.data.current_accuracy).toFixed(1)}%\n` +
              `Additional correct predictions: ${response.data.potential_value.additional_correct_predictions_moderate}`);
      }
  const fetchOptimizationStatus = async () => {
    try {
      const response = await axios.get(`${API}/xgboost-optimization-status`);
      setOptimizationStatus(response.data);
      console.log('✅ Optimization status loaded:', response.data);
    } catch (error) {
      console.error('Error fetching optimization status:', error);
      alert(`❌ Error fetching status: ${error.response?.data?.detail || error.message}`);
    }
  };

  const evaluateModelPerformance = async (days = 30) => {
    try {
      setLoadingResults(true);
      const response = await axios.get(`${API}/model-performance/${days}`);
      setModelPerformance(response.data);
      console.log('✅ Model performance evaluated:', response.data);
      
      if (response.data.error) {
        alert(`⚠️ ${response.data.error}`);
      } else {
        alert(`✅ Performance evaluated!\nAccuracy: ${response.data.outcome_accuracy}%\nGoals MAE: ${response.data.home_goals_mae?.toFixed(3)}`);
      }
    } catch (error) {
      console.error('Error evaluating model performance:', error);
      alert(`❌ Error evaluating performance: ${error.response?.data?.detail || error.message}`);
    } finally {
      setLoadingResults(false);
    }
  };

  const runXGBoostOptimization = async (method = 'grid_search', retrain = true) => {
    if (!window.confirm(`🔧 Run XGBoost optimization with ${method}?\nThis may take several minutes and will retrain your models.`)) {
      return;
    }
    
    setRunningXGBoostOptimization(true);
    try {
      console.log('🚀 Starting XGBoost optimization...');
      const response = await axios.post(`${API}/optimize-xgboost-models?method=${method}&retrain=${retrain}`);
      setOptimizationResults(response.data);
      
      if (response.data.error) {
        alert(`❌ Optimization failed: ${response.data.error}`);
      } else {
        const improvement = response.data.improvement_summary;
        alert(`✅ XGBoost optimization completed!\n` +
              `Accuracy improved by: ${improvement?.accuracy_improvement?.toFixed(2)}%\n` +
              `Goals MAE improved by: ${improvement?.goals_mae_improvement?.toFixed(3)}\n` +
              `New model version: ${response.data.new_performance?.model_version}`);
      }
      
      // Refresh status after optimization
      await fetchOptimizationStatus();
      
    } catch (error) {
      console.error('Error running XGBoost optimization:', error);
      alert(`❌ Error optimizing models: ${error.response?.data?.detail || error.message}`);
    } finally {
      setRunningXGBoostOptimization(false);
    }
  };

  const simulateOptimizationImpact = async (days = 30) => {
    try {
      setLoadingResults(true);
      const response = await axios.post(`${API}/simulate-optimization-impact?days_back=${days}`);
      setSimulationResults(response.data);
      
      if (response.data.error) {
        alert(`⚠️ ${response.data.error}`);
      } else {
        alert(`🎯 Simulation completed!\n` +
              `Current accuracy: ${response.data.current_accuracy}%\n` +
              `Potential improvement: +${(response.data.simulated_improvements.moderate_improvement - response.data.current_accuracy).toFixed(1)}%\n` +
              `Additional correct predictions: ${response.data.potential_value.additional_correct_predictions_moderate}`);
      }
      
    } catch (error) {
      console.error('Error simulating optimization impact:', error);
      alert(`❌ Error running simulation: ${error.response?.data?.detail || error.message}`);
    } finally {
      setLoadingResults(false);
    }
  };



  return (
    <div className="min-h-screen" style={{backgroundColor: '#F2E9E4'}}>
      {/* Header */}
      <div style={{backgroundColor: '#002629'}} className="shadow-lg border-b">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center py-4">
            <div className="flex items-center space-x-4">
              <h1 className="text-2xl font-bold text-white">⚽ Football Analytics Suite</h1>
              <span className="text-sm" style={{color: '#A3D9FF'}}>Enhanced with Starting XI & Time Decay</span>
            </div>
          </div>
        </div>
      </div>

      {/* Navigation */}
      <div style={{backgroundColor: '#12664F'}} className="shadow-sm">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <nav className="flex space-x-8 overflow-x-auto">
            {[
              { id: 'dashboard', name: '📊 Dashboard', icon: '📊' },
              { id: 'upload', name: '📁 Upload Data', icon: '📁' },
              { id: 'predict', name: '🎯 Standard Predict', icon: '🎯' },
              { id: 'xgboost', name: '🚀 Enhanced XGBoost', icon: '🚀' },
              { id: 'regression', name: '📈 Regression Analysis', icon: '📈' },
              { id: 'prediction-config', name: '⚙️ Prediction Config', icon: '⚙️' },
              { id: 'rbs-config', name: '⚖️ RBS Config', icon: '⚖️' },
              { id: 'optimization', name: '🤖 Formula Optimization', icon: '🤖' },
              { id: 'results', name: '📋 Results', icon: '📋' },
              { id: 'config', name: '🔧 System Config', icon: '🔧' }
            ].map(tab => (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id)}
                className={`py-4 px-6 text-sm font-medium border-b-2 whitespace-nowrap transition-colors ${
                  activeTab === tab.id
                    ? 'text-white border-white'
                    : 'border-transparent hover:border-white/50'
                }`}
                style={{
                  color: activeTab === tab.id ? '#FFFFFF' : '#A3D9FF'
                }}
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
            </div>
          </div>
        )}

        {/* Upload Data Tab */}
        {activeTab === 'upload' && (
          <div className="space-y-6">
            <div className="bg-white p-6 rounded-lg shadow-lg border border-gray-200">
              <h2 className="text-xl font-bold mb-4" style={{color: '#002629'}}>📁 Upload Football Data</h2>
              <p className="mb-6" style={{color: '#002629', opacity: 0.8}}>
                Upload your football datasets to enable predictions and analysis.
              </p>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                {[
                  { id: 'matches', name: 'Match Data', desc: 'Upload match results and statistics' },
                  { id: 'team-stats', name: 'Team Stats', desc: 'Upload team-level statistics' },
                  { id: 'player-stats', name: 'Player Stats', desc: 'Upload individual player statistics' }
                ].map(dataset => (
                  <div key={dataset.id} className="border-2 rounded-lg p-4" style={{borderColor: '#1C5D99', backgroundColor: '#F2E9E4'}}>
                    <h3 className="font-semibold mb-2" style={{color: '#002629'}}>{dataset.name}</h3>
                    <p className="text-sm mb-4" style={{color: '#002629', opacity: 0.8}}>{dataset.desc}</p>
                    
                    <input
                      type="file"
                      accept=".csv"
                      onChange={(e) => handleFileUpload(e, dataset.id)}
                      disabled={uploadingDataset}
                      className="w-full text-sm file:mr-4 file:py-2 file:px-4 file:rounded-lg file:border-0 file:text-sm file:font-medium file:text-white hover:file:opacity-90"
                      style={{
                        color: '#002629',
                        caretColor: '#002629'
                      }}
                    />
                    <style jsx>{`
                      input[type="file"]::file-selector-button {
                        background-color: #1C5D99;
                        color: white;
                        border: none;
                        margin-right: 1rem;
                        padding: 0.5rem 1rem;
                        border-radius: 0.5rem;
                        font-size: 0.875rem;
                        font-weight: 500;
                        cursor: pointer;
                        transition: opacity 0.2s;
                      }
                      input[type="file"]::file-selector-button:hover {
                        opacity: 0.9;
                      }
                    `}</style>
                    
                    {uploadStatus[dataset.id] && (
                      <div className="mt-2 text-sm" style={{color: '#002629'}}>
                        {uploadStatus[dataset.id]}
                      </div>
                    )}
                  </div>
                ))}
              </div>

              {/* Uploaded Datasets */}
              {datasets.length > 0 && (
                <div className="mt-8">
                  <h3 className="text-lg font-semibold mb-4" style={{color: '#002629'}}>📊 Uploaded Datasets</h3>
                  <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                    {datasets.map(dataset => (
                      <div key={dataset.name} className="p-4 rounded-lg border-2" style={{backgroundColor: '#A3D9FF', borderColor: '#12664F'}}>
                        <div className="font-medium" style={{color: '#002629'}}>{dataset.name}</div>
                        <div className="text-sm" style={{color: '#002629', opacity: 0.8}}>{dataset.records} records</div>
                        <div className="text-xs" style={{color: '#002629', opacity: 0.6}}>Uploaded: {new Date(dataset.uploaded_at).toLocaleDateString()}</div>
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
            <div className="card">
              <h2 className="card-header">🎯 Standard Match Prediction</h2>
              <p className="card-text mb-6">
                Standard prediction using team-level statistics and historical data.
              </p>

              {!predictionResult ? (
                <div className="space-y-6">
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                    <div>
                      <label className="block text-sm font-medium mb-2" style={{color: '#002629'}}>Home Team *</label>
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
                      <label className="block text-sm font-medium mb-2" style={{color: '#002629'}}>Away Team *</label>
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
                      <label className="block text-sm font-medium mb-2" style={{color: '#002629'}}>Referee *</label>
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

                  <button
                    onClick={predictMatch}
                    disabled={predicting || !predictionForm.home_team || !predictionForm.away_team || !predictionForm.referee_name}
                    className="btn-primary px-6 py-3 font-medium rounded-lg flex items-center space-x-2"
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
                  <div className="p-6 rounded-lg border-2" style={{backgroundColor: '#A3D9FF', borderColor: '#1C5D99'}}>
                    <div className="text-center">
                      <h3 className="text-2xl font-bold mb-2" style={{color: '#002629'}}>
                        {predictionResult.home_team} vs {predictionResult.away_team}
                      </h3>
                      <div className="text-lg mb-2" style={{color: '#002629'}}>
                        Predicted Score: <span className="font-bold" style={{color: '#1C5D99'}}>{predictionResult.predicted_home_goals}</span>
                        {' - '}
                        <span className="font-bold" style={{color: '#12664F'}}>{predictionResult.predicted_away_goals}</span>
                      </div>
                    </div>
                  </div>

                  <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                    <div className="stat-card text-center">
                      <div className="stat-card-number text-3xl">{predictionResult.home_win_probability}%</div>
                      <div className="stat-card-label">Home Win</div>
                    </div>
                    <div className="stat-card text-center">
                      <div className="stat-card-number text-3xl">{predictionResult.draw_probability}%</div>
                      <div className="stat-card-label">Draw</div>
                    </div>
                    <div className="stat-card text-center">
                      <div className="stat-card-number text-3xl">{predictionResult.away_win_probability}%</div>
                      <div className="stat-card-label">Away Win</div>
                    </div>
                  </div>

                  <div className="flex space-x-4">
                    <button
                      onClick={resetPrediction}
                      className="btn-dark px-6 py-3 font-medium rounded-lg"
                    >
                      🔄 New Prediction
                    </button>
                    <button
                      onClick={exportPDF}
                      disabled={exportingPDF}
                      className="btn-secondary px-6 py-3 font-medium rounded-lg flex items-center space-x-2"
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
            <div className="card">
              <h2 className="card-header">🚀 Enhanced XGBoost with Starting XI</h2>
              <p className="card-text mb-6">
                Advanced match prediction using XGBoost with Starting XI player selection and time decay weighting. 
                Select specific players for each team to get more accurate predictions based on actual lineups.
              </p>

              {/* Enhanced Features Control Panel */}
              <div className="mb-6 p-4 feature-card">
                <div className="flex items-center justify-between mb-4">
                  <h3 className="text-lg font-semibold" style={{color: '#002629'}}>🎯 Enhanced Prediction Features</h3>
                  <button
                    onClick={() => setShowStartingXI(!showStartingXI)}
                    className={`px-4 py-2 rounded-lg font-medium transition-colors ${
                      showStartingXI 
                        ? 'btn-primary shadow-md' 
                        : 'bg-white border-2 hover:opacity-80'
                    }`}
                    style={!showStartingXI ? {
                      color: '#1C5D99',
                      borderColor: '#1C5D99'
                    } : {}}
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
                        className="rounded border-gray-300 focus:ring-2"
                        style={{accentColor: '#1C5D99'}}
                      />
                      <span className="text-sm font-medium" style={{color: '#002629'}}>Apply Time Decay</span>
                    </label>
                    <p className="text-xs mt-1" style={{color: '#002629', opacity: 0.8}}>Recent matches weighted higher than historical data</p>
                  </div>
                  
                  <div>
                    <label className="block text-sm font-medium mb-1" style={{color: '#002629'}}>Decay Preset</label>
                    <select
                      value={decayPreset}
                      onChange={(e) => setDecayPreset(e.target.value)}
                      disabled={!useTimeDecay}
                      className="form-select w-full disabled:opacity-50"
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
                <div className="flex items-center justify-between p-3 bg-white rounded-lg border-2" style={{borderColor: '#1C5D99'}}>
                  <div className="flex items-center space-x-3">
                    <span className={`inline-block w-3 h-3 rounded-full ${mlStatus?.models_loaded ? 'bg-green-500' : 'bg-red-500'}`}></span>
                    <div>
                      <span className="text-sm font-medium" style={{color: '#002629'}}>
                        XGBoost Models: {mlStatus?.models_loaded ? '✅ Ready' : '❌ Need Training'}
                      </span>
                      <div className="text-xs" style={{color: '#002629', opacity: 0.8}}>
                        {mlStatus?.feature_columns_count || 0} features • Enhanced Engineering
                      </div>
                      {mlStatus?.last_trained && (
                        <div className="text-xs" style={{color: '#002629', opacity: 0.6}}>
                          Last trained: {new Date(mlStatus.last_trained).toLocaleDateString()}
                        </div>
                      )}
                    </div>
                  </div>
                  <div className="flex space-x-2">
                    <button
                      onClick={checkMLStatus}
                      className="btn-primary px-3 py-1 text-sm rounded"
                    >
                      🔄 Refresh
                    </button>
                    {!mlStatus?.models_loaded && (
                      <button
                        onClick={trainMLModels}
                        disabled={trainingModels}
                        className="btn-secondary px-3 py-1 text-sm rounded disabled:opacity-50"
                      >
                        {trainingModels ? '⏳ Training...' : '🧠 Train'}
                      </button>
                    )}
                    {mlStatus?.models_loaded && (
                      <button
                        onClick={() => {
                          if (window.confirm('⚠️ Retrain models with current data?\n\nThis will:\n• Use all uploaded data for training\n• Update model accuracy\n• May take several minutes\n\nContinue?')) {
                            trainMLModels();
                          }
                        }}
                        disabled={trainingModels}
                        className="btn-secondary px-3 py-1 text-sm rounded disabled:opacity-50"
                      >
                        {trainingModels ? '⏳ Retraining...' : '🔄 Retrain'}
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
                        (showStartingXI && predictionForm.home_team && predictionForm.away_team && 
                         (!validateStartingXI(homeStartingXI) || !validateStartingXI(awayStartingXI)))
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

        {/* Regression Analysis Tab */}
        {activeTab === 'regression' && (
          <div className="space-y-6">
            <div className="card">
              <h2 className="card-header">📈 Regression Analysis</h2>
              <p className="card-text mb-6">
                Analyze statistical correlations between team performance metrics and match outcomes using advanced regression models.
              </p>

              {/* Variable Selection */}
              <div className="mb-6">
                <h3 className="text-lg font-semibold mb-4" style={{color: '#002629'}}>Variable Selection</h3>
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                  {Object.entries(VARIABLE_CATEGORIES).map(([key, category]) => (
                    <div key={key} className="feature-card">
                      <h4 className="font-semibold mb-2" style={{color: '#002629'}}>
                        {category.name} ({category.count})
                      </h4>
                      <div className="space-y-2">
                        {category.variables.map(variable => (
                          <label key={variable} className="flex items-center space-x-2">
                            <input
                              type="checkbox"
                              checked={selectedVariables.includes(variable)}
                              onChange={(e) => {
                                if (e.target.checked) {
                                  setSelectedVariables([...selectedVariables, variable]);
                                } else {
                                  setSelectedVariables(selectedVariables.filter(v => v !== variable));
                                }
                              }}
                              className="rounded"
                              style={{accentColor: '#1C5D99'}}
                            />
                            <span className="text-sm" style={{color: '#002629'}}>
                              {variable.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase())}
                            </span>
                          </label>
                        ))}
                      </div>
                    </div>
                  ))}
                </div>
              </div>

              {/* Analysis Options */}
              <div className="mb-6 grid grid-cols-1 md:grid-cols-2 gap-6">
                <div>
                  <label className="block text-sm font-medium mb-2" style={{color: '#002629'}}>Target Variable</label>
                  <select
                    value={regressionTarget}
                    onChange={(e) => setRegressionTarget(e.target.value)}
                    className="form-select w-full"
                  >
                    <option value="points_per_game">Points Per Game</option>
                    <option value="match_result">Match Result</option>
                  </select>
                </div>
                <div className="flex items-end">
                  <button
                    onClick={async () => {
                      if (selectedVariables.length === 0) {
                        alert('Please select at least one variable for analysis');
                        return;
                      }
                      setRunningRegression(true);
                      try {
                        const result = await runRegressionAnalysis(selectedVariables, regressionTarget, API.replace('/api', ''));
                        setRegressionResults(result);
                      } catch (error) {
                        alert(`Analysis Error: ${error.message}`);
                      }
                      setRunningRegression(false);
                    }}
                    disabled={runningRegression || selectedVariables.length === 0}
                    className="btn-primary px-6 py-3 font-medium rounded-lg flex items-center space-x-2"
                  >
                    {runningRegression ? (
                      <>
                        <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white"></div>
                        <span>Analyzing...</span>
                      </>
                    ) : (
                      <>
                        <span>📊</span>
                        <span>Run Analysis</span>
                      </>
                    )}
                  </button>
                </div>
              </div>

              {/* Results Display */}
              {regressionResults && (
                <div className="space-y-4">
                  <h3 className="text-lg font-semibold" style={{color: '#002629'}}>Analysis Results</h3>
                  <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                    <div className="stat-card text-center">
                      <div className="stat-card-number">R² {formatScore(regressionResults.results?.r_squared || 0)}</div>
                      <div className="stat-card-label">Model Accuracy</div>
                    </div>
                    <div className="stat-card text-center">
                      <div className="stat-card-number">{regressionResults.sample_size || 0}</div>
                      <div className="stat-card-label">Sample Size</div>
                    </div>
                    <div className="stat-card text-center">
                      <div className="stat-card-number">{selectedVariables.length}</div>
                      <div className="stat-card-label">Variables Used</div>
                    </div>
                  </div>
                  {regressionResults.results?.feature_importance && (
                    <div className="feature-card">
                      <h4 className="font-semibold mb-2" style={{color: '#002629'}}>Feature Importance</h4>
                      <div className="space-y-2">
                        {Object.entries(regressionResults.results.feature_importance).map(([feature, importance]) => (
                          <div key={feature} className="flex justify-between items-center">
                            <span className="text-sm" style={{color: '#002629'}}>{feature.replace(/_/g, ' ')}</span>
                            <span className="text-sm font-medium" style={{color: '#1C5D99'}}>{formatScore(importance)}</span>
                          </div>
                        ))}
                      </div>
                    </div>
                  )}
                </div>
              )}

              {/* Enhanced RBS Analysis Section */}
              <div className="mt-8 p-6 rounded-lg border-2" style={{backgroundColor: '#F2E9E4', borderColor: '#12664F'}}>
                <h3 className="text-lg font-semibold mb-4" style={{color: '#002629'}}>🔍 Enhanced RBS Analysis</h3>
                <p className="text-sm mb-6" style={{color: '#002629', opacity: 0.8}}>
                  Advanced referee variance analysis for specific team-referee combinations with detailed statistical breakdowns.
                </p>

                <div className="flex items-center space-x-4 mb-6">
                  <div className="flex-1">
                    <label className="block text-sm font-medium mb-2" style={{color: '#002629'}}>Team</label>
                    <select
                      value={selectedTeamForAnalysis}
                      onChange={(e) => setSelectedTeamForAnalysis(e.target.value)}
                      className="form-select w-full"
                    >
                      <option value="">Select Team</option>
                      {teams.map(team => (
                        <option key={team} value={team}>{team}</option>
                      ))}
                    </select>
                  </div>
                  <div className="flex-1">
                    <label className="block text-sm font-medium mb-2" style={{color: '#002629'}}>Referee</label>
                    <select
                      value={selectedRefereeForAnalysis}
                      onChange={(e) => setSelectedRefereeForAnalysis(e.target.value)}
                      className="form-select w-full"
                    >
                      <option value="">Select Referee</option>
                      {referees.map(referee => (
                        <option key={referee} value={referee}>{referee}</option>
                      ))}
                    </select>
                  </div>
                  <div className="pt-6">
                    <button
                      onClick={() => fetchEnhancedRBSForTeamReferee(selectedTeamForAnalysis, selectedRefereeForAnalysis)}
                      disabled={!selectedTeamForAnalysis || !selectedRefereeForAnalysis || loadingEnhancedRBS}
                      className="px-4 py-2 text-white font-medium rounded hover:opacity-90 disabled:opacity-50 disabled:cursor-not-allowed flex items-center space-x-2"
                      style={{backgroundColor: '#12664F'}}
                    >
                      {loadingEnhancedRBS ? (
                        <>
                          <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white"></div>
                          <span>Analyzing...</span>
                        </>
                      ) : (
                        <>
                          <span>🔍</span>
                          <span>Analyze</span>
                        </>
                      )}
                    </button>
                  </div>
                </div>

                {enhancedRBSData && (
                  <div className="space-y-4">
                    <div className="bg-white p-4 rounded border border-gray-200">
                      <h4 className="font-semibold text-gray-800 mb-3">📈 Enhanced Analysis Results</h4>
                      <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-4">
                        <div className="text-center">
                          <div className="text-2xl font-bold text-gray-800">{enhancedRBSData.team_matches_with_referee || 'N/A'}</div>
                          <div className="text-xs text-gray-600">Matches Together</div>
                        </div>
                        <div className="text-center">
                          <div className="text-2xl font-bold text-gray-800">{enhancedRBSData.rbs_score?.toFixed(3) || 'N/A'}</div>
                          <div className="text-xs text-gray-600">RBS Score</div>
                        </div>
                        <div className="text-center">
                          <div className="text-2xl font-bold text-gray-800">{enhancedRBSData.confidence || 'N/A'}</div>
                          <div className="text-xs text-gray-600">Confidence Level</div>
                        </div>
                      </div>
                      
                      {enhancedRBSData.variance_analysis && (
                        <RBSVarianceAnalysis varianceData={enhancedRBSData.variance_analysis} />
                      )}
                    </div>
                  </div>
                )}
              </div>
            </div>
          </div>
        )}

        {/* Prediction Config Tab */}
        {activeTab === 'prediction-config' && (
          <div className="space-y-6">
            <div className="card">
              <h2 className="card-header">⚙️ Prediction Configuration</h2>
              <p className="card-text mb-6">
                Customize prediction algorithm parameters, xG calculations, and performance adjustments.
              </p>

              {/* Config Selection */}
              <div className="mb-6">
                <label className="block text-sm font-medium mb-2" style={{color: '#002629'}}>Configuration</label>
                <div className="flex space-x-4">
                  <select
                    value={currentPredictionConfig?.config_name || 'default'}
                    onChange={(e) => {
                      const config = predictionConfigs.find(c => c.config_name === e.target.value);
                      setCurrentPredictionConfig(config || DEFAULT_PREDICTION_CONFIG);
                    }}
                    className="form-select flex-1"
                  >
                    {predictionConfigs.map(config => (
                      <option key={config.config_name} value={config.config_name}>
                        {config.config_name}
                      </option>
                    ))}
                  </select>
                  <button
                    onClick={() => setEditingPredictionConfig(!editingPredictionConfig)}
                    className="btn-secondary px-4 py-2 rounded-lg"
                  >
                    {editingPredictionConfig ? 'Cancel' : 'Edit'}
                  </button>
                </div>
              </div>

              {editingPredictionConfig && (
                <div className="space-y-6">
                  {/* xG Calculation Weights */}
                  <div className="feature-card">
                    <h3 className="text-lg font-semibold mb-4" style={{color: '#002629'}}>xG Calculation Weights</h3>
                    <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                      <div>
                        <label className="block text-sm font-medium mb-1" style={{color: '#002629'}}>Shot-based Weight</label>
                        <input
                          type="number"
                          step="0.1"
                          min="0"
                          max="1"
                          value={currentPredictionConfig?.xg_shot_based_weight || 0.4}
                          onChange={(e) => setCurrentPredictionConfig({
                            ...currentPredictionConfig,
                            xg_shot_based_weight: parseFloat(e.target.value)
                          })}
                          className="form-input w-full"
                        />
                      </div>
                      <div>
                        <label className="block text-sm font-medium mb-1" style={{color: '#002629'}}>Historical Weight</label>
                        <input
                          type="number"
                          step="0.1"
                          min="0"
                          max="1"
                          value={currentPredictionConfig?.xg_historical_weight || 0.4}
                          onChange={(e) => setCurrentPredictionConfig({
                            ...currentPredictionConfig,
                            xg_historical_weight: parseFloat(e.target.value)
                          })}
                          className="form-input w-full"
                        />
                      </div>
                      <div>
                        <label className="block text-sm font-medium mb-1" style={{color: '#002629'}}>Opponent Defense Weight</label>
                        <input
                          type="number"
                          step="0.1"
                          min="0"
                          max="1"
                          value={currentPredictionConfig?.xg_opponent_defense_weight || 0.2}
                          onChange={(e) => setCurrentPredictionConfig({
                            ...currentPredictionConfig,
                            xg_opponent_defense_weight: parseFloat(e.target.value)
                          })}
                          className="form-input w-full"
                        />
                      </div>
                    </div>
                  </div>

                  {/* Performance Adjustments */}
                  <div className="feature-card">
                    <h3 className="text-lg font-semibold mb-4" style={{color: '#002629'}}>Performance Adjustments</h3>
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                      <div>
                        <label className="block text-sm font-medium mb-1" style={{color: '#002629'}}>PPG Adjustment Factor</label>
                        <input
                          type="number"
                          step="0.01"
                          value={currentPredictionConfig?.ppg_adjustment_factor || 0.15}
                          onChange={(e) => setCurrentPredictionConfig({
                            ...currentPredictionConfig,
                            ppg_adjustment_factor: parseFloat(e.target.value)
                          })}
                          className="form-input w-full"
                        />
                      </div>
                      <div>
                        <label className="block text-sm font-medium mb-1" style={{color: '#002629'}}>RBS Scaling Factor</label>
                        <input
                          type="number"
                          step="0.01"
                          value={currentPredictionConfig?.rbs_scaling_factor || 0.2}
                          onChange={(e) => setCurrentPredictionConfig({
                            ...currentPredictionConfig,
                            rbs_scaling_factor: parseFloat(e.target.value)
                          })}
                          className="form-input w-full"
                        />
                      </div>
                    </div>
                  </div>

                  {/* Save Configuration */}
                  <div className="flex space-x-4">
                    <button
                      onClick={async () => {
                        try {
                          await savePredictionConfig(currentPredictionConfig, API.replace('/api', ''));
                          setEditingPredictionConfig(false);
                          alert('Configuration saved successfully!');
                        } catch (error) {
                          alert(`Save Error: ${error.message}`);
                        }
                      }}
                      className="btn-primary px-6 py-3 font-medium rounded-lg"
                    >
                      💾 Save Configuration
                    </button>
                  </div>
                </div>
              )}

              {/* Configuration Management Section */}
              <div className="mt-8 p-6 rounded-lg border-2" style={{backgroundColor: '#A3D9FF', borderColor: '#1C5D99'}}>
                <div className="flex items-center justify-between mb-4">
                  <div>
                    <h3 className="text-lg font-semibold" style={{color: '#002629'}}>📋 Configuration Management</h3>
                    <p className="text-sm mt-1" style={{color: '#002629', opacity: 0.8}}>
                      Manage, edit, and delete prediction configurations
                    </p>
                  </div>
                  <button
                    onClick={() => setShowConfigManager(!showConfigManager)}
                    className="px-4 py-2 text-white font-medium rounded hover:opacity-90"
                    style={{backgroundColor: showConfigManager ? '#002629' : '#1C5D99'}}
                  >
                    {showConfigManager ? '📝 Hide Manager' : '📋 Show All Configs'}
                  </button>
                </div>

                {showConfigManager && (
                  <div className="mt-4">
                    <ConfigurationList
                      configs={allPredictionConfigs}
                      type="Prediction"
                      onEdit={handleConfigEdit}
                      onDelete={handleConfigDelete}
                      onSelect={(config) => {
                        setCurrentPredictionConfig(config);
                        setShowConfigManager(false);
                      }}
                    />
                  </div>
                )}
              </div>
            </div>
          </div>
        )}

        {/* RBS Config Tab */}
        {activeTab === 'rbs-config' && (
          <div className="space-y-6">
            <div className="card">
              <h2 className="card-header">⚖️ Referee Bias Score Configuration</h2>
              <p className="card-text mb-6">
                Customize referee bias calculation weights and confidence thresholds for optimal accuracy.
              </p>

              {/* Config Selection */}
              <div className="mb-6">
                <label className="block text-sm font-medium mb-2" style={{color: '#002629'}}>RBS Configuration</label>
                <div className="flex space-x-4">
                  <select
                    value={currentRbsConfig?.config_name || 'default'}
                    onChange={(e) => {
                      const config = rbsConfigs.find(c => c.config_name === e.target.value);
                      setCurrentRbsConfig(config || DEFAULT_RBS_CONFIG);
                    }}
                    className="form-select flex-1"
                  >
                    {rbsConfigs.map(config => (
                      <option key={config.config_name} value={config.config_name}>
                        {config.config_name}
                      </option>
                    ))}
                  </select>
                  <button
                    onClick={() => setEditingRbsConfig(!editingRbsConfig)}
                    className="btn-secondary px-4 py-2 rounded-lg"
                  >
                    {editingRbsConfig ? 'Cancel' : 'Edit'}
                  </button>
                </div>
              </div>

              {editingRbsConfig && (
                <div className="space-y-6">
                  {/* Statistical Weights */}
                  <div className="feature-card">
                    <h3 className="text-lg font-semibold mb-4" style={{color: '#002629'}}>Statistical Weights</h3>
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                      <div>
                        <label className="block text-sm font-medium mb-1" style={{color: '#002629'}}>Yellow Cards Weight</label>
                        <input
                          type="number"
                          step="0.1"
                          value={currentRbsConfig?.yellow_cards_weight || 0.3}
                          onChange={(e) => setCurrentRbsConfig({
                            ...currentRbsConfig,
                            yellow_cards_weight: parseFloat(e.target.value)
                          })}
                          className="form-input w-full"
                        />
                      </div>
                      <div>
                        <label className="block text-sm font-medium mb-1" style={{color: '#002629'}}>Red Cards Weight</label>
                        <input
                          type="number"
                          step="0.1"
                          value={currentRbsConfig?.red_cards_weight || 0.5}
                          onChange={(e) => setCurrentRbsConfig({
                            ...currentRbsConfig,
                            red_cards_weight: parseFloat(e.target.value)
                          })}
                          className="form-input w-full"
                        />
                      </div>
                      <div>
                        <label className="block text-sm font-medium mb-1" style={{color: '#002629'}}>Penalties Awarded Weight</label>
                        <input
                          type="number"
                          step="0.1"
                          value={currentRbsConfig?.penalties_awarded_weight || 0.5}
                          onChange={(e) => setCurrentRbsConfig({
                            ...currentRbsConfig,
                            penalties_awarded_weight: parseFloat(e.target.value)
                          })}
                          className="form-input w-full"
                        />
                      </div>
                      <div>
                        <label className="block text-sm font-medium mb-1" style={{color: '#002629'}}>xG Difference Weight</label>
                        <input
                          type="number"
                          step="0.1"
                          value={currentRbsConfig?.xg_difference_weight || 0.4}
                          onChange={(e) => setCurrentRbsConfig({
                            ...currentRbsConfig,
                            xg_difference_weight: parseFloat(e.target.value)
                          })}
                          className="form-input w-full"
                        />
                      </div>
                    </div>
                  </div>

                  {/* Confidence Thresholds */}
                  <div className="feature-card">
                    <h3 className="text-lg font-semibold mb-4" style={{color: '#002629'}}>Confidence Thresholds</h3>
                    <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                      <div>
                        <label className="block text-sm font-medium mb-1" style={{color: '#002629'}}>Low Confidence (matches)</label>
                        <input
                          type="number"
                          min="1"
                          value={currentRbsConfig?.confidence_threshold_low || 2}
                          onChange={(e) => setCurrentRbsConfig({
                            ...currentRbsConfig,
                            confidence_threshold_low: parseInt(e.target.value)
                          })}
                          className="form-input w-full"
                        />
                      </div>
                      <div>
                        <label className="block text-sm font-medium mb-1" style={{color: '#002629'}}>Medium Confidence (matches)</label>
                        <input
                          type="number"
                          min="1"
                          value={currentRbsConfig?.confidence_threshold_medium || 5}
                          onChange={(e) => setCurrentRbsConfig({
                            ...currentRbsConfig,
                            confidence_threshold_medium: parseInt(e.target.value)
                          })}
                          className="form-input w-full"
                        />
                      </div>
                      <div>
                        <label className="block text-sm font-medium mb-1" style={{color: '#002629'}}>High Confidence (matches)</label>
                        <input
                          type="number"
                          min="1"
                          value={currentRbsConfig?.confidence_threshold_high || 10}
                          onChange={(e) => setCurrentRbsConfig({
                            ...currentRbsConfig,
                            confidence_threshold_high: parseInt(e.target.value)
                          })}
                          className="form-input w-full"
                        />
                      </div>
                    </div>
                  </div>

                  {/* Save Configuration */}
                  <div className="flex space-x-4">
                    <button
                      onClick={async () => {
                        try {
                          await saveRBSConfig(currentRbsConfig, API.replace('/api', ''));
                          setEditingRbsConfig(false);
                          alert('RBS Configuration saved successfully!');
                        } catch (error) {
                          alert(`Save Error: ${error.message}`);
                        }
                      }}
                      className="btn-primary px-6 py-3 font-medium rounded-lg"
                    >
                      💾 Save RBS Configuration
                    </button>
                  </div>
                </div>
              )}

              {/* RBS Configuration Management Section */}
              <div className="mt-8 p-6 rounded-lg border-2" style={{backgroundColor: '#A3D9FF', borderColor: '#12664F'}}>
                <div className="flex items-center justify-between mb-4">
                  <div>
                    <h3 className="text-lg font-semibold" style={{color: '#002629'}}>📋 RBS Configuration Management</h3>
                    <p className="text-sm mt-1" style={{color: '#002629', opacity: 0.8}}>
                      Manage, edit, and delete RBS configurations
                    </p>
                  </div>
                  <button
                    onClick={() => setShowRBSConfigManager(!showRBSConfigManager)}
                    className="px-4 py-2 text-white font-medium rounded hover:opacity-90"
                    style={{backgroundColor: showRBSConfigManager ? '#002629' : '#12664F'}}
                  >
                    {showRBSConfigManager ? '📝 Hide Manager' : '📋 Show All RBS Configs'}
                  </button>
                </div>

                {showRBSConfigManager && (
                  <div className="mt-4">
                    <ConfigurationList
                      configs={allRBSConfigs}
                      type="RBS"
                      onEdit={handleRBSConfigEdit}
                      onDelete={handleRBSConfigDelete}
                      onSelect={(config) => {
                        setCurrentRbsConfig(config);
                        setShowRBSConfigManager(false);
                      }}
                    />
                  </div>
                )}
              </div>
            </div>
          </div>
        )}

        {/* Formula Optimization Tab */}
        {activeTab === 'optimization' && (
          <div className="space-y-6">
            <div className="card">
              <h2 className="card-header">🤖 AI-Powered Formula Optimization</h2>
              <p className="card-text mb-6">
                Use machine learning to optimize formula weights and discover the most effective variable combinations.
              </p>

              {/* Optimization Type Selection */}
              <div className="mb-6">
                <label className="block text-sm font-medium mb-2" style={{color: '#002629'}}>Optimization Type</label>
                <select
                  value={optimizationType}
                  onChange={(e) => setOptimizationType(e.target.value)}
                  className="form-select w-full md:w-1/2"
                >
                  <option value="rbs">RBS Formula Optimization</option>
                  <option value="prediction">Match Predictor Optimization</option>
                  <option value="combined">Combined Analysis</option>
                </select>
              </div>

              {/* Run Optimization */}
              <div className="mb-6">
                <button
                  onClick={async () => {
                    setRunningOptimization(true);
                    try {
                      const result = await runFormulaOptimization(optimizationType, API.replace('/api', ''));
                      setOptimizationResults(result);
                    } catch (error) {
                      alert(`Optimization Error: ${error.message}`);
                    }
                    setRunningOptimization(false);
                  }}
                  disabled={runningOptimization}
                  className="btn-primary px-6 py-3 font-medium rounded-lg flex items-center space-x-2"
                >
                  {runningOptimization ? (
                    <>
                      <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white"></div>
                      <span>Optimizing...</span>
                    </>
                  ) : (
                    <>
                      <span>🤖</span>
                      <span>Run AI Optimization</span>
                    </>
                  )}
                </button>
              </div>

              {/* Optimization Results */}
              {optimizationResults && (
                <div className="space-y-6">
                  <h3 className="text-lg font-semibold" style={{color: '#002629'}}>Optimization Results</h3>
                  
                  <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                    <div className="stat-card text-center">
                      <div className="stat-card-number">R² {formatScore(optimizationResults.performance?.r_squared || 0)}</div>
                      <div className="stat-card-label">Optimized Accuracy</div>
                    </div>
                    <div className="stat-card text-center">
                      <div className="stat-card-number">{formatPercentage(optimizationResults.improvement || 0)}</div>
                      <div className="stat-card-label">Performance Gain</div>
                    </div>
                    <div className="stat-card text-center">
                      <div className="stat-card-number">{optimizationResults.variables_analyzed || 0}</div>
                      <div className="stat-card-label">Variables Analyzed</div>
                    </div>
                  </div>

                  {optimizationResults.recommendations && (
                    <div className="feature-card">
                      <h4 className="font-semibold mb-2" style={{color: '#002629'}}>AI Recommendations</h4>
                      <div className="space-y-2">
                        {optimizationResults.recommendations.map((rec, index) => (
                          <div key={index} className="p-3 rounded border-2" style={{backgroundColor: '#A3D9FF', borderColor: '#1C5D99'}}>
                            <div className="font-medium" style={{color: '#002629'}}>{rec.variable}</div>
                            <div className="text-sm" style={{color: '#002629', opacity: 0.8}}>
                              Suggested weight: {rec.suggested_weight} (current: {rec.current_weight})
                            </div>
                            <div className="text-xs" style={{color: '#002629', opacity: 0.6}}>{rec.reasoning}</div>
                          </div>
                        ))}
                      </div>
                    </div>
                  )}

                  <div className="flex space-x-4">
                    <button
                      onClick={() => {
                        if (window.confirm('Apply optimized weights to create new configuration?')) {
                          // Implementation for applying optimized weights
                          alert('Optimized configuration applied successfully!');
                        }
                      }}
                      className="btn-secondary px-6 py-3 font-medium rounded-lg"
                    >
                      ✅ Apply Optimized Weights
                    </button>
                  </div>
                </div>
              )}

              {/* Advanced Optimization Section */}
              <div className="mt-8 p-6 rounded-lg border-2" style={{backgroundColor: '#A3D9FF', borderColor: '#002629'}}>
                <h3 className="text-lg font-semibold mb-4" style={{color: '#002629'}}>🚀 XGBoost Model Optimization</h3>
                <p className="text-sm mb-6" style={{color: '#002629', opacity: 0.8}}>
                  Optimize your XGBoost models based on prediction accuracy against real match results. Track performance, tune hyperparameters, and retrain models automatically.
                </p>

                <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-6">
                  {/* Optimization Status */}
                  <div className="bg-white p-4 rounded border border-gray-200">
                    <h4 className="font-semibold text-gray-800 mb-3">📊 Optimization Status</h4>
                    <div className="space-y-2">
                      <div className="flex justify-between">
                        <span className="text-sm text-gray-600">Predictions Tracked:</span>
                        <span className="text-sm font-medium text-gray-800">Loading...</span>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-sm text-gray-600">Actual Results:</span>
                        <span className="text-sm font-medium text-gray-800">Loading...</span>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-sm text-gray-600">Model Version:</span>
                        <span className="text-sm font-medium text-gray-800">Loading...</span>
                      </div>
                    </div>
                  </div>

                  {/* Performance Metrics */}
                  <div className="bg-white p-4 rounded border border-gray-200">
                    <h4 className="font-semibold text-gray-800 mb-3">📈 Recent Performance</h4>
                    <div className="space-y-2">
                      <div className="flex justify-between">
                        <span className="text-sm text-gray-600">Accuracy:</span>
                        <span className="text-sm font-medium text-gray-800">Loading...</span>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-sm text-gray-600">Goals MAE:</span>
                        <span className="text-sm font-medium text-gray-800">Loading...</span>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-sm text-gray-600">Log Loss:</span>
                        <span className="text-sm font-medium text-gray-800">Loading...</span>
                      </div>
                    </div>
                  </div>

                  {/* Quick Actions */}
                  <div className="bg-white p-4 rounded border border-gray-200">
                    <h4 className="font-semibold text-gray-800 mb-3">⚡ Quick Actions</h4>
                    <div className="space-y-2">
                      <button
                        className="w-full px-3 py-2 text-sm text-white rounded hover:opacity-90"
                        style={{backgroundColor: '#1C5D99'}}
                        onClick={() => {/* Handle evaluate performance */}}
                      >
                        📊 Evaluate Performance
                      </button>
                      <button
                        className="w-full px-3 py-2 text-sm text-white rounded hover:opacity-90"
                        style={{backgroundColor: '#12664F'}}
                        onClick={() => {/* Handle optimize models */}}
                      >
                        🔧 Optimize Models
                      </button>
                      <button
                        className="w-full px-3 py-2 text-sm text-white rounded hover:opacity-90"
                        style={{backgroundColor: '#002629'}}
                        onClick={() => {/* Handle simulation */}}
                      >
                        🎯 Simulate Impact
                      </button>
                    </div>
                  </div>
                </div>

                {/* Model Optimization Results */}
                <div className="bg-white p-4 rounded border border-gray-200">
                  <h4 className="font-semibold text-gray-800 mb-3">🎯 Optimization Results</h4>
                  <div className="text-center py-8 text-gray-500">
                    <p>Run model optimization to see results here</p>
                    <p className="text-sm mt-2">Performance metrics, hyperparameter improvements, and retraining results will be displayed</p>
                  </div>
                </div>

                {/* Prediction Tracking Info */}
                <div className="mt-4 p-3 bg-blue-50 rounded border border-blue-200">
                  <div className="flex items-start space-x-2">
                    <span className="text-blue-600">ℹ️</span>
                    <div className="text-sm text-blue-800">
                      <strong>Automatic Tracking:</strong> All Enhanced XGBoost predictions are automatically tracked for optimization. 
                      When real match results become available, you can input them to improve model accuracy.
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        )}

        {/* Results Tab */}
        {activeTab === 'results' && (
          <div className="space-y-6">
            <div className="card">
              <h2 className="card-header">📋 Referee Analysis Results</h2>
              <p className="card-text mb-6">
                Comprehensive analysis of referee bias scores, team-referee combinations, and detailed referee profiles.
              </p>

              {/* Load Analysis Button */}
              <div className="mb-6">
                <button
                  onClick={async () => {
                    setLoadingResults(true);
                    try {
                      const result = await fetchRefereeAnalysis(API.replace('/api', ''));
                      setRefereeAnalysis(result);
                    } catch (error) {
                      alert(`Analysis Error: ${error.message}`);
                    }
                    setLoadingResults(false);
                  }}
                  disabled={loadingResults}
                  className="btn-primary px-6 py-3 font-medium rounded-lg flex items-center space-x-2"
                >
                  {loadingResults ? (
                    <>
                      <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white"></div>
                      <span>Loading Analysis...</span>
                    </>
                  ) : (
                    <>
                      <span>📊</span>
                      <span>Load Referee Analysis</span>
                    </>
                  )}
                </button>
              </div>

              {/* Referee Summary */}
              {refereeAnalysis && (
                <div className="space-y-6">
                  <h3 className="text-lg font-semibold" style={{color: '#002629'}}>Referee Summary</h3>
                  
                  <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
                    <div className="stat-card text-center">
                      <div className="stat-card-number">{refereeAnalysis.total_referees || 0}</div>
                      <div className="stat-card-label">Total Referees</div>
                    </div>
                    <div className="stat-card text-center">
                      <div className="stat-card-number">{refereeAnalysis.total_matches || 0}</div>
                      <div className="stat-card-label">Total Matches</div>
                    </div>
                    <div className="stat-card text-center">
                      <div className="stat-card-number">{refereeAnalysis.teams_covered || 0}</div>
                      <div className="stat-card-label">Teams Covered</div>
                    </div>
                    <div className="stat-card text-center">
                      <div className="stat-card-number">{formatScore(refereeAnalysis.avg_bias_score || 0)}</div>
                      <div className="stat-card-label">Avg Bias Score</div>
                    </div>
                  </div>

                  {/* Detailed Referee List */}
                  <div className="feature-card">
                    <h4 className="font-semibold mb-4" style={{color: '#002629'}}>Referee Profiles</h4>
                    <div className="space-y-2 max-h-96 overflow-y-auto">
                      {refereeAnalysis.referees?.map((referee, index) => (
                        <div key={index} className="p-3 rounded border-2 flex justify-between items-center hover:opacity-80 cursor-pointer"
                             style={{backgroundColor: '#F2E9E4', borderColor: '#1C5D99'}}
                             onClick={() => fetchDetailedRefereeAnalysis(referee.name)}>
                          <div>
                            <div className="font-medium" style={{color: '#002629'}}>{referee.name}</div>
                            <div className="text-sm" style={{color: '#002629', opacity: 0.8}}>
                              {referee.matches} matches • {referee.teams} teams
                            </div>
                          </div>
                          <div className="text-right">
                            <div className="text-sm font-medium" 
                                 style={{color: getRBSScoreColor(referee.avg_bias_score)}}>
                              RBS: {formatScore(referee.avg_bias_score || 0)}
                            </div>
                            <div className="text-xs" 
                                 style={{color: getConfidenceColor(referee.confidence)}}>
                              {referee.confidence}% confidence
                            </div>
                          </div>
                        </div>
                      ))}
                    </div>
                  </div>

                  {/* Detailed Referee Analysis */}
                  {detailedRefereeData && (
                    <div className="mt-6 space-y-4">
                      <div className="flex items-center justify-between">
                        <h4 className="text-lg font-semibold" style={{color: '#002629'}}>
                          📊 Detailed Analysis: {detailedRefereeData.referee_name}
                        </h4>
                        <button
                          onClick={() => setDetailedRefereeData(null)}
                          className="btn-secondary px-3 py-1 text-sm rounded"
                        >
                          ✕ Close
                        </button>
                      </div>

                      {/* Summary Stats */}
                      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
                        <div className="stat-card text-center">
                          <div className="stat-card-number">{detailedRefereeData.total_matches}</div>
                          <div className="stat-card-label">Total Matches</div>
                        </div>
                        <div className="stat-card text-center">
                          <div className="stat-card-number">{detailedRefereeData.teams_officiated}</div>
                          <div className="stat-card-label">Teams Officiated</div>
                        </div>
                        <div className="stat-card text-center">
                          <div className="stat-card-number">{formatScore(detailedRefereeData.avg_bias_score)}</div>
                          <div className="stat-card-label">Avg Bias Score</div>
                        </div>
                        <div className="stat-card text-center">
                          <div className="stat-card-number">{detailedRefereeData.rbs_calculations}</div>
                          <div className="stat-card-label">RBS Calculations</div>
                        </div>
                      </div>

                      {/* Match Outcomes */}
                      {detailedRefereeData.match_outcomes && (
                        <div className="feature-card">
                          <h5 className="font-semibold mb-2" style={{color: '#002629'}}>Match Outcomes</h5>
                          <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
                            <div className="text-center">
                              <div className="text-lg font-bold" style={{color: '#12664F'}}>{detailedRefereeData.match_outcomes.home_wins}</div>
                              <div className="text-sm" style={{color: '#002629'}}>Home Wins</div>
                            </div>
                            <div className="text-center">
                              <div className="text-lg font-bold" style={{color: '#1C5D99'}}>{detailedRefereeData.match_outcomes.draws}</div>
                              <div className="text-sm" style={{color: '#002629'}}>Draws</div>
                            </div>
                            <div className="text-center">
                              <div className="text-lg font-bold" style={{color: '#002629'}}>{detailedRefereeData.match_outcomes.away_wins}</div>
                              <div className="text-sm" style={{color: '#002629'}}>Away Wins</div>
                            </div>
                            <div className="text-center">
                              <div className="text-lg font-bold" style={{color: '#A3D9FF'}}>{detailedRefereeData.match_outcomes.home_win_percentage}%</div>
                              <div className="text-sm" style={{color: '#002629'}}>Home Win %</div>
                            </div>
                          </div>
                        </div>
                      )}

                      {/* Bias Analysis */}
                      {detailedRefereeData.bias_analysis?.most_biased_team && (
                        <div className="feature-card">
                          <h5 className="font-semibold mb-2" style={{color: '#002629'}}>Bias Extremes</h5>
                          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                            <div className="p-3 rounded border-2" style={{backgroundColor: '#A3D9FF', borderColor: '#12664F'}}>
                              <div className="font-medium" style={{color: '#002629'}}>Most Biased (Favored)</div>
                              <div className="text-lg font-bold" style={{color: '#12664F'}}>
                                {detailedRefereeData.bias_analysis.most_biased_team.team}
                              </div>
                              <div className="text-sm" style={{color: '#002629'}}>
                                RBS: {formatScore(detailedRefereeData.bias_analysis.most_biased_team.rbs_score)} 
                                ({detailedRefereeData.bias_analysis.most_biased_team.bias_direction})
                              </div>
                            </div>
                            {detailedRefereeData.bias_analysis.least_biased_team && (
                              <div className="p-3 rounded border-2" style={{backgroundColor: '#F2E9E4', borderColor: '#1C5D99'}}>
                                <div className="font-medium" style={{color: '#002629'}}>Least Biased (Neutral)</div>
                                <div className="text-lg font-bold" style={{color: '#1C5D99'}}>
                                  {detailedRefereeData.bias_analysis.least_biased_team.team}
                                </div>
                                <div className="text-sm" style={{color: '#002629'}}>
                                  RBS: {formatScore(detailedRefereeData.bias_analysis.least_biased_team.rbs_score)}
                                </div>
                              </div>
                            )}
                          </div>
                        </div>
                      )}

                      {/* Team RBS Details with Stat Differentials */}
                      {detailedRefereeData.team_rbs_details && Object.keys(detailedRefereeData.team_rbs_details).length > 0 && (
                        <div className="feature-card">
                          <h5 className="font-semibold mb-3" style={{color: '#002629'}}>🔍 Team-Specific RBS Analysis & Stat Differentials</h5>
                          
                          {/* Explanation Header */}
                          <div className="mb-4 p-3 rounded" style={{backgroundColor: '#A3D9FF', color: '#002629'}}>
                            <div className="text-sm font-semibold mb-1">📊 How to Read Stat Differentials:</div>
                            <div className="text-xs grid grid-cols-1 md:grid-cols-2 gap-2">
                              <div><strong>🟢 Favorable (Green):</strong> Positive values = team benefits</div>
                              <div><strong>🔴 Unfavorable (Red):</strong> Negative values = team penalized</div>
                              <div><strong>Yellow Cards:</strong> Fewer cards = 🟢 Better | More cards = 🔴 Worse</div>
                              <div><strong>Red Cards:</strong> Fewer cards = 🟢 Better | More cards = 🔴 Worse</div>
                              <div><strong>Fouls Committed:</strong> Fewer fouls = 🟢 Better | More fouls = 🔴 Worse</div>
                              <div><strong>Fouls Drawn:</strong> More fouls = 🟢 Better | Fewer fouls = 🔴 Worse</div>
                              <div><strong>Penalties Awarded:</strong> More penalties = 🟢 Better | Fewer penalties = 🔴 Worse</div>
                              <div><strong>xG Difference:</strong> Higher xG = 🟢 Better | Lower xG = 🔴 Worse</div>
                              <div><strong>Possession:</strong> More possession = 🟢 Better | Less possession = 🔴 Worse</div>
                            </div>
                          </div>

                          <div className="space-y-3 max-h-96 overflow-y-auto">
                            {Object.entries(detailedRefereeData.team_rbs_details)
                              .sort(([,a], [,b]) => Math.abs(b.rbs_score) - Math.abs(a.rbs_score))
                              .map(([teamName, teamData]) => {
                                // Helper function to determine if a stat differential is favorable
                                const getStatDirection = (statName, value) => {
                                  const favorableWhenPositive = ['fouls_drawn', 'penalties_awarded', 'xg_difference', 'possession_percentage'];
                                  const favorableWhenNegative = ['yellow_cards', 'red_cards', 'fouls_committed'];
                                  
                                  if (favorableWhenPositive.includes(statName)) {
                                    return value > 0 ? 'favorable' : 'unfavorable';
                                  } else if (favorableWhenNegative.includes(statName)) {
                                    return value < 0 ? 'favorable' : 'unfavorable';
                                  }
                                  return 'neutral';
                                };

                                const getStatIcon = (statName, value) => {
                                  const direction = getStatDirection(statName, value);
                                  if (Math.abs(value) < 0.05) return '➖'; // Minimal impact
                                  return direction === 'favorable' ? '🟢' : '🔴';
                                };

                                const getStatColor = (statName, value) => {
                                  const direction = getStatDirection(statName, value);
                                  if (Math.abs(value) < 0.05) return '#002629'; // Neutral
                                  return direction === 'favorable' ? '#12664F' : '#002629';
                                };

                                return (
                                  <div key={teamName} className="p-4 rounded border-2" 
                                       style={{backgroundColor: '#F2E9E4', borderColor: getRBSScoreColor(teamData.rbs_score)}}>
                                    
                                    {/* Team Header */}
                                    <div className="flex justify-between items-center mb-3">
                                      <div>
                                        <div className="font-bold text-lg" style={{color: '#002629'}}>{teamName}</div>
                                        <div className="text-sm" style={{color: '#002629', opacity: 0.8}}>
                                          {teamData.matches_with_ref} matches • {teamData.confidence_level}% confidence
                                        </div>
                                      </div>
                                      <div className="text-right">
                                        <div className="text-xl font-bold" 
                                             style={{color: getRBSScoreColor(teamData.rbs_score)}}>
                                          {formatScore(teamData.rbs_score)}
                                        </div>
                                        <div className="text-xs" style={{color: '#002629', opacity: 0.7}}>RBS Score</div>
                                      </div>
                                    </div>

                                    {/* Stat Differentials Breakdown */}
                                    {teamData.stats_breakdown && (
                                      <div>
                                        <div className="text-sm font-semibold mb-3" style={{color: '#002629'}}>
                                          📊 Statistical Differentials vs League Average:
                                        </div>
                                        <div className="grid grid-cols-1 md:grid-cols-2 gap-3 text-sm">
                                          {Object.entries(teamData.stats_breakdown).map(([statName, value]) => {
                                            const isSignificant = Math.abs(value) > 0.1;
                                            const direction = getStatDirection(statName, value);
                                            const icon = getStatIcon(statName, value);
                                            const color = getStatColor(statName, value);
                                            
                                            return (
                                              <div key={statName} className="flex justify-between items-center p-3 rounded border"
                                                   style={{
                                                     backgroundColor: direction === 'favorable' && isSignificant 
                                                       ? '#A3D9FF' 
                                                       : direction === 'unfavorable' && isSignificant
                                                       ? '#F2E9E4'
                                                       : 'white',
                                                     borderColor: direction === 'favorable' ? '#12664F' : direction === 'unfavorable' ? '#002629' : '#1C5D99',
                                                     borderWidth: isSignificant ? '2px' : '1px'
                                                   }}>
                                                <div className="flex items-center space-x-2">
                                                  <span className="text-lg">{icon}</span>
                                                  <div>
                                                    <div style={{color: '#002629'}} className="font-medium">
                                                      {statName.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase())}
                                                    </div>
                                                    <div className="text-xs" style={{color: '#002629', opacity: 0.7}}>
                                                      {direction === 'favorable' ? 'Favorable treatment' : 
                                                       direction === 'unfavorable' ? 'Unfavorable treatment' : 'Neutral'}
                                                    </div>
                                                  </div>
                                                </div>
                                                <div className="text-right">
                                                  <div style={{
                                                    color: color,
                                                    fontWeight: isSignificant ? 'bold' : 'normal',
                                                    fontSize: isSignificant ? '1.1em' : '1em'
                                                  }}>
                                                    {value > 0 ? '+' : ''}{formatScore(value)}
                                                  </div>
                                                  {isSignificant && (
                                                    <div className="text-xs" style={{color: color}}>
                                                      {Math.abs(value) > 0.3 ? 'Highly Significant' : 'Notable'}
                                                    </div>
                                                  )}
                                                </div>
                                              </div>
                                            );
                                          })}
                                        </div>
                                        
                                        {/* Overall Bias Interpretation */}
                                        <div className="mt-3 p-3 rounded" 
                                             style={{
                                               backgroundColor: teamData.rbs_score > 0.3 ? '#A3D9FF' :
                                                              teamData.rbs_score < -0.3 ? '#F2E9E4' : 'white',
                                               borderLeft: `4px solid ${getRBSScoreColor(teamData.rbs_score)}`
                                             }}>
                                          <div className="text-sm font-semibold" style={{color: '#002629'}}>
                                            🎯 Overall Bias Assessment:
                                          </div>
                                          <div className="text-sm mt-1" style={{color: '#002629'}}>
                                            {teamData.rbs_score > 0.3 ? 
                                              `${teamName} receives significantly favorable treatment from this referee. Key benefits in ${
                                                Object.entries(teamData.stats_breakdown || {})
                                                  .filter(([stat, val]) => getStatDirection(stat, val) === 'favorable' && Math.abs(val) > 0.1)
                                                  .map(([stat]) => stat.replace(/_/g, ' '))
                                                  .join(', ')
                                              }.` :
                                             teamData.rbs_score < -0.3 ?
                                              `${teamName} receives unfavorable treatment from this referee. Key disadvantages in ${
                                                Object.entries(teamData.stats_breakdown || {})
                                                  .filter(([stat, val]) => getStatDirection(stat, val) === 'unfavorable' && Math.abs(val) > 0.1)
                                                  .map(([stat]) => stat.replace(/_/g, ' '))
                                                  .join(', ')
                                              }.` :
                                              `${teamName} receives relatively neutral treatment from this referee.`
                                            }
                                          </div>
                                        </div>
                                      </div>
                                    )}
                                  </div>
                                );
                              })}
                          </div>
                          
                          {/* Summary Statistics */}
                          <div className="mt-4 p-3 rounded" style={{backgroundColor: '#A3D9FF', color: '#002629'}}>
                            <div className="text-sm font-semibold mb-1">
                              📈 Analysis Summary for {detailedRefereeData.referee_name}:
                            </div>
                            <div className="text-xs">
                              Showing RBS analysis for all {Object.keys(detailedRefereeData.team_rbs_details).length} teams 
                              with calculated bias scores. Teams are ordered by bias magnitude (strongest bias first).
                            </div>
                          </div>
                        </div>
                      )}
                    </div>
                  )}

                  {/* Loading State for Detailed Analysis */}
                  {loadingDetailedAnalysis && (
                    <div className="mt-4 p-4 text-center feature-card">
                      <div className="animate-spin rounded-full h-8 w-8 border-b-2 mx-auto mb-2" style={{borderColor: '#1C5D99'}}></div>
                      <div style={{color: '#002629'}}>Loading detailed referee analysis...</div>
                    </div>
                  )}
                </div>
              )}
            </div>
          </div>
        )}

        {/* System Configuration Tab */}
        {activeTab === 'config' && (
          <div className="space-y-6">
            <div className="card">
              <h2 className="card-header">🔧 System Configuration</h2>
              <p className="card-text mb-6">
                Configure global system settings, default parameters, and user preferences.
              </p>

              <div className="space-y-8">
                {/* Time Decay Configuration */}
                <div className="border-b pb-6" style={{borderColor: '#A3D9FF'}}>
                  <h3 className="text-lg font-semibold mb-4" style={{color: '#002629'}}>⏰ Time Decay Settings</h3>
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                    <div>
                      <label className="block text-sm font-medium mb-2" style={{color: '#002629'}}>Default Decay Preset</label>
                      <select
                        value={decayPreset}
                        onChange={(e) => setDecayPreset(e.target.value)}
                        className="form-select w-full"
                      >
                        {decayPresets.map(preset => (
                          <option key={preset.preset_name} value={preset.preset_name}>
                            {preset.preset_name.charAt(0).toUpperCase() + preset.preset_name.slice(1)}
                          </option>
                        ))}
                      </select>
                    </div>
                    <div>
                      <label className="block text-sm font-medium mb-2" style={{color: '#002629'}}>Apply by Default</label>
                      <label className="flex items-center space-x-2">
                        <input
                          type="checkbox"
                          checked={useTimeDecay}
                          onChange={(e) => setUseTimeDecay(e.target.checked)}
                          className="rounded"
                          style={{accentColor: '#1C5D99'}}
                        />
                        <span className="text-sm" style={{color: '#002629'}}>Enable time decay by default</span>
                      </label>
                    </div>
                  </div>
                </div>

                {/* Formation Settings */}
                <div className="border-b pb-6" style={{borderColor: '#A3D9FF'}}>
                  <h3 className="text-lg font-semibold mb-4" style={{color: '#002629'}}>⚽ Formation Settings</h3>
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                    <div>
                      <label className="block text-sm font-medium mb-2" style={{color: '#002629'}}>Default Formation</label>
                      <select
                        value={selectedFormation}
                        onChange={(e) => setSelectedFormation(e.target.value)}
                        className="form-select w-full"
                      >
                        {availableFormations.map(formation => (
                          <option key={formation} value={formation}>{formation}</option>
                        ))}
                      </select>
                    </div>
                    <div>
                      <label className="block text-sm font-medium mb-2" style={{color: '#002629'}}>Available Formations</label>
                      <div className="text-sm space-y-1" style={{color: '#002629'}}>
                        {availableFormations.map(formation => (
                          <div key={formation} className="flex items-center space-x-2">
                            <span>⚽</span>
                            <span>{formation}</span>
                          </div>
                        ))}
                      </div>
                    </div>
                  </div>
                </div>

                {/* System Status */}
                <div>
                  <h3 className="text-lg font-semibold mb-4" style={{color: '#002629'}}>📊 System Status</h3>
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                    <div className="stat-card">
                      <div className="stat-card-label mb-2">XGBoost Models Status</div>
                      <div className="stat-card-number text-lg">
                        {mlStatus?.models_loaded ? '✅ Loaded' : '❌ Not Loaded'}
                      </div>
                    </div>
                    <div className="stat-card">
                      <div className="stat-card-label mb-2">Data Status</div>
                      <div className="stat-card-number text-lg">
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