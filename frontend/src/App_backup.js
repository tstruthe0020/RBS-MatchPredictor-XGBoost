import React, { useState, useEffect } from 'react';
import './App.css';
import axios from 'axios';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

function App() {
  const [activeTab, setActiveTab] = useState('dashboard');
  const [stats, setStats] = useState({});
  const [rbsResults, setRbsResults] = useState([]);
  const [teams, setTeams] = useState([]);
  const [referees, setReferees] = useState([]);
  const [selectedTeam, setSelectedTeam] = useState('');
  const [selectedReferee, setSelectedReferee] = useState('');
  const [uploading, setUploading] = useState(false);
  const [calculating, setCalculating] = useState(false);
  const [uploadMessages, setUploadMessages] = useState({});
  
  // Multi-dataset upload state
  const [datasets, setDatasets] = useState([]);
  const [multiDatasetFiles, setMultiDatasetFiles] = useState([]);
  const [uploadingMultiDataset, setUploadingMultiDataset] = useState(false);
  const [multiDatasetResults, setMultiDatasetResults] = useState(null);
  
  // Formula optimization state
  const [optimizationResults, setOptimizationResults] = useState({
    rbs: null,
    predictor: null
  });
  const [analyzingFormulas, setAnalyzingFormulas] = useState(false);
  const [applyingWeights, setApplyingWeights] = useState(false);
  
  // New state for referee-based navigation
  const [refereeSummary, setRefereeSummary] = useState([]);
  const [selectedRefereeDetails, setSelectedRefereeDetails] = useState(null);
  const [enhancedRBSData, setEnhancedRBSData] = useState({});
  const [viewingReferee, setViewingReferee] = useState(null);

  // Match prediction state
  const [predictionForm, setPredictionForm] = useState({
    home_team: '',
    away_team: '',
    referee_name: '',
    match_date: ''
  });
  const [predictionResult, setPredictionResult] = useState(null);
  const [predicting, setPredicting] = useState(false);

  // ML Training state
  const [mlStatus, setMlStatus] = useState(null);
  const [trainingModels, setTrainingModels] = useState(false);
  const [trainingResults, setTrainingResults] = useState(null);

  // PDF Export state
  const [exportingPDF, setExportingPDF] = useState(false);

  // Configuration state
  const [configName, setConfigName] = useState('default');
  const [configs, setConfigs] = useState([]);
  const [currentConfig, setCurrentConfig] = useState(null);
  const [configEditing, setConfigEditing] = useState(false);
  const [configForm, setConfigForm] = useState({
    config_name: 'default',
    xg_shot_based_weight: 0.4,
    xg_historical_weight: 0.4,
    xg_opponent_defense_weight: 0.2,
    ppg_adjustment_factor: 0.15,
    possession_adjustment_per_percent: 0.01,
    fouls_drawn_factor: 0.02,
    fouls_drawn_baseline: 10.0,
    fouls_drawn_min_multiplier: 0.8,
    fouls_drawn_max_multiplier: 1.3,
    penalty_xg_value: 0.79,
    rbs_scaling_factor: 0.2,
    min_conversion_rate: 0.5,
    max_conversion_rate: 2.0,
    min_xg_per_match: 0.1,
    confidence_matches_multiplier: 4,
    max_confidence: 90,
    min_confidence: 20
  });

  // RBS Configuration state
  const [rbsConfigName, setRbsConfigName] = useState('default');
  const [rbsConfigs, setRbsConfigs] = useState([]);
  const [currentRbsConfig, setCurrentRbsConfig] = useState(null);
  const [rbsConfigEditing, setRbsConfigEditing] = useState(false);
  const [rbsConfigForm, setRbsConfigForm] = useState({
    config_name: 'default',
    yellow_cards_weight: 0.3,
    red_cards_weight: 0.5,
    fouls_committed_weight: 0.1,
    fouls_drawn_weight: 0.1,
    penalties_awarded_weight: 0.5,
    xg_difference_weight: 0.4,
    possession_percentage_weight: 0.2,
    confidence_matches_multiplier: 4,
    max_confidence: 95,
    min_confidence: 10,
    confidence_threshold_low: 2,
    confidence_threshold_medium: 5,
    confidence_threshold_high: 10
  });

  // Regression Analysis state
  const [availableStats, setAvailableStats] = useState([]);
  const [statDescriptions, setStatDescriptions] = useState({});
  const [statCategories, setStatCategories] = useState({});
  const [selectedStats, setSelectedStats] = useState([]);
  const [regressionTarget, setRegressionTarget] = useState('points_per_game');
  const [regressionResult, setRegressionResult] = useState(null);
  const [analyzing, setAnalyzing] = useState(false);

  // Starting XI and Enhanced Prediction state
  const [showStartingXI, setShowStartingXI] = useState(false);
  const [availableFormations, setAvailableFormations] = useState(['4-4-2', '4-3-3', '3-5-2', '4-5-1', '3-4-3']);
  const [homeTeamPlayers, setHomeTeamPlayers] = useState([]);
  const [awayTeamPlayers, setAwayTeamPlayers] = useState([]);
  const [homeStartingXI, setHomeStartingXI] = useState(null);
  const [awayStartingXI, setAwayStartingXI] = useState(null);
  const [selectedFormation, setSelectedFormation] = useState('4-4-2');
  const [useTimeDecay, setUseTimeDecay] = useState(true);
  const [decayPreset, setDecayPreset] = useState('moderate');
  const [decayPresets, setDecayPresets] = useState([]);
  const [loadingPlayers, setLoadingPlayers] = useState(false);

  // Fetch initial data
  useEffect(() => {
    fetchStats();
    fetchTeams();
    fetchReferees();
    fetchConfigs();
    fetchRbsConfigs();
    fetchDatasets();
    checkMLStatus(); // Load ML status on page load
    fetchFormations(); // Load available formations
    fetchDecayPresets(); // Load time decay presets
  }, []);

  const fetchStats = async () => {
    try {
      const response = await axios.get(`${API}/stats`);
      setStats(response.data);
    } catch (error) {
      console.error('Error fetching stats:', error);
    }
  };

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

  const fetchRefereeSummary = async () => {
    try {
      console.log('Fetching referee summary...');
      const response = await axios.get(`${API}/referee-summary`);
      console.log('Referee summary response:', response.data);
      setRefereeSummary(response.data.referees || []);
    } catch (error) {
      console.error('Error fetching referee summary:', error);
    }
  };

  const loadEnhancedRBSData = async (refereeName, rbsResults) => {
    try {
      console.log('Loading enhanced RBS data for referee:', refereeName);
      const enhancedData = {};
      
      // Show loading state
      const loadingData = {};
      rbsResults.forEach(result => {
        loadingData[result.team_name] = { loading: true };
      });
      setEnhancedRBSData(loadingData);
      
      // For each team in the RBS results, fetch enhanced analysis
      for (const result of rbsResults) {
        try {
          const response = await axios.get(`${API}/enhanced-rbs-analysis/${encodeURIComponent(result.team_name)}/${encodeURIComponent(refereeName)}`);
          if (response.data.success) {
            enhancedData[result.team_name] = response.data;
          } else {
            enhancedData[result.team_name] = { error: 'No data available' };
          }
        } catch (error) {
          console.error(`Error loading enhanced data for ${result.team_name}:`, error);
          enhancedData[result.team_name] = { error: 'Failed to load' };
          // Continue with other teams even if one fails
        }
      }
      
      setEnhancedRBSData(enhancedData);
      console.log('Enhanced RBS data loaded:', enhancedData);
    } catch (error) {
      console.error('Error loading enhanced RBS data:', error);
    }
  };

  const fetchRefereeDetails = async (refereeName) => {
    try {
      console.log('Fetching referee details for:', refereeName);
      const response = await axios.get(`${API}/referee/${encodeURIComponent(refereeName)}`);
      console.log('Referee details response:', response.data);
      setSelectedRefereeDetails(response.data);
      setViewingReferee(refereeName);
      
      // Load enhanced RBS data for all teams
      if (response.data.rbs_results) {
        await loadEnhancedRBSData(refereeName, response.data.rbs_results);
      }
    } catch (error) {
      console.error('Error fetching referee details:', error);
      alert(`Error loading referee details: ${error.response?.data?.detail || error.message}`);
    }
  };

  const goBackToRefereeList = () => {
    setViewingReferee(null);
    setSelectedRefereeDetails(null);
  };

  const handleFileUpload = async (event, endpoint, type) => {
    const file = event.target.files[0];
    if (!file) return;

    setUploading(true);
    const formData = new FormData();
    formData.append('file', file);

    try {
      const response = await axios.post(`${API}/upload/${endpoint}`, formData, {
        headers: { 'Content-Type': 'multipart/form-data' }
      });
      
      setUploadMessages(prev => ({
        ...prev,
        [type]: `✅ ${response.data.message}`
      }));
      
      fetchStats();
    } catch (error) {
      setUploadMessages(prev => ({
        ...prev,
        [type]: `❌ Error: ${error.response?.data?.detail || error.message}`
      }));
    }
    
    setUploading(false);
  };

  const calculateRBS = async () => {
    setCalculating(true);
    try {
      const response = await axios.post(`${API}/calculate-rbs`);
      alert(`✅ ${response.data.message}`);
      fetchStats();
      fetchRefereeSummary();
    } catch (error) {
      alert(`❌ Error calculating RBS: ${error.response?.data?.detail || error.message}`);
    }
    setCalculating(false);
  };

  // Multi-dataset functions
  const fetchDatasets = async () => {
    try {
      const response = await axios.get(`${API}/datasets`);
      setDatasets(response.data.datasets || []);
    } catch (error) {
      console.error('Error fetching datasets:', error);
    }
  };

  const deleteDataset = async (datasetName) => {
    if (!window.confirm(`Are you sure you want to delete dataset "${datasetName}"? This action cannot be undone.`)) {
      return;
    }
    
    try {
      const response = await axios.delete(`${API}/datasets/${datasetName}`);
      alert(`✅ ${response.data.message}`);
      fetchDatasets();
      fetchStats();
      fetchRefereeSummary();
    } catch (error) {
      alert(`❌ Error deleting dataset: ${error.response?.data?.detail || error.message}`);
    }
  };

  const addDatasetUpload = () => {
    setMultiDatasetFiles([...multiDatasetFiles, {
      id: Date.now(),
      dataset_name: '',
      matches_file: null,
      team_stats_file: null,
      player_stats_file: null
    }]);
  };

  const removeDatasetUpload = (id) => {
    setMultiDatasetFiles(multiDatasetFiles.filter(dataset => dataset.id !== id));
  };

  const updateDatasetField = (id, field, value) => {
    setMultiDatasetFiles(multiDatasetFiles.map(dataset => 
      dataset.id === id ? { ...dataset, [field]: value } : dataset
    ));
  };

  const uploadMultiDataset = async () => {
    if (multiDatasetFiles.length === 0) {
      alert('Please add at least one dataset to upload');
      return;
    }

    // Validation
    for (const dataset of multiDatasetFiles) {
      if (!dataset.dataset_name) {
        alert('Please provide a name for all datasets');
        return;
      }
      if (!dataset.matches_file || !dataset.team_stats_file || !dataset.player_stats_file) {
        alert(`Please upload all 3 files for dataset "${dataset.dataset_name}"`);
        return;
      }
    }

    // Check for duplicate names
    const names = multiDatasetFiles.map(d => d.dataset_name);
    if (new Set(names).size !== names.length) {
      alert('Dataset names must be unique');
      return;
    }

    setUploadingMultiDataset(true);
    try {
      const formData = new FormData();
      
      // Add dataset names as form data
      const datasetNames = [];
      for (const dataset of multiDatasetFiles) {
        datasetNames.push(dataset.dataset_name);
        formData.append('files', dataset.matches_file);
        formData.append('files', dataset.team_stats_file);
        formData.append('files', dataset.player_stats_file);
      }
      
      // Add dataset names as JSON string
      for (const name of datasetNames) {
        formData.append('dataset_names', name);
      }

      const response = await axios.post(`${API}/upload/multi-dataset`, formData, {
        headers: { 'Content-Type': 'multipart/form-data' }
      });
      
      setMultiDatasetResults(response.data);
      setMultiDatasetFiles([]);
      fetchDatasets();
      fetchStats();
      fetchRefereeSummary();
    } catch (error) {
      alert(`❌ Error uploading datasets: ${error.response?.data?.detail || error.message}`);
    }
    setUploadingMultiDataset(false);
  };

  // Formula optimization functions
  const analyzeRBSOptimization = async () => {
    setAnalyzingFormulas(true);
    try {
      const response = await axios.post(`${API}/analyze-rbs-optimization`);
      setOptimizationResults(prev => ({
        ...prev,
        rbs: response.data
      }));
    } catch (error) {
      alert(`❌ Error analyzing RBS formula: ${error.response?.data?.detail || error.message}`);
    }
    setAnalyzingFormulas(false);
  };

  const analyzePredictorOptimization = async () => {
    setAnalyzingFormulas(true);
    try {
      const response = await axios.post(`${API}/analyze-predictor-optimization`);
      setOptimizationResults(prev => ({
        ...prev,
        predictor: response.data
      }));
    } catch (error) {
      alert(`❌ Error analyzing Match Predictor formula: ${error.response?.data?.detail || error.message}`);
    }
    setAnalyzingFormulas(false);
  };

  const applyRBSWeights = async (suggestedWeights) => {
    if (!window.confirm('Apply the suggested RBS weights? This will create a new RBS configuration.')) {
      return;
    }

    setApplyingWeights(true);
    try {
      const now = new Date();
      const timestamp = now.toISOString().replace(/[:.]/g, '-').slice(0, 19); // Format: 2024-06-05T14-30-45
      const configName = `rbs_optimized_${timestamp}`;
      
      const configData = {
        config_name: configName,
        yellow_cards_weight: suggestedWeights.yellow_cards || 0.3,
        red_cards_weight: suggestedWeights.red_cards || 0.5,
        fouls_committed_weight: suggestedWeights.fouls_committed || 0.1,
        fouls_drawn_weight: suggestedWeights.fouls_drawn || 0.1,
        penalties_awarded_weight: suggestedWeights.penalties_awarded || 0.5,
        xg_difference_weight: suggestedWeights.xg_difference || 0.4,
        possession_percentage_weight: suggestedWeights.possession_percentage || 0.2
      };

      const response = await axios.post(`${API}/rbs-configs`, configData);
      alert(`✅ RBS configuration "${configName}" created successfully!`);
      fetchRbsConfigs();
    } catch (error) {
      alert(`❌ Error applying RBS weights: ${error.response?.data?.detail || error.message}`);
    }
    setApplyingWeights(false);
  };

  const applyPredictorWeights = async (analysisResults) => {
    if (!window.confirm('Apply optimized Match Predictor weights? This will create a new prediction configuration.')) {
      return;
    }

    setApplyingWeights(true);
    try {
      const now = new Date();
      const timestamp = now.toISOString().replace(/[:.]/g, '-').slice(0, 19); // Format: 2024-06-05T14-30-45
      const configName = `predictor_optimized_${timestamp}`;
      
      // Extract insights from predictor analysis to suggest configuration
      const predictorAnalysis = analysisResults.results.predictor_vs_points;
      let configData = {
        config_name: configName,
        // Default values that can be adjusted based on analysis
        xg_shot_based_weight: 0.4,
        xg_historical_weight: 0.4,
        xg_opponent_defense_weight: 0.2,
        ppg_adjustment_factor: 0.15,
        possession_adjustment_per_percent: 0.01,
        fouls_drawn_factor: 0.02,
        penalty_xg_value: 0.79,
        rbs_scaling_factor: 0.2
      };

      // Adjust weights based on variable importance if available
      if (predictorAnalysis.success && predictorAnalysis.results.coefficients) {
        const coeffs = predictorAnalysis.results.coefficients;
        
        // Adjust possession factor based on its coefficient
        if (coeffs.possession_percentage) {
          configData.possession_adjustment_per_percent = Math.max(0.005, Math.min(0.02, Math.abs(coeffs.possession_percentage) * 0.01));
        }
        
        // Adjust RBS scaling based on its importance
        if (coeffs.rbs_score) {
          configData.rbs_scaling_factor = Math.max(0.1, Math.min(0.3, Math.abs(coeffs.rbs_score) * 0.2));
        }
        
        // Adjust fouls drawn factor
        if (coeffs.fouls_drawn) {
          configData.fouls_drawn_factor = Math.max(0.01, Math.min(0.05, Math.abs(coeffs.fouls_drawn) * 0.02));
        }
      }

      const response = await axios.post(`${API}/prediction-configs`, configData);
      alert(`✅ Prediction configuration "${configName}" created successfully!`);
      fetchConfigs();
    } catch (error) {
      alert(`❌ Error applying Predictor weights: ${error.response?.data?.detail || error.message}`);
    }
    setApplyingWeights(false);
  };

  const getRBSColor = (score) => {
    if (score > 0.1) return 'text-green-600 bg-green-50';
    if (score < -0.1) return 'text-red-600 bg-red-50';
    return 'text-gray-600 bg-gray-50';
  };

  const getRBSInterpretation = (score) => {
    if (score > 0.2) return 'Strongly Favorable';
    if (score > 0.1) return 'Moderately Favorable';
    if (score < -0.2) return 'Strongly Unfavorable';
    if (score < -0.1) return 'Moderately Unfavorable';
    return 'Neutral';
  };

  const getConfidenceColor = (confidence) => {
    if (confidence >= 70) return 'bg-green-100 text-green-800';
    if (confidence >= 50) return 'bg-yellow-100 text-yellow-800';
    if (confidence >= 30) return 'bg-orange-100 text-orange-800';
    return 'bg-red-100 text-red-800';
  };

  // Match prediction functions
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

  // Enhanced prediction with Starting XI support
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

  // Fetch team players and generate default starting XI
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

  // Fetch available formations
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

  // Fetch time decay presets
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

  // Handle formation change
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

  // Update starting XI player selection
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

  // Validate starting XI (ensure 11 players selected)
  const validateStartingXI = (startingXI) => {
    if (!startingXI || !startingXI.positions) return false;
    return startingXI.positions.filter(pos => pos.player).length === 11;
  };

  // This function has been commented out to avoid duplication
  /* const predictMatchEnhanced = async () => {
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
      }; */
      
  // Fetch team players and generate default starting XI - commented out to avoid duplication
  /* const fetchTeamPlayers = async (teamName, isHomeTeam = true) => {
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
  }; */

  // Fetch available formations - commented out to avoid duplication
  /* const fetchFormations = async () => {
    try {
      const response = await axios.get(`${API}/formations`);
      if (response.data.success) {
        setAvailableFormations(response.data.formations.map(f => f.name));
      }
    } catch (error) {
      console.error('Error fetching formations:', error);
    }
  }; */

  // Fetch time decay presets - commented out to avoid duplication
  /* const fetchDecayPresets = async () => {
    try {
      const response = await axios.get(`${API}/time-decay/presets`);
      if (response.data.success) {
        setDecayPresets(response.data.presets);
      }
    } catch (error) {
      console.error('Error fetching decay presets:', error);
    }
  }; */

  // Handle formation change - commented out to avoid duplication
  /* const handleFormationChange = async (newFormation) => {
    setSelectedFormation(newFormation);
    
    // Regenerate starting XIs for both teams with new formation
    if (predictionForm.home_team) {
      await fetchTeamPlayers(predictionForm.home_team, true);
    }
    if (predictionForm.away_team) {
      await fetchTeamPlayers(predictionForm.away_team, false);
    }
  }; */

  // Update starting XI player selection - commented out to avoid duplication
  /* const updateStartingXIPlayer = (isHomeTeam, positionId, selectedPlayer) => {
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
  }; */

  // Validate starting XI (ensure 11 players selected) - commented out to avoid duplication
  /* const validateStartingXI = (startingXI) => {
    if (!startingXI || !startingXI.positions) return false;
    return startingXI.positions.filter(pos => pos.player).length === 11;
  }; */

  const resetPrediction = () => {
    setPredictionForm({
      home_team: '',
      away_team: '',
      referee_name: '',
      match_date: ''
    });
    setPredictionResult(null);
  };

  // ML Training functions
  const checkMLStatus = async () => {
    try {
      const response = await axios.get(`${API}/ml-models/status`);
      setMlStatus(response.data);
    } catch (error) {
      console.error('Error checking ML status:', error);
    }
  };

  const trainMLModels = async () => {
    if (!window.confirm('Train ML models? This will take several minutes and use all available match data.')) {
      return;
    }

    setTrainingModels(true);
    setTrainingResults(null);
    try {
      const response = await axios.post(`${API}/train-ml-models`);
      setTrainingResults(response.data);
      // Refresh ML status after training
      await checkMLStatus();
      alert('✅ ML models trained successfully!');
    } catch (error) {
      alert(`❌ Training Error: ${error.response?.data?.detail || error.message}`);
    }
    setTrainingModels(false);
  };

  const reloadMLModels = async () => {
    try {
      const response = await axios.post(`${API}/ml-models/reload`);
      await checkMLStatus();
      alert('✅ ML models reloaded successfully!');
    } catch (error) {
      alert(`❌ Reload Error: ${error.response?.data?.detail || error.message}`);
    }
  };

  // PDF Export function
  const exportPredictionPDF = async () => {
    if (!predictionResult) {
      alert('No prediction data available to export');
      return;
    }

    setExportingPDF(true);
    try {
      const exportData = {
        home_team: predictionResult.home_team,
        away_team: predictionResult.away_team,
        referee_name: predictionResult.referee,
        match_date: predictionForm.match_date || null,
        config_name: configName
      };

      const response = await axios.post(`${API}/export-prediction-pdf`, exportData, {
        responseType: 'blob',
        headers: {
          'Content-Type': 'application/json'
        }
      });

      // Create download link
      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement('a');
      link.href = url;
      
      // Generate filename with teams and date
      const date = new Date().toISOString().split('T')[0];
      const filename = `${predictionResult.home_team}_vs_${predictionResult.away_team}_prediction_${date}.pdf`;
      link.setAttribute('download', filename);
      
      // Trigger download
      document.body.appendChild(link);
      link.click();
      link.remove();
      window.URL.revokeObjectURL(url);

      alert('✅ PDF exported successfully!');
    } catch (error) {
      console.error('PDF Export Error:', error);
      alert(`❌ PDF Export Error: ${error.response?.data?.detail || error.message}`);
    }
    setExportingPDF(false);
  };

  // Database management functions
  const wipeDatabase = async () => {
    const confirmText = "WIPE DATABASE";
    const userInput = prompt(
      `⚠️ DANGER: This will permanently delete ALL data!\n\n` +
      `This includes:\n` +
      `- All match data\n` +
      `- All team statistics\n` +
      `- All player statistics\n` +
      `- All RBS results\n` +
      `- All configuration settings\n\n` +
      `Type "${confirmText}" to confirm:`
    );

    if (userInput !== confirmText) {
      alert('❌ Operation cancelled. Database not wiped.');
      return;
    }

    try {
      const response = await axios.delete(`${API}/database/wipe`);
      
      // Reset all frontend state
      setStats({ matches: 0, team_stats: 0, player_stats: 0, rbs_results: 0 });
      setTeams([]);
      setReferees([]);
      setConfigs([]);
      setRbsConfigs([]);
      setDatasets([]);
      setPredictionResult(null);
      setRbsResults([]);
      setOptimizationResults([]);
      setTrainingResults(null);
      setMlStatus(null);
      
      alert(`✅ Database wiped successfully!\n\nDeleted:\n${JSON.stringify(response.data.deleted_counts, null, 2)}`);
      
      // Refresh stats
      fetchStats();
    } catch (error) {
      alert(`❌ Wipe Error: ${error.response?.data?.detail || error.message}`);
    }
  };

  // Configuration functions
  const fetchConfigs = async () => {
    try {
      const response = await axios.get(`${API}/prediction-configs`);
      setConfigs(response.data.configs);
    } catch (error) {
      console.error('Error fetching configs:', error);
    }
  };

  const fetchConfig = async (name) => {
    try {
      const response = await axios.get(`${API}/prediction-config/${name}`);
      setCurrentConfig(response.data.config);
      setConfigForm(response.data.config);
    } catch (error) {
      console.error('Error fetching config:', error);
    }
  };

  const saveConfig = async () => {
    try {
      const response = await axios.post(`${API}/prediction-config`, configForm);
      alert('✅ Configuration saved successfully!');
      await fetchConfigs();
      setConfigEditing(false);
    } catch (error) {
      alert(`❌ Error saving configuration: ${error.response?.data?.detail || error.message}`);
    }
  };

  const handleConfigFormChange = (field, value) => {
    setConfigForm(prev => ({
      ...prev,
      [field]: parseFloat(value) || value
    }));
  };

  const resetConfigForm = () => {
    setConfigForm({
      config_name: 'custom',
      xg_shot_based_weight: 0.4,
      xg_historical_weight: 0.4,
      xg_opponent_defense_weight: 0.2,
      ppg_adjustment_factor: 0.15,
      possession_adjustment_per_percent: 0.01,
      fouls_drawn_factor: 0.02,
      fouls_drawn_baseline: 10.0,
      fouls_drawn_min_multiplier: 0.8,
      fouls_drawn_max_multiplier: 1.3,
      penalty_xg_value: 0.79,
      rbs_scaling_factor: 0.2,
      min_conversion_rate: 0.5,
      max_conversion_rate: 2.0,
      min_xg_per_match: 0.1,
      confidence_matches_multiplier: 4,
      max_confidence: 90,
      min_confidence: 20
    });
  };

  // RBS Configuration functions
  const fetchRbsConfigs = async () => {
    try {
      const response = await axios.get(`${API}/rbs-configs`);
      setRbsConfigs(response.data.configs);
    } catch (error) {
      console.error('Error fetching RBS configs:', error);
    }
  };

  const fetchRbsConfig = async (name) => {
    try {
      const response = await axios.get(`${API}/rbs-config/${name}`);
      setCurrentRbsConfig(response.data.config);
      setRbsConfigForm(response.data.config);
    } catch (error) {
      console.error('Error fetching RBS config:', error);
    }
  };

  const saveRbsConfig = async () => {
    try {
      const response = await axios.post(`${API}/rbs-config`, rbsConfigForm);
      alert('✅ RBS Configuration saved successfully!');
      await fetchRbsConfigs();
      setRbsConfigEditing(false);
    } catch (error) {
      alert(`❌ Error saving RBS configuration: ${error.response?.data?.detail || error.message}`);
    }
  };

  const handleRbsConfigFormChange = (field, value) => {
    setRbsConfigForm(prev => ({
      ...prev,
      [field]: parseFloat(value) || value
    }));
  };

  const resetRbsConfigForm = () => {
    setRbsConfigForm({
      config_name: 'custom_rbs',
      yellow_cards_weight: 0.3,
      red_cards_weight: 0.5,
      fouls_committed_weight: 0.1,
      fouls_drawn_weight: 0.1,
      penalties_awarded_weight: 0.5,
      xg_difference_weight: 0.4,
      possession_percentage_weight: 0.2,
      confidence_matches_multiplier: 4,
      max_confidence: 95,
      min_confidence: 10,
      confidence_threshold_low: 2,
      confidence_threshold_medium: 5,
      confidence_threshold_high: 10
    });
  };

  // Regression Analysis functions
  const fetchAvailableStats = async () => {
    try {
      const response = await axios.get(`${API}/regression-stats`);
      setAvailableStats(response.data.available_stats || []);
      setStatDescriptions(response.data.descriptions || {});
      setStatCategories(response.data.categories || {});
    } catch (error) {
      console.error('Error fetching available stats:', error);
    }
  };

  const runRegressionAnalysis = async () => {
    if (selectedStats.length === 0) {
      alert('Please select at least one statistic for analysis');
      return;
    }

    setAnalyzing(true);
    try {
      const requestData = {
        selected_stats: selectedStats,
        target: regressionTarget
      };
      const response = await axios.post(`${API}/regression-analysis`, requestData);
      setRegressionResult(response.data);
    } catch (error) {
      alert(`❌ Analysis Error: ${error.response?.data?.detail || error.message}`);
    }
    setAnalyzing(false);
  };

  const resetAnalysis = () => {
    setSelectedStats([]);
    setRegressionResult(null);
  };

  const toggleStat = (stat) => {
    setSelectedStats(prev => {
      if (prev.includes(stat)) {
        return prev.filter(s => s !== stat);
      } else {
        return [...prev, stat];
      }
    });
  };

  // Apply filters when team/referee selection changes  
  useEffect(() => {
    if (activeTab === 'results') {
      fetchRefereeSummary();
    }
  }, [selectedTeam, selectedReferee, activeTab]);

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white shadow-sm border-b">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center py-4">
            <div className="flex items-center space-x-3">
              <div className="w-8 h-8 bg-blue-600 rounded-lg flex items-center justify-center">
                <span className="text-white font-bold text-sm">⚽</span>
              </div>
              <h1 className="text-2xl font-bold text-gray-900">Soccer Referee Bias Analysis</h1>
            </div>
            <div className="flex space-x-4">
              <span className="text-sm text-gray-500">Matches: {stats.matches || 0}</span>
              <span className="text-sm text-gray-500">RBS Results: {stats.rbs_results || 0}</span>
            </div>
          </div>
        </div>
      </header>

      {/* Navigation */}
      <nav className="bg-white border-b">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex space-x-8">
            {['dashboard', 'upload', 'predict', 'xgboost', 'analysis', 'config', 'rbs-config', 'optimization', 'results'].map((tab) => (
              <button
                key={tab}
                onClick={() => {
                  setActiveTab(tab);
                  if (tab === 'results') {
                    console.log('Results tab clicked, fetching referee summary...');
                    fetchRefereeSummary();
                  }
                  if (tab === 'config') {
                    fetchConfigs();
                    fetchConfig(configName);
                  }
                  if (tab === 'rbs-config') {
                    fetchRbsConfigs();
                    fetchRbsConfig(rbsConfigName);
                  }
                  if (tab === 'analysis') {
                    fetchAvailableStats();
                  }
                }}
                className={`py-4 px-1 border-b-2 font-medium text-sm capitalize ${
                  activeTab === tab
                    ? 'border-blue-500 text-blue-600'
                    : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                }`}
              >
                {tab === 'predict' ? 'Match Prediction' : 
                 tab === 'xgboost' ? 'XGBoost + Poisson' :
                 tab === 'config' ? 'Prediction Config' :
                 tab === 'rbs-config' ? 'RBS Config' :
                 tab === 'analysis' ? 'Regression Analysis' :
                 tab === 'optimization' ? 'Formula Optimization' : tab}
              </button>
            ))}
          </div>
        </div>
      </nav>

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Dashboard Tab */}
        {activeTab === 'dashboard' && (
          <div className="space-y-6">
            <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
              <div className="bg-white p-6 rounded-lg shadow-sm border">
                <h3 className="text-lg font-semibold text-gray-900">Matches</h3>
                <p className="text-3xl font-bold text-blue-600">{stats.matches || 0}</p>
              </div>
              <div className="bg-white p-6 rounded-lg shadow-sm border">
                <h3 className="text-lg font-semibold text-gray-900">Team Stats</h3>
                <p className="text-3xl font-bold text-green-600">{stats.team_stats || 0}</p>
              </div>
              <div className="bg-white p-6 rounded-lg shadow-sm border">
                <h3 className="text-lg font-semibold text-gray-900">Player Stats</h3>
                <p className="text-3xl font-bold text-purple-600">{stats.player_stats || 0}</p>
              </div>
              <div className="bg-white p-6 rounded-lg shadow-sm border">
                <h3 className="text-lg font-semibold text-gray-900">RBS Results</h3>
                <p className="text-3xl font-bold text-orange-600">{stats.rbs_results || 0}</p>
              </div>
            </div>

            <div className="bg-white p-6 rounded-lg shadow-sm border">
              <h2 className="text-xl font-bold text-gray-900 mb-4">🏛️ RBS Algorithm Methodology</h2>
              <div className="text-gray-700 space-y-4">
                <div className="bg-blue-50 p-4 rounded-lg">
                  <h3 className="font-semibold text-blue-900 mb-2">Performance Differential Analysis</h3>
                  <p><strong>RBS (Referee Bias Score)</strong> compares a team's performance when a specific referee officiates vs when other referees officiate.</p>
                  <p className="text-sm mt-2"><strong>Method:</strong> Calculate the difference in team statistics with vs without the referee, then apply weighted importance factors.</p>
                </div>
                
                <div className="bg-green-50 p-4 rounded-lg">
                  <h3 className="font-semibold text-green-900 mb-2">Core Formula</h3>
                  <div className="font-mono text-sm bg-white p-2 rounded border">
                    RBS = tanh(Σ(differential_i × weight_i))
                  </div>
                  <p className="text-sm mt-2">Where differential = avg_with_referee - avg_without_referee</p>
                </div>
                
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div className="bg-gray-50 p-3 rounded">
                    <h4 className="font-semibold text-gray-900">📊 Analyzed Statistics:</h4>
                    <ul className="mt-2 space-y-1 text-sm">
                      <li>• <span className="text-red-600">Yellow cards</span> (fewer = positive bias)</li>
                      <li>• <span className="text-red-800">Red cards</span> (fewer = positive bias)</li>
                      <li>• <span className="text-orange-600">Fouls committed</span> (fewer = positive bias)</li>
                      <li>• <span className="text-green-600">Fouls drawn</span> (more = positive bias)</li>
                    </ul>
                  </div>
                  <div className="bg-gray-50 p-3 rounded">
                    <h4 className="font-semibold text-gray-900">🎯 Key Advantages:</h4>
                    <ul className="mt-2 space-y-1 text-sm">
                      <li>• <span className="text-purple-600">Penalties awarded</span> (more = positive bias)</li>
                      <li>• <span className="text-blue-600">xG difference</span> (higher = positive bias)</li>
                      <li>• <span className="text-indigo-600">Possession %</span> (more = positive bias)</li>
                    </ul>
                  </div>
                </div>
                
                <div className="bg-yellow-50 p-4 rounded-lg">
                  <h3 className="font-semibold text-yellow-900 mb-2">Enhanced Variance Analysis</h3>
                  <p className="text-sm">Additionally analyzes how consistently a referee makes decisions for a specific team compared to their overall patterns across all teams.</p>
                  <p className="text-sm mt-1"><strong>Variance Ratio:</strong> team_specific_variance ÷ overall_variance</p>
                  <p className="text-sm mt-1">Ratios &gt;1.5 indicate more variable/inconsistent treatment than usual.</p>
                </div>
              </div>
            </div>
          </div>
        )}

        {/* Upload Tab */}
        {activeTab === 'upload' && (
          <div className="space-y-6">
            <div className="bg-white p-6 rounded-lg shadow-sm border">
              <h2 className="text-xl font-bold text-gray-900 mb-6">Data Upload</h2>
              
              <div className="space-y-6">
                {/* Matches Upload */}
                <div className="border-b pb-6">
                  <h3 className="text-lg font-semibold text-gray-900 mb-2">1. Upload Matches CSV</h3>
                  <p className="text-sm text-gray-600 mb-4">Required columns: match_id, referee, home_team, away_team, home_score, away_score, result, season, competition, match_date</p>
                  <input
                    type="file"
                    accept=".csv"
                    onChange={(e) => handleFileUpload(e, 'matches', 'matches')}
                    className="block w-full text-sm text-gray-500 file:mr-4 file:py-2 file:px-4 file:rounded-full file:border-0 file:text-sm file:font-semibold file:bg-blue-50 file:text-blue-700 hover:file:bg-blue-100"
                  />
                  {uploadMessages.matches && (
                    <p className="mt-2 text-sm">{uploadMessages.matches}</p>
                  )}
                </div>

                {/* Team Stats Upload */}
                <div className="border-b pb-6">
                  <h3 className="text-lg font-semibold text-gray-900 mb-2">2. Upload Team Stats CSV</h3>
                  <p className="text-sm text-gray-600 mb-4">Required columns: match_id, team_name, is_home, yellow_cards, red_cards, fouls, possession_pct, shots_total, shots_on_target, fouls_drawn, penalties_awarded, xg</p>
                  <input
                    type="file"
                    accept=".csv"
                    onChange={(e) => handleFileUpload(e, 'team-stats', 'team-stats')}
                    className="block w-full text-sm text-gray-500 file:mr-4 file:py-2 file:px-4 file:rounded-full file:border-0 file:text-sm file:font-semibold file:bg-green-50 file:text-green-700 hover:file:bg-green-100"
                  />
                  {uploadMessages['team-stats'] && (
                    <p className="mt-2 text-sm">{uploadMessages['team-stats']}</p>
                  )}
                </div>

                {/* Player Stats Upload */}
                <div className="border-b pb-6">
                  <h3 className="text-lg font-semibold text-gray-900 mb-2">3. Upload Player Stats CSV (Optional)</h3>
                  <p className="text-sm text-gray-600 mb-4">Required columns: match_id, player_name, team_name, is_home, goals, assists, yellow_cards, fouls_committed, fouls_drawn, xg, shots_total, shots_on_target, penalty_attempts, penalty_goals</p>
                  <input
                    type="file"
                    accept=".csv"
                    onChange={(e) => handleFileUpload(e, 'player-stats', 'player-stats')}
                    className="block w-full text-sm text-gray-500 file:mr-4 file:py-2 file:px-4 file:rounded-full file:border-0 file:text-sm file:font-semibold file:bg-purple-50 file:text-purple-700 hover:file:bg-purple-100"
                  />
                  {uploadMessages['player-stats'] && (
                    <p className="mt-2 text-sm">{uploadMessages['player-stats']}</p>
                  )}
                </div>

                {/* Calculate RBS */}
                <div>
                  <h3 className="text-lg font-semibold text-gray-900 mb-2">4. Calculate RBS Scores</h3>
                  <p className="text-sm text-gray-600 mb-4">After uploading matches and team stats, calculate referee bias scores for all team-referee combinations.</p>
                  <button
                    onClick={calculateRBS}
                    disabled={calculating || !stats.matches || !stats.team_stats}
                    className="px-6 py-3 bg-orange-600 text-white font-medium rounded-lg hover:bg-orange-700 disabled:bg-gray-400 disabled:cursor-not-allowed"
                  >
                    {calculating ? 'Calculating...' : 'Calculate RBS Scores'}
                  </button>
                </div>
              </div>
            </div>

            {/* Multi-Dataset Upload Section */}
            <div className="bg-white p-6 rounded-lg shadow-sm border">
              <h2 className="text-xl font-bold text-gray-900 mb-6">📊 Multi-Dataset Upload</h2>
              <p className="text-gray-600 mb-6">
                Upload multiple datasets (seasons) at once. Each dataset contains 3 files: matches.csv, team_stats.csv, and player_stats.csv.
              </p>

              {/* Dataset Management */}
              {datasets.length > 0 && (
                <div className="mb-6">
                  <h3 className="text-lg font-semibold text-gray-900 mb-4">📁 Existing Datasets</h3>
                  <div className="bg-gray-50 rounded-lg p-4">
                    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                      {datasets.map((dataset) => (
                        <div key={dataset.dataset_name} className="bg-white p-4 rounded-lg border shadow-sm">
                          <div className="flex justify-between items-start mb-2">
                            <h4 className="font-semibold text-gray-900">{dataset.dataset_name}</h4>
                            <button
                              onClick={() => deleteDataset(dataset.dataset_name)}
                              className="text-red-600 hover:text-red-800 text-sm"
                              title="Delete dataset"
                            >
                              🗑️
                            </button>
                          </div>
                          <div className="text-sm text-gray-600 space-y-1">
                            <div>Matches: {dataset.matches_count}</div>
                            <div>Team Stats: {dataset.team_stats_count}</div>
                            <div>Player Stats: {dataset.player_stats_count}</div>
                          </div>
                        </div>
                      ))}
                    </div>
                  </div>
                </div>
              )}

              {/* Multi-Dataset Upload Form */}
              <div className="space-y-6">
                <div className="flex justify-between items-center">
                  <h3 className="text-lg font-semibold text-gray-900">Upload New Datasets</h3>
                  <button
                    onClick={addDatasetUpload}
                    className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
                  >
                    ➕ Add Dataset
                  </button>
                </div>

                {multiDatasetFiles.length === 0 && (
                  <div className="text-center py-8 text-gray-500">
                    <p>No datasets added yet. Click "Add Dataset" to start uploading.</p>
                  </div>
                )}

                {multiDatasetFiles.map((dataset, index) => (
                  <div key={dataset.id} className="border rounded-lg p-4 bg-gray-50">
                    <div className="flex justify-between items-center mb-4">
                      <h4 className="font-medium text-gray-900">Dataset #{index + 1}</h4>
                      <button
                        onClick={() => removeDatasetUpload(dataset.id)}
                        className="text-red-600 hover:text-red-800"
                      >
                        ❌ Remove
                      </button>
                    </div>

                    <div className="space-y-4">
                      {/* Dataset Name */}
                      <div>
                        <label className="block text-sm font-medium text-gray-700 mb-2">
                          Dataset Name *
                        </label>
                        <input
                          type="text"
                          value={dataset.dataset_name}
                          onChange={(e) => updateDatasetField(dataset.id, 'dataset_name', e.target.value)}
                          placeholder="e.g., Premier League 2023-24"
                          className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                        />
                      </div>

                      {/* File Uploads */}
                      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                        <div>
                          <label className="block text-sm font-medium text-gray-700 mb-2">
                            Matches CSV *
                          </label>
                          <input
                            type="file"
                            accept=".csv"
                            onChange={(e) => updateDatasetField(dataset.id, 'matches_file', e.target.files[0])}
                            className="block w-full text-sm text-gray-500 file:mr-4 file:py-2 file:px-4 file:rounded-full file:border-0 file:text-sm file:font-semibold file:bg-blue-50 file:text-blue-700 hover:file:bg-blue-100"
                          />
                          {dataset.matches_file && (
                            <p className="mt-1 text-sm text-green-600">✅ {dataset.matches_file.name}</p>
                          )}
                        </div>
                        <div>
                          <label className="block text-sm font-medium text-gray-700 mb-2">
                            Team Stats CSV *
                          </label>
                          <input
                            type="file"
                            accept=".csv"
                            onChange={(e) => updateDatasetField(dataset.id, 'team_stats_file', e.target.files[0])}
                            className="block w-full text-sm text-gray-500 file:mr-4 file:py-2 file:px-4 file:rounded-full file:border-0 file:text-sm file:font-semibold file:bg-green-50 file:text-green-700 hover:file:bg-green-100"
                          />
                          {dataset.team_stats_file && (
                            <p className="mt-1 text-sm text-green-600">✅ {dataset.team_stats_file.name}</p>
                          )}
                        </div>
                        <div>
                          <label className="block text-sm font-medium text-gray-700 mb-2">
                            Player Stats CSV *
                          </label>
                          <input
                            type="file"
                            accept=".csv"
                            onChange={(e) => updateDatasetField(dataset.id, 'player_stats_file', e.target.files[0])}
                            className="block w-full text-sm text-gray-500 file:mr-4 file:py-2 file:px-4 file:rounded-full file:border-0 file:text-sm file:font-semibold file:bg-purple-50 file:text-purple-700 hover:file:bg-purple-100"
                          />
                          {dataset.player_stats_file && (
                            <p className="mt-1 text-sm text-green-600">✅ {dataset.player_stats_file.name}</p>
                          )}
                        </div>
                      </div>
                    </div>
                  </div>
                ))}

                {/* Upload Button */}
                {multiDatasetFiles.length > 0 && (
                  <div className="flex space-x-4">
                    <button
                      onClick={uploadMultiDataset}
                      disabled={uploadingMultiDataset}
                      className="px-6 py-3 bg-green-600 text-white font-medium rounded-lg hover:bg-green-700 disabled:bg-gray-400 disabled:cursor-not-allowed flex items-center space-x-2"
                    >
                      {uploadingMultiDataset ? (
                        <>
                          <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white"></div>
                          <span>Uploading...</span>
                        </>
                      ) : (
                        <>
                          <span>🚀</span>
                          <span>Upload All Datasets</span>
                        </>
                      )}
                    </button>
                  </div>
                )}

                {/* Upload Results */}
                {multiDatasetResults && (
                  <div className="bg-green-50 border border-green-200 rounded-lg p-4">
                    <h4 className="font-semibold text-green-900 mb-2">✅ Upload Successful!</h4>
                    <p className="text-green-800 mb-3">{multiDatasetResults.message}</p>
                    <div className="space-y-2">
                      {multiDatasetResults.datasets?.map((dataset, index) => (
                        <div key={index} className="text-sm text-green-700">
                          <strong>{dataset.dataset_name}:</strong> {dataset.matches} matches, {dataset.team_stats} team stats, {dataset.player_stats} player stats
                        </div>
                      ))}
                    </div>
                    <button
                      onClick={() => setMultiDatasetResults(null)}
                      className="mt-3 text-sm text-green-600 hover:text-green-800"
                    >
                      Dismiss
                    </button>
                  </div>
                )}

                {/* Usage Instructions */}
                <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
                  <h4 className="font-semibold text-blue-900 mb-2">📝 Instructions</h4>
                  <div className="text-sm text-blue-800 space-y-1">
                    <p>1. Click "Add Dataset" to create a new dataset upload</p>
                    <p>2. Give each dataset a unique name (e.g., "Premier League 2023-24")</p>
                    <p>3. Upload all 3 CSV files for each dataset</p>
                    <p>4. Click "Upload All Datasets" to process everything at once</p>
                    <p>5. Each dataset will be stored separately and can be managed independently</p>
                  </div>
                </div>
              </div>
            </div>

            {/* Database Management Section */}
            <div className="bg-white p-6 rounded-lg shadow-sm border">
              <h2 className="text-xl font-bold text-gray-900 mb-4">🗄️ Database Management</h2>
              <p className="text-gray-600 mb-6">
                Manage your database with caution. These actions are irreversible.
              </p>

              <div className="space-y-4">
                {/* Current Database Stats */}
                <div className="bg-gray-50 p-4 rounded-lg">
                  <h3 className="text-lg font-semibold text-gray-900 mb-3">📊 Current Database Contents</h3>
                  <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
                    <div className="text-center">
                      <div className="text-2xl font-bold text-blue-600">{stats.matches}</div>
                      <div className="text-gray-600">Matches</div>
                    </div>
                    <div className="text-center">
                      <div className="text-2xl font-bold text-green-600">{stats.team_stats}</div>
                      <div className="text-gray-600">Team Stats</div>
                    </div>
                    <div className="text-center">
                      <div className="text-2xl font-bold text-purple-600">{stats.player_stats}</div>
                      <div className="text-gray-600">Player Stats</div>
                    </div>
                    <div className="text-center">
                      <div className="text-2xl font-bold text-orange-600">{stats.rbs_results}</div>
                      <div className="text-gray-600">RBS Results</div>
                    </div>
                  </div>
                </div>

                {/* Wipe Database Section */}
                <div className="bg-red-50 border border-red-200 rounded-lg p-4">
                  <h3 className="text-lg font-semibold text-red-900 mb-2">⚠️ Danger Zone</h3>
                  <p className="text-red-700 mb-4 text-sm">
                    This action will permanently delete ALL data from the database including matches, team statistics, player statistics, RBS results, and configuration settings. This cannot be undone.
                  </p>
                  <button
                    onClick={wipeDatabase}
                    className="px-6 py-3 bg-red-600 text-white font-medium rounded-lg hover:bg-red-700 focus:ring-2 focus:ring-red-500 focus:ring-offset-2"
                  >
                    🗑️ Wipe Entire Database
                  </button>
                </div>
              </div>
            </div>
          </div>
        )}

        {/* Match Prediction Tab */}
        {activeTab === 'predict' && (
          <div className="space-y-6">
            <div className="bg-white p-6 rounded-lg shadow-sm border">
              <h2 className="text-xl font-bold text-gray-900 mb-4">⚽ ML-Based Match Prediction</h2>
              <p className="text-gray-600 mb-6">
                Predict match outcomes using trained Machine Learning models (Random Forest) with comprehensive feature engineering including team stats, referee bias, and historical data.
              </p>

              {/* ML Status Section */}
              <div className="mb-6 p-4 bg-blue-50 rounded-lg border border-blue-200">
                <div className="flex justify-between items-center mb-3">
                  <h3 className="text-lg font-semibold text-blue-900">🤖 ML Models Status</h3>
                  <button
                    onClick={checkMLStatus}
                    className="px-3 py-1 text-sm bg-blue-600 text-white rounded hover:bg-blue-700"
                  >
                    Refresh Status
                  </button>
                </div>
                
                {mlStatus ? (
                  <div className="space-y-2">
                    <div className="flex items-center space-x-2">
                      <span className={`inline-block w-3 h-3 rounded-full ${mlStatus.models_loaded ? 'bg-green-500' : 'bg-red-500'}`}></span>
                      <span className="text-sm font-medium">
                        Models Status: {mlStatus.models_loaded ? '✅ Loaded' : '❌ Not Loaded'}
                      </span>
                    </div>
                    <div className="text-sm text-blue-700">
                      Features: {mlStatus.feature_columns_count} | Models: {Object.keys(mlStatus.models_status).length}
                    </div>
                    
                    {!mlStatus.models_loaded && (
                      <div className="mt-3 p-3 bg-yellow-50 border border-yellow-200 rounded">
                        <p className="text-sm text-yellow-800">
                          ⚠️ ML models not found. Train models first to enable ML-based predictions.
                        </p>
                      </div>
                    )}
                  </div>
                ) : (
                  <div className="text-sm text-blue-700">Click "Refresh Status" to check ML models status</div>
                )}

                {/* Training Controls */}
                <div className="mt-4 flex space-x-3">
                  <button
                    onClick={trainMLModels}
                    disabled={trainingModels}
                    className="px-4 py-2 bg-green-600 text-white font-medium rounded-lg hover:bg-green-700 disabled:bg-gray-400 disabled:cursor-not-allowed flex items-center space-x-2"
                  >
                    {trainingModels ? (
                      <>
                        <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white"></div>
                        <span>Training...</span>
                      </>
                    ) : (
                      <>
                        <span>🧠</span>
                        <span>Train ML Models</span>
                      </>
                    )}
                  </button>
                  
                  {mlStatus?.models_loaded && (
                    <button
                      onClick={reloadMLModels}
                      className="px-4 py-2 bg-gray-600 text-white font-medium rounded-lg hover:bg-gray-700"
                    >
                      🔄 Reload Models
                    </button>
                  )}
                </div>
              </div>
            </div>
          </div>
        )}

        {/* XGBoost + Poisson Prediction Tab */}
        {activeTab === 'xgboost' && (
          <div className="space-y-6">
            <div className="bg-white p-6 rounded-lg shadow-sm border">
              <h2 className="text-xl font-bold text-gray-900 mb-4">🚀 XGBoost + Poisson Distribution Prediction</h2>
              <p className="text-gray-600 mb-6">
                Advanced match prediction using XGBoost gradient boosting with Poisson distribution simulation for detailed scoreline probabilities. This combines the power of XGBoost feature engineering with statistical modeling for comprehensive match analysis.
              </p>

              {/* XGBoost Status Section */}
              <div className="mb-6 p-4 bg-gradient-to-r from-orange-50 to-red-50 rounded-lg border border-orange-200">
                <div className="flex justify-between items-center mb-3">
                  <h3 className="text-lg font-semibold text-orange-900">🧠 XGBoost Models Status</h3>
                  <button
                    onClick={checkMLStatus}
                    className="px-3 py-1 text-sm bg-orange-600 text-white rounded hover:bg-orange-700"
                  >
                    Refresh Status
                  </button>
                </div>
                
                {mlStatus ? (
                  <div className="space-y-2">
                    <div className="flex items-center space-x-2">
                      <span className={`inline-block w-3 h-3 rounded-full ${mlStatus.models_loaded ? 'bg-green-500' : 'bg-red-500'}`}></span>
                      <span className="text-sm font-medium">
                        XGBoost Models: {mlStatus.models_loaded ? '✅ Ready' : '❌ Need Training'}
                      </span>
                    </div>
                    <div className="text-sm text-orange-700">
                      Features: {mlStatus.feature_columns_count} | Enhanced Engineering: XGBoost + Poisson
                    </div>
                    
                    {!mlStatus.models_loaded && (
                      <div className="mt-3 p-3 bg-yellow-50 border border-yellow-200 rounded">
                        <p className="text-sm text-yellow-800">
                          ⚠️ XGBoost models not found. Train models first to enable advanced predictions with Poisson simulation.
                        </p>
                      </div>
                    )}
                  </div>
                ) : (
                  <div className="text-sm text-orange-700">Click "Refresh Status" to check XGBoost models status</div>
                )}

                {/* Training Controls */}
                <div className="mt-4 flex space-x-3">
                  <button
                    onClick={trainMLModels}
                    disabled={trainingModels}
                    className="px-4 py-2 bg-gradient-to-r from-orange-600 to-red-600 text-white font-medium rounded-lg hover:from-orange-700 hover:to-red-700 disabled:bg-gray-400 disabled:cursor-not-allowed flex items-center space-x-2"
                  >
                    {trainingModels ? (
                      <>
                        <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white"></div>
                        <span>Training XGBoost...</span>
                      </>
                    ) : (
                      <>
                        <span>🚀</span>
                        <span>Train XGBoost Models</span>
                      </>
                    )}
                  </button>
                  
                  {mlStatus?.models_loaded && (
                    <button
                      onClick={reloadMLModels}
                      className="px-4 py-2 bg-gray-600 text-white font-medium rounded-lg hover:bg-gray-700"
                    >
                      🔄 Reload Models
                    </button>
                  )}
                </div>

                {/* Training Results */}
                {trainingResults && (
                  <div className="mt-4 p-3 bg-green-50 border border-green-200 rounded">
                    <h4 className="text-sm font-semibold text-green-900 mb-2">✅ XGBoost Training Complete!</h4>
                    <div className="text-xs text-green-800 space-y-1">
                      {trainingResults.training_results && Object.entries(trainingResults.training_results).map(([model, metrics]) => (
                        <div key={model}>
                          <strong>{model}:</strong> {
                            metrics.accuracy ? `Accuracy: ${(metrics.accuracy * 100).toFixed(1)}%` : 
                            `R² Score: ${(metrics.r2_score * 100).toFixed(1)}%`
                          }
                          {metrics.log_loss && ` | Log Loss: ${metrics.log_loss.toFixed(3)}`}
                        </div>
                      ))}
                    </div>
                  </div>
                )}
              </div>

              {!predictionResult ? (
                /* XGBoost Prediction Form */
                <div className="space-y-6">
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                    {/* Configuration Selection */}
                    <div className="md:col-span-2">
                      <label className="block text-sm font-medium text-gray-700 mb-2">
                        Prediction Configuration
                      </label>
                      <select
                        value={configName}
                        onChange={(e) => setConfigName(e.target.value)}
                        className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-orange-500 focus:border-orange-500"
                      >
                        <option value="default">Default Configuration</option>
                        {configs.map(config => (
                          <option key={config.config_name} value={config.config_name}>
                            {config.config_name}
                          </option>
                        ))}
                      </select>
                    </div>

                    {/* Home Team */}
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-2">
                        Home Team *
                      </label>
                      <select
                        value={predictionForm.home_team}
                        onChange={(e) => handlePredictionFormChange('home_team', e.target.value)}
                        className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-orange-500 focus:border-orange-500"
                      >
                        <option value="">Select Home Team</option>
                        {teams.map(team => (
                          <option key={team} value={team}>{team}</option>
                        ))}
                      </select>
                    </div>

                    {/* Away Team */}
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-2">
                        Away Team *
                      </label>
                      <select
                        value={predictionForm.away_team}
                        onChange={(e) => handlePredictionFormChange('away_team', e.target.value)}
                        className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-orange-500 focus:border-orange-500"
                      >
                        <option value="">Select Away Team</option>
                        {teams.filter(team => team !== predictionForm.home_team).map(team => (
                          <option key={team} value={team}>{team}</option>
                        ))}
                      </select>
                    </div>

                    {/* Referee */}
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-2">
                        Referee *
                      </label>
                      <select
                        value={predictionForm.referee_name}
                        onChange={(e) => handlePredictionFormChange('referee_name', e.target.value)}
                        className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-orange-500 focus:border-orange-500"
                      >
                        <option value="">Select Referee</option>
                        {referees.map(referee => (
                          <option key={referee} value={referee}>{referee}</option>
                        ))}
                      </select>
                    </div>

                    {/* Match Date (Optional) */}
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-2">
                        Match Date (Optional)
                      </label>
                      <input
                        type="date"
                        value={predictionForm.match_date}
                        onChange={(e) => handlePredictionFormChange('match_date', e.target.value)}
                        className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-orange-500 focus:border-orange-500"
                      />
                    </div>
                  </div>

                  {/* Prediction Button */}
                  <div className="flex space-x-4">
                    <button
                      onClick={predictMatch}
                      disabled={predicting || !predictionForm.home_team || !predictionForm.away_team || !predictionForm.referee_name}
                      className="px-6 py-3 bg-gradient-to-r from-orange-600 to-red-600 text-white font-medium rounded-lg hover:from-orange-700 hover:to-red-700 disabled:bg-gray-400 disabled:cursor-not-allowed flex items-center space-x-2"
                    >
                      {predicting ? (
                        <>
                          <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white"></div>
                          <span>Calculating...</span>
                        </>
                      ) : (
                        <>
                          <span>🚀</span>
                          <span>XGBoost Predict</span>
                        </>
                      )}
                    </button>
                  </div>

                  {/* Algorithm Explanation */}
                  <div className="bg-gradient-to-r from-orange-50 to-red-50 p-4 rounded-lg border border-orange-200">
                    <h3 className="text-md font-semibold text-orange-900 mb-2">🚀 XGBoost + Poisson Prediction Algorithm</h3>
                    <div className="text-sm text-orange-800 space-y-2">
                      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                        <div>
                          <p><strong>🧠 XGBoost Features:</strong></p>
                          <ul className="ml-4 space-y-1 text-xs">
                            <li>• Enhanced feature engineering (60+ features)</li>
                            <li>• Team performance differentials</li>
                            <li>• Advanced referee bias analysis</li>
                            <li>• Form trends and momentum indicators</li>
                            <li>• Head-to-head historical patterns</li>
                          </ul>
                        </div>
                        <div>
                          <p><strong>📊 Poisson Simulation:</strong></p>
                          <ul className="ml-4 space-y-1 text-xs">
                            <li>• Detailed scoreline probabilities (0-0, 1-0, etc.)</li>
                            <li>• Uses XGBoost predicted goals as λ parameters</li>
                            <li>• Statistical match outcome modeling</li>
                            <li>• Most likely scoreline identification</li>
                            <li>• Comprehensive probability distributions</li>
                          </ul>
                        </div>
                      </div>
                      <div className="mt-3 p-2 bg-white rounded text-xs">
                        <strong>🎯 Why XGBoost + Poisson?</strong> XGBoost excels at capturing complex feature interactions for accurate goal predictions, while Poisson distribution provides statistically sound scoreline probabilities based on those predictions. This dual approach offers both high-level match outcomes and detailed score predictions.
                      </div>
                    </div>
                  </div>
                </div>
              ) : (
                /* XGBoost Prediction Results */
                <div className="space-y-6">
                  {predictionResult.success ? (
                    <>
                      {/* Header with predicted score */}
                      <div className="bg-gradient-to-r from-orange-50 to-red-50 p-6 rounded-lg border border-orange-200">
                        <div className="text-center">
                          <h3 className="text-lg font-semibold text-gray-800 mb-2">🚀 XGBoost + Poisson Prediction</h3>
                          <div className="text-4xl font-bold text-gray-900 mb-2">
                            {predictionResult.home_team} {parseFloat(predictionResult.predicted_home_goals).toFixed(2)} - {parseFloat(predictionResult.predicted_away_goals).toFixed(2)} {predictionResult.away_team}
                          </div>
                          <div className="text-sm text-gray-600">
                            Expected xG: {parseFloat(predictionResult.home_xg).toFixed(2)} - {parseFloat(predictionResult.away_xg).toFixed(2)}
                          </div>
                          <div className="text-xs text-gray-500 mt-1">
                            Referee: {predictionResult.referee}
                          </div>
                        </div>
                      </div>

                      {/* Match Outcome Probabilities */}
                      <div className="bg-white p-6 rounded-lg border border-gray-200">
                        <h3 className="text-lg font-semibold text-gray-900 mb-4 text-center">🎯 Match Outcome Probabilities (Poisson)</h3>
                        <div className="space-y-4">
                          {/* Home Win */}
                          <div>
                            <div className="flex justify-between items-center mb-2">
                              <span className="text-sm font-medium text-gray-700">{predictionResult.home_team} Win</span>
                              <span className="text-sm font-bold text-green-600">{predictionResult.home_win_probability}%</span>
                            </div>
                            <div className="w-full bg-gray-200 rounded-full h-2">
                              <div 
                                className="bg-green-500 h-2 rounded-full transition-all duration-500"
                                style={{width: `${predictionResult.home_win_probability}%`}}
                              ></div>
                            </div>
                          </div>
                          
                          {/* Draw */}
                          <div>
                            <div className="flex justify-between items-center mb-2">
                              <span className="text-sm font-medium text-gray-700">Draw</span>
                              <span className="text-sm font-bold text-gray-600">{predictionResult.draw_probability}%</span>
                            </div>
                            <div className="w-full bg-gray-200 rounded-full h-2">
                              <div 
                                className="bg-gray-500 h-2 rounded-full transition-all duration-500"
                                style={{width: `${predictionResult.draw_probability}%`}}
                              ></div>
                            </div>
                          </div>
                          
                          {/* Away Win */}
                          <div>
                            <div className="flex justify-between items-center mb-2">
                              <span className="text-sm font-medium text-gray-700">{predictionResult.away_team} Win</span>
                              <span className="text-sm font-bold text-red-600">{predictionResult.away_win_probability}%</span>
                            </div>
                            <div className="w-full bg-gray-200 rounded-full h-2">
                              <div 
                                className="bg-red-500 h-2 rounded-full transition-all duration-500"
                                style={{width: `${predictionResult.away_win_probability}%`}}
                              ></div>
                            </div>
                          </div>
                        </div>
                      </div>

                      {/* Detailed Scoreline Probabilities */}
                      {predictionResult.scoreline_probabilities && (
                        <div className="bg-white p-6 rounded-lg border border-gray-200">
                          <h3 className="text-lg font-semibold text-gray-900 mb-4 text-center">📊 Detailed Scoreline Probabilities</h3>
                          <div className="grid grid-cols-3 md:grid-cols-6 lg:grid-cols-8 gap-3">
                            {Object.entries(predictionResult.scoreline_probabilities).slice(0, 24).map(([scoreline, probability]) => (
                              <div key={scoreline} className="text-center p-3 bg-gray-50 rounded-lg border">
                                <div className="font-semibold text-sm text-gray-900">{scoreline}</div>
                                <div className="text-xs text-blue-600 font-medium">{probability}%</div>
                              </div>
                            ))}
                          </div>
                          
                          {/* Most Likely Scoreline */}
                          {predictionResult.prediction_breakdown?.poisson_analysis && (
                            <div className="mt-4 p-3 bg-blue-50 rounded-lg border border-blue-200">
                              <div className="text-center">
                                <span className="text-sm font-medium text-blue-900">Most Likely Scoreline: </span>
                                <span className="text-lg font-bold text-blue-800">
                                  {predictionResult.prediction_breakdown.poisson_analysis.most_likely_scoreline}
                                </span>
                                <span className="text-sm text-blue-700 ml-2">
                                  ({predictionResult.prediction_breakdown.poisson_analysis.scoreline_probability}% probability)
                                </span>
                              </div>
                            </div>
                          )}
                        </div>
                      )}

                      {/* XGBoost Model Analysis */}
                      {predictionResult.prediction_breakdown && (
                        <div className="bg-white p-6 rounded-lg border border-gray-200">
                          <h3 className="text-lg font-semibold text-gray-900 mb-4">🧠 XGBoost Model Analysis</h3>
                          
                          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                            {/* Model Confidence */}
                            <div className="bg-gray-50 p-4 rounded-lg">
                              <h4 className="font-semibold text-gray-900 mb-2">Model Confidence</h4>
                              <div className="space-y-2 text-sm">
                                <div className="flex justify-between">
                                  <span>Classifier Confidence:</span>
                                  <span className="font-medium">{(predictionResult.prediction_breakdown.xgboost_confidence?.classifier_confidence * 100).toFixed(1)}%</span>
                                </div>
                                <div className="flex justify-between">
                                  <span>Features Used:</span>
                                  <span className="font-medium">{predictionResult.prediction_breakdown.xgboost_confidence?.features_used}</span>
                                </div>
                                <div className="text-xs text-gray-600 mt-2">
                                  Method: {predictionResult.prediction_breakdown.prediction_method}
                                </div>
                              </div>
                            </div>

                            {/* Top Features */}
                            <div className="bg-gray-50 p-4 rounded-lg">
                              <h4 className="font-semibold text-gray-900 mb-2">Top Influential Features</h4>
                              <div className="space-y-1 text-sm">
                                {predictionResult.prediction_breakdown.feature_importance?.top_features && 
                                  Object.entries(predictionResult.prediction_breakdown.feature_importance.top_features).map(([feature, importance]) => (
                                    <div key={feature} className="flex justify-between">
                                      <span className="text-gray-700 truncate">{feature.replace(/_/g, ' ')}</span>
                                      <span className="font-medium text-orange-600">{(importance * 100).toFixed(1)}%</span>
                                    </div>
                                  ))
                                }
                              </div>
                            </div>
                          </div>

                          {/* Poisson Parameters */}
                          {predictionResult.prediction_breakdown.poisson_analysis?.lambda_parameters && (
                            <div className="mt-4 bg-blue-50 p-4 rounded-lg border border-blue-200">
                              <h4 className="font-semibold text-blue-900 mb-2">📊 Poisson Distribution Parameters</h4>
                              <div className="grid grid-cols-2 gap-4 text-sm">
                                <div>
                                  <span className="text-blue-700">Home λ (lambda): </span>
                                  <span className="font-medium">{predictionResult.prediction_breakdown.poisson_analysis.lambda_parameters.home_lambda.toFixed(2)}</span>
                                </div>
                                <div>
                                  <span className="text-blue-700">Away λ (lambda): </span>
                                  <span className="font-medium">{predictionResult.prediction_breakdown.poisson_analysis.lambda_parameters.away_lambda.toFixed(2)}</span>
                                </div>
                              </div>
                              <div className="text-xs text-blue-600 mt-2">
                                Lambda parameters represent the expected number of goals based on XGBoost predictions, used in Poisson distribution to calculate scoreline probabilities.
                              </div>
                            </div>
                          )}
                        </div>
                      )}

                      {/* Actions */}
                      <div className="flex space-x-4">
                        <button
                          onClick={() => setPredictionResult(null)}
                          className="px-6 py-3 bg-gray-600 text-white font-medium rounded-lg hover:bg-gray-700"
                        >
                          🔄 New Prediction
                        </button>
                        <button
                          onClick={exportPredictionPDF}
                          disabled={exportingPDF}
                          className="px-6 py-3 bg-red-600 text-white font-medium rounded-lg hover:bg-red-700 disabled:bg-gray-400 disabled:cursor-not-allowed flex items-center space-x-2"
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
                    </>
                  ) : (
                    /* Error Display */
                    <div className="bg-red-50 border border-red-200 rounded-lg p-6">
                      <div className="flex items-center mb-3">
                        <div className="text-red-600 mr-3">❌</div>
                        <h3 className="text-lg font-semibold text-red-900">Prediction Failed</h3>
                      </div>
                      <p className="text-red-700 mb-4">{predictionResult.error}</p>
                      <button
                        onClick={() => setPredictionResult(null)}
                        className="px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700"
                      >
                        Try Again
                      </button>
                    </div>
                  )}
                </div>
              )}
            </div>
          </div>
        )}

        {/* Regression Analysis Tab */}
        {activeTab === 'analysis' && (
          <div className="space-y-6">
            <div className="bg-white p-6 rounded-lg shadow-sm border">
              <h2 className="text-xl font-bold text-gray-900 mb-4">📈 Regression Analysis</h2>
              <p className="text-gray-600 mb-6">
                Analyze how different team-level statistics correlate with match outcomes using machine learning models.
              </p>

              {/* Available Statistics */}
              <div className="mb-6">
                <h3 className="text-lg font-semibold text-gray-900 mb-4">📊 Available Statistics</h3>
                {availableStats.length > 0 ? (
                  <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                    {availableStats.map(stat => (
                      <div
                        key={stat}
                        className={`p-3 border rounded-lg cursor-pointer transition-colors ${
                          selectedStats.includes(stat)
                            ? 'border-blue-500 bg-blue-50'
                            : 'border-gray-300 hover:border-blue-300'
                        }`}
                        onClick={() => {
                          if (selectedStats.includes(stat)) {
                            setSelectedStats(selectedStats.filter(s => s !== stat));
                          } else {
                            setSelectedStats([...selectedStats, stat]);
                          }
                        }}
                      >
                        <div className="font-medium text-gray-900">{stat.replace(/_/g, ' ').toUpperCase()}</div>
                        {statDescriptions[stat] && (
                          <div className="text-sm text-gray-600 mt-1">{statDescriptions[stat]}</div>
                        )}
                      </div>
                    ))}
                  </div>
                ) : (
                  <div className="text-center py-8 text-gray-500">
                    <p>Loading available statistics...</p>
                    <button
                      onClick={fetchAvailableStats}
                      className="mt-2 px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700"
                    >
                      Refresh Statistics
                    </button>
                  </div>
                )}
              </div>

              {/* Analysis Controls */}
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-6">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Target Variable
                  </label>
                  <select
                    value={regressionTarget}
                    onChange={(e) => setRegressionTarget(e.target.value)}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                  >
                    <option value="points_per_game">Points Per Game</option>
                    <option value="match_result">Match Result</option>
                  </select>
                </div>
                
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Selected Statistics: {selectedStats.length}
                  </label>
                  <button
                    onClick={() => setSelectedStats([])}
                    disabled={selectedStats.length === 0}
                    className="px-4 py-2 bg-gray-600 text-white rounded-lg hover:bg-gray-700 disabled:bg-gray-400"
                  >
                    Clear Selection
                  </button>
                </div>
              </div>

              {/* Run Analysis Button */}
              <div className="mb-6">
                <button
                  onClick={runRegressionAnalysis}
                  disabled={analyzing || selectedStats.length === 0}
                  className="px-6 py-3 bg-blue-600 text-white font-medium rounded-lg hover:bg-blue-700 disabled:bg-gray-400 disabled:cursor-not-allowed flex items-center space-x-2"
                >
                  {analyzing ? (
                    <>
                      <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white"></div>
                      <span>Analyzing...</span>
                    </>
                  ) : (
                    <>
                      <span>🧪</span>
                      <span>Run Regression Analysis</span>
                    </>
                  )}
                </button>
              </div>

              {/* Analysis Results */}
              {regressionResult && (
                <div className="bg-white p-6 rounded-lg border">
                  <h3 className="text-lg font-semibold text-gray-900 mb-4">📊 Analysis Results</h3>
                  
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                    <div>
                      <h4 className="font-medium text-gray-900 mb-3">Model Performance</h4>
                      <div className="space-y-2 text-sm">
                        <div className="flex justify-between">
                          <span className="text-gray-600">Model Type:</span>
                          <span className="font-medium">{regressionResult.model_type}</span>
                        </div>
                        <div className="flex justify-between">
                          <span className="text-gray-600">R² Score:</span>
                          <span className="font-medium">{(regressionResult.results?.r2_score * 100).toFixed(1)}%</span>
                        </div>
                        <div className="flex justify-between">
                          <span className="text-gray-600">Sample Size:</span>
                          <span className="font-medium">{regressionResult.sample_size}</span>
                        </div>
                      </div>
                    </div>
                    
                    <div>
                      <h4 className="font-medium text-gray-900 mb-3">Feature Importance</h4>
                      <div className="space-y-1 text-sm">
                        {regressionResult.results?.feature_importance && 
                          Object.entries(regressionResult.results.feature_importance)
                            .slice(0, 5)
                            .map(([feature, importance]) => (
                              <div key={feature} className="flex justify-between">
                                <span className="text-gray-600">{feature.replace(/_/g, ' ')}:</span>
                                <span className="font-medium">{(importance * 100).toFixed(1)}%</span>
                              </div>
                            ))
                        }
                      </div>
                    </div>
                  </div>
                </div>
              )}
            </div>
          </div>
        )}
        {activeTab === 'analysis' && (
          <div className="space-y-6">
            <div className="bg-white p-6 rounded-lg shadow-sm border">
              <h2 className="text-xl font-bold text-gray-900 mb-4">📈 Regression Analysis</h2>
              <p className="text-gray-600 mb-6">
                Analyze how different team-level statistics correlate with match outcomes using machine learning models.
              </p>

              {/* Available Statistics */}
              <div className="mb-6">
                <h3 className="text-lg font-semibold text-gray-900 mb-4">📊 Available Statistics</h3>
                {availableStats.length > 0 ? (
                  <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                    {availableStats.map(stat => (
                      <div
                        key={stat}
                        className={`p-3 border rounded-lg cursor-pointer transition-colors ${
                          selectedStats.includes(stat)
                            ? 'border-blue-500 bg-blue-50'
                            : 'border-gray-300 hover:border-blue-300'
                        }`}
                        onClick={() => {
                          if (selectedStats.includes(stat)) {
                            setSelectedStats(selectedStats.filter(s => s !== stat));
                          } else {
                            setSelectedStats([...selectedStats, stat]);
                          }
                        }}
                      >
                        <div className="font-medium text-gray-900">{stat.replace(/_/g, ' ').toUpperCase()}</div>
                        {statDescriptions[stat] && (
                          <div className="text-sm text-gray-600 mt-1">{statDescriptions[stat]}</div>
                        )}
                      </div>
                    ))}
                  </div>
                ) : (
                  <div className="text-center py-8 text-gray-500">
                    <p>Loading available statistics...</p>
                    <button
                      onClick={fetchAvailableStats}
                      className="mt-2 px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700"
                    >
                      Refresh Statistics
                    </button>
                  </div>
                )}
              </div>

              {/* Analysis Controls */}
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-6">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Target Variable
                  </label>
                  <select
                    value={regressionTarget}
                    onChange={(e) => setRegressionTarget(e.target.value)}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                  >
                    <option value="points_per_game">Points Per Game</option>
                    <option value="match_result">Match Result</option>
                  </select>
                </div>
                
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Selected Statistics: {selectedStats.length}
                  </label>
                  <button
                    onClick={() => setSelectedStats([])}
                    disabled={selectedStats.length === 0}
                    className="px-4 py-2 bg-gray-600 text-white rounded-lg hover:bg-gray-700 disabled:bg-gray-400"
                  >
                    Clear Selection
                  </button>
                </div>
              </div>

              {/* Run Analysis Button */}
              <div className="mb-6">
                <button
                  onClick={runRegressionAnalysis}
                  disabled={analyzing || selectedStats.length === 0}
                  className="px-6 py-3 bg-blue-600 text-white font-medium rounded-lg hover:bg-blue-700 disabled:bg-gray-400 disabled:cursor-not-allowed flex items-center space-x-2"
                >
                  {analyzing ? (
                    <>
                      <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white"></div>
                      <span>Analyzing...</span>
                    </>
                  ) : (
                    <>
                      <span>🧪</span>
                      <span>Run Regression Analysis</span>
                    </>
                  )}
                </button>
              </div>

              {/* Analysis Results */}
              {regressionResult && (
                <div className="bg-white p-6 rounded-lg border">
                  <h3 className="text-lg font-semibold text-gray-900 mb-4">📊 Analysis Results</h3>
                  
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                    <div>
                      <h4 className="font-medium text-gray-900 mb-3">Model Performance</h4>
                      <div className="space-y-2 text-sm">
                        <div className="flex justify-between">
                          <span className="text-gray-600">Model Type:</span>
                          <span className="font-medium">{regressionResult.model_type}</span>
                        </div>
                        <div className="flex justify-between">
                          <span className="text-gray-600">R² Score:</span>
                          <span className="font-medium">{(regressionResult.results?.r2_score * 100).toFixed(1)}%</span>
                        </div>
                        <div className="flex justify-between">
                          <span className="text-gray-600">Sample Size:</span>
                          <span className="font-medium">{regressionResult.sample_size}</span>
                        </div>
                      </div>
                    </div>
                    
                    <div>
                      <h4 className="font-medium text-gray-900 mb-3">Feature Importance</h4>
                      <div className="space-y-1 text-sm">
                        {regressionResult.results?.feature_importance && 
                          Object.entries(regressionResult.results.feature_importance)
                            .slice(0, 5)
                            .map(([feature, importance]) => (
                              <div key={feature} className="flex justify-between">
                                <span className="text-gray-600">{feature.replace(/_/g, ' ')}:</span>
                                <span className="font-medium">{(importance * 100).toFixed(1)}%</span>
                              </div>
                            ))
                        }
                      </div>
                    </div>
                  </div>
                </div>
              )}
            </div>
          </div>
        )}

        {/* Prediction Config Tab */}
        {activeTab === 'config' && (
          <div className="space-y-6">
            <div className="bg-white p-6 rounded-lg shadow-sm border">
              <h2 className="text-xl font-bold text-gray-900 mb-4">⚙️ Prediction Configuration</h2>
              <p className="text-gray-600 mb-6">
                Configure the parameters used in match prediction algorithms. These settings affect how different factors are weighted in the prediction calculations.
              </p>

              {/* Configuration Selection */}
              <div className="mb-6">
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Select Configuration
                </label>
                <div className="flex space-x-4">
                  <select
                    value={configName}
                    onChange={(e) => {
                      setConfigName(e.target.value);
                      fetchConfig(e.target.value);
                    }}
                    className="flex-1 px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                  >
                    <option value="default">Default Configuration</option>
                    {configs.map(config => (
                      <option key={config.config_name} value={config.config_name}>
                        {config.config_name}
                      </option>
                    ))}
                  </select>
                  <button
                    onClick={() => setConfigEditing(!configEditing)}
                    className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
                  >
                    {configEditing ? 'Cancel' : 'Edit'}
                  </button>
                </div>
              </div>

              {/* Configuration Form */}
              {configEditing && (
                <div className="space-y-6">
                  <div className="border-t pt-6">
                    <h3 className="text-lg font-semibold text-gray-900 mb-4">Configuration Parameters</h3>
                    
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                      <div>
                        <label className="block text-sm font-medium text-gray-700 mb-1">Configuration Name</label>
                        <input
                          type="text"
                          value={configForm.config_name}
                          onChange={(e) => handleConfigFormChange('config_name', e.target.value)}
                          className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                        />
                      </div>
                      <div>
                        <label className="block text-sm font-medium text-gray-700 mb-1">xG Shot Based Weight</label>
                        <input
                          type="number"
                          step="0.01"
                          value={configForm.xg_shot_based_weight}
                          onChange={(e) => handleConfigFormChange('xg_shot_based_weight', e.target.value)}
                          className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                        />
                      </div>
                    </div>

                    <div className="mt-6 flex space-x-4">
                      <button
                        onClick={saveConfig}
                        className="px-6 py-3 bg-green-600 text-white font-medium rounded-lg hover:bg-green-700"
                      >
                        Save Configuration
                      </button>
                      <button
                        onClick={() => setConfigEditing(false)}
                        className="px-6 py-3 bg-gray-600 text-white font-medium rounded-lg hover:bg-gray-700"
                      >
                        Cancel
                      </button>
                    </div>
                  </div>
                </div>
              )}

              {/* Current Configuration Display */}
              {currentConfig && !configEditing && (
                <div className="bg-gray-50 p-4 rounded-lg">
                  <h3 className="text-lg font-semibold text-gray-900 mb-3">Current Configuration: {currentConfig.config_name}</h3>
                  <div className="grid grid-cols-2 md:grid-cols-3 gap-4 text-sm">
                    <div>
                      <span className="text-gray-600">xG Shot Weight:</span>
                      <span className="ml-2 font-medium">{currentConfig.xg_shot_based_weight}</span>
                    </div>
                    <div>
                      <span className="text-gray-600">xG Historical Weight:</span>
                      <span className="ml-2 font-medium">{currentConfig.xg_historical_weight}</span>
                    </div>
                    <div>
                      <span className="text-gray-600">PPG Adjustment:</span>
                      <span className="ml-2 font-medium">{currentConfig.ppg_adjustment_factor}</span>
                    </div>
                  </div>
                </div>
              )}
            </div>
          </div>
        )}

        {/* RBS Config Tab */}
        {activeTab === 'rbs-config' && (
          <div className="space-y-6">
            <div className="bg-white p-6 rounded-lg shadow-sm border">
              <h2 className="text-xl font-bold text-gray-900 mb-4">⚖️ RBS Configuration</h2>
              <p className="text-gray-600 mb-6">
                Configure the Referee Bias Score (RBS) calculation parameters. These weights determine how different referee decisions impact the bias score.
              </p>

              {/* RBS Configuration Selection */}
              <div className="mb-6">
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Select RBS Configuration
                </label>
                <div className="flex space-x-4">
                  <select
                    value={rbsConfigName}
                    onChange={(e) => {
                      setRbsConfigName(e.target.value);
                      fetchRbsConfig(e.target.value);
                    }}
                    className="flex-1 px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                  >
                    <option value="default">Default RBS Configuration</option>
                    {rbsConfigs.map(config => (
                      <option key={config.config_name} value={config.config_name}>
                        {config.config_name}
                      </option>
                    ))}
                  </select>
                  <button
                    onClick={() => setRbsConfigEditing(!rbsConfigEditing)}
                    className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
                  >
                    {rbsConfigEditing ? 'Cancel' : 'Edit'}
                  </button>
                </div>
              </div>

              {/* Current RBS Configuration Display */}
              {currentRbsConfig && !rbsConfigEditing && (
                <div className="bg-gray-50 p-4 rounded-lg">
                  <h3 className="text-lg font-semibold text-gray-900 mb-3">Current RBS Configuration: {currentRbsConfig.config_name}</h3>
                  <div className="grid grid-cols-2 md:grid-cols-3 gap-4 text-sm">
                    <div>
                      <span className="text-gray-600">Yellow Cards Weight:</span>
                      <span className="ml-2 font-medium">{currentRbsConfig.yellow_cards_weight}</span>
                    </div>
                    <div>
                      <span className="text-gray-600">Red Cards Weight:</span>
                      <span className="ml-2 font-medium">{currentRbsConfig.red_cards_weight}</span>
                    </div>
                    <div>
                      <span className="text-gray-600">Fouls Weight:</span>
                      <span className="ml-2 font-medium">{currentRbsConfig.fouls_committed_weight}</span>
                    </div>
                  </div>
                </div>
              )}
            </div>
          </div>
        )}

        {/* Formula Optimization Tab */}
        {activeTab === 'optimization' && (
          <div className="space-y-6">
            <div className="bg-white p-6 rounded-lg shadow-sm border">
              <h2 className="text-xl font-bold text-gray-900 mb-4">🔬 Formula Optimization</h2>
              <p className="text-gray-600 mb-6">
                Analyze and optimize the RBS formula and Match Predictor algorithm based on statistical regression analysis.
              </p>

              <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
                {/* RBS Formula Optimization */}
                <div className="bg-blue-50 p-6 rounded-lg border border-blue-200">
                  <h3 className="text-lg font-semibold text-blue-900 mb-4">⚖️ RBS Formula Optimization</h3>
                  <p className="text-blue-700 mb-4 text-sm">
                    Analyze the statistical significance of RBS variables and get suggestions for optimal weight adjustments.
                  </p>
                  
                  <button
                    onClick={analyzeRBSFormula}
                    disabled={analyzingFormulas}
                    className="w-full px-4 py-3 bg-blue-600 text-white font-medium rounded-lg hover:bg-blue-700 disabled:bg-gray-400 disabled:cursor-not-allowed flex items-center justify-center space-x-2"
                  >
                    {analyzingFormulas ? (
                      <>
                        <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white"></div>
                        <span>Analyzing...</span>
                      </>
                    ) : (
                      <>
                        <span>🧪</span>
                        <span>Analyze RBS Formula</span>
                      </>
                    )}
                  </button>

                  {optimizationResults.rbs && (
                    <div className="mt-4 space-y-3">
                      <h4 className="font-medium text-blue-900">📊 Analysis Results</h4>
                      <div className="text-sm text-blue-800 space-y-2">
                        <p><strong>R² Score:</strong> {(optimizationResults.rbs.analysis?.r2_score * 100).toFixed(1)}%</p>
                        <p><strong>Sample Size:</strong> {optimizationResults.rbs.analysis?.sample_size}</p>
                      </div>
                      
                      <button
                        onClick={() => applyOptimizedWeights('rbs')}
                        disabled={applyingWeights}
                        className="w-full px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 disabled:bg-gray-400"
                      >
                        Apply Suggested Weights
                      </button>
                    </div>
                  )}
                </div>

                {/* Match Predictor Optimization */}
                <div className="bg-green-50 p-6 rounded-lg border border-green-200">
                  <h3 className="text-lg font-semibold text-green-900 mb-4">🎯 Match Predictor Optimization</h3>
                  <p className="text-green-700 mb-4 text-sm">
                    Analyze predictor variables and get recommendations for optimizing the match prediction algorithm.
                  </p>
                  
                  <button
                    onClick={analyzeMatchPredictor}
                    disabled={analyzingFormulas}
                    className="w-full px-4 py-3 bg-green-600 text-white font-medium rounded-lg hover:bg-green-700 disabled:bg-gray-400 disabled:cursor-not-allowed flex items-center justify-center space-x-2"
                  >
                    {analyzingFormulas ? (
                      <>
                        <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white"></div>
                        <span>Analyzing...</span>
                      </>
                    ) : (
                      <>
                        <span>🎯</span>
                        <span>Analyze Match Predictor</span>
                      </>
                    )}
                  </button>

                  {optimizationResults.predictor && (
                    <div className="mt-4 space-y-3">
                      <h4 className="font-medium text-green-900">📊 Analysis Results</h4>
                      <div className="text-sm text-green-800 space-y-2">
                        <p><strong>R² Score:</strong> {(optimizationResults.predictor.analysis?.r2_score * 100).toFixed(1)}%</p>
                        <p><strong>Sample Size:</strong> {optimizationResults.predictor.analysis?.sample_size}</p>
                      </div>
                      
                      <button
                        onClick={() => applyOptimizedWeights('predictor')}
                        disabled={applyingWeights}
                        className="w-full px-4 py-2 bg-orange-600 text-white rounded-lg hover:bg-orange-700 disabled:bg-gray-400"
                      >
                        Apply Optimized Configuration
                      </button>
                    </div>
                  )}
                </div>
              </div>
            </div>
          </div>
        )}

        {/* Results Tab */}
        {activeTab === 'results' && (
          <div className="space-y-6">
            {!viewingReferee ? (
              /* Referee Summary View */
              <div className="bg-white p-6 rounded-lg shadow-sm border">
                <h2 className="text-xl font-bold text-gray-900 mb-4">📊 Referee Analysis Results</h2>
                <p className="text-gray-600 mb-6">
                  Browse referee performance analysis and bias scores. Click on any referee to view detailed statistics.
                </p>

                {refereeSummary.length > 0 ? (
                  <div className="overflow-x-auto">
                    <table className="min-w-full divide-y divide-gray-200">
                      <thead className="bg-gray-50">
                        <tr>
                          <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Referee</th>
                          <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Total Matches</th>
                          <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Teams Analyzed</th>
                          <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Avg RBS Score</th>
                          <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Action</th>
                        </tr>
                      </thead>
                      <tbody className="bg-white divide-y divide-gray-200">
                        {refereeSummary.map((referee) => (
                          <tr key={referee.referee} className="hover:bg-gray-50">
                            <td className="px-6 py-4 whitespace-nowrap">
                              <div className="text-sm font-medium text-gray-900">{referee.referee}</div>
                            </td>
                            <td className="px-6 py-4 whitespace-nowrap">
                              <div className="text-sm text-gray-900">{referee.total_matches}</div>
                            </td>
                            <td className="px-6 py-4 whitespace-nowrap">
                              <div className="text-sm text-gray-900">{referee.teams_count}</div>
                            </td>
                            <td className="px-6 py-4 whitespace-nowrap">
                              <div className={`text-sm font-medium ${
                                referee.avg_rbs_score > 0 ? 'text-green-600' : 
                                referee.avg_rbs_score < 0 ? 'text-red-600' : 'text-gray-600'
                              }`}>
                                {referee.avg_rbs_score?.toFixed(3) || 'N/A'}
                              </div>
                            </td>
                            <td className="px-6 py-4 whitespace-nowrap">
                              <button
                                onClick={() => fetchRefereeDetails(referee.referee)}
                                className="text-blue-600 hover:text-blue-900 text-sm font-medium"
                              >
                                View Details
                              </button>
                            </td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                ) : (
                  <div className="text-center py-8 text-gray-500">
                    <p>No referee data available. Upload match data first.</p>
                  </div>
                )}
              </div>
            ) : (
              /* Referee Details View */
              <div className="bg-white p-6 rounded-lg shadow-sm border">
                <div className="flex items-center justify-between mb-6">
                  <div>
                    <h2 className="text-xl font-bold text-gray-900">Referee: {viewingReferee}</h2>
                    <p className="text-gray-600">Detailed bias analysis and team-specific statistics</p>
                  </div>
                  <button
                    onClick={goBackToRefereeList}
                    className="px-4 py-2 bg-gray-600 text-white rounded-lg hover:bg-gray-700"
                  >
                    ← Back to List
                  </button>
                </div>

                {selectedRefereeDetails && (
                  <div className="space-y-6">
                    {/* Summary Stats */}
                    <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
                      <div className="bg-blue-50 p-4 rounded-lg border border-blue-200">
                        <div className="text-2xl font-bold text-blue-600">{selectedRefereeDetails.total_matches}</div>
                        <div className="text-blue-700">Total Matches</div>
                      </div>
                      <div className="bg-green-50 p-4 rounded-lg border border-green-200">
                        <div className="text-2xl font-bold text-green-600">{selectedRefereeDetails.teams_analyzed}</div>
                        <div className="text-green-700">Teams Analyzed</div>
                      </div>
                      <div className="bg-purple-50 p-4 rounded-lg border border-purple-200">
                        <div className="text-2xl font-bold text-purple-600">{selectedRefereeDetails.avg_goals_per_match?.toFixed(1)}</div>
                        <div className="text-purple-700">Avg Goals/Match</div>
                      </div>
                      <div className="bg-orange-50 p-4 rounded-lg border border-orange-200">
                        <div className="text-2xl font-bold text-orange-600">{selectedRefereeDetails.avg_cards_per_match?.toFixed(1)}</div>
                        <div className="text-orange-700">Avg Cards/Match</div>
                      </div>
                    </div>

                    {/* RBS Results Table */}
                    {selectedRefereeDetails.rbs_results && selectedRefereeDetails.rbs_results.length > 0 && (
                      <div className="overflow-x-auto">
                        <h3 className="text-lg font-semibold text-gray-900 mb-4">🎯 Team-Specific Bias Scores</h3>
                        <table className="min-w-full divide-y divide-gray-200">
                          <thead className="bg-gray-50">
                            <tr>
                              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Team</th>
                              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">RBS Score</th>
                              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Matches</th>
                              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Confidence</th>
                            </tr>
                          </thead>
                          <tbody className="bg-white divide-y divide-gray-200">
                            {selectedRefereeDetails.rbs_results.map((result) => (
                              <tr key={result.team_name}>
                                <td className="px-6 py-4 whitespace-nowrap">
                                  <div className="text-sm font-medium text-gray-900">{result.team_name}</div>
                                </td>
                                <td className="px-6 py-4 whitespace-nowrap">
                                  <div className={`text-sm font-medium ${
                                    result.rbs_score > 0 ? 'text-green-600' : 
                                    result.rbs_score < 0 ? 'text-red-600' : 'text-gray-600'
                                  }`}>
                                    {result.rbs_score?.toFixed(3)}
                                  </div>
                                </td>
                                <td className="px-6 py-4 whitespace-nowrap">
                                  <div className="text-sm text-gray-900">{result.matches_with_ref}</div>
                                </td>
                                <td className="px-6 py-4 whitespace-nowrap">
                                  <div className="text-sm text-gray-900">{result.confidence_level}%</div>
                                </td>
                              </tr>
                            ))}
                          </tbody>
                        </table>
                      </div>
                    )}
                  </div>
                )}
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
}

export default App;