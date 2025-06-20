import React, { useState, useEffect } from 'react';
import axios from 'axios';
import Header from './components/Header';
import Navigation from './components/Navigation';
import Dashboard from './components/Dashboard';
import UploadData from './components/UploadData';
import StandardPredict from './components/StandardPredict';
import EnhancedXGBoost from './components/EnhancedXGBoost';
import EnsemblePredictions from './components/EnsemblePredictions';
import RegressionAnalysis from './components/RegressionAnalysis';
import PredictionConfig from './components/PredictionConfig';
import RBSConfig from './components/RBSConfig';
import FormulaOptimization from './components/FormulaOptimization';
import Results from './components/Results';
import SystemConfig from './components/SystemConfig';
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

  // Ensemble Prediction states  
  const [ensembleModelStatus, setEnsembleModelStatus] = useState(null);
  const [ensemblePredictionData, setEnsemblePredictionData] = useState(null);
  const [ensembleComparison, setEnsembleComparison] = useState(null);
  const [selectedEnsembleTeams, setSelectedEnsembleTeams] = useState({
    home: '',
    away: '',
    referee: ''
  });
  const [loadingEnsemblePrediction, setLoadingEnsemblePrediction] = useState(false);
  const [loadingEnsembleTraining, setLoadingEnsembleTraining] = useState(false);
  const [loadingComparison, setLoadingComparison] = useState(false);

  // Database management states
  const [wipingDatabase, setWipingDatabase] = useState(false);
  const [databaseStats, setDatabaseStats] = useState(null);

  // RBS Calculation states
  const [rbsStatus, setRbsStatus] = useState(null);
  const [calculatingRBS, setCalculatingRBS] = useState(false);
  const [rbsResults, setRbsResults] = useState(null);

  // Team Performance Analysis
  const [teamPerformanceData, setTeamPerformanceData] = useState(null);
  const [selectedTeamForAnalysis, setSelectedTeamForAnalysis] = useState('');
  const [loadingTeamPerformance, setLoadingTeamPerformance] = useState(false);

  // Model Performance Dashboard States
  const [modelPerformanceData, setModelPerformanceData] = useState(null);
  const [optimizationHistory, setOptimizationHistory] = useState(null);
  const [accuracyTrends, setAccuracyTrends] = useState(null);
  const [loadingModelPerformance, setLoadingModelPerformance] = useState(false);
  const [performanceDays, setPerformanceDays] = useState(30);

  // Regression Analysis states
  const [regressionData, setRegressionData] = useState(null);
  const [selectedVariables, setSelectedVariables] = useState([]);
  const [selectedTarget, setSelectedTarget] = useState('');
  const [loadingRegression, setLoadingRegression] = useState(false);

  // Configuration states
  const [predictionConfig, setPredictionConfig] = useState({...DEFAULT_PREDICTION_CONFIG});
  const [allPredictionConfigs, setAllPredictionConfigs] = useState([]);
  const [loadingConfigs, setLoadingConfigs] = useState(false);
  const [savingConfig, setSavingConfig] = useState(false);

  // RBS Configuration states
  const [rbsConfig, setRbsConfig] = useState({...DEFAULT_RBS_CONFIG});
  const [rbsConfigName, setRbsConfigName] = useState('');
  const [allRbsConfigs, setAllRbsConfigs] = useState([]);
  const [loadingRbsConfigs, setLoadingRbsConfigs] = useState(false);
  const [savingRbsConfig, setSavingRbsConfig] = useState(false);

  // Formula Optimization states
  const [optimizationResults, setOptimizationResults] = useState(null);
  const [loadingOptimization, setLoadingOptimization] = useState(false);
  const [selectedOptimizationType, setSelectedOptimizationType] = useState('');

  // Results states
  const [refereeAnalysis, setRefereeAnalysis] = useState(null);
  const [selectedRefereeForDetails, setSelectedRefereeForDetails] = useState(null);
  const [detailedRefereeAnalysis, setDetailedRefereeAnalysis] = useState(null);
  const [enhancedRefereeAnalysis, setEnhancedRefereeAnalysis] = useState(null);
  const [selectedTeamForRefereeAnalysis, setSelectedTeamForRefereeAnalysis] = useState('');
  const [loadingRefereeAnalysis, setLoadingRefereeAnalysis] = useState(false);
  const [loadingDetailedAnalysis, setLoadingDetailedAnalysis] = useState(false);
  const [loadingEnhancedAnalysis, setLoadingEnhancedAnalysis] = useState(false);

  // System Config states
  const [reloadingModels, setReloadingModels] = useState(false);
  const [systemStatus, setSystemStatus] = useState(null);
  const [loadingSystemStatus, setLoadingSystemStatus] = useState(false);
  const [defaultDecayPreset, setDefaultDecayPreset] = useState('moderate');
  const [defaultFormation, setDefaultFormation] = useState('4-4-2');

  // Config wrapper functions to provide API endpoint
  const handleSavePredictionConfig = async (configName, configData) => {
    // Create the correct config object with config_name
    const config = {
      config_name: configName,
      ...configData
    };
    return await savePredictionConfig(config, API);
  };

  const handleSaveRBSConfig = async (configName, configData) => {
    // Create the correct config object with config_name
    const config = {
      config_name: configName,
      ...configData
    };
    return await saveRBSConfig(config, API);
  };

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
        fetchAllPredictionConfigs(),
        fetchAllRBSConfigs()
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

  const fetchDatabaseStats = async () => {
    try {
      const response = await axios.get(`${API}/stats`);
      setDatabaseStats(response.data);
    } catch (error) {
      console.error('Error fetching database stats:', error);
    }
  };

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

  // Team Performance Analysis Functions
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

  // Ensemble Prediction Functions
  const getEnsembleModelStatus = async () => {
    try {
      const response = await axios.get(`${API}/ensemble-model-status`);
      return response.data;
    } catch (error) {
      console.error('Error getting ensemble model status:', error);
      throw error;
    }
  };

  const trainEnsembleModels = async () => {
    try {
      const response = await axios.post(`${API}/train-ensemble-models`);
      return response.data;
    } catch (error) {
      console.error('Error training ensemble models:', error);
      throw error;
    }
  };

  const makeEnsemblePrediction = async (homeTeam, awayTeam, referee) => {
    try {
      const requestData = {
        home_team: homeTeam,
        away_team: awayTeam,
        referee_name: referee,
        use_time_decay: useTimeDecay,
        decay_preset: decayPreset
      };
      const response = await axios.post(`${API}/predict-match-ensemble`, requestData);
      return response.data;
    } catch (error) {
      console.error('Error making ensemble prediction:', error);
      throw error;
    }
  };

  const comparePredictionMethods = async (homeTeam, awayTeam, referee) => {
    try {
      const requestData = {
        home_team: homeTeam,
        away_team: awayTeam,
        referee_name: referee,
        use_time_decay: useTimeDecay,
        decay_preset: decayPreset
      };
      const response = await axios.post(`${API}/compare-prediction-methods`, requestData);
      return response.data;
      return response.data;
    } catch (error) {
      console.error('Error comparing prediction methods:', error);
      throw error;
    }
  };

  // Regression Analysis Functions
  const runRegressionAnalysis = async (variables, target) => {
    try {
      const requestData = {
        variables: variables,
        target: target
      };
      const response = await axios.post(`${API}/regression-analysis`, requestData);
      return response.data;
    } catch (error) {
      console.error('Error running regression analysis:', error);
      throw error;
    }
  };

  // Configuration Functions
  const fetchAllPredictionConfigs = async () => {
    try {
      const response = await axios.get(`${API}/prediction-configs`);
      setAllPredictionConfigs(response.data.configs || []);
    } catch (error) {
      console.error('Error fetching prediction configs:', error);
    }
  };

  const loadPredictionConfig = async (configName) => {
    try {
      const response = await axios.get(`${API}/prediction-configs/${configName}`);
      return response.data.config;
    } catch (error) {
      console.error('Error loading prediction config:', error);
      throw error;
    }
  };

  const deletePredictionConfig = async (configName) => {
    try {
      await axios.delete(`${API}/prediction-configs/${configName}`);
    } catch (error) {
      console.error('Error deleting prediction config:', error);
      throw error;
    }
  };

  // RBS Configuration Functions
  const fetchAllRBSConfigs = async () => {
    try {
      const response = await axios.get(`${API}/rbs-configs`);
      setAllRbsConfigs(response.data.configs || []);
    } catch (error) {
      console.error('Error fetching RBS configs:', error);
    }
  };

  const loadRBSConfig = async (configName) => {
    try {
      const response = await axios.get(`${API}/rbs-configs/${configName}`);
      return response.data.config;
    } catch (error) {
      console.error('Error loading RBS config:', error);
      throw error;
    }
  };

  const deleteRBSConfig = async (configName) => {
    try {
      await axios.delete(`${API}/rbs-configs/${configName}`);
    } catch (error) {
      console.error('Error deleting RBS config:', error);
      throw error;
    }
  };

  // Optimization Functions
  const runRBSOptimizationAnalysis = async () => {
    try {
      const response = await axios.post(`${API}/analyze-rbs-optimization`);
      return response.data;
    } catch (error) {
      console.error('Error running RBS optimization:', error);
      throw error;
    }
  };

  const runPredictorAnalysis = async () => {
    try {
      const response = await axios.post(`${API}/predictor-analysis`);
      return response.data;
    } catch (error) {
      console.error('Error running predictor analysis:', error);
      throw error;
    }
  };

  const runXGBoostHyperparameterOptimization = async () => {
    try {
      const response = await axios.post(`${API}/xgboost-hyperparameter-optimization`);
      return response.data;
    } catch (error) {
      console.error('Error running XGBoost optimization:', error);
      throw error;
    }
  };

  // Results Functions
  const fetchRefereeAnalysis = async () => {
    try {
      const response = await axios.get(`${API}/referee-analysis`);
      return response.data;
    } catch (error) {
      console.error('Error fetching referee analysis:', error);
      throw error;
    }
  };

  const fetchDetailedRefereeAnalysis = async (refereeName) => {
    try {
      const response = await axios.get(`${API}/referee-analysis/${encodeURIComponent(refereeName)}`);
      return response.data;
    } catch (error) {
      console.error('Error fetching detailed referee analysis:', error);
      throw error;
    }
  };

  // System Config Functions
  const fetchSystemStatus = async () => {
    try {
      const response = await axios.get(`${API}/system-status`);
      return response.data;
    } catch (error) {
      console.error('Error fetching system status:', error);
      throw error;
    }
  };

  const saveSystemConfig = async (config) => {
    try {
      const response = await axios.post(`${API}/system-config`, config);
      return response.data;
    } catch (error) {
      console.error('Error saving system config:', error);
      throw error;
    }
  };

  // Model Performance API Functions
  const fetchModelPerformance = async (days = 30) => {
    try {
      const response = await axios.get(`${API}/model-performance/${days}`);
      return response.data;
    } catch (error) {
      console.error('Error fetching model performance:', error);
      return null;
    }
  };

  const fetchOptimizationHistory = async () => {
    try {
      const response = await axios.get(`${API}/optimization-history`);
      return response.data;
    } catch (error) {
      console.error('Error fetching optimization history:', error);
      return null;
    }
  };

  const fetchPredictionAccuracyTrends = async () => {
    try {
      const response = await axios.get(`${API}/prediction-accuracy-trends`);
      return response.data;
    } catch (error) {
      console.error('Error fetching prediction accuracy trends:', error);
      return null;
    }
  };

  // Render main content based on active tab
  const renderTabContent = () => {
    switch (activeTab) {
      case 'dashboard':
        return (
          <Dashboard
            teams={teams}
            referees={referees}
            stats={stats}
            mlStatus={mlStatus}
            rbsStatus={rbsStatus}
            databaseStats={databaseStats}
            teamPerformanceData={teamPerformanceData}
            selectedTeamForAnalysis={selectedTeamForAnalysis}
            setSelectedTeamForAnalysis={setSelectedTeamForAnalysis}
            loadingTeamPerformance={loadingTeamPerformance}
            fetchTeamPerformanceData={fetchTeamPerformanceData}
            modelPerformanceData={modelPerformanceData}
            optimizationHistory={optimizationHistory}
            accuracyTrends={accuracyTrends}
            loadingModelPerformance={loadingModelPerformance}
            setLoadingModelPerformance={setLoadingModelPerformance}
            performanceDays={performanceDays}
            setPerformanceDays={setPerformanceDays}
            fetchModelPerformance={fetchModelPerformance}
            fetchOptimizationHistory={fetchOptimizationHistory}
            fetchPredictionAccuracyTrends={fetchPredictionAccuracyTrends}
            setModelPerformanceData={setModelPerformanceData}
            setOptimizationHistory={setOptimizationHistory}
            setAccuracyTrends={setAccuracyTrends}
            checkMLStatus={checkMLStatus}
            checkRBSStatus={checkRBSStatus}
            calculateRBS={calculateRBS}
            calculatingRBS={calculatingRBS}
            fetchDatabaseStats={fetchDatabaseStats}
            wipeDatabase={wipeDatabase}
            wipingDatabase={wipingDatabase}
          />
        );
      case 'upload':
        return (
          <UploadData
            uploadStatus={uploadStatus}
            uploadingDataset={uploadingDataset}
            handleFileUpload={handleFileUpload}
            datasets={datasets}
          />
        );
      case 'predict':
        return (
          <StandardPredict
            teams={teams}
            referees={referees}
            configs={configs}
            predictionForm={predictionForm}
            setPredictionForm={setPredictionForm}
            configName={configName}
            setConfigName={setConfigName}
            predictionResult={predictionResult}
            predicting={predicting}
            predictMatch={predictMatch}
            resetPrediction={resetPrediction}
            exportPDF={exportPDF}
            exportingPDF={exportingPDF}
          />
        );
      case 'xgboost':
        return (
          <EnhancedXGBoost
            teams={teams}
            referees={referees}
            predictionForm={predictionForm}
            setPredictionForm={setPredictionForm}
            predictionResult={predictionResult}
            predicting={predicting}
            showStartingXI={showStartingXI}
            setShowStartingXI={setShowStartingXI}
            selectedFormation={selectedFormation}
            setSelectedFormation={setSelectedFormation}
            availableFormations={availableFormations}
            homeStartingXI={homeStartingXI}
            awayStartingXI={awayStartingXI}
            setHomeStartingXI={setHomeStartingXI}
            setAwayStartingXI={setAwayStartingXI}
            useTimeDecay={useTimeDecay}
            setUseTimeDecay={setUseTimeDecay}
            decayPreset={decayPreset}
            setDecayPreset={setDecayPreset}
            decayPresets={decayPresets}
            mlStatus={mlStatus}
            checkMLStatus={checkMLStatus}
            trainMLModels={trainMLModels}
            trainingModels={trainingModels}
            reloadMLModels={reloadMLModels}
            predictMatchEnhanced={predictMatchEnhanced}
            resetPrediction={resetPrediction}
            exportPDF={exportPDF}
            exportingPDF={exportingPDF}
            fetchTeamPlayers={fetchTeamPlayers}
            loadingPlayers={loadingPlayers}
            playerSearchTerms={playerSearchTerms}
            searchResults={searchResults}
            handlePlayerSearch={handlePlayerSearch}
            selectPlayerFromSearch={selectPlayerFromSearch}
            validateStartingXI={validateStartingXI}
            getButtonTooltip={getButtonTooltip}
            handleFormationChange={handleFormationChange}
          />
        );
      case 'ensemble':
        return (
          <EnsemblePredictions
            teams={teams}
            referees={referees}
            ensembleModelStatus={ensembleModelStatus}
            setEnsembleModelStatus={setEnsembleModelStatus}
            ensemblePredictionData={ensemblePredictionData}
            setEnsemblePredictionData={setEnsemblePredictionData}
            ensembleComparison={ensembleComparison}
            setEnsembleComparison={setEnsembleComparison}
            selectedEnsembleTeams={selectedEnsembleTeams}
            setSelectedEnsembleTeams={setSelectedEnsembleTeams}
            loadingEnsemblePrediction={loadingEnsemblePrediction}
            setLoadingEnsemblePrediction={setLoadingEnsemblePrediction}
            loadingEnsembleTraining={loadingEnsembleTraining}
            setLoadingEnsembleTraining={setLoadingEnsembleTraining}
            loadingComparison={loadingComparison}
            setLoadingComparison={setLoadingComparison}
            useTimeDecay={useTimeDecay}
            setUseTimeDecay={setUseTimeDecay}
            decayPreset={decayPreset}
            setDecayPreset={setDecayPreset}
            decayPresets={decayPresets}
            getEnsembleModelStatus={getEnsembleModelStatus}
            trainEnsembleModels={trainEnsembleModels}
            makeEnsemblePrediction={makeEnsemblePrediction}
            comparePredictionMethods={comparePredictionMethods}
          />
        );
      case 'regression':
        return (
          <RegressionAnalysis
            regressionData={regressionData}
            setRegressionData={setRegressionData}
            selectedVariables={selectedVariables}
            setSelectedVariables={setSelectedVariables}
            selectedTarget={selectedTarget}
            setSelectedTarget={setSelectedTarget}
            loadingRegression={loadingRegression}
            setLoadingRegression={setLoadingRegression}
            runRegressionAnalysis={runRegressionAnalysis}
          />
        );
      case 'prediction-config':
        return (
          <PredictionConfig
            predictionConfig={predictionConfig}
            setPredictionConfig={setPredictionConfig}
            configName={configName}
            setConfigName={setConfigName}
            allPredictionConfigs={allPredictionConfigs}
            setAllPredictionConfigs={setAllPredictionConfigs}
            loadingConfigs={loadingConfigs}
            setLoadingConfigs={setLoadingConfigs}
            savingConfig={savingConfig}
            setSavingConfig={setSavingConfig}
            savePredictionConfig={handleSavePredictionConfig}
            loadPredictionConfig={loadPredictionConfig}
            deletePredictionConfig={deletePredictionConfig}
            fetchAllPredictionConfigs={fetchAllPredictionConfigs}
          />
        );
      case 'rbs-config':
        return (
          <RBSConfig
            rbsConfig={rbsConfig}
            setRbsConfig={setRbsConfig}
            rbsConfigName={rbsConfigName}
            setRbsConfigName={setRbsConfigName}
            allRbsConfigs={allRbsConfigs}
            setAllRbsConfigs={setAllRbsConfigs}
            loadingRbsConfigs={loadingRbsConfigs}
            setLoadingRbsConfigs={setLoadingRbsConfigs}
            savingRbsConfig={savingRbsConfig}
            setSavingRbsConfig={setSavingRbsConfig}
            saveRBSConfig={handleSaveRBSConfig}
            loadRBSConfig={loadRBSConfig}
            deleteRBSConfig={deleteRBSConfig}
            fetchAllRBSConfigs={fetchAllRBSConfigs}
          />
        );
      case 'optimization':
        return (
          <FormulaOptimization
            optimizationResults={optimizationResults}
            setOptimizationResults={setOptimizationResults}
            loadingOptimization={loadingOptimization}
            setLoadingOptimization={setLoadingOptimization}
            optimizationHistory={optimizationHistory}
            setOptimizationHistory={setOptimizationHistory}
            selectedOptimizationType={selectedOptimizationType}
            setSelectedOptimizationType={setSelectedOptimizationType}
            runAdvancedOptimization={runAdvancedOptimization}
            runRBSOptimizationAnalysis={runRBSOptimizationAnalysis}
            runPredictorAnalysis={runPredictorAnalysis}
            runXGBoostHyperparameterOptimization={runXGBoostHyperparameterOptimization}
            fetchOptimizationHistory={fetchOptimizationHistory}
          />
        );
      case 'results':
        return (
          <Results
            refereeAnalysis={refereeAnalysis}
            setRefereeAnalysis={setRefereeAnalysis}
            selectedRefereeForDetails={selectedRefereeForDetails}
            setSelectedRefereeForDetails={setSelectedRefereeForDetails}
            detailedRefereeAnalysis={detailedRefereeAnalysis}
            setDetailedRefereeAnalysis={setDetailedRefereeAnalysis}
            enhancedRefereeAnalysis={enhancedRefereeAnalysis}
            setEnhancedRefereeAnalysis={setEnhancedRefereeAnalysis}
            selectedTeamForRefereeAnalysis={selectedTeamForRefereeAnalysis}
            setSelectedTeamForRefereeAnalysis={setSelectedTeamForRefereeAnalysis}
            loadingRefereeAnalysis={loadingRefereeAnalysis}
            setLoadingRefereeAnalysis={setLoadingRefereeAnalysis}
            loadingDetailedAnalysis={loadingDetailedAnalysis}
            setLoadingDetailedAnalysis={setLoadingDetailedAnalysis}
            loadingEnhancedAnalysis={loadingEnhancedAnalysis}
            setLoadingEnhancedAnalysis={setLoadingEnhancedAnalysis}
            teams={teams}
            referees={referees}
            fetchRefereeAnalysis={fetchRefereeAnalysis}
            fetchDetailedRefereeAnalysis={fetchDetailedRefereeAnalysis}
            fetchEnhancedRBSAnalysis={fetchEnhancedRBSAnalysis}
            defaultDecayPreset={defaultDecayPreset}
            setDefaultDecayPreset={setDefaultDecayPreset}
            decayPresets={decayPresets}
            saveSystemConfig={saveSystemConfig}
          />
        );
      case 'config':
        return (
          <SystemConfig
            mlStatus={mlStatus}
            ensembleModelStatus={ensembleModelStatus}
            trainingModels={trainingModels}
            setTrainingModels={setTrainingModels}
            trainingResults={trainingResults}
            setTrainingResults={setTrainingResults}
            reloadingModels={reloadingModels}
            setReloadingModels={setReloadingModels}
            checkMLStatus={checkMLStatus}
            trainMLModels={trainMLModels}
            reloadMLModels={reloadMLModels}
            trainEnsembleModels={trainEnsembleModels}
            getEnsembleModelStatus={getEnsembleModelStatus}
            systemStatus={systemStatus}
            setSystemStatus={setSystemStatus}
            fetchSystemStatus={fetchSystemStatus}
            defaultDecayPreset={defaultDecayPreset}
            setDefaultDecayPreset={setDefaultDecayPreset}
            defaultFormation={defaultFormation}
            setDefaultFormation={setDefaultFormation}
            decayPresets={decayPresets}
            availableFormations={availableFormations}
            saveSystemConfig={saveSystemConfig}
            loadingSystemStatus={loadingSystemStatus}
            setLoadingSystemStatus={setLoadingSystemStatus}
          />
        );
      default:
        return (
          <div className="space-y-6">
            <div className="bg-white p-6 rounded-lg shadow-lg border border-gray-200">
              <h2 className="text-xl font-bold mb-4" style={{color: '#002629'}}>🚧 Coming Soon</h2>
              <p style={{color: '#002629', opacity: 0.8}}>
                This tab is being rebuilt with improved modular components. More functionality will be available soon!
              </p>
            </div>
          </div>
        );
    }
  };

  return (
    <div className="min-h-screen" style={{backgroundColor: '#F2E9E4'}}>
      <Header />
      <Navigation activeTab={activeTab} setActiveTab={setActiveTab} />
      
      {/* Main Content */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {renderTabContent()}
      </div>
    </div>
  );
}

export default App;