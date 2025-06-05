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

  // Fetch initial data
  useEffect(() => {
    fetchStats();
    fetchTeams();
    fetchReferees();
    fetchConfigs();
    fetchRbsConfigs();
    fetchDatasets();
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
            {['dashboard', 'upload', 'predict', 'analysis', 'config', 'rbs-config', 'optimization', 'results'].map((tab) => (
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

                {/* Training Results */}
                {trainingResults && (
                  <div className="mt-4 p-3 bg-green-50 border border-green-200 rounded">
                    <h4 className="text-sm font-semibold text-green-900 mb-2">✅ Training Complete!</h4>
                    <div className="text-xs text-green-800 space-y-1">
                      {trainingResults.training_results && Object.entries(trainingResults.training_results).map(([model, metrics]) => (
                        <div key={model}>
                          <strong>{model}:</strong> {
                            metrics.accuracy ? `Accuracy: ${(metrics.accuracy * 100).toFixed(1)}%` : 
                            `R² Score: ${(metrics.r2_score * 100).toFixed(1)}%`
                          }
                        </div>
                      ))}
                    </div>
                  </div>
                )}
              </div>

              {!predictionResult ? (
                /* Prediction Form */
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
                        className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
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
                        className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
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
                        className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
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
                        className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
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
                        className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                      />
                    </div>
                  </div>

                  {/* Prediction Button */}
                  <div className="flex space-x-4">
                    <button
                      onClick={predictMatch}
                      disabled={predicting || !predictionForm.home_team || !predictionForm.away_team || !predictionForm.referee_name}
                      className="px-6 py-3 bg-blue-600 text-white font-medium rounded-lg hover:bg-blue-700 disabled:bg-gray-400 disabled:cursor-not-allowed flex items-center space-x-2"
                    >
                      {predicting ? (
                        <>
                          <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white"></div>
                          <span>Calculating...</span>
                        </>
                      ) : (
                        <>
                          <span>🔮</span>
                          <span>Predict Match</span>
                        </>
                      )}
                    </button>
                  </div>

                  {/* Algorithm Explanation */}
                  <div className="bg-gray-50 p-4 rounded-lg">
                    <h3 className="text-md font-semibold text-gray-900 mb-2">🤖 ML-Based Prediction Algorithm</h3>
                    <div className="text-sm text-gray-700 space-y-1">
                      <p><strong>1. Feature Engineering:</strong> Extract 45+ features from historical data (team stats, form, referee bias, head-to-head)</p>
                      <p><strong>2. Team Performance:</strong> Offensive/defensive stats, xG per shot, possession, conversion rates</p>
                      <p><strong>3. Situational Factors:</strong> Home advantage, last 5 matches form, referee bias scores (RBS)</p>
                      <p><strong>4. Historical Context:</strong> Head-to-head results, penalties, fouls drawn, card statistics</p>
                      <p><strong>5. ML Classification:</strong> Random Forest model predicts Win/Draw/Loss probabilities</p>
                      <p><strong>6. ML Regression:</strong> Separate models predict Home/Away goals and expected xG</p>
                      <p><strong>7. Feature Scaling:</strong> StandardScaler ensures all features contribute equally</p>
                      <p><strong>8. Model Ensemble:</strong> 5 trained models working together for comprehensive predictions</p>
                    </div>
                    <div className="mt-3 p-3 bg-green-50 rounded text-xs text-green-800">
                      <strong>ML Models:</strong> Random Forest algorithms trained on all historical match data with comprehensive feature engineering. 
                      Models are retrained automatically to incorporate new data and improve accuracy over time.
                    </div>
                  </div>
                </div>
              ) : (
                /* Prediction Results */
                <div className="space-y-6">
                  {predictionResult.success ? (
                    <>
                      {/* Header with predicted score */}
                      <div className="bg-gradient-to-r from-blue-50 to-indigo-50 p-6 rounded-lg border border-blue-200">
                        <div className="text-center">
                          <h3 className="text-lg font-semibold text-gray-800 mb-2">Predicted Match Result</h3>
                          <div className="text-4xl font-bold text-gray-900 mb-2">
                            {predictionResult.home_team} {predictionResult.predicted_home_goals} - {predictionResult.predicted_away_goals} {predictionResult.away_team}
                          </div>
                          <div className="text-sm text-gray-600">
                            Expected xG: {predictionResult.home_xg} - {predictionResult.away_xg}
                          </div>
                          <div className="text-xs text-gray-500 mt-1">
                            Referee: {predictionResult.referee}
                          </div>
                        </div>
                      </div>

                      {/* Match Outcome Probabilities */}
                      <div className="bg-white p-6 rounded-lg border border-gray-200">
                        <h3 className="text-lg font-semibold text-gray-900 mb-4 text-center">Match Outcome Probabilities</h3>
                        <div className="space-y-4">
                          {/* Home Win */}
                          <div>
                            <div className="flex justify-between items-center mb-2">
                              <span className="text-sm font-medium text-gray-700">{predictionResult.home_team} Win</span>
                              <span className="text-sm font-bold text-green-600">{predictionResult.home_win_probability}%</span>
                            </div>
                            <div className="w-full bg-gray-200 rounded-full h-3">
                              <div 
                                className="bg-green-500 h-3 rounded-full transition-all duration-300" 
                                style={{width: `${predictionResult.home_win_probability}%`}}
                              ></div>
                            </div>
                          </div>

                          {/* Draw */}
                          <div>
                            <div className="flex justify-between items-center mb-2">
                              <span className="text-sm font-medium text-gray-700">Draw</span>
                              <span className="text-sm font-bold text-yellow-600">{predictionResult.draw_probability}%</span>
                            </div>
                            <div className="w-full bg-gray-200 rounded-full h-3">
                              <div 
                                className="bg-yellow-500 h-3 rounded-full transition-all duration-300" 
                                style={{width: `${predictionResult.draw_probability}%`}}
                              ></div>
                            </div>
                          </div>

                          {/* Away Win */}
                          <div>
                            <div className="flex justify-between items-center mb-2">
                              <span className="text-sm font-medium text-gray-700">{predictionResult.away_team} Win</span>
                              <span className="text-sm font-bold text-blue-600">{predictionResult.away_win_probability}%</span>
                            </div>
                            <div className="w-full bg-gray-200 rounded-full h-3">
                              <div 
                                className="bg-blue-500 h-3 rounded-full transition-all duration-300" 
                                style={{width: `${predictionResult.away_win_probability}%`}}
                              ></div>
                            </div>
                          </div>
                        </div>

                        {/* Explanation */}
                        <div className="mt-4 p-3 bg-gray-50 rounded-lg">
                          <p className="text-xs text-gray-600">
                            <strong>How probabilities are calculated:</strong> Using Poisson distribution based on predicted goals. 
                            The algorithm simulates thousands of possible match outcomes to determine the likelihood of each result.
                          </p>
                        </div>
                      </div>

                      {/* Detailed Breakdown */}
                      <div className="grid grid-cols-1 gap-6">
                        {/* Algorithm Steps Breakdown */}
                        <div className="bg-white p-6 rounded-lg border">
                          <h4 className="text-lg font-semibold text-gray-900 mb-4">📊 Detailed Algorithm Breakdown</h4>
                          
                          {/* Step 1: Base xG Calculation */}
                          <div className="mb-6 p-4 bg-blue-50 rounded-lg">
                            <h5 className="font-semibold text-blue-900 mb-3">Step 1: Base xG Calculation</h5>
                            <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-sm">
                              <div className="space-y-2">
                                <div className="flex justify-between">
                                  <span className="text-gray-600">{predictionResult.home_team} Shots/Game:</span>
                                  <span className="font-medium">{predictionResult.prediction_breakdown?.home_shots_avg}</span>
                                </div>
                                <div className="flex justify-between">
                                  <span className="text-gray-600">{predictionResult.home_team} xG per Shot:</span>
                                  <span className="font-medium">{predictionResult.prediction_breakdown?.home_xg_per_shot}</span>
                                </div>
                                <div className="flex justify-between border-t pt-2">
                                  <span className="text-blue-700 font-medium">Base xG (Home):</span>
                                  <span className="font-bold text-blue-700">{predictionResult.prediction_breakdown?.home_base_xg}</span>
                                </div>
                              </div>
                              <div className="space-y-2">
                                <div className="flex justify-between">
                                  <span className="text-gray-600">{predictionResult.away_team} Shots/Game:</span>
                                  <span className="font-medium">{predictionResult.prediction_breakdown?.away_shots_avg}</span>
                                </div>
                                <div className="flex justify-between">
                                  <span className="text-gray-600">{predictionResult.away_team} xG per Shot:</span>
                                  <span className="font-medium">{predictionResult.prediction_breakdown?.away_xg_per_shot}</span>
                                </div>
                                <div className="flex justify-between border-t pt-2">
                                  <span className="text-blue-700 font-medium">Base xG (Away):</span>
                                  <span className="font-bold text-blue-700">{predictionResult.prediction_breakdown?.away_base_xg}</span>
                                </div>
                              </div>
                            </div>
                          </div>

                          {/* Step 2: Possession Adjustment */}
                          <div className="mb-6 p-4 bg-green-50 rounded-lg">
                            <h5 className="font-semibold text-green-900 mb-3">Step 2: Possession Adjustment</h5>
                            <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-sm">
                              <div className="space-y-2">
                                <div className="flex justify-between">
                                  <span className="text-gray-600">{predictionResult.home_team} Possession:</span>
                                  <span className="font-medium">{predictionResult.prediction_breakdown?.home_possession_avg}%</span>
                                </div>
                                <div className="flex justify-between">
                                  <span className="text-gray-600">Possession Factor:</span>
                                  <span className="font-medium">{predictionResult.prediction_breakdown?.home_possession_factor}x</span>
                                </div>
                              </div>
                              <div className="space-y-2">
                                <div className="flex justify-between">
                                  <span className="text-gray-600">{predictionResult.away_team} Possession:</span>
                                  <span className="font-medium">{predictionResult.prediction_breakdown?.away_possession_avg}%</span>
                                </div>
                                <div className="flex justify-between">
                                  <span className="text-gray-600">Possession Factor:</span>
                                  <span className="font-medium">{predictionResult.prediction_breakdown?.away_possession_factor}x</span>
                                </div>
                              </div>
                            </div>
                          </div>

                          {/* Step 3: Fouls Drawn Adjustment */}
                          <div className="mb-6 p-4 bg-yellow-50 rounded-lg">
                            <h5 className="font-semibold text-yellow-900 mb-3">Step 3: Fouls Drawn Adjustment</h5>
                            <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-sm">
                              <div className="space-y-2">
                                <div className="flex justify-between">
                                  <span className="text-gray-600">{predictionResult.home_team} Fouls Drawn:</span>
                                  <span className="font-medium">{predictionResult.prediction_breakdown?.home_fouls_drawn_avg}</span>
                                </div>
                                <div className="flex justify-between">
                                  <span className="text-gray-600">Fouls Factor:</span>
                                  <span className="font-medium">{predictionResult.prediction_breakdown?.home_fouls_factor}x</span>
                                </div>
                              </div>
                              <div className="space-y-2">
                                <div className="flex justify-between">
                                  <span className="text-gray-600">{predictionResult.away_team} Fouls Drawn:</span>
                                  <span className="font-medium">{predictionResult.prediction_breakdown?.away_fouls_drawn_avg}</span>
                                </div>
                                <div className="flex justify-between">
                                  <span className="text-gray-600">Fouls Factor:</span>
                                  <span className="font-medium">{predictionResult.prediction_breakdown?.away_fouls_factor}x</span>
                                </div>
                              </div>
                            </div>
                          </div>

                          {/* Step 4: Penalty Factor */}
                          <div className="mb-6 p-4 bg-purple-50 rounded-lg">
                            <h5 className="font-semibold text-purple-900 mb-3">Step 4: Penalty Factor</h5>
                            <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-sm">
                              <div className="space-y-2">
                                <div className="flex justify-between">
                                  <span className="text-gray-600">{predictionResult.home_team} Penalties/Game:</span>
                                  <span className="font-medium">{predictionResult.prediction_breakdown?.home_penalties_avg}</span>
                                </div>
                                <div className="flex justify-between">
                                  <span className="text-gray-600">Penalty Conversion:</span>
                                  <span className="font-medium">{Math.round((predictionResult.prediction_breakdown?.home_penalty_conversion || 0) * 100)}%</span>
                                </div>
                                <div className="flex justify-between border-t pt-2">
                                  <span className="text-purple-700 font-medium">Penalty xG Added:</span>
                                  <span className="font-bold text-purple-700">+{predictionResult.prediction_breakdown?.home_penalty_xg}</span>
                                </div>
                              </div>
                              <div className="space-y-2">
                                <div className="flex justify-between">
                                  <span className="text-gray-600">{predictionResult.away_team} Penalties/Game:</span>
                                  <span className="font-medium">{predictionResult.prediction_breakdown?.away_penalties_avg}</span>
                                </div>
                                <div className="flex justify-between">
                                  <span className="text-gray-600">Penalty Conversion:</span>
                                  <span className="font-medium">{Math.round((predictionResult.prediction_breakdown?.away_penalty_conversion || 0) * 100)}%</span>
                                </div>
                                <div className="flex justify-between border-t pt-2">
                                  <span className="text-purple-700 font-medium">Penalty xG Added:</span>
                                  <span className="font-bold text-purple-700">+{predictionResult.prediction_breakdown?.away_penalty_xg}</span>
                                </div>
                              </div>
                            </div>
                          </div>

                          {/* Step 5: Team Quality Adjustment */}
                          <div className="mb-6 p-4 bg-indigo-50 rounded-lg">
                            <h5 className="font-semibold text-indigo-900 mb-3">Step 5: Team Quality Adjustment (PPG)</h5>
                            <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-sm">
                              <div className="space-y-2">
                                <div className="flex justify-between">
                                  <span className="text-gray-600">{predictionResult.home_team} PPG:</span>
                                  <span className="font-medium">{predictionResult.prediction_breakdown?.home_ppg}</span>
                                </div>
                              </div>
                              <div className="space-y-2">
                                <div className="flex justify-between">
                                  <span className="text-gray-600">{predictionResult.away_team} PPG:</span>
                                  <span className="font-medium">{predictionResult.prediction_breakdown?.away_ppg}</span>
                                </div>
                              </div>
                              <div className="md:col-span-2 border-t pt-2">
                                <div className="flex justify-between">
                                  <span className="text-indigo-700 font-medium">PPG Adjustment:</span>
                                  <span className={`font-bold ${predictionResult.prediction_breakdown?.ppg_adjustment > 0 ? 'text-green-600' : predictionResult.prediction_breakdown?.ppg_adjustment < 0 ? 'text-red-600' : 'text-gray-600'}`}>
                                    {predictionResult.prediction_breakdown?.ppg_adjustment > 0 ? '+' : ''}{predictionResult.prediction_breakdown?.ppg_adjustment}
                                  </span>
                                </div>
                              </div>
                            </div>
                          </div>

                          {/* Step 6: Referee Bias Adjustment */}
                          <div className="mb-6 p-4 bg-red-50 rounded-lg">
                            <h5 className="font-semibold text-red-900 mb-3">Step 6: Referee Bias Adjustment</h5>
                            <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-sm">
                              <div className="space-y-2">
                                <div className="flex justify-between">
                                  <span className="text-gray-600">{predictionResult.home_team} RBS:</span>
                                  <span className="font-medium">{predictionResult.confidence_factors?.home_rbs_score}</span>
                                </div>
                                <div className="flex justify-between border-t pt-2">
                                  <span className="text-red-700 font-medium">Referee Adjustment:</span>
                                  <span className={`font-bold ${predictionResult.prediction_breakdown?.home_ref_adjustment > 0 ? 'text-green-600' : predictionResult.prediction_breakdown?.home_ref_adjustment < 0 ? 'text-red-600' : 'text-gray-600'}`}>
                                    {predictionResult.prediction_breakdown?.home_ref_adjustment > 0 ? '+' : ''}{predictionResult.prediction_breakdown?.home_ref_adjustment}
                                  </span>
                                </div>
                              </div>
                              <div className="space-y-2">
                                <div className="flex justify-between">
                                  <span className="text-gray-600">{predictionResult.away_team} RBS:</span>
                                  <span className="font-medium">{predictionResult.confidence_factors?.away_rbs_score}</span>
                                </div>
                                <div className="flex justify-between border-t pt-2">
                                  <span className="text-red-700 font-medium">Referee Adjustment:</span>
                                  <span className={`font-bold ${predictionResult.prediction_breakdown?.away_ref_adjustment > 0 ? 'text-green-600' : predictionResult.prediction_breakdown?.away_ref_adjustment < 0 ? 'text-red-600' : 'text-gray-600'}`}>
                                    {predictionResult.prediction_breakdown?.away_ref_adjustment > 0 ? '+' : ''}{predictionResult.prediction_breakdown?.away_ref_adjustment}
                                  </span>
                                </div>
                              </div>
                            </div>
                          </div>

                          {/* Step 7: Final Conversion */}
                          <div className="mb-6 p-4 bg-gray-800 text-white rounded-lg">
                            <h5 className="font-semibold mb-3">Step 7: Final Goal Conversion</h5>
                            <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-sm">
                              <div className="space-y-2">
                                <div className="flex justify-between">
                                  <span className="text-gray-300">Final xG:</span>
                                  <span className="font-medium">{predictionResult.home_xg}</span>
                                </div>
                                <div className="flex justify-between">
                                  <span className="text-gray-300">Conversion Rate (goals/xG):</span>
                                  <span className="font-medium">{predictionResult.prediction_breakdown?.home_conversion_rate}</span>
                                </div>
                                <div className="flex justify-between border-t pt-2 border-gray-600">
                                  <span className="font-bold text-white">Predicted Goals:</span>
                                  <span className="font-bold text-white">{predictionResult.predicted_home_goals}</span>
                                </div>
                              </div>
                              <div className="space-y-2">
                                <div className="flex justify-between">
                                  <span className="text-gray-300">Final xG:</span>
                                  <span className="font-medium">{predictionResult.away_xg}</span>
                                </div>
                                <div className="flex justify-between">
                                  <span className="text-gray-300">Conversion Rate (goals/xG):</span>
                                  <span className="font-medium">{predictionResult.prediction_breakdown?.away_conversion_rate}</span>
                                </div>
                                <div className="flex justify-between border-t pt-2 border-gray-600">
                                  <span className="font-bold text-white">Predicted Goals:</span>
                                  <span className="font-bold text-white">{predictionResult.predicted_away_goals}</span>
                                </div>
                              </div>
                            </div>
                          </div>

                          {/* Step 8: Probability Calculation */}
                          <div className="p-4 bg-gradient-to-r from-blue-100 to-purple-100 rounded-lg">
                            <h5 className="font-semibold text-gray-900 mb-3">Step 8: Probability Calculation</h5>
                            <div className="text-sm text-gray-700">
                              <p className="mb-2">Using Poisson distribution with predicted goals ({predictionResult.predicted_home_goals} vs {predictionResult.predicted_away_goals}):</p>
                              <div className="grid grid-cols-3 gap-4 text-center">
                                <div className="bg-green-200 p-2 rounded">
                                  <div className="font-bold text-green-800">{predictionResult.home_win_probability}%</div>
                                  <div className="text-xs text-green-700">{predictionResult.home_team} Win</div>
                                </div>
                                <div className="bg-yellow-200 p-2 rounded">
                                  <div className="font-bold text-yellow-800">{predictionResult.draw_probability}%</div>
                                  <div className="text-xs text-yellow-700">Draw</div>
                                </div>
                                <div className="bg-blue-200 p-2 rounded">
                                  <div className="font-bold text-blue-800">{predictionResult.away_win_probability}%</div>
                                  <div className="text-xs text-blue-700">{predictionResult.away_team} Win</div>
                                </div>
                              </div>
                            </div>
                          </div>
                        </div>

                        {/* Confidence Factors */}
                        <div className="bg-white p-4 rounded-lg border">
                          <h4 className="text-md font-semibold text-gray-900 mb-3">Confidence Factors</h4>
                          <div className="space-y-2 text-sm">
                            <div className="flex justify-between">
                              <span className="text-gray-600">Overall Confidence:</span>
                              <span className="font-medium">{Math.round(predictionResult.confidence_factors?.overall_confidence || 0)}%</span>
                            </div>
                            <div className="flex justify-between">
                              <span className="text-gray-600">Home Matches:</span>
                              <span className="font-medium">{predictionResult.confidence_factors?.home_matches_count}</span>
                            </div>
                            <div className="flex justify-between">
                              <span className="text-gray-600">Away Matches:</span>
                              <span className="font-medium">{predictionResult.confidence_factors?.away_matches_count}</span>
                            </div>
                            <div className="flex justify-between">
                              <span className="text-gray-600">Home PPG:</span>
                              <span className="font-medium">{predictionResult.confidence_factors?.home_ppg}</span>
                            </div>
                            <div className="flex justify-between">
                              <span className="text-gray-600">Away PPG:</span>
                              <span className="font-medium">{predictionResult.confidence_factors?.away_ppg}</span>
                            </div>
                            <div className="flex justify-between">
                              <span className="text-gray-600">Home RBS:</span>
                              <span className={`font-medium ${predictionResult.confidence_factors?.home_rbs_score > 0 ? 'text-green-600' : predictionResult.confidence_factors?.home_rbs_score < 0 ? 'text-red-600' : 'text-gray-600'}`}>
                                {predictionResult.confidence_factors?.home_rbs_score > 0 ? '+' : ''}{predictionResult.confidence_factors?.home_rbs_score}
                              </span>
                            </div>
                            <div className="flex justify-between">
                              <span className="text-gray-600">Away RBS:</span>
                              <span className={`font-medium ${predictionResult.confidence_factors?.away_rbs_score > 0 ? 'text-green-600' : predictionResult.confidence_factors?.away_rbs_score < 0 ? 'text-red-600' : 'text-gray-600'}`}>
                                {predictionResult.confidence_factors?.away_rbs_score > 0 ? '+' : ''}{predictionResult.confidence_factors?.away_rbs_score}
                              </span>
                            </div>
                          </div>
                        </div>
                      </div>

                      {/* Comprehensive Team Stats Used */}
                      <div className="bg-white p-4 rounded-lg border">
                        <h4 className="text-md font-semibold text-gray-900 mb-3">Team Performance Analysis (Used in Prediction)</h4>
                        <div className="grid grid-cols-1 md:grid-cols-2 gap-6 text-sm">
                          <div>
                            <h5 className="font-medium text-gray-800 mb-3">{predictionResult.home_team} (Home)</h5>
                            <div className="space-y-2">
                              <div className="grid grid-cols-2 gap-2">
                                <div className="flex justify-between">
                                  <span className="text-gray-600">Shots/Game:</span>
                                  <span className="font-medium">{predictionResult.prediction_breakdown?.home_shots_avg}</span>
                                </div>
                                <div className="flex justify-between">
                                  <span className="text-gray-600">xG per Shot:</span>
                                  <span className="font-medium">{predictionResult.prediction_breakdown?.home_xg_per_shot}</span>
                                </div>
                              </div>
                              <div className="grid grid-cols-2 gap-2">
                                <div className="flex justify-between">
                                  <span className="text-gray-600">Goals/Game:</span>
                                  <span className="font-medium">{predictionResult.prediction_breakdown?.home_goals_avg}</span>
                                </div>
                                <div className="flex justify-between">
                                  <span className="text-gray-600">Conversion:</span>
                                  <span className="font-medium">{predictionResult.prediction_breakdown?.home_conversion_rate}</span>
                                </div>
                              </div>
                              <div className="grid grid-cols-2 gap-2">
                                <div className="flex justify-between">
                                  <span className="text-gray-600">Possession:</span>
                                  <span className="font-medium">{predictionResult.prediction_breakdown?.home_possession_avg}%</span>
                                </div>
                                <div className="flex justify-between">
                                  <span className="text-gray-600">Fouls Drawn:</span>
                                  <span className="font-medium">{predictionResult.prediction_breakdown?.home_fouls_drawn_avg}</span>
                                </div>
                              </div>
                              <div className="flex justify-between">
                                <span className="text-gray-600">Penalties/Game:</span>
                                <span className="font-medium">{predictionResult.prediction_breakdown?.home_penalties_avg}</span>
                              </div>
                              <div className="flex justify-between">
                                <span className="text-gray-600">Penalty Conversion:</span>
                                <span className="font-medium">{Math.round((predictionResult.prediction_breakdown?.home_penalty_conversion || 0) * 100)}%</span>
                              </div>
                            </div>
                          </div>
                          <div>
                            <h5 className="font-medium text-gray-800 mb-3">{predictionResult.away_team} (Away)</h5>
                            <div className="space-y-2">
                              <div className="grid grid-cols-2 gap-2">
                                <div className="flex justify-between">
                                  <span className="text-gray-600">Shots/Game:</span>
                                  <span className="font-medium">{predictionResult.prediction_breakdown?.away_shots_avg}</span>
                                </div>
                                <div className="flex justify-between">
                                  <span className="text-gray-600">xG per Shot:</span>
                                  <span className="font-medium">{predictionResult.prediction_breakdown?.away_xg_per_shot}</span>
                                </div>
                              </div>
                              <div className="grid grid-cols-2 gap-2">
                                <div className="flex justify-between">
                                  <span className="text-gray-600">Goals/Game:</span>
                                  <span className="font-medium">{predictionResult.prediction_breakdown?.away_goals_avg}</span>
                                </div>
                                <div className="flex justify-between">
                                  <span className="text-gray-600">Conversion:</span>
                                  <span className="font-medium">{predictionResult.prediction_breakdown?.away_conversion_rate}</span>
                                </div>
                              </div>
                              <div className="grid grid-cols-2 gap-2">
                                <div className="flex justify-between">
                                  <span className="text-gray-600">Possession:</span>
                                  <span className="font-medium">{predictionResult.prediction_breakdown?.away_possession_avg}%</span>
                                </div>
                                <div className="flex justify-between">
                                  <span className="text-gray-600">Fouls Drawn:</span>
                                  <span className="font-medium">{predictionResult.prediction_breakdown?.away_fouls_drawn_avg}</span>
                                </div>
                              </div>
                              <div className="flex justify-between">
                                <span className="text-gray-600">Penalties/Game:</span>
                                <span className="font-medium">{predictionResult.prediction_breakdown?.away_penalties_avg}</span>
                              </div>
                              <div className="flex justify-between">
                                <span className="text-gray-600">Penalty Conversion:</span>
                                <span className="font-medium">{Math.round((predictionResult.prediction_breakdown?.away_penalty_conversion || 0) * 100)}%</span>
                              </div>
                            </div>
                          </div>
                        </div>
                      </div>

                      {/* Data Quality Indicators */}
                      {predictionResult.confidence_factors?.data_quality && (
                        <div className="bg-gray-50 p-4 rounded-lg border">
                          <h4 className="text-md font-semibold text-gray-900 mb-3">Data Quality</h4>
                          <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
                            <div className="text-center">
                              <div className={`inline-block px-2 py-1 rounded text-xs font-medium ${
                                predictionResult.confidence_factors.data_quality.home_shots_data === 'good' ? 'bg-green-100 text-green-800' : 'bg-yellow-100 text-yellow-800'
                              }`}>
                                {predictionResult.confidence_factors.data_quality.home_shots_data}
                              </div>
                              <div className="text-gray-600 mt-1">Home Shots</div>
                            </div>
                            <div className="text-center">
                              <div className={`inline-block px-2 py-1 rounded text-xs font-medium ${
                                predictionResult.confidence_factors.data_quality.away_shots_data === 'good' ? 'bg-green-100 text-green-800' : 'bg-yellow-100 text-yellow-800'
                              }`}>
                                {predictionResult.confidence_factors.data_quality.away_shots_data}
                              </div>
                              <div className="text-gray-600 mt-1">Away Shots</div>
                            </div>
                            <div className="text-center">
                              <div className={`inline-block px-2 py-1 rounded text-xs font-medium ${
                                predictionResult.confidence_factors.data_quality.home_xg_data === 'good' ? 'bg-green-100 text-green-800' : 'bg-yellow-100 text-yellow-800'
                              }`}>
                                {predictionResult.confidence_factors.data_quality.home_xg_data}
                              </div>
                              <div className="text-gray-600 mt-1">Home xG</div>
                            </div>
                            <div className="text-center">
                              <div className={`inline-block px-2 py-1 rounded text-xs font-medium ${
                                predictionResult.confidence_factors.data_quality.away_xg_data === 'good' ? 'bg-green-100 text-green-800' : 'bg-yellow-100 text-yellow-800'
                              }`}>
                                {predictionResult.confidence_factors.data_quality.away_xg_data}
                              </div>
                              <div className="text-gray-600 mt-1">Away xG</div>
                            </div>
                          </div>
                        </div>
                      )}

                      {/* Enhanced Algorithm Explanation */}
                      <div className="bg-blue-50 p-4 rounded-lg border border-blue-200">
                        <h4 className="text-md font-semibold text-blue-900 mb-3">Enhanced Algorithm Explanation</h4>
                        <div className="text-sm text-blue-800 space-y-2">
                          <p><strong>🎯 xG Calculation Methods:</strong></p>
                          <ul className="list-disc list-inside ml-4 space-y-1">
                            <li>Shot-based xG (40%): Team shots × xG per shot ratio</li>
                            <li>Historical xG average (40%): Direct team xG averages</li>
                            <li>Opponent defense factor (20%): How teams perform vs specific opposition</li>
                          </ul>
                          <p><strong>📊 Additional Factors:</strong></p>
                          <ul className="list-disc list-inside ml-4 space-y-1">
                            <li><strong>Possession Adjustment:</strong> ±1% per percentage point above/below 50%</li>
                            <li><strong>Fouls Drawn Factor:</strong> Teams drawing more fouls get set pieces & penalties</li>
                            <li><strong>Penalty Boost:</strong> Penalty attempts × 0.79 xG × team penalty conversion rate</li>
                            <li><strong>RBS Scaling:</strong> Referee bias of -5.0 = -1.0 xG adjustment</li>
                            <li><strong>Team Quality (PPG):</strong> Points per game difference × 0.15 factor</li>
                          </ul>
                        </div>
                      </div>

                      {/* Action Buttons */}
                      <div className="flex space-x-4">
                        <button
                          onClick={resetPrediction}
                          className="px-6 py-2 bg-gray-100 text-gray-700 font-medium rounded-lg hover:bg-gray-200"
                        >
                          Predict Another Match
                        </button>
                      </div>
                    </>
                  ) : (
                    /* Error State */
                    <div className="bg-red-50 p-4 rounded-lg border border-red-200">
                      <h3 className="text-lg font-semibold text-red-800 mb-2">Prediction Failed</h3>
                      <p className="text-red-700">{predictionResult.prediction_breakdown?.error || 'Unknown error occurred'}</p>
                      <button
                        onClick={resetPrediction}
                        className="mt-4 px-4 py-2 bg-red-100 text-red-800 font-medium rounded-lg hover:bg-red-200"
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

        {/* Configuration Tab */}
        {activeTab === 'config' && (
          <div className="space-y-6">
            <div className="bg-white p-6 rounded-lg shadow-sm border">
              <h2 className="text-xl font-bold text-gray-900 mb-4">⚙️ Prediction Algorithm Configuration</h2>
              <p className="text-gray-600 mb-6">
                Customize the weights and parameters used in the match prediction algorithm. Each setting controls how different factors influence the final prediction.
              </p>

              {/* Configuration Guide */}
              <div className="bg-gradient-to-r from-blue-50 to-indigo-50 border border-blue-200 rounded-lg p-4 mb-6">
                <h3 className="text-lg font-semibold text-blue-900 mb-3">📚 Configuration Guide</h3>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-sm text-blue-800">
                  <div>
                    <h4 className="font-medium mb-2">🎯 Algorithm Overview</h4>
                    <p className="mb-2">The prediction algorithm works in 5 steps:</p>
                    <ol className="list-decimal list-inside space-y-1 text-xs">
                      <li><strong>Calculate base xG</strong> using 3 weighted methods</li>
                      <li><strong>Apply performance adjustments</strong> (possession, fouls, etc.)</li>
                      <li><strong>Add penalty boost</strong> based on team penalty frequency</li>
                      <li><strong>Apply team quality</strong> (PPG) and referee bias</li>
                      <li><strong>Convert to goals</strong> using team conversion rates</li>
                    </ol>
                  </div>
                  <div>
                    <h4 className="font-medium mb-2">🔧 Weight Strategies</h4>
                    <div className="space-y-2 text-xs">
                      <div><strong>Conservative:</strong> Higher historical weight (0.5), lower adjustments</div>
                      <div><strong>Aggressive:</strong> Higher shot-based weight (0.5), stronger adjustments</div>
                      <div><strong>Balanced:</strong> Equal weights (0.4/0.4/0.2), moderate adjustments</div>
                      <div><strong>Defensive-focused:</strong> Higher opponent defense weight (0.3)</div>
                    </div>
                  </div>
                </div>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-6">
                {/* Configuration Selection */}
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Select Configuration
                  </label>
                  <select
                    value={configName}
                    onChange={(e) => {
                      setConfigName(e.target.value);
                      fetchConfig(e.target.value);
                    }}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                  >
                    <option value="default">Default Configuration</option>
                    {configs.map(config => (
                      <option key={config.config_name} value={config.config_name}>
                        {config.config_name}
                      </option>
                    ))}
                  </select>
                </div>

                {/* Action Buttons */}
                <div className="flex items-end space-x-2">
                  <button
                    onClick={() => {
                      setConfigEditing(true);
                      resetConfigForm();
                    }}
                    className="px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700"
                  >
                    Create New
                  </button>
                  <button
                    onClick={() => {
                      setConfigEditing(true);
                      setConfigForm(currentConfig);
                    }}
                    disabled={!currentConfig}
                    className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:bg-gray-400"
                  >
                    Edit Current
                  </button>
                  <div className="ml-4">
                    <label className="block text-xs font-medium text-gray-600 mb-1">Quick Templates:</label>
                    <select
                      onChange={(e) => {
                        if (e.target.value) {
                          const templates = {
                            conservative: {
                              config_name: 'conservative',
                              xg_shot_based_weight: 0.3,
                              xg_historical_weight: 0.5,
                              xg_opponent_defense_weight: 0.2,
                              ppg_adjustment_factor: 0.10,
                              possession_adjustment_per_percent: 0.005,
                              fouls_drawn_factor: 0.015,
                              penalty_xg_value: 0.75,
                              rbs_scaling_factor: 0.15
                            },
                            aggressive: {
                              config_name: 'aggressive',
                              xg_shot_based_weight: 0.5,
                              xg_historical_weight: 0.3,
                              xg_opponent_defense_weight: 0.2,
                              ppg_adjustment_factor: 0.20,
                              possession_adjustment_per_percent: 0.015,
                              fouls_drawn_factor: 0.025,
                              penalty_xg_value: 0.85,
                              rbs_scaling_factor: 0.25
                            },
                            defensive: {
                              config_name: 'defensive-focused',
                              xg_shot_based_weight: 0.35,
                              xg_historical_weight: 0.35,
                              xg_opponent_defense_weight: 0.3,
                              ppg_adjustment_factor: 0.12,
                              possession_adjustment_per_percent: 0.008,
                              fouls_drawn_factor: 0.018,
                              penalty_xg_value: 0.79,
                              rbs_scaling_factor: 0.18
                            }
                          };
                          const template = templates[e.target.value];
                          setConfigForm({
                            ...configForm,
                            ...template,
                            fouls_drawn_baseline: 10.0,
                            fouls_drawn_min_multiplier: 0.8,
                            fouls_drawn_max_multiplier: 1.3,
                            min_conversion_rate: 0.5,
                            max_conversion_rate: 2.0,
                            min_xg_per_match: 0.1,
                            confidence_matches_multiplier: 4,
                            max_confidence: 90,
                            min_confidence: 20
                          });
                          setConfigEditing(true);
                          e.target.value = '';
                        }
                      }}
                      className="px-3 py-1 text-xs border border-gray-300 rounded focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                    >
                      <option value="">Select Template</option>
                      <option value="conservative">Conservative</option>
                      <option value="aggressive">Aggressive</option>
                      <option value="defensive">Defensive-focused</option>
                    </select>
                  </div>
                </div>
              </div>

              {/* Configuration Form */}
              {configEditing && (
                <div className="border-t pt-6">
                  <h3 className="text-lg font-semibold text-gray-900 mb-4">
                    {configForm.config_name === 'default' ? 'Edit Configuration' : 'Create Configuration'}
                  </h3>

                  <div className="space-y-6">
                    {/* Configuration Name */}
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-2">
                        Configuration Name
                      </label>
                      <input
                        type="text"
                        value={configForm.config_name}
                        onChange={(e) => handleConfigFormChange('config_name', e.target.value)}
                        className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                        placeholder="Enter configuration name"
                      />
                    </div>

                    {/* xG Calculation Weights */}
                    <div className="border rounded-lg p-4">
                      <h4 className="font-medium text-gray-900 mb-3">xG Calculation Weights (must sum to 1.0)</h4>
                      <div className="mb-3 text-sm text-gray-600 bg-blue-50 p-3 rounded">
                        <strong>How xG is calculated:</strong> The algorithm combines three methods to calculate expected goals (xG) for each team. These weights determine how much influence each method has on the final xG calculation.
                      </div>
                      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                        <div>
                          <label className="block text-sm font-medium text-gray-700 mb-1">Shot-based Weight</label>
                          <input
                            type="number"
                            step="0.01"
                            min="0"
                            max="1"
                            value={configForm.xg_shot_based_weight}
                            onChange={(e) => handleConfigFormChange('xg_shot_based_weight', e.target.value)}
                            className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                          />
                          <div className="mt-1 text-xs text-gray-500">
                            <strong>What it does:</strong> Uses team's average shots per game × xG per shot ratio. Higher values favor teams with more shooting volume and quality.
                          </div>
                        </div>
                        <div>
                          <label className="block text-sm font-medium text-gray-700 mb-1">Historical Weight</label>
                          <input
                            type="number"
                            step="0.01"
                            min="0"
                            max="1"
                            value={configForm.xg_historical_weight}
                            onChange={(e) => handleConfigFormChange('xg_historical_weight', e.target.value)}
                            className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                          />
                          <div className="mt-1 text-xs text-gray-500">
                            <strong>What it does:</strong> Uses team's direct historical xG average. Higher values favor teams with consistently high xG regardless of shot volume.
                          </div>
                        </div>
                        <div>
                          <label className="block text-sm font-medium text-gray-700 mb-1">Opponent Defense Weight</label>
                          <input
                            type="number"
                            step="0.01"
                            min="0"
                            max="1"
                            value={configForm.xg_opponent_defense_weight}
                            onChange={(e) => handleConfigFormChange('xg_opponent_defense_weight', e.target.value)}
                            className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                          />
                          <div className="mt-1 text-xs text-gray-500">
                            <strong>What it does:</strong> Considers how many goals the opponent typically concedes. Higher values favor teams playing against weaker defenses.
                          </div>
                        </div>
                      </div>
                      <div className="mt-2 text-sm text-gray-600">
                        Current sum: {(configForm.xg_shot_based_weight + configForm.xg_historical_weight + configForm.xg_opponent_defense_weight).toFixed(2)}
                      </div>
                    </div>

                    {/* Team Performance Adjustments */}
                    <div className="border rounded-lg p-4">
                      <h4 className="font-medium text-gray-900 mb-3">Team Performance Adjustments</h4>
                      <div className="mb-3 text-sm text-gray-600 bg-green-50 p-3 rounded">
                        <strong>Performance modifiers:</strong> These factors adjust the base xG calculation based on team playing style and quality metrics.
                      </div>
                      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                        <div>
                          <label className="block text-sm font-medium text-gray-700 mb-1">PPG Adjustment Factor</label>
                          <input
                            type="number"
                            step="0.01"
                            value={configForm.ppg_adjustment_factor}
                            onChange={(e) => handleConfigFormChange('ppg_adjustment_factor', e.target.value)}
                            className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                          />
                          <div className="mt-1 text-xs text-gray-500">
                            <strong>What it does:</strong> Adjusts xG based on team quality (Points Per Game difference). If Arsenal has 2.0 PPG and opponent has 1.0 PPG, Arsenal gets +0.15 xG boost (with default 0.15 factor).
                          </div>
                        </div>
                        <div>
                          <label className="block text-sm font-medium text-gray-700 mb-1">Possession Adjustment (/percent)</label>
                          <input
                            type="number"
                            step="0.001"
                            value={configForm.possession_adjustment_per_percent}
                            onChange={(e) => handleConfigFormChange('possession_adjustment_per_percent', e.target.value)}
                            className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                          />
                          <div className="mt-1 text-xs text-gray-500">
                            <strong>What it does:</strong> Teams with higher possession create more chances. For every 1% possession above 50%, xG increases by this factor. Default 0.01 = 1% boost per possession percent.
                          </div>
                        </div>
                        <div>
                          <label className="block text-sm font-medium text-gray-700 mb-1">Fouls Drawn Factor</label>
                          <input
                            type="number"
                            step="0.001"
                            value={configForm.fouls_drawn_factor}
                            onChange={(e) => handleConfigFormChange('fouls_drawn_factor', e.target.value)}
                            className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                          />
                          <div className="mt-1 text-xs text-gray-500">
                            <strong>What it does:</strong> Teams that draw more fouls get more set pieces and penalties. For every foul drawn above baseline (10), xG increases by this factor.
                          </div>
                        </div>
                        <div>
                          <label className="block text-sm font-medium text-gray-700 mb-1">Fouls Drawn Baseline</label>
                          <input
                            type="number"
                            step="0.1"
                            value={configForm.fouls_drawn_baseline}
                            onChange={(e) => handleConfigFormChange('fouls_drawn_baseline', e.target.value)}
                            className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                          />
                          <div className="mt-1 text-xs text-gray-500">
                            <strong>What it does:</strong> The "normal" number of fouls drawn per match. Teams drawing more than this get a boost, teams drawing less get a penalty.
                          </div>
                        </div>
                      </div>
                    </div>

                    {/* Penalty & Referee Settings */}
                    <div className="border rounded-lg p-4">
                      <h4 className="font-medium text-gray-900 mb-3">Penalty & Referee Settings</h4>
                      <div className="mb-3 text-sm text-gray-600 bg-yellow-50 p-3 rounded">
                        <strong>Penalty and referee influence:</strong> How penalties and referee bias affect the final prediction.
                      </div>
                      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                        <div>
                          <label className="block text-sm font-medium text-gray-700 mb-1">Penalty xG Value</label>
                          <input
                            type="number"
                            step="0.01"
                            value={configForm.penalty_xg_value}
                            onChange={(e) => handleConfigFormChange('penalty_xg_value', e.target.value)}
                            className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                          />
                          <div className="mt-1 text-xs text-gray-500">
                            <strong>What it does:</strong> The xG value of each penalty. Professional football standard is 0.79. Each penalty attempt adds this value × team conversion rate to xG.
                          </div>
                        </div>
                        <div>
                          <label className="block text-sm font-medium text-gray-700 mb-1">RBS Scaling Factor</label>
                          <input
                            type="number"
                            step="0.01"
                            value={configForm.rbs_scaling_factor}
                            onChange={(e) => handleConfigFormChange('rbs_scaling_factor', e.target.value)}
                            className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                          />
                          <div className="mt-1 text-xs text-gray-500">
                            <strong>What it does:</strong> How much referee bias affects xG. Default 0.2 means RBS score of -5.0 gives -1.0 xG adjustment. Higher values make referee bias more influential.
                          </div>
                        </div>
                      </div>
                    </div>

                    {/* Bounds & Limits */}
                    <div className="border rounded-lg p-4">
                      <h4 className="font-medium text-gray-900 mb-3">Bounds & Limits</h4>
                      <div className="mb-3 text-sm text-gray-600 bg-purple-50 p-3 rounded">
                        <strong>Safety constraints:</strong> These prevent unrealistic predictions by capping extreme values.
                      </div>
                      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                        <div>
                          <label className="block text-sm font-medium text-gray-700 mb-1">Min Conversion Rate</label>
                          <input
                            type="number"
                            step="0.1"
                            value={configForm.min_conversion_rate}
                            onChange={(e) => handleConfigFormChange('min_conversion_rate', e.target.value)}
                            className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                          />
                          <div className="mt-1 text-xs text-gray-500">
                            <strong>What it does:</strong> Minimum goals-per-xG ratio. Prevents predictions being too low for poor finishing teams. Default 0.5 means teams score at least half their xG.
                          </div>
                        </div>
                        <div>
                          <label className="block text-sm font-medium text-gray-700 mb-1">Max Conversion Rate</label>
                          <input
                            type="number"
                            step="0.1"
                            value={configForm.max_conversion_rate}
                            onChange={(e) => handleConfigFormChange('max_conversion_rate', e.target.value)}
                            className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                          />
                          <div className="mt-1 text-xs text-gray-500">
                            <strong>What it does:</strong> Maximum goals-per-xG ratio. Prevents predictions being too high for clinical finishing teams. Default 2.0 means teams score at most double their xG.
                          </div>
                        </div>
                        <div>
                          <label className="block text-sm font-medium text-gray-700 mb-1">Min xG per Match</label>
                          <input
                            type="number"
                            step="0.01"
                            value={configForm.min_xg_per_match}
                            onChange={(e) => handleConfigFormChange('min_xg_per_match', e.target.value)}
                            className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                          />
                          <div className="mt-1 text-xs text-gray-500">
                            <strong>What it does:</strong> Minimum xG any team can have in a match. Prevents unrealistic 0.0 xG predictions. Every team creates at least some chances.
                          </div>
                        </div>
                      </div>
                    </div>

                    {/* Confidence Calculation */}
                    <div className="border rounded-lg p-4">
                      <h4 className="font-medium text-gray-900 mb-3">Confidence Calculation</h4>
                      <div className="mb-3 text-sm text-gray-600 bg-indigo-50 p-3 rounded">
                        <strong>Prediction reliability:</strong> How the system calculates confidence in its predictions based on data quality.
                      </div>
                      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                        <div>
                          <label className="block text-sm font-medium text-gray-700 mb-1">Confidence Matches Multiplier</label>
                          <input
                            type="number"
                            step="1"
                            value={configForm.confidence_matches_multiplier}
                            onChange={(e) => handleConfigFormChange('confidence_matches_multiplier', e.target.value)}
                            className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                          />
                          <div className="mt-1 text-xs text-gray-500">
                            <strong>What it does:</strong> More matches = higher confidence. Average match count × this multiplier = confidence percentage. Default 4 means 20 matches = 80% confidence.
                          </div>
                        </div>
                        <div>
                          <label className="block text-sm font-medium text-gray-700 mb-1">Max Confidence</label>
                          <input
                            type="number"
                            step="1"
                            value={configForm.max_confidence}
                            onChange={(e) => handleConfigFormChange('max_confidence', e.target.value)}
                            className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                          />
                          <div className="mt-1 text-xs text-gray-500">
                            <strong>What it does:</strong> Maximum confidence percentage. Even with lots of data, confidence is capped at this level to account for football's unpredictability.
                          </div>
                        </div>
                        <div>
                          <label className="block text-sm font-medium text-gray-700 mb-1">Min Confidence</label>
                          <input
                            type="number"
                            step="1"
                            value={configForm.min_confidence}
                            onChange={(e) => handleConfigFormChange('min_confidence', e.target.value)}
                            className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                          />
                          <div className="mt-1 text-xs text-gray-500">
                            <strong>What it does:</strong> Minimum confidence percentage. Even with little data, predictions have at least this confidence level. Prevents 0% confidence.
                          </div>
                        </div>
                      </div>
                    </div>

                    {/* Action Buttons */}
                    <div className="flex space-x-4">
                      <button
                        onClick={saveConfig}
                        className="px-6 py-2 bg-green-600 text-white font-medium rounded-lg hover:bg-green-700"
                      >
                        Save Configuration
                      </button>
                      <button
                        onClick={() => setConfigEditing(false)}
                        className="px-6 py-2 bg-gray-100 text-gray-700 font-medium rounded-lg hover:bg-gray-200"
                      >
                        Cancel
                      </button>
                    </div>
                  </div>
                </div>
              )}

              {/* Current Configuration Display */}
              {!configEditing && currentConfig && (
                <div className="border-t pt-6">
                  <h3 className="text-lg font-semibold text-gray-900 mb-4">Current Configuration: {currentConfig.config_name}</h3>
                  <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4 text-sm">
                    <div className="space-y-2">
                      <h4 className="font-medium text-gray-800">xG Weights</h4>
                      <div className="text-gray-600">
                        <div>Shot-based: {currentConfig.xg_shot_based_weight}</div>
                        <div>Historical: {currentConfig.xg_historical_weight}</div>
                        <div>Opponent Def: {currentConfig.xg_opponent_defense_weight}</div>
                      </div>
                    </div>
                    <div className="space-y-2">
                      <h4 className="font-medium text-gray-800">Adjustments</h4>
                      <div className="text-gray-600">
                        <div>PPG Factor: {currentConfig.ppg_adjustment_factor}</div>
                        <div>Possession: {currentConfig.possession_adjustment_per_percent}</div>
                        <div>Fouls Factor: {currentConfig.fouls_drawn_factor}</div>
                      </div>
                    </div>
                    <div className="space-y-2">
                      <h4 className="font-medium text-gray-800">Key Values</h4>
                      <div className="text-gray-600">
                        <div>Penalty xG: {currentConfig.penalty_xg_value}</div>
                        <div>RBS Scaling: {currentConfig.rbs_scaling_factor}</div>
                        <div>Min xG: {currentConfig.min_xg_per_match}</div>
                      </div>
                    </div>
                  </div>
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

              {!regressionResult ? (
                /* Analysis Form */
                <div className="space-y-6">
                  {/* Analysis Configuration */}
                  <div className="bg-gradient-to-r from-purple-50 to-blue-50 border border-purple-200 rounded-lg p-4 mb-6">
                    <h3 className="text-lg font-semibold text-purple-900 mb-3">📊 Analysis Configuration</h3>
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-sm text-purple-800">
                      <div>
                        <h4 className="font-medium mb-2">🎯 Analysis Types</h4>
                        <div className="space-y-1 text-xs">
                          <div><strong>Points Per Game:</strong> Linear regression to predict match points (0, 1, 3)</div>
                          <div><strong>Match Result:</strong> Classification to predict Win/Draw/Loss</div>
                        </div>
                      </div>
                      <div>
                        <h4 className="font-medium mb-2">🔬 Model Details</h4>
                        <div className="space-y-1 text-xs">
                          <div><strong>Linear Regression:</strong> Shows coefficient relationships and R² score</div>
                          <div><strong>Random Forest:</strong> Shows feature importance and classification metrics</div>
                        </div>
                      </div>
                    </div>
                  </div>

                  <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                    {/* Target Selection */}
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-2">
                        Analysis Target
                      </label>
                      <select
                        value={regressionTarget}
                        onChange={(e) => setRegressionTarget(e.target.value)}
                        className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-purple-500"
                      >
                        <option value="points_per_game">Points Per Game (Linear Regression)</option>
                        <option value="match_result">Match Result (Classification)</option>
                      </select>
                    </div>

                    {/* Statistics Selection */}
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-2">
                        Selected Statistics ({selectedStats.length})
                      </label>
                      <div className="text-sm text-gray-600">
                        {selectedStats.length > 0 ? selectedStats.join(', ') : 'None selected'}
                      </div>
                    </div>
                  </div>

                  {/* Statistics Grid */}
                  <div>
                    <h3 className="text-lg font-semibold text-gray-900 mb-3">Select Statistics for Analysis</h3>
                    
                    {/* Basic Statistics */}
                    {statCategories.basic_stats && statCategories.basic_stats.length > 0 && (
                      <div className="mb-6">
                        <h4 className="text-md font-medium text-gray-800 mb-3">📊 Basic Team Statistics</h4>
                        <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-5 gap-3">
                          {statCategories.basic_stats.map(stat => (
                            <button
                              key={stat}
                              onClick={() => toggleStat(stat)}
                              className={`p-3 text-sm rounded-lg border-2 transition-colors ${
                                selectedStats.includes(stat)
                                  ? 'border-purple-500 bg-purple-50 text-purple-800'
                                  : 'border-gray-200 bg-white text-gray-700 hover:border-purple-300 hover:bg-purple-50'
                              }`}
                            >
                              <div className="font-medium">{stat.replace(/_/g, ' ')}</div>
                              <div className="text-xs text-gray-500 mt-1">
                                {statDescriptions[stat] && statDescriptions[stat].substring(0, 50)}
                                {statDescriptions[stat] && statDescriptions[stat].length > 50 && '...'}
                              </div>
                            </button>
                          ))}
                        </div>
                      </div>
                    )}

                    {/* Advanced Statistics */}
                    {statCategories.advanced_stats && statCategories.advanced_stats.length > 0 && (
                      <div className="mb-6">
                        <h4 className="text-md font-medium text-gray-800 mb-3">🎯 Advanced Performance Metrics</h4>
                        <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-5 gap-3">
                          {statCategories.advanced_stats.map(stat => (
                            <button
                              key={stat}
                              onClick={() => toggleStat(stat)}
                              className={`p-3 text-sm rounded-lg border-2 transition-colors ${
                                selectedStats.includes(stat)
                                  ? 'border-blue-500 bg-blue-50 text-blue-800'
                                  : 'border-gray-200 bg-white text-gray-700 hover:border-blue-300 hover:bg-blue-50'
                              }`}
                            >
                              <div className="font-medium">{stat.replace(/_/g, ' ')}</div>
                              <div className="text-xs text-gray-500 mt-1">
                                {statDescriptions[stat] && statDescriptions[stat].substring(0, 50)}
                                {statDescriptions[stat] && statDescriptions[stat].length > 50 && '...'}
                              </div>
                            </button>
                          ))}
                        </div>
                      </div>
                    )}

                    {/* Fallback for all stats if categories aren't available */}
                    {(!statCategories.basic_stats && !statCategories.advanced_stats) && (
                      <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-5 gap-3">
                        {availableStats.map(stat => (
                          <button
                            key={stat}
                            onClick={() => toggleStat(stat)}
                            className={`p-3 text-sm rounded-lg border-2 transition-colors ${
                              selectedStats.includes(stat)
                                ? 'border-purple-500 bg-purple-50 text-purple-800'
                                : 'border-gray-200 bg-white text-gray-700 hover:border-purple-300 hover:bg-purple-50'
                            }`}
                          >
                            <div className="font-medium">{stat.replace(/_/g, ' ')}</div>
                            <div className="text-xs text-gray-500 mt-1">
                              {statDescriptions[stat] && statDescriptions[stat].substring(0, 50)}
                              {statDescriptions[stat] && statDescriptions[stat].length > 50 && '...'}
                            </div>
                          </button>
                        ))}
                      </div>
                    )}
                  </div>

                  {/* Analysis Button */}
                  <div className="flex space-x-4">
                    <button
                      onClick={runRegressionAnalysis}
                      disabled={analyzing || selectedStats.length === 0}
                      className="px-6 py-3 bg-purple-600 text-white font-medium rounded-lg hover:bg-purple-700 disabled:bg-gray-400 disabled:cursor-not-allowed flex items-center space-x-2"
                    >
                      {analyzing ? (
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
                    <button
                      onClick={resetAnalysis}
                      className="px-6 py-2 bg-gray-100 text-gray-700 font-medium rounded-lg hover:bg-gray-200"
                    >
                      Reset
                    </button>
                  </div>

                  {/* Help Text */}
                  <div className="bg-gray-50 p-4 rounded-lg">
                    <h4 className="text-md font-semibold text-gray-900 mb-2">How to Use</h4>
                    <div className="text-sm text-gray-700 space-y-1">
                      <p>1. <strong>Select your target:</strong> Choose whether to predict points per game or match results</p>
                      <p>2. <strong>Choose statistics:</strong> Click on the statistics you want to include in your analysis</p>
                      <p>3. <strong>Run analysis:</strong> The system will train a model and show you the results</p>
                      <p>4. <strong>Interpret results:</strong> See which statistics have the strongest correlation with match outcomes</p>
                    </div>
                  </div>
                </div>
              ) : (
                /* Analysis Results */
                <div className="space-y-6">
                  {regressionResult.success ? (
                    <>
                      {/* Header with analysis details */}
                      <div className="bg-gradient-to-r from-purple-50 to-blue-50 p-6 rounded-lg border border-purple-200">
                        <div className="text-center">
                          <h3 className="text-lg font-semibold text-gray-800 mb-2">Analysis Results</h3>
                          <div className="text-2xl font-bold text-gray-900 mb-2">
                            {regressionResult.model_type}
                          </div>
                          <div className="text-sm text-gray-600">
                            Target: {regressionResult.target} | Sample Size: {regressionResult.sample_size}
                          </div>
                          <div className="text-xs text-gray-500 mt-1">
                            Statistics: {regressionResult.selected_stats.join(', ')}
                          </div>
                        </div>
                      </div>

                      {/* Results Content */}
                      {regressionTarget === 'points_per_game' ? (
                        /* Linear Regression Results */
                        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                          <div className="bg-white p-4 rounded-lg border">
                            <h4 className="text-md font-semibold text-gray-900 mb-3">Model Performance</h4>
                            <div className="space-y-2 text-sm">
                              <div className="flex justify-between">
                                <span className="text-gray-600">R² Score:</span>
                                <span className="font-medium text-blue-600">{regressionResult.results.r2_score?.toFixed(4)}</span>
                              </div>
                              <div className="flex justify-between">
                                <span className="text-gray-600">RMSE:</span>
                                <span className="font-medium">{regressionResult.results.rmse?.toFixed(4)}</span>
                              </div>
                              <div className="flex justify-between">
                                <span className="text-gray-600">Intercept:</span>
                                <span className="font-medium">{regressionResult.results.intercept?.toFixed(4)}</span>
                              </div>
                              <div className="flex justify-between">
                                <span className="text-gray-600">Train/Test Split:</span>
                                <span className="font-medium">{regressionResult.results.train_samples}/{regressionResult.results.test_samples}</span>
                              </div>
                            </div>
                          </div>
                          
                          <div className="bg-white p-4 rounded-lg border">
                            <h4 className="text-md font-semibold text-gray-900 mb-3">Coefficients</h4>
                            <div className="space-y-2 text-sm">
                              {Object.entries(regressionResult.results.coefficients || {}).map(([stat, coef]) => (
                                <div key={stat} className="flex justify-between">
                                  <span className="text-gray-600">{stat.replace('_', ' ')}:</span>
                                  <span className={`font-medium ${coef > 0 ? 'text-green-600' : coef < 0 ? 'text-red-600' : 'text-gray-600'}`}>
                                    {coef > 0 ? '+' : ''}{coef.toFixed(4)}
                                  </span>
                                </div>
                              ))}
                            </div>
                          </div>
                        </div>
                      ) : (
                        /* Classification Results */
                        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                          <div className="bg-white p-4 rounded-lg border">
                            <h4 className="text-md font-semibold text-gray-900 mb-3">Model Performance</h4>
                            <div className="space-y-2 text-sm">
                              <div className="flex justify-between">
                                <span className="text-gray-600">Accuracy:</span>
                                <span className="font-medium text-blue-600">{(regressionResult.results.accuracy * 100)?.toFixed(2)}%</span>
                              </div>
                              <div className="flex justify-between">
                                <span className="text-gray-600">Train/Test Split:</span>
                                <span className="font-medium">{regressionResult.results.train_samples}/{regressionResult.results.test_samples}</span>
                              </div>
                              <div className="flex justify-between">
                                <span className="text-gray-600">Classes:</span>
                                <span className="font-medium">{regressionResult.results.classes?.join(', ')}</span>
                              </div>
                            </div>
                          </div>
                          
                          <div className="bg-white p-4 rounded-lg border">
                            <h4 className="text-md font-semibold text-gray-900 mb-3">Feature Importance</h4>
                            <div className="space-y-2 text-sm">
                              {Object.entries(regressionResult.results.feature_importance || {})
                                .sort(([,a], [,b]) => b - a)
                                .map(([stat, importance]) => (
                                  <div key={stat} className="flex justify-between">
                                    <span className="text-gray-600">{stat.replace('_', ' ')}:</span>
                                    <span className="font-medium text-purple-600">{(importance * 100).toFixed(2)}%</span>
                                  </div>
                                ))}
                            </div>
                          </div>
                        </div>
                      )}

                      {/* Classification Report for Match Result */}
                      {regressionTarget === 'match_result' && regressionResult.results.classification_report && (
                        <div className="bg-white p-4 rounded-lg border">
                          <h4 className="text-md font-semibold text-gray-900 mb-3">Classification Report</h4>
                          <div className="overflow-x-auto">
                            <table className="min-w-full text-sm">
                              <thead>
                                <tr className="border-b">
                                  <th className="text-left p-2">Class</th>
                                  <th className="text-right p-2">Precision</th>
                                  <th className="text-right p-2">Recall</th>
                                  <th className="text-right p-2">F1-Score</th>
                                  <th className="text-right p-2">Support</th>
                                </tr>
                              </thead>
                              <tbody>
                                {Object.entries(regressionResult.results.classification_report)
                                  .filter(([key]) => ['W', 'D', 'L'].includes(key))
                                  .map(([className, metrics]) => (
                                    <tr key={className} className="border-b">
                                      <td className="p-2 font-medium">{className}</td>
                                      <td className="p-2 text-right">{metrics.precision?.toFixed(3)}</td>
                                      <td className="p-2 text-right">{metrics.recall?.toFixed(3)}</td>
                                      <td className="p-2 text-right">{metrics['f1-score']?.toFixed(3)}</td>
                                      <td className="p-2 text-right">{metrics.support}</td>
                                    </tr>
                                  ))}
                              </tbody>
                            </table>
                          </div>
                        </div>
                      )}

                      {/* Interpretation */}
                      <div className="bg-blue-50 p-4 rounded-lg border border-blue-200">
                        <h4 className="text-md font-semibold text-blue-900 mb-3">🧠 Interpretation</h4>
                        <div className="text-sm text-blue-800 space-y-2">
                          {regressionTarget === 'points_per_game' ? (
                            <>
                              <p><strong>R² Score:</strong> {(regressionResult.results.r2_score * 100)?.toFixed(1)}% of the variance in points per game is explained by these statistics.</p>
                              <p><strong>Positive coefficients:</strong> Higher values of these stats increase expected points per game.</p>
                              <p><strong>Negative coefficients:</strong> Higher values of these stats decrease expected points per game.</p>
                            </>
                          ) : (
                            <>
                              <p><strong>Accuracy:</strong> The model correctly predicts match results {(regressionResult.results.accuracy * 100)?.toFixed(1)}% of the time.</p>
                              <p><strong>Feature Importance:</strong> Shows which statistics are most useful for predicting match outcomes.</p>
                              <p><strong>Precision/Recall:</strong> Precision = accuracy when predicting each class; Recall = ability to find all instances of each class.</p>
                            </>
                          )}
                        </div>
                      </div>

                      {/* Action Buttons */}
                      <div className="flex space-x-4">
                        <button
                          onClick={resetAnalysis}
                          className="px-6 py-2 bg-gray-100 text-gray-700 font-medium rounded-lg hover:bg-gray-200"
                        >
                          Run New Analysis
                        </button>
                        {regressionTarget === 'points_per_game' && (
                          <button
                            onClick={async () => {
                              try {
                                const response = await axios.post(`${API}/suggest-prediction-config`);
                                if (response.data.success) {
                                  const suggestions = response.data.suggestions;
                                  alert(`🎯 Config Suggestions Generated!\n\nR² Score: ${suggestions.analysis_basis.r2_score.toFixed(3)}\nSample Size: ${suggestions.analysis_basis.sample_size}\n\nCheck browser console for detailed suggestions.`);
                                  console.log('Prediction Config Suggestions:', suggestions);
                                } else {
                                  alert(`❌ Failed to generate suggestions: ${response.data.message}`);
                                }
                              } catch (error) {
                                alert(`❌ Error: ${error.response?.data?.detail || error.message}`);
                              }
                            }}
                            className="px-6 py-2 bg-blue-600 text-white font-medium rounded-lg hover:bg-blue-700"
                          >
                            Suggest Config Optimizations
                          </button>
                        )}
                      </div>
                    </>
                  ) : (
                    /* Error State */
                    <div className="bg-red-50 p-4 rounded-lg border border-red-200">
                      <h3 className="text-lg font-semibold text-red-800 mb-2">Analysis Failed</h3>
                      <p className="text-red-700">{regressionResult.message}</p>
                      <button
                        onClick={resetAnalysis}
                        className="mt-4 px-4 py-2 bg-red-100 text-red-800 font-medium rounded-lg hover:bg-red-200"
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

        {/* RBS Configuration Tab */}
        {activeTab === 'rbs-config' && (
          <div className="space-y-6">
            <div className="bg-white p-6 rounded-lg shadow-sm border">
              <h2 className="text-xl font-bold text-gray-900 mb-4">⚖️ RBS Algorithm Configuration</h2>
              <p className="text-gray-600 mb-6">
                Customize the weights and parameters used in the RBS (Referee Bias Score) calculation. Each setting controls how different team statistics influence the final bias score.
              </p>

              {/* RBS Configuration Guide */}
              <div className="bg-gradient-to-r from-orange-50 to-red-50 border border-orange-200 rounded-lg p-4 mb-6">
                <h3 className="text-lg font-semibold text-orange-900 mb-3">📚 RBS Configuration Guide</h3>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-sm text-orange-800">
                  <div>
                    <h4 className="font-medium mb-2">⚖️ Algorithm Overview</h4>
                    <p className="mb-2">The RBS calculation works in 4 steps:</p>
                    <ol className="list-decimal list-inside space-y-1 text-xs">
                      <li><strong>Calculate team averages</strong> with and without specific referee</li>
                      <li><strong>Compute differences</strong> for each statistic (with ref - without ref)</li>
                      <li><strong>Apply weights and direction</strong> (negative for bad stats, positive for good)</li>
                      <li><strong>Normalize with tanh</strong> to get scores between -1 and +1</li>
                    </ol>
                  </div>
                  <div>
                    <h4 className="font-medium mb-2">🎯 Weight Strategies</h4>
                    <div className="space-y-2 text-xs">
                      <div><strong>Disciplinary Focus:</strong> Higher weights on cards (yellow 0.4, red 0.6)</div>
                      <div><strong>Performance Focus:</strong> Higher weights on xG difference (0.5) and possession (0.3)</div>
                      <div><strong>Balanced:</strong> Default weights spread across all factors</div>
                      <div><strong>Conservative:</strong> Lower overall weights for subtle bias detection</div>
                    </div>
                  </div>
                </div>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-6">
                {/* RBS Configuration Selection */}
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Select RBS Configuration
                  </label>
                  <select
                    value={rbsConfigName}
                    onChange={(e) => {
                      setRbsConfigName(e.target.value);
                      fetchRbsConfig(e.target.value);
                    }}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-orange-500 focus:border-orange-500"
                  >
                    <option value="default">Default RBS Configuration</option>
                    {rbsConfigs.map(config => (
                      <option key={config.config_name} value={config.config_name}>
                        {config.config_name}
                      </option>
                    ))}
                  </select>
                </div>

                {/* Action Buttons */}
                <div className="flex items-end space-x-2">
                  <button
                    onClick={() => {
                      setRbsConfigEditing(true);
                      resetRbsConfigForm();
                    }}
                    className="px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700"
                  >
                    Create New
                  </button>
                  <button
                    onClick={() => {
                      setRbsConfigEditing(true);
                      setRbsConfigForm(currentRbsConfig);
                    }}
                    disabled={!currentRbsConfig}
                    className="px-4 py-2 bg-orange-600 text-white rounded-lg hover:bg-orange-700 disabled:bg-gray-400"
                  >
                    Edit Current
                  </button>
                  <div className="ml-4">
                    <label className="block text-xs font-medium text-gray-600 mb-1">Quick Templates:</label>
                    <select
                      onChange={(e) => {
                        if (e.target.value) {
                          const templates = {
                            disciplinary: {
                              config_name: 'disciplinary-focus',
                              yellow_cards_weight: 0.4,
                              red_cards_weight: 0.6,
                              fouls_committed_weight: 0.2,
                              fouls_drawn_weight: 0.1,
                              penalties_awarded_weight: 0.4,
                              xg_difference_weight: 0.2,
                              possession_percentage_weight: 0.1
                            },
                            performance: {
                              config_name: 'performance-focus',
                              yellow_cards_weight: 0.2,
                              red_cards_weight: 0.3,
                              fouls_committed_weight: 0.05,
                              fouls_drawn_weight: 0.15,
                              penalties_awarded_weight: 0.6,
                              xg_difference_weight: 0.5,
                              possession_percentage_weight: 0.3
                            },
                            conservative: {
                              config_name: 'conservative',
                              yellow_cards_weight: 0.2,
                              red_cards_weight: 0.3,
                              fouls_committed_weight: 0.05,
                              fouls_drawn_weight: 0.05,
                              penalties_awarded_weight: 0.3,
                              xg_difference_weight: 0.25,
                              possession_percentage_weight: 0.1
                            }
                          };
                          const template = templates[e.target.value];
                          setRbsConfigForm({
                            ...rbsConfigForm,
                            ...template,
                            confidence_matches_multiplier: 4,
                            max_confidence: 95,
                            min_confidence: 10,
                            confidence_threshold_low: 2,
                            confidence_threshold_medium: 5,
                            confidence_threshold_high: 10
                          });
                          setRbsConfigEditing(true);
                          e.target.value = '';
                        }
                      }}
                      className="px-3 py-1 text-xs border border-gray-300 rounded focus:ring-2 focus:ring-orange-500 focus:border-orange-500"
                    >
                      <option value="">Select Template</option>
                      <option value="disciplinary">Disciplinary Focus</option>
                      <option value="performance">Performance Focus</option>
                      <option value="conservative">Conservative</option>
                    </select>
                  </div>
                </div>
              </div>

              {/* RBS Configuration Form */}
              {rbsConfigEditing && (
                <div className="border-t pt-6">
                  <h3 className="text-lg font-semibold text-gray-900 mb-4">
                    {rbsConfigForm.config_name === 'default' ? 'Edit RBS Configuration' : 'Create RBS Configuration'}
                  </h3>

                  <div className="space-y-6">
                    {/* Configuration Name */}
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-2">
                        Configuration Name
                      </label>
                      <input
                        type="text"
                        value={rbsConfigForm.config_name}
                        onChange={(e) => handleRbsConfigFormChange('config_name', e.target.value)}
                        className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-orange-500 focus:border-orange-500"
                        placeholder="Enter RBS configuration name"
                      />
                    </div>

                    {/* RBS Weights */}
                    <div className="border rounded-lg p-4">
                      <h4 className="font-medium text-gray-900 mb-3">RBS Statistic Weights</h4>
                      <div className="mb-3 text-sm text-gray-600 bg-orange-50 p-3 rounded">
                        <strong>How RBS weights work:</strong> Each weight determines how much influence that statistic has on the final bias score. Higher weights mean the statistic has more impact on detecting referee bias.
                      </div>
                      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                        <div>
                          <label className="block text-sm font-medium text-gray-700 mb-1">Yellow Cards Weight</label>
                          <input
                            type="number"
                            step="0.01"
                            min="0"
                            value={rbsConfigForm.yellow_cards_weight}
                            onChange={(e) => handleRbsConfigFormChange('yellow_cards_weight', e.target.value)}
                            className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-orange-500 focus:border-orange-500"
                          />
                          <div className="mt-1 text-xs text-gray-500">
                            <strong>Direction:</strong> Higher yellow cards = worse for team (negative impact)
                          </div>
                        </div>
                        <div>
                          <label className="block text-sm font-medium text-gray-700 mb-1">Red Cards Weight</label>
                          <input
                            type="number"
                            step="0.01"
                            min="0"
                            value={rbsConfigForm.red_cards_weight}
                            onChange={(e) => handleRbsConfigFormChange('red_cards_weight', e.target.value)}
                            className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-orange-500 focus:border-orange-500"
                          />
                          <div className="mt-1 text-xs text-gray-500">
                            <strong>Direction:</strong> Higher red cards = worse for team (negative impact)
                          </div>
                        </div>
                        <div>
                          <label className="block text-sm font-medium text-gray-700 mb-1">Fouls Committed Weight</label>
                          <input
                            type="number"
                            step="0.01"
                            min="0"
                            value={rbsConfigForm.fouls_committed_weight}
                            onChange={(e) => handleRbsConfigFormChange('fouls_committed_weight', e.target.value)}
                            className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-orange-500 focus:border-orange-500"
                          />
                          <div className="mt-1 text-xs text-gray-500">
                            <strong>Direction:</strong> More fouls committed = worse for team (negative impact)
                          </div>
                        </div>
                        <div>
                          <label className="block text-sm font-medium text-gray-700 mb-1">Fouls Drawn Weight</label>
                          <input
                            type="number"
                            step="0.01"
                            min="0"
                            value={rbsConfigForm.fouls_drawn_weight}
                            onChange={(e) => handleRbsConfigFormChange('fouls_drawn_weight', e.target.value)}
                            className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-orange-500 focus:border-orange-500"
                          />
                          <div className="mt-1 text-xs text-gray-500">
                            <strong>Direction:</strong> More fouls drawn = better for team (positive impact)
                          </div>
                        </div>
                        <div>
                          <label className="block text-sm font-medium text-gray-700 mb-1">Penalties Awarded Weight</label>
                          <input
                            type="number"
                            step="0.01"
                            min="0"
                            value={rbsConfigForm.penalties_awarded_weight}
                            onChange={(e) => handleRbsConfigFormChange('penalties_awarded_weight', e.target.value)}
                            className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-orange-500 focus:border-orange-500"
                          />
                          <div className="mt-1 text-xs text-gray-500">
                            <strong>Direction:</strong> More penalties awarded = better for team (positive impact)
                          </div>
                        </div>
                        <div>
                          <label className="block text-sm font-medium text-gray-700 mb-1">xG Difference Weight</label>
                          <input
                            type="number"
                            step="0.01"
                            min="0"
                            value={rbsConfigForm.xg_difference_weight}
                            onChange={(e) => handleRbsConfigFormChange('xg_difference_weight', e.target.value)}
                            className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-orange-500 focus:border-orange-500"
                          />
                          <div className="mt-1 text-xs text-gray-500">
                            <strong>Direction:</strong> Higher xG difference (team xG - opponent xG) = better for team (positive impact)
                          </div>
                        </div>
                        <div>
                          <label className="block text-sm font-medium text-gray-700 mb-1">Possession Percentage Weight</label>
                          <input
                            type="number"
                            step="0.01"
                            min="0"
                            value={rbsConfigForm.possession_percentage_weight}
                            onChange={(e) => handleRbsConfigFormChange('possession_percentage_weight', e.target.value)}
                            className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-orange-500 focus:border-orange-500"
                          />
                          <div className="mt-1 text-xs text-gray-500">
                            <strong>Direction:</strong> Higher possession % = better for team (positive impact)
                          </div>
                        </div>
                      </div>
                    </div>

                    {/* Confidence Settings */}
                    <div className="border rounded-lg p-4">
                      <h4 className="font-medium text-gray-900 mb-3">Confidence Calculation Settings</h4>
                      <div className="mb-3 text-sm text-gray-600 bg-blue-50 p-3 rounded">
                        <strong>Confidence settings:</strong> These control how confidence levels are calculated based on the number of matches a team has played with a specific referee.
                      </div>
                      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                        <div>
                          <label className="block text-sm font-medium text-gray-700 mb-1">Min Confidence</label>
                          <input
                            type="number"
                            step="1"
                            min="0"
                            max="100"
                            value={rbsConfigForm.min_confidence}
                            onChange={(e) => handleRbsConfigFormChange('min_confidence', e.target.value)}
                            className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-orange-500 focus:border-orange-500"
                          />
                        </div>
                        <div>
                          <label className="block text-sm font-medium text-gray-700 mb-1">Max Confidence</label>
                          <input
                            type="number"
                            step="1"
                            min="0"
                            max="100"
                            value={rbsConfigForm.max_confidence}
                            onChange={(e) => handleRbsConfigFormChange('max_confidence', e.target.value)}
                            className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-orange-500 focus:border-orange-500"
                          />
                        </div>
                        <div>
                          <label className="block text-sm font-medium text-gray-700 mb-1">Low Threshold (matches)</label>
                          <input
                            type="number"
                            step="1"
                            min="1"
                            value={rbsConfigForm.confidence_threshold_low}
                            onChange={(e) => handleRbsConfigFormChange('confidence_threshold_low', e.target.value)}
                            className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-orange-500 focus:border-orange-500"
                          />
                          <div className="mt-1 text-xs text-gray-500">
                            Minimum matches needed for any confidence calculation
                          </div>
                        </div>
                        <div>
                          <label className="block text-sm font-medium text-gray-700 mb-1">Medium Threshold (matches)</label>
                          <input
                            type="number"
                            step="1"
                            min="1"
                            value={rbsConfigForm.confidence_threshold_medium}
                            onChange={(e) => handleRbsConfigFormChange('confidence_threshold_medium', e.target.value)}
                            className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-orange-500 focus:border-orange-500"
                          />
                          <div className="mt-1 text-xs text-gray-500">
                            Matches needed for medium confidence (50-70%)
                          </div>
                        </div>
                        <div>
                          <label className="block text-sm font-medium text-gray-700 mb-1">High Threshold (matches)</label>
                          <input
                            type="number"
                            step="1"
                            min="1"
                            value={rbsConfigForm.confidence_threshold_high}
                            onChange={(e) => handleRbsConfigFormChange('confidence_threshold_high', e.target.value)}
                            className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-orange-500 focus:border-orange-500"
                          />
                          <div className="mt-1 text-xs text-gray-500">
                            Matches needed for high confidence (70%+)
                          </div>
                        </div>
                      </div>
                    </div>

                    {/* Action Buttons */}
                    <div className="flex space-x-4">
                      <button
                        onClick={saveRbsConfig}
                        className="px-6 py-2 bg-orange-600 text-white font-medium rounded-lg hover:bg-orange-700"
                      >
                        Save Configuration
                      </button>
                      <button
                        onClick={() => setRbsConfigEditing(false)}
                        className="px-6 py-2 bg-gray-100 text-gray-700 font-medium rounded-lg hover:bg-gray-200"
                      >
                        Cancel
                      </button>
                    </div>
                  </div>
                </div>
              )}

              {/* Current Configuration Display */}
              {!rbsConfigEditing && currentRbsConfig && (
                <div className="border-t pt-6">
                  <h3 className="text-lg font-semibold text-gray-900 mb-4">Current RBS Configuration: {currentRbsConfig.config_name}</h3>
                  <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm mb-6">
                    <div className="bg-gray-50 p-3 rounded">
                      <div className="font-medium text-gray-700">Yellow Cards</div>
                      <div className="text-lg font-bold text-orange-600">{currentRbsConfig.yellow_cards_weight}</div>
                    </div>
                    <div className="bg-gray-50 p-3 rounded">
                      <div className="font-medium text-gray-700">Red Cards</div>
                      <div className="text-lg font-bold text-red-600">{currentRbsConfig.red_cards_weight}</div>
                    </div>
                    <div className="bg-gray-50 p-3 rounded">
                      <div className="font-medium text-gray-700">Fouls Committed</div>
                      <div className="text-lg font-bold text-red-600">{currentRbsConfig.fouls_committed_weight}</div>
                    </div>
                    <div className="bg-gray-50 p-3 rounded">
                      <div className="font-medium text-gray-700">Fouls Drawn</div>
                      <div className="text-lg font-bold text-green-600">{currentRbsConfig.fouls_drawn_weight}</div>
                    </div>
                    <div className="bg-gray-50 p-3 rounded">
                      <div className="font-medium text-gray-700">Penalties Awarded</div>
                      <div className="text-lg font-bold text-green-600">{currentRbsConfig.penalties_awarded_weight}</div>
                    </div>
                    <div className="bg-gray-50 p-3 rounded">
                      <div className="font-medium text-gray-700">xG Difference</div>
                      <div className="text-lg font-bold text-blue-600">{currentRbsConfig.xg_difference_weight}</div>
                    </div>
                    <div className="bg-gray-50 p-3 rounded">
                      <div className="font-medium text-gray-700">Possession %</div>
                      <div className="text-lg font-bold text-blue-600">{currentRbsConfig.possession_percentage_weight}</div>
                    </div>
                  </div>

                  {/* Calculate RBS with Current Config */}
                  <div className="bg-orange-50 p-4 rounded-lg border">
                    <h4 className="font-medium text-orange-900 mb-2">Apply Configuration</h4>
                    <p className="text-sm text-orange-700 mb-4">
                      Recalculate all RBS scores using the current configuration: <strong>{currentRbsConfig.config_name}</strong>
                    </p>
                    <button
                      onClick={async () => {
                        setCalculating(true);
                        try {
                          const response = await axios.post(`${API}/calculate-rbs?config_name=${rbsConfigName}`);
                          alert(`✅ ${response.data.message}`);
                          fetchStats();
                          fetchRefereeSummary();
                        } catch (error) {
                          alert(`❌ Error calculating RBS: ${error.response?.data?.detail || error.message}`);
                        }
                        setCalculating(false);
                      }}
                      disabled={calculating || !stats.matches || !stats.team_stats}
                      className="px-6 py-3 bg-orange-600 text-white font-medium rounded-lg hover:bg-orange-700 disabled:bg-gray-400 disabled:cursor-not-allowed"
                    >
                      {calculating ? 'Calculating...' : `Calculate RBS with ${rbsConfigName} Config`}
                    </button>
                  </div>
                </div>
              )}

              {/* RBS Formula Explanation */}
              <div className="bg-orange-50 p-4 rounded-lg border border-orange-200 mt-6">
                <h4 className="text-md font-semibold text-orange-900 mb-3">🧮 RBS Formula Explanation</h4>
                <div className="text-sm text-orange-800 space-y-2">
                  <p><strong>📊 Formula:</strong> RBS = tanh(Σ(delta_i × weight_i))</p>
                  <p><strong>📈 Where delta_i:</strong> (team_stat_with_referee - team_stat_without_referee)</p>
                  <p><strong>⚖️ Normalization:</strong> tanh() ensures RBS scores are between -1 and +1</p>
                  <ul className="list-disc list-inside ml-4 space-y-1">
                    <li><strong>+1.0 = Strong favorable bias:</strong> Referee significantly helps the team</li>
                    <li><strong>0.0 = Neutral:</strong> No bias detected</li>
                    <li><strong>-1.0 = Strong unfavorable bias:</strong> Referee significantly hurts the team</li>
                  </ul>
                  <p><strong>🔄 Direction:</strong> Yellow cards, red cards, and fouls committed are multiplied by -1 (higher = worse for team)</p>
                </div>
              </div>
            </div>
          </div>
        )}

        {/* Formula Optimization Tab */}
        {activeTab === 'optimization' && (
          <div className="space-y-6">
            <div className="bg-white p-6 rounded-lg shadow-sm border">
              <h2 className="text-xl font-bold text-gray-900 mb-6">🧪 Formula Optimization</h2>
              <p className="text-gray-600 mb-6">
                Use regression analysis to optimize your RBS formula weights and Match Predictor algorithm parameters based on statistical correlations with match outcomes.
              </p>

              {/* Analysis Actions */}
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-8">
                <div className="bg-gradient-to-r from-orange-50 to-red-50 p-6 rounded-lg border border-orange-200">
                  <h3 className="text-lg font-semibold text-gray-900 mb-2">🎯 RBS Formula Optimization</h3>
                  <p className="text-sm text-gray-600 mb-4">
                    Analyze which RBS variables have the strongest correlation with match outcomes and get suggested weight adjustments.
                  </p>
                  <button
                    onClick={analyzeRBSOptimization}
                    disabled={analyzingFormulas}
                    className="w-full px-4 py-2 bg-orange-600 text-white rounded-lg hover:bg-orange-700 disabled:bg-gray-400 disabled:cursor-not-allowed flex items-center justify-center space-x-2"
                  >
                    {analyzingFormulas ? (
                      <>
                        <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white"></div>
                        <span>Analyzing...</span>
                      </>
                    ) : (
                      <>
                        <span>📊</span>
                        <span>Analyze RBS Formula</span>
                      </>
                    )}
                  </button>
                </div>

                <div className="bg-gradient-to-r from-blue-50 to-indigo-50 p-6 rounded-lg border border-blue-200">
                  <h3 className="text-lg font-semibold text-gray-900 mb-2">⚽ Match Predictor Optimization</h3>
                  <p className="text-sm text-gray-600 mb-4">
                    Analyze which predictor variables are most important for match outcomes and optimize algorithm parameters.
                  </p>
                  <button
                    onClick={analyzePredictorOptimization}
                    disabled={analyzingFormulas}
                    className="w-full px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:bg-gray-400 disabled:cursor-not-allowed flex items-center justify-center space-x-2"
                  >
                    {analyzingFormulas ? (
                      <>
                        <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white"></div>
                        <span>Analyzing...</span>
                      </>
                    ) : (
                      <>
                        <span>🔮</span>
                        <span>Analyze Match Predictor</span>
                      </>
                    )}
                  </button>
                </div>
              </div>

              {/* RBS Optimization Results */}
              {optimizationResults.rbs && (
                <div className="bg-orange-50 p-6 rounded-lg border border-orange-200 mb-6">
                  <div className="flex justify-between items-start mb-4">
                    <h3 className="text-lg font-semibold text-orange-900">🎯 RBS Formula Analysis Results</h3>
                    <span className="text-sm text-orange-600">
                      Sample Size: {optimizationResults.rbs.sample_size}
                    </span>
                  </div>

                  {optimizationResults.rbs.success ? (
                    <>
                      {/* Current vs Suggested Weights */}
                      {optimizationResults.rbs.results.suggested_rbs_weights && (
                        <div className="bg-white p-4 rounded-lg mb-4">
                          <h4 className="font-semibold text-gray-900 mb-3">Suggested Weight Adjustments</h4>
                          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                            {Object.entries(optimizationResults.rbs.results.suggested_rbs_weights).map(([variable, weight]) => (
                              <div key={variable} className="flex justify-between items-center">
                                <span className="text-sm text-gray-700 capitalize">
                                  {variable.replace('_', ' ')}:
                                </span>
                                <span className="font-medium text-orange-700">{weight}</span>
                              </div>
                            ))}
                          </div>
                          <div className="mt-4">
                            <button
                              onClick={() => applyRBSWeights(optimizationResults.rbs.results.suggested_rbs_weights)}
                              disabled={applyingWeights}
                              className="px-4 py-2 bg-orange-600 text-white rounded-lg hover:bg-orange-700 disabled:bg-gray-400 disabled:cursor-not-allowed flex items-center space-x-2"
                            >
                              {applyingWeights ? (
                                <>
                                  <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white"></div>
                                  <span>Applying...</span>
                                </>
                              ) : (
                                <>
                                  <span>✅</span>
                                  <span>Apply Suggested Weights</span>
                                </>
                              )}
                            </button>
                          </div>
                        </div>
                      )}

                      {/* Variable Correlations */}
                      {optimizationResults.rbs.results.correlations_with_points && (
                        <div className="bg-white p-4 rounded-lg mb-4">
                          <h4 className="font-semibold text-gray-900 mb-3">Variable Correlations with Match Outcomes</h4>
                          <div className="space-y-2">
                            {Object.entries(optimizationResults.rbs.results.correlations_with_points)
                              .sort(([,a], [,b]) => Math.abs(b) - Math.abs(a))
                              .map(([variable, correlation]) => (
                                <div key={variable} className="flex justify-between items-center">
                                  <span className="text-sm text-gray-700 capitalize">
                                    {variable.replace('_', ' ')}:
                                  </span>
                                  <span className={`font-medium ${correlation > 0 ? 'text-green-600' : correlation < 0 ? 'text-red-600' : 'text-gray-600'}`}>
                                    {correlation > 0 ? '+' : ''}{(correlation * 100).toFixed(1)}%
                                  </span>
                                </div>
                              ))}
                          </div>
                        </div>
                      )}

                      {/* Recommendations */}
                      {optimizationResults.rbs.recommendations && optimizationResults.rbs.recommendations.length > 0 && (
                        <div className="bg-white p-4 rounded-lg">
                          <h4 className="font-semibold text-gray-900 mb-3">Recommendations</h4>
                          <div className="space-y-2">
                            {optimizationResults.rbs.recommendations.map((rec, index) => (
                              <div key={index} className="border-l-4 border-orange-400 pl-3">
                                <div className="text-sm font-medium text-gray-900">{rec.recommendation}</div>
                                <div className="text-xs text-gray-600">Priority: {rec.priority}</div>
                              </div>
                            ))}
                          </div>
                        </div>
                      )}
                    </>
                  ) : (
                    <div className="bg-red-50 p-4 rounded-lg">
                      <p className="text-red-800">{optimizationResults.rbs.message}</p>
                    </div>
                  )}
                </div>
              )}

              {/* Match Predictor Optimization Results */}
              {optimizationResults.predictor && (
                <div className="bg-blue-50 p-6 rounded-lg border border-blue-200">
                  <div className="flex justify-between items-start mb-4">
                    <h3 className="text-lg font-semibold text-blue-900">⚽ Match Predictor Analysis Results</h3>
                    <span className="text-sm text-blue-600">
                      Sample Size: {optimizationResults.predictor.sample_size}
                    </span>
                  </div>

                  {optimizationResults.predictor.success ? (
                    <>
                      {/* Variable Importance Ranking */}
                      {optimizationResults.predictor.results.variable_importance_ranking && (
                        <div className="bg-white p-4 rounded-lg mb-4">
                          <h4 className="font-semibold text-gray-900 mb-3">Variable Importance Ranking</h4>
                          <div className="space-y-2">
                            {optimizationResults.predictor.results.variable_importance_ranking.slice(0, 8).map(([variable, coefficient], index) => (
                              <div key={variable} className="flex justify-between items-center">
                                <div className="flex items-center space-x-2">
                                  <span className="text-xs bg-blue-100 text-blue-800 px-2 py-1 rounded">#{index + 1}</span>
                                  <span className="text-sm text-gray-700 capitalize">
                                    {variable.replace('_', ' ')}
                                  </span>
                                </div>
                                <span className={`font-medium ${coefficient > 0 ? 'text-green-600' : coefficient < 0 ? 'text-red-600' : 'text-gray-600'}`}>
                                  {coefficient > 0 ? '+' : ''}{coefficient.toFixed(3)}
                                </span>
                              </div>
                            ))}
                          </div>
                        </div>
                      )}

                      {/* Performance Metrics */}
                      {optimizationResults.predictor.results.predictor_vs_points && (
                        <div className="bg-white p-4 rounded-lg mb-4">
                          <h4 className="font-semibold text-gray-900 mb-3">Model Performance</h4>
                          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                            <div className="text-center">
                              <div className="text-2xl font-bold text-blue-600">
                                {(optimizationResults.predictor.results.predictor_vs_points.results?.r2_score * 100 || 0).toFixed(1)}%
                              </div>
                              <div className="text-sm text-gray-600">R² Score</div>
                            </div>
                            <div className="text-center">
                              <div className="text-2xl font-bold text-blue-600">
                                {optimizationResults.predictor.results.predictor_vs_points.sample_size || 0}
                              </div>
                              <div className="text-sm text-gray-600">Samples</div>
                            </div>
                            <div className="text-center">
                              <div className="text-2xl font-bold text-blue-600">
                                {optimizationResults.predictor.predictor_variables_analyzed?.length || 0}
                              </div>
                              <div className="text-sm text-gray-600">Variables</div>
                            </div>
                          </div>
                        </div>
                      )}

                      {/* Apply Optimizations */}
                      <div className="bg-white p-4 rounded-lg">
                        <h4 className="font-semibold text-gray-900 mb-3">Apply Optimizations</h4>
                        <p className="text-sm text-gray-600 mb-3">
                          Create a new prediction configuration based on the analysis results.
                        </p>
                        <button
                          onClick={() => applyPredictorWeights(optimizationResults.predictor)}
                          disabled={applyingWeights}
                          className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:bg-gray-400 disabled:cursor-not-allowed flex items-center space-x-2"
                        >
                          {applyingWeights ? (
                            <>
                              <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white"></div>
                              <span>Applying...</span>
                            </>
                          ) : (
                            <>
                              <span>✅</span>
                              <span>Apply Optimized Configuration</span>
                            </>
                          )}
                        </button>
                      </div>

                      {/* Recommendations */}
                      {optimizationResults.predictor.recommendations && optimizationResults.predictor.recommendations.length > 0 && (
                        <div className="bg-white p-4 rounded-lg mt-4">
                          <h4 className="font-semibold text-gray-900 mb-3">Recommendations</h4>
                          <div className="space-y-2">
                            {optimizationResults.predictor.recommendations.map((rec, index) => (
                              <div key={index} className="border-l-4 border-blue-400 pl-3">
                                <div className="text-sm font-medium text-gray-900">{rec.recommendation}</div>
                                {rec.details && typeof rec.details === 'string' && (
                                  <div className="text-xs text-gray-600">{rec.details}</div>
                                )}
                                <div className="text-xs text-gray-600">Priority: {rec.priority}</div>
                              </div>
                            ))}
                          </div>
                        </div>
                      )}
                    </>
                  ) : (
                    <div className="bg-red-50 p-4 rounded-lg">
                      <p className="text-red-800">{optimizationResults.predictor.message}</p>
                    </div>
                  )}
                </div>
              )}

              {/* Instructions */}
              {!optimizationResults.rbs && !optimizationResults.predictor && (
                <div className="bg-gray-50 p-6 rounded-lg border">
                  <h3 className="text-lg font-semibold text-gray-900 mb-3">📚 How to Use Formula Optimization</h3>
                  <div className="space-y-3 text-sm text-gray-700">
                    <div className="flex items-start space-x-2">
                      <span className="text-orange-600 font-bold">1.</span>
                      <div>
                        <strong>RBS Formula Optimization:</strong> Analyzes which RBS variables (yellow cards, red cards, fouls, etc.) have the strongest correlation with match outcomes. Provides suggested weight adjustments to improve RBS accuracy.
                      </div>
                    </div>
                    <div className="flex items-start space-x-2">
                      <span className="text-blue-600 font-bold">2.</span>
                      <div>
                        <strong>Match Predictor Optimization:</strong> Evaluates which variables are most important for predicting match results. Helps optimize algorithm parameters for better prediction accuracy.
                      </div>
                    </div>
                    <div className="flex items-start space-x-2">
                      <span className="text-green-600 font-bold">3.</span>
                      <div>
                        <strong>Apply Changes:</strong> Once analysis is complete, you can apply the suggested optimizations to create new, improved configurations for your algorithms.
                      </div>
                    </div>
                  </div>
                  <div className="mt-4 p-3 bg-yellow-50 rounded border border-yellow-200">
                    <p className="text-sm text-yellow-800">
                      <strong>Note:</strong> Optimization analysis requires existing match data and RBS calculations. Make sure you have uploaded data and calculated RBS scores before running optimization.
                    </p>
                  </div>
                </div>
              )}
            </div>
          </div>
        )}

        {/* Results Tab */}
        {activeTab === 'results' && (
          <div className="space-y-6">
            {!viewingReferee ? (
              /* Referee List View */
              <>
                <div className="bg-white p-6 rounded-lg shadow-sm border">
                  <h2 className="text-xl font-bold text-gray-900 mb-4">Referee Analysis Dashboard</h2>
                  <p className="text-gray-600 mb-4">Click on any referee to view their detailed bias analysis and team-specific statistics.</p>
                  
                  <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                    {console.log('Rendering referee cards, refereeSummary length:', refereeSummary.length)}
                    {refereeSummary.map((referee) => (
                      <div 
                        key={referee._id}
                        onClick={() => fetchRefereeDetails(referee._id)}
                        className="bg-gray-50 p-4 rounded-lg border hover:border-blue-500 hover:bg-blue-50 cursor-pointer transition-all duration-200"
                      >
                        <h3 className="text-lg font-semibold text-gray-900 mb-2">{referee._id}</h3>
                        <div className="space-y-1 text-sm text-gray-600">
                          <div className="flex justify-between">
                            <span>Total Matches:</span>
                            <span className="font-medium">{referee.total_matches}</span>
                          </div>
                          <div className="flex justify-between">
                            <span>Teams Analyzed:</span>
                            <span className="font-medium">{referee.rbs_count || 0}</span>
                          </div>
                          <div className="flex justify-between">
                            <span>Avg Bias Score:</span>
                            <span className={`font-medium ${
                              referee.avg_bias > 0.1 ? 'text-green-600' : 
                              referee.avg_bias < -0.1 ? 'text-red-600' : 
                              'text-gray-600'
                            }`}>
                              {referee.avg_bias > 0 ? '+' : ''}{referee.avg_bias}
                            </span>
                          </div>
                          <div className="flex justify-between">
                            <span>Competitions:</span>
                            <span className="font-medium">{referee.competitions?.length || 0}</span>
                          </div>
                        </div>
                        <div className="mt-3 text-xs text-blue-600 font-medium">
                          Click to view details →
                        </div>
                      </div>
                    ))}
                  </div>
                  
                  {refereeSummary.length === 0 && (
                    <div className="text-center py-12">
                      <p className="text-gray-500">No referee data found. Upload data and calculate RBS scores first.</p>
                    </div>
                  )}
                </div>
              </>
            ) : (
              /* Individual Referee Detail View */
              <>
                <div className="bg-white p-6 rounded-lg shadow-sm border">
                  <div className="flex items-center justify-between mb-6">
                    <div>
                      <h2 className="text-2xl font-bold text-gray-900">{viewingReferee}</h2>
                      <p className="text-gray-600">Comprehensive bias analysis and statistics</p>
                    </div>
                    <button
                      onClick={goBackToRefereeList}
                      className="px-4 py-2 bg-gray-100 text-gray-700 rounded-lg hover:bg-gray-200 transition-colors"
                    >
                      ← Back to All Referees
                    </button>
                  </div>

                  {selectedRefereeDetails && (
                    <div className="space-y-6">
                      {/* Overview Stats */}
                      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
                        <div className="bg-blue-50 p-4 rounded-lg">
                          <h3 className="text-sm font-medium text-blue-800">Total Matches</h3>
                          <p className="text-2xl font-bold text-blue-900">{selectedRefereeDetails.total_matches}</p>
                        </div>
                        <div className="bg-green-50 p-4 rounded-lg">
                          <h3 className="text-sm font-medium text-green-800">Teams Analyzed</h3>
                          <p className="text-2xl font-bold text-green-900">{selectedRefereeDetails.total_teams}</p>
                        </div>
                        <div className="bg-purple-50 p-4 rounded-lg">
                          <h3 className="text-sm font-medium text-purple-800">RBS Results</h3>
                          <p className="text-2xl font-bold text-purple-900">{selectedRefereeDetails.rbs_results?.length || 0}</p>
                        </div>
                        <div className="bg-orange-50 p-4 rounded-lg">
                          <h3 className="text-sm font-medium text-orange-800">Avg Cards/Match</h3>
                          <p className="text-2xl font-bold text-orange-900">
                            {(selectedRefereeDetails.overall_averages?.yellow_cards || 0).toFixed(1)}
                          </p>
                        </div>
                      </div>

                      {/* Overall Averages */}
                      <div className="bg-white p-6 rounded-lg border">
                        <h3 className="text-lg font-semibold text-gray-900 mb-4">Overall Match Averages</h3>
                        <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
                          <div className="text-center p-3 bg-gray-50 rounded">
                            <div className="font-medium text-gray-900">{(selectedRefereeDetails.overall_averages?.yellow_cards || 0).toFixed(1)}</div>
                            <div className="text-gray-600">Yellow Cards</div>
                          </div>
                          <div className="text-center p-3 bg-gray-50 rounded">
                            <div className="font-medium text-gray-900">{(selectedRefereeDetails.overall_averages?.red_cards || 0).toFixed(1)}</div>
                            <div className="text-gray-600">Red Cards</div>
                          </div>
                          <div className="text-center p-3 bg-gray-50 rounded">
                            <div className="font-medium text-gray-900">{(selectedRefereeDetails.overall_averages?.fouls || 0).toFixed(1)}</div>
                            <div className="text-gray-600">Fouls</div>
                          </div>
                          <div className="text-center p-3 bg-gray-50 rounded">
                            <div className="font-medium text-gray-900">{(selectedRefereeDetails.overall_averages?.penalties_awarded || 0).toFixed(1)}</div>
                            <div className="text-gray-600">Penalties</div>
                          </div>
                          <div className="text-center p-3 bg-gray-50 rounded">
                            <div className="font-medium text-gray-900">{(selectedRefereeDetails.overall_averages?.possession_pct || 0).toFixed(1)}%</div>
                            <div className="text-gray-600">Avg Possession</div>
                          </div>
                          <div className="text-center p-3 bg-gray-50 rounded">
                            <div className="font-medium text-gray-900">{(selectedRefereeDetails.overall_averages?.xg || 0).toFixed(2)}</div>
                            <div className="text-gray-600">Avg xG</div>
                          </div>
                          <div className="text-center p-3 bg-gray-50 rounded">
                            <div className="font-medium text-gray-900">{(selectedRefereeDetails.overall_averages?.shots_total || 0).toFixed(1)}</div>
                            <div className="text-gray-600">Shots</div>
                          </div>
                          <div className="text-center p-3 bg-gray-50 rounded">
                            <div className="font-medium text-gray-900">{(selectedRefereeDetails.overall_averages?.shots_on_target || 0).toFixed(1)}</div>
                            <div className="text-gray-600">Shots on Target</div>
                          </div>
                        </div>
                      </div>

                      {/* Team-Specific RBS Results */}
                      <div className="bg-white p-6 rounded-lg border">
                        <h3 className="text-lg font-semibold text-gray-900 mb-4">Team-Specific Bias Analysis</h3>
                        <div className="overflow-x-auto">
                          <table className="min-w-full divide-y divide-gray-200">
                            <thead className="bg-gray-50">
                              <tr>
                                <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Team</th>
                                <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider" title="Referee Bias Score: Normalized performance differential with vs without this referee (range: -1 to +1)">RBS Score</th>
                                <th className="px-3 py-3 text-center text-xs font-medium text-gray-500 uppercase tracking-wider" title="Yellow cards differential: Average with referee - Average without referee">Yellow Cards</th>
                                <th className="px-3 py-3 text-center text-xs font-medium text-gray-500 uppercase tracking-wider" title="Red cards differential: Average with referee - Average without referee">Red Cards</th>
                                <th className="px-3 py-3 text-center text-xs font-medium text-gray-500 uppercase tracking-wider" title="Fouls committed differential: Average with referee - Average without referee">Fouls</th>
                                <th className="px-3 py-3 text-center text-xs font-medium text-gray-500 uppercase tracking-wider" title="Fouls drawn differential: Average with referee - Average without referee">Fouls Drawn</th>
                                <th className="px-3 py-3 text-center text-xs font-medium text-gray-500 uppercase tracking-wider" title="Penalties awarded differential: Average with referee - Average without referee">Penalties</th>
                                <th className="px-3 py-3 text-center text-xs font-medium text-gray-500 uppercase tracking-wider" title="xG difference differential: (Team xG - Opponent xG) with referee vs without referee">xG Diff</th>
                                <th className="px-3 py-3 text-center text-xs font-medium text-gray-500 uppercase tracking-wider" title="Possession % differential: Average with referee - Average without referee">Possession</th>
                                <th className="px-3 py-3 text-center text-xs font-medium text-gray-500 uppercase tracking-wider" title="Decision variance ratios: How consistently referee treats this team vs overall patterns (&gt;1.5 = more variable)">Variance</th>
                                <th className="px-3 py-3 text-center text-xs font-medium text-gray-500 uppercase tracking-wider" title="Number of matches where this referee officiated this team">Matches</th>
                                <th className="px-3 py-3 text-center text-xs font-medium text-gray-500 uppercase tracking-wider" title="Statistical confidence level based on sample size (more matches = higher confidence)">Confidence</th>
                              </tr>
                            </thead>
                            <tbody className="bg-white divide-y divide-gray-200">
                              {selectedRefereeDetails.rbs_results?.map((result, index) => (
                                <tr key={index} className="hover:bg-gray-50">
                                  <td className="px-4 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                                    {result.team_name}
                                  </td>
                                  <td className="px-4 py-4 whitespace-nowrap">
                                    <span className={`inline-flex px-2 py-1 text-xs font-semibold rounded-full ${getRBSColor(result.rbs_score)}`}
                                          title={`RBS Score: ${result.rbs_score} - ${getRBSInterpretation(result.rbs_score)} bias toward this team`}>
                                      {result.rbs_score > 0 ? '+' : ''}{result.rbs_score}
                                    </span>
                                  </td>
                                  <td className="px-3 py-4 whitespace-nowrap text-center text-xs">
                                    <span className={`inline-flex px-1 py-0.5 rounded text-xs ${
                                      result.stats_breakdown?.yellow_cards > 0.05 ? 'bg-red-100 text-red-700' :
                                      result.stats_breakdown?.yellow_cards < -0.05 ? 'bg-green-100 text-green-700' :
                                      'bg-gray-100 text-gray-600'
                                    }`}
                                    title={`Yellow cards differential: ${result.stats_breakdown?.yellow_cards > 0 ? 'Team gets ' + Math.abs(result.stats_breakdown?.yellow_cards || 0).toFixed(2) + ' more yellow cards per game with this referee' : result.stats_breakdown?.yellow_cards < 0 ? 'Team gets ' + Math.abs(result.stats_breakdown?.yellow_cards || 0).toFixed(2) + ' fewer yellow cards per game with this referee' : 'No significant difference'}`}>
                                      {result.stats_breakdown?.yellow_cards > 0 ? '+' : ''}
                                      {(result.stats_breakdown?.yellow_cards || 0).toFixed(2)}
                                    </span>
                                  </td>
                                  <td className="px-3 py-4 whitespace-nowrap text-center text-xs">
                                    <span className={`inline-flex px-1 py-0.5 rounded text-xs ${
                                      result.stats_breakdown?.red_cards > 0.05 ? 'bg-red-100 text-red-700' :
                                      result.stats_breakdown?.red_cards < -0.05 ? 'bg-green-100 text-green-700' :
                                      'bg-gray-100 text-gray-600'
                                    }`}>
                                      {result.stats_breakdown?.red_cards > 0 ? '+' : ''}
                                      {(result.stats_breakdown?.red_cards || 0).toFixed(2)}
                                    </span>
                                  </td>
                                  <td className="px-3 py-4 whitespace-nowrap text-center text-xs">
                                    <span className={`inline-flex px-1 py-0.5 rounded text-xs ${
                                      result.stats_breakdown?.fouls > 0.02 ? 'bg-red-100 text-red-700' :
                                      result.stats_breakdown?.fouls < -0.02 ? 'bg-green-100 text-green-700' :
                                      'bg-gray-100 text-gray-600'
                                    }`}>
                                      {result.stats_breakdown?.fouls > 0 ? '+' : ''}
                                      {(result.stats_breakdown?.fouls || 0).toFixed(2)}
                                    </span>
                                  </td>
                                  <td className="px-3 py-4 whitespace-nowrap text-center text-xs">
                                    <span className={`inline-flex px-1 py-0.5 rounded text-xs ${
                                      result.stats_breakdown?.fouls_drawn > 0.02 ? 'bg-green-100 text-green-700' :
                                      result.stats_breakdown?.fouls_drawn < -0.02 ? 'bg-red-100 text-red-700' :
                                      'bg-gray-100 text-gray-600'
                                    }`}>
                                      {result.stats_breakdown?.fouls_drawn > 0 ? '+' : ''}
                                      {(result.stats_breakdown?.fouls_drawn || 0).toFixed(2)}
                                    </span>
                                  </td>
                                  <td className="px-3 py-4 whitespace-nowrap text-center text-xs">
                                    <span className={`inline-flex px-1 py-0.5 rounded text-xs ${
                                      result.stats_breakdown?.penalties_awarded > 0.05 ? 'bg-green-100 text-green-700' :
                                      result.stats_breakdown?.penalties_awarded < -0.05 ? 'bg-red-100 text-red-700' :
                                      'bg-gray-100 text-gray-600'
                                    }`}>
                                      {result.stats_breakdown?.penalties_awarded > 0 ? '+' : ''}
                                      {(result.stats_breakdown?.penalties_awarded || 0).toFixed(2)}
                                    </span>
                                  </td>
                                  <td className="px-3 py-4 whitespace-nowrap text-center text-xs">
                                    <span className={`inline-flex px-1 py-0.5 rounded text-xs ${
                                      result.stats_breakdown?.xg_difference > 0.1 ? 'bg-green-100 text-green-700' :
                                      result.stats_breakdown?.xg_difference < -0.1 ? 'bg-red-100 text-red-700' :
                                      'bg-gray-100 text-gray-600'
                                    }`}>
                                      {result.stats_breakdown?.xg_difference > 0 ? '+' : ''}
                                      {(result.stats_breakdown?.xg_difference || 0).toFixed(2)}
                                    </span>
                                  </td>
                                  <td className="px-3 py-4 whitespace-nowrap text-center text-xs">
                                    <span className={`inline-flex px-1 py-0.5 rounded text-xs ${
                                      result.stats_breakdown?.possession_pct > 0.5 ? 'bg-green-100 text-green-700' :
                                      result.stats_breakdown?.possession_pct < -0.5 ? 'bg-red-100 text-red-700' :
                                      'bg-gray-100 text-gray-600'
                                    }`}>
                                      {result.stats_breakdown?.possession_pct > 0 ? '+' : ''}
                                      {(result.stats_breakdown?.possession_pct || 0).toFixed(2)}
                                    </span>
                                  </td>
                                  <td className="px-3 py-4 whitespace-nowrap text-center text-xs">
                                    {enhancedRBSData[result.team_name] ? (
                                      enhancedRBSData[result.team_name].loading ? (
                                        <div className="flex items-center justify-center">
                                          <div className="animate-spin rounded-full h-3 w-3 border-b border-blue-500"></div>
                                          <span className="ml-1 text-xs text-gray-400">Loading...</span>
                                        </div>
                                      ) : enhancedRBSData[result.team_name].error ? (
                                        <span className="text-xs text-red-400" title={enhancedRBSData[result.team_name].error}>Error</span>
                                      ) : enhancedRBSData[result.team_name].variance_analysis?.variance_ratios ? (
                                        <div className="space-y-1">
                                          {Object.entries(enhancedRBSData[result.team_name].variance_analysis.variance_ratios || {}).slice(0, 2).map(([stat, ratio]) => (
                                            <span key={stat} className={`inline-flex px-1 py-0.5 rounded text-xs ${
                                              ratio > 1.5 ? 'bg-orange-100 text-orange-700' :
                                              ratio < 0.5 ? 'bg-blue-100 text-blue-700' :
                                              'bg-gray-100 text-gray-600'
                                            }`}
                                            title={`${stat.replace(/_/g, ' ')}: ${ratio.toFixed(2)}x variance ratio (${ratio > 1.5 ? 'more variable than usual' : ratio < 0.5 ? 'very consistent' : 'normal variance'})`}>
                                              {stat.substring(0, 3)}: {ratio?.toFixed(1)}x
                                            </span>
                                          ))}
                                        </div>
                                      ) : (
                                        <span className="text-xs text-gray-400">No data</span>
                                      )
                                    ) : (
                                      <span className="text-xs text-gray-400">Loading...</span>
                                    )}
                                  </td>
                                  <td className="px-3 py-4 whitespace-nowrap text-center text-sm text-gray-900" title={`Total matches: ${result.matches_with_ref || 0} with referee, ${(result.total_matches || 0) - (result.matches_with_ref || 0)} without referee`}>
                                    <div className="text-center">
                                      <div className="font-medium">{result.matches_with_ref || 0}</div>
                                      <div className="text-xs text-gray-500">with ref</div>
                                      {result.total_matches && result.total_matches > result.matches_with_ref && (
                                        <div className="text-xs text-gray-400">{result.total_matches - result.matches_with_ref} without</div>
                                      )}
                                    </div>
                                  </td>
                                  <td className="px-3 py-4 whitespace-nowrap text-center">
                                    <span className={`inline-flex px-2 py-1 text-xs font-medium rounded-full ${getConfidenceColor(result.confidence_level)}`}>
                                      {result.confidence_level}%
                                    </span>
                                  </td>
                                </tr>
                              ))}
                            </tbody>
                          </table>
                          
                          {(!selectedRefereeDetails.rbs_results || selectedRefereeDetails.rbs_results.length === 0) && (
                            <div className="text-center py-8">
                              <p className="text-gray-500">No RBS results found for this referee.</p>
                            </div>
                          )}
                        </div>
                        
                        {/* Enhanced RBS Analysis */}
                        <div className="mt-6 bg-gradient-to-r from-blue-50 to-purple-50 p-4 rounded-lg border border-blue-200">
                          <h4 className="text-sm font-semibold text-blue-900 mb-3">🔬 Enhanced RBS Analysis</h4>
                          <p className="text-xs text-blue-800 mb-3">
                            Get detailed performance differential analysis and referee decision variance patterns for specific team-referee combinations.
                          </p>
                          <div className="flex flex-wrap gap-2">
                            {selectedRefereeDetails.rbs_results?.map((result, idx) => (
                              <button
                                key={idx}
                                onClick={async () => {
                                  try {
                                    const response = await axios.get(
                                      `${API}/enhanced-rbs-analysis/${encodeURIComponent(result.team_name)}/${encodeURIComponent(selectedRefereeDetails.referee)}`
                                    );
                                    
                                    if (response.data.success) {
                                      alert(`📊 Enhanced RBS Analysis for ${result.team_name}:

🎯 Performance Differential:
${Object.entries(response.data.standard_rbs.stats_breakdown || {}).map(([stat, value]) => 
  `• ${stat.replace(/_/g, ' ')}: ${value > 0 ? '+' : ''}${value}`).join('\n')}

📈 Variance Analysis:
${Object.entries(response.data.variance_analysis.variance_ratios || {}).map(([stat, ratio]) => 
  `• ${stat.replace(/_/g, ' ')}: ${ratio}x ${ratio > 1.5 ? '(more variable)' : ratio < 0.5 ? '(very consistent)' : '(normal)'}`).join('\n')}

📋 Summary:
• RBS Score: ${response.data.standard_rbs.rbs_score}
• Confidence: ${response.data.variance_analysis.confidence}
• Sample: ${response.data.standard_rbs.matches_with_ref} matches with referee`);
                                    } else {
                                      alert(`❌ ${response.data.message}`);
                                    }
                                  } catch (error) {
                                    alert(`❌ Error fetching enhanced analysis: ${error.response?.data?.detail || error.message}`);
                                  }
                                }}
                                className="px-3 py-1 bg-blue-600 text-white text-xs rounded hover:bg-blue-700"
                              >
                                📊 {result.team_name}
                              </button>
                            ))}
                          </div>
                          <div className="mt-2 text-xs text-blue-700">
                            <strong>Variance Analysis:</strong> Compares referee's decision consistency for each team vs their overall patterns. 
                            Ratios &gt;1.5 indicate more variable treatment than usual.
                          </div>
                        </div>
                        
                        {/* Legend for the statistics */}
                        <div className="mt-4 p-4 bg-gray-50 rounded-lg">
                          <h4 className="text-sm font-semibold text-gray-900 mb-2">RBS Component Legend</h4>
                          <div className="grid grid-cols-1 md:grid-cols-2 gap-2 text-xs text-gray-600">
                            <div>• <strong>Yellow Cards:</strong> Weight 0.3 (negative = more cards with this ref)</div>
                            <div>• <strong>Red Cards:</strong> Weight 0.5 (negative = more cards with this ref)</div>
                            <div>• <strong>Fouls:</strong> Weight 0.1 (negative = more fouls committed with this ref)</div>
                            <div>• <strong>Fouls Drawn:</strong> Weight 0.1 (positive = more fouls drawn with this ref)</div>
                            <div>• <strong>Penalties:</strong> Weight 0.5 (positive = more penalties awarded with this ref)</div>
                            <div>• <strong>xG Difference:</strong> Weight 0.4 (positive = higher xG with this ref)</div>
                            <div>• <strong>Possession:</strong> Weight 0.2 (positive = higher possession with this ref)</div>
                          </div>
                          <div className="mt-2 text-xs text-gray-500">
                            <span className="inline-block w-3 h-3 bg-green-100 rounded mr-1"></span>Favorable to team
                            <span className="inline-block w-3 h-3 bg-red-100 rounded mr-1 ml-3"></span>Unfavorable to team
                            <span className="inline-block w-3 h-3 bg-gray-100 rounded mr-1 ml-3"></span>Neutral
                          </div>
                        </div>
                      </div>
                    </div>
                  )}

                  {/* Detailed Enhanced RBS Analysis Table */}
                  {Object.keys(enhancedRBSData).length > 0 && (
                    <div className="mt-8">
                      <h4 className="text-lg font-semibold text-gray-900 mb-4">📊 Detailed Performance Differential Analysis</h4>
                      <div className="overflow-x-auto">
                        <table className="min-w-full divide-y divide-gray-200">
                          <thead className="bg-gray-50">
                            <tr>
                              <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Team</th>
                              <th className="px-3 py-3 text-center text-xs font-medium text-gray-500 uppercase tracking-wider">Goals Diff</th>
                              <th className="px-3 py-3 text-center text-xs font-medium text-gray-500 uppercase tracking-wider">Shots Diff</th>
                              <th className="px-3 py-3 text-center text-xs font-medium text-gray-500 uppercase tracking-wider">xG Diff</th>
                              <th className="px-3 py-3 text-center text-xs font-medium text-gray-500 uppercase tracking-wider">Penalties Diff</th>
                              <th className="px-3 py-3 text-center text-xs font-medium text-gray-500 uppercase tracking-wider">Fouls Drawn Diff</th>
                              <th className="px-3 py-3 text-center text-xs font-medium text-gray-500 uppercase tracking-wider">Possession Diff</th>
                              <th className="px-3 py-3 text-center text-xs font-medium text-gray-500 uppercase tracking-wider">Variance Confidence</th>
                            </tr>
                          </thead>
                          <tbody className="bg-white divide-y divide-gray-200">
                            {Object.entries(enhancedRBSData).map(([teamName, data]) => (
                              <tr key={teamName} className="hover:bg-gray-50">
                                <td className="px-4 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                                  {teamName}
                                </td>
                                <td className="px-3 py-4 whitespace-nowrap text-center text-xs">
                                  <span className={`inline-flex px-1 py-0.5 rounded text-xs ${
                                    (data.standard_rbs?.stats_breakdown?.goals || 0) > 0.1 ? 'bg-green-100 text-green-700' :
                                    (data.standard_rbs?.stats_breakdown?.goals || 0) < -0.1 ? 'bg-red-100 text-red-700' :
                                    'bg-gray-100 text-gray-600'
                                  }`}>
                                    {(data.standard_rbs?.stats_breakdown?.goals || 0) > 0 ? '+' : ''}
                                    {(data.standard_rbs?.stats_breakdown?.goals || 0).toFixed(2)}
                                  </span>
                                </td>
                                <td className="px-3 py-4 whitespace-nowrap text-center text-xs">
                                  <span className={`inline-flex px-1 py-0.5 rounded text-xs ${
                                    (data.standard_rbs?.stats_breakdown?.shots_total || 0) > 0.5 ? 'bg-green-100 text-green-700' :
                                    (data.standard_rbs?.stats_breakdown?.shots_total || 0) < -0.5 ? 'bg-red-100 text-red-700' :
                                    'bg-gray-100 text-gray-600'
                                  }`}>
                                    {(data.standard_rbs?.stats_breakdown?.shots_total || 0) > 0 ? '+' : ''}
                                    {(data.standard_rbs?.stats_breakdown?.shots_total || 0).toFixed(1)}
                                  </span>
                                </td>
                                <td className="px-3 py-4 whitespace-nowrap text-center text-xs">
                                  <span className={`inline-flex px-1 py-0.5 rounded text-xs ${
                                    (data.standard_rbs?.stats_breakdown?.xg_difference || 0) > 0.1 ? 'bg-green-100 text-green-700' :
                                    (data.standard_rbs?.stats_breakdown?.xg_difference || 0) < -0.1 ? 'bg-red-100 text-red-700' :
                                    'bg-gray-100 text-gray-600'
                                  }`}>
                                    {(data.standard_rbs?.stats_breakdown?.xg_difference || 0) > 0 ? '+' : ''}
                                    {(data.standard_rbs?.stats_breakdown?.xg_difference || 0).toFixed(2)}
                                  </span>
                                </td>
                                <td className="px-3 py-4 whitespace-nowrap text-center text-xs">
                                  <span className={`inline-flex px-1 py-0.5 rounded text-xs ${
                                    (data.standard_rbs?.stats_breakdown?.penalties_awarded || 0) > 0.05 ? 'bg-green-100 text-green-700' :
                                    (data.standard_rbs?.stats_breakdown?.penalties_awarded || 0) < -0.05 ? 'bg-red-100 text-red-700' :
                                    'bg-gray-100 text-gray-600'
                                  }`}>
                                    {(data.standard_rbs?.stats_breakdown?.penalties_awarded || 0) > 0 ? '+' : ''}
                                    {(data.standard_rbs?.stats_breakdown?.penalties_awarded || 0).toFixed(3)}
                                  </span>
                                </td>
                                <td className="px-3 py-4 whitespace-nowrap text-center text-xs">
                                  <span className={`inline-flex px-1 py-0.5 rounded text-xs ${
                                    (data.standard_rbs?.stats_breakdown?.fouls_drawn || 0) > 0.1 ? 'bg-green-100 text-green-700' :
                                    (data.standard_rbs?.stats_breakdown?.fouls_drawn || 0) < -0.1 ? 'bg-red-100 text-red-700' :
                                    'bg-gray-100 text-gray-600'
                                  }`}>
                                    {(data.standard_rbs?.stats_breakdown?.fouls_drawn || 0) > 0 ? '+' : ''}
                                    {(data.standard_rbs?.stats_breakdown?.fouls_drawn || 0).toFixed(2)}
                                  </span>
                                </td>
                                <td className="px-3 py-4 whitespace-nowrap text-center text-xs">
                                  <span className={`inline-flex px-1 py-0.5 rounded text-xs ${
                                    (data.standard_rbs?.stats_breakdown?.possession_percentage || 0) > 0.5 ? 'bg-green-100 text-green-700' :
                                    (data.standard_rbs?.stats_breakdown?.possession_percentage || 0) < -0.5 ? 'bg-red-100 text-red-700' :
                                    'bg-gray-100 text-gray-600'
                                  }`}>
                                    {(data.standard_rbs?.stats_breakdown?.possession_percentage || 0) > 0 ? '+' : ''}
                                    {(data.standard_rbs?.stats_breakdown?.possession_percentage || 0).toFixed(2)}
                                  </span>
                                </td>
                                <td className="px-3 py-4 whitespace-nowrap text-center text-xs">
                                  <span className={`inline-flex px-2 py-1 text-xs font-medium rounded-full ${
                                    data.variance_analysis?.confidence === 'Very High' ? 'bg-green-100 text-green-800' :
                                    data.variance_analysis?.confidence === 'High' ? 'bg-blue-100 text-blue-800' :
                                    data.variance_analysis?.confidence === 'Medium' ? 'bg-yellow-100 text-yellow-800' :
                                    'bg-gray-100 text-gray-800'
                                  }`}>
                                    {data.variance_analysis?.confidence || 'N/A'}
                                  </span>
                                </td>
                              </tr>
                            ))}
                          </tbody>
                        </table>
                      </div>
                      
                      {/* Explanation */}
                      <div className="mt-4 p-4 bg-blue-50 rounded-lg">
                        <h5 className="text-sm font-semibold text-blue-900 mb-2">📋 Performance Differential Explanation</h5>
                        <div className="text-xs text-blue-800 space-y-1">
                          <p><strong>Positive values (green):</strong> Team performs better with this referee</p>
                          <p><strong>Negative values (red):</strong> Team performs worse with this referee</p>
                          <p><strong>Variance Confidence:</strong> Statistical reliability of the variance analysis</p>
                          <p><strong>Calculation:</strong> Each value shows the difference between average performance with this referee vs all other referees</p>
                        </div>
                      </div>
                    </div>
                  )}

                  {/* Detailed Enhanced RBS Analysis Table */}
                  {Object.keys(enhancedRBSData).length > 0 && (
                    <div className="mt-8">
                      <h4 className="text-lg font-semibold text-gray-900 mb-4">📊 Detailed Performance Differential Analysis</h4>
                      <div className="overflow-x-auto">
                        <table className="min-w-full divide-y divide-gray-200">
                          <thead className="bg-gray-50">
                            <tr>
                              <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Team</th>
                              <th className="px-3 py-3 text-center text-xs font-medium text-gray-500 uppercase tracking-wider">Goals Diff</th>
                              <th className="px-3 py-3 text-center text-xs font-medium text-gray-500 uppercase tracking-wider">Shots Diff</th>
                              <th className="px-3 py-3 text-center text-xs font-medium text-gray-500 uppercase tracking-wider">xG Diff</th>
                              <th className="px-3 py-3 text-center text-xs font-medium text-gray-500 uppercase tracking-wider">Penalties Diff</th>
                              <th className="px-3 py-3 text-center text-xs font-medium text-gray-500 uppercase tracking-wider">Fouls Drawn Diff</th>
                              <th className="px-3 py-3 text-center text-xs font-medium text-gray-500 uppercase tracking-wider">Possession Diff</th>
                              <th className="px-3 py-3 text-center text-xs font-medium text-gray-500 uppercase tracking-wider">Variance Confidence</th>
                            </tr>
                          </thead>
                          <tbody className="bg-white divide-y divide-gray-200">
                            {Object.entries(enhancedRBSData).map(([teamName, data]) => (
                              <tr key={teamName} className="hover:bg-gray-50">
                                <td className="px-4 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                                  {teamName}
                                </td>
                                <td className="px-3 py-4 whitespace-nowrap text-center text-xs">
                                  <span className={`inline-flex px-1 py-0.5 rounded text-xs ${
                                    (data.standard_rbs?.stats_breakdown?.goals || 0) > 0.1 ? 'bg-green-100 text-green-700' :
                                    (data.standard_rbs?.stats_breakdown?.goals || 0) < -0.1 ? 'bg-red-100 text-red-700' :
                                    'bg-gray-100 text-gray-600'
                                  }`}>
                                    {(data.standard_rbs?.stats_breakdown?.goals || 0) > 0 ? '+' : ''}
                                    {(data.standard_rbs?.stats_breakdown?.goals || 0).toFixed(2)}
                                  </span>
                                </td>
                                <td className="px-3 py-4 whitespace-nowrap text-center text-xs">
                                  <span className={`inline-flex px-1 py-0.5 rounded text-xs ${
                                    (data.standard_rbs?.stats_breakdown?.shots_total || 0) > 0.5 ? 'bg-green-100 text-green-700' :
                                    (data.standard_rbs?.stats_breakdown?.shots_total || 0) < -0.5 ? 'bg-red-100 text-red-700' :
                                    'bg-gray-100 text-gray-600'
                                  }`}>
                                    {(data.standard_rbs?.stats_breakdown?.shots_total || 0) > 0 ? '+' : ''}
                                    {(data.standard_rbs?.stats_breakdown?.shots_total || 0).toFixed(1)}
                                  </span>
                                </td>
                                <td className="px-3 py-4 whitespace-nowrap text-center text-xs">
                                  <span className={`inline-flex px-1 py-0.5 rounded text-xs ${
                                    (data.standard_rbs?.stats_breakdown?.xg_difference || 0) > 0.1 ? 'bg-green-100 text-green-700' :
                                    (data.standard_rbs?.stats_breakdown?.xg_difference || 0) < -0.1 ? 'bg-red-100 text-red-700' :
                                    'bg-gray-100 text-gray-600'
                                  }`}>
                                    {(data.standard_rbs?.stats_breakdown?.xg_difference || 0) > 0 ? '+' : ''}
                                    {(data.standard_rbs?.stats_breakdown?.xg_difference || 0).toFixed(2)}
                                  </span>
                                </td>
                                <td className="px-3 py-4 whitespace-nowrap text-center text-xs">
                                  <span className={`inline-flex px-1 py-0.5 rounded text-xs ${
                                    (data.standard_rbs?.stats_breakdown?.penalties_awarded || 0) > 0.05 ? 'bg-green-100 text-green-700' :
                                    (data.standard_rbs?.stats_breakdown?.penalties_awarded || 0) < -0.05 ? 'bg-red-100 text-red-700' :
                                    'bg-gray-100 text-gray-600'
                                  }`}>
                                    {(data.standard_rbs?.stats_breakdown?.penalties_awarded || 0) > 0 ? '+' : ''}
                                    {(data.standard_rbs?.stats_breakdown?.penalties_awarded || 0).toFixed(3)}
                                  </span>
                                </td>
                                <td className="px-3 py-4 whitespace-nowrap text-center text-xs">
                                  <span className={`inline-flex px-1 py-0.5 rounded text-xs ${
                                    (data.standard_rbs?.stats_breakdown?.fouls_drawn || 0) > 0.1 ? 'bg-green-100 text-green-700' :
                                    (data.standard_rbs?.stats_breakdown?.fouls_drawn || 0) < -0.1 ? 'bg-red-100 text-red-700' :
                                    'bg-gray-100 text-gray-600'
                                  }`}>
                                    {(data.standard_rbs?.stats_breakdown?.fouls_drawn || 0) > 0 ? '+' : ''}
                                    {(data.standard_rbs?.stats_breakdown?.fouls_drawn || 0).toFixed(2)}
                                  </span>
                                </td>
                                <td className="px-3 py-4 whitespace-nowrap text-center text-xs">
                                  <span className={`inline-flex px-1 py-0.5 rounded text-xs ${
                                    (data.standard_rbs?.stats_breakdown?.possession_percentage || 0) > 0.5 ? 'bg-green-100 text-green-700' :
                                    (data.standard_rbs?.stats_breakdown?.possession_percentage || 0) < -0.5 ? 'bg-red-100 text-red-700' :
                                    'bg-gray-100 text-gray-600'
                                  }`}>
                                    {(data.standard_rbs?.stats_breakdown?.possession_percentage || 0) > 0 ? '+' : ''}
                                    {(data.standard_rbs?.stats_breakdown?.possession_percentage || 0).toFixed(2)}
                                  </span>
                                </td>
                                <td className="px-3 py-4 whitespace-nowrap text-center text-xs">
                                  <span className={`inline-flex px-2 py-1 text-xs font-medium rounded-full ${
                                    data.variance_analysis?.confidence === 'Very High' ? 'bg-green-100 text-green-800' :
                                    data.variance_analysis?.confidence === 'High' ? 'bg-blue-100 text-blue-800' :
                                    data.variance_analysis?.confidence === 'Medium' ? 'bg-yellow-100 text-yellow-800' :
                                    'bg-gray-100 text-gray-800'
                                  }`}>
                                    {data.variance_analysis?.confidence || 'N/A'}
                                  </span>
                                </td>
                              </tr>
                            ))}
                          </tbody>
                        </table>
                      </div>
                      
                      {/* Explanation */}
                      <div className="mt-4 p-4 bg-blue-50 rounded-lg">
                        <h5 className="text-sm font-semibold text-blue-900 mb-2">📋 Performance Differential Explanation</h5>
                        <div className="text-xs text-blue-800 space-y-1">
                          <p><strong>Positive values (green):</strong> Team performs better with this referee</p>
                          <p><strong>Negative values (red):</strong> Team performs worse with this referee</p>
                          <p><strong>Variance Confidence:</strong> Statistical reliability of the variance analysis</p>
                          <p><strong>Calculation:</strong> Each value shows the difference between average performance with this referee vs all other referees</p>
                        </div>
                      </div>
                    </div>
                  )}
                  
                  {/* Detailed Enhanced RBS Analysis Table */}
                  {Object.keys(enhancedRBSData).length > 0 && (
                    <div className="mt-8">
                      <h4 className="text-lg font-semibold text-gray-900 mb-4">📊 Detailed Performance Differential Analysis</h4>
                      <div className="overflow-x-auto">
                        <table className="min-w-full divide-y divide-gray-200">
                          <thead className="bg-gray-50">
                            <tr>
                              <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Team</th>
                              <th className="px-3 py-3 text-center text-xs font-medium text-gray-500 uppercase tracking-wider">Goals Diff</th>
                              <th className="px-3 py-3 text-center text-xs font-medium text-gray-500 uppercase tracking-wider">Shots Diff</th>
                              <th className="px-3 py-3 text-center text-xs font-medium text-gray-500 uppercase tracking-wider">xG Diff</th>
                              <th className="px-3 py-3 text-center text-xs font-medium text-gray-500 uppercase tracking-wider">Penalties Diff</th>
                              <th className="px-3 py-3 text-center text-xs font-medium text-gray-500 uppercase tracking-wider">Fouls Drawn Diff</th>
                              <th className="px-3 py-3 text-center text-xs font-medium text-gray-500 uppercase tracking-wider">Possession Diff</th>
                              <th className="px-3 py-3 text-center text-xs font-medium text-gray-500 uppercase tracking-wider">Variance Confidence</th>
                            </tr>
                          </thead>
                          <tbody className="bg-white divide-y divide-gray-200">
                            {Object.entries(enhancedRBSData).map(([teamName, data]) => (
                              <tr key={teamName} className="hover:bg-gray-50">
                                <td className="px-4 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                                  {teamName}
                                </td>
                                <td className="px-3 py-4 whitespace-nowrap text-center text-xs">
                                  <span className={`inline-flex px-1 py-0.5 rounded text-xs ${
                                    (data.standard_rbs?.stats_breakdown?.goals || 0) > 0.1 ? 'bg-green-100 text-green-700' :
                                    (data.standard_rbs?.stats_breakdown?.goals || 0) < -0.1 ? 'bg-red-100 text-red-700' :
                                    'bg-gray-100 text-gray-600'
                                  }`}>
                                    {(data.standard_rbs?.stats_breakdown?.goals || 0) > 0 ? '+' : ''}
                                    {(data.standard_rbs?.stats_breakdown?.goals || 0).toFixed(2)}
                                  </span>
                                </td>
                                <td className="px-3 py-4 whitespace-nowrap text-center text-xs">
                                  <span className={`inline-flex px-1 py-0.5 rounded text-xs ${
                                    (data.standard_rbs?.stats_breakdown?.shots_total || 0) > 0.5 ? 'bg-green-100 text-green-700' :
                                    (data.standard_rbs?.stats_breakdown?.shots_total || 0) < -0.5 ? 'bg-red-100 text-red-700' :
                                    'bg-gray-100 text-gray-600'
                                  }`}>
                                    {(data.standard_rbs?.stats_breakdown?.shots_total || 0) > 0 ? '+' : ''}
                                    {(data.standard_rbs?.stats_breakdown?.shots_total || 0).toFixed(1)}
                                  </span>
                                </td>
                                <td className="px-3 py-4 whitespace-nowrap text-center text-xs">
                                  <span className={`inline-flex px-1 py-0.5 rounded text-xs ${
                                    (data.standard_rbs?.stats_breakdown?.xg_difference || 0) > 0.1 ? 'bg-green-100 text-green-700' :
                                    (data.standard_rbs?.stats_breakdown?.xg_difference || 0) < -0.1 ? 'bg-red-100 text-red-700' :
                                    'bg-gray-100 text-gray-600'
                                  }`}>
                                    {(data.standard_rbs?.stats_breakdown?.xg_difference || 0) > 0 ? '+' : ''}
                                    {(data.standard_rbs?.stats_breakdown?.xg_difference || 0).toFixed(2)}
                                  </span>
                                </td>
                                <td className="px-3 py-4 whitespace-nowrap text-center text-xs">
                                  <span className={`inline-flex px-1 py-0.5 rounded text-xs ${
                                    (data.standard_rbs?.stats_breakdown?.penalties_awarded || 0) > 0.05 ? 'bg-green-100 text-green-700' :
                                    (data.standard_rbs?.stats_breakdown?.penalties_awarded || 0) < -0.05 ? 'bg-red-100 text-red-700' :
                                    'bg-gray-100 text-gray-600'
                                  }`}>
                                    {(data.standard_rbs?.stats_breakdown?.penalties_awarded || 0) > 0 ? '+' : ''}
                                    {(data.standard_rbs?.stats_breakdown?.penalties_awarded || 0).toFixed(3)}
                                  </span>
                                </td>
                                <td className="px-3 py-4 whitespace-nowrap text-center text-xs">
                                  <span className={`inline-flex px-1 py-0.5 rounded text-xs ${
                                    (data.standard_rbs?.stats_breakdown?.fouls_drawn || 0) > 0.1 ? 'bg-green-100 text-green-700' :
                                    (data.standard_rbs?.stats_breakdown?.fouls_drawn || 0) < -0.1 ? 'bg-red-100 text-red-700' :
                                    'bg-gray-100 text-gray-600'
                                  }`}>
                                    {(data.standard_rbs?.stats_breakdown?.fouls_drawn || 0) > 0 ? '+' : ''}
                                    {(data.standard_rbs?.stats_breakdown?.fouls_drawn || 0).toFixed(2)}
                                  </span>
                                </td>
                                <td className="px-3 py-4 whitespace-nowrap text-center text-xs">
                                  <span className={`inline-flex px-1 py-0.5 rounded text-xs ${
                                    (data.standard_rbs?.stats_breakdown?.possession_percentage || 0) > 0.5 ? 'bg-green-100 text-green-700' :
                                    (data.standard_rbs?.stats_breakdown?.possession_percentage || 0) < -0.5 ? 'bg-red-100 text-red-700' :
                                    'bg-gray-100 text-gray-600'
                                  }`}>
                                    {(data.standard_rbs?.stats_breakdown?.possession_percentage || 0) > 0 ? '+' : ''}
                                    {(data.standard_rbs?.stats_breakdown?.possession_percentage || 0).toFixed(2)}
                                  </span>
                                </td>
                                <td className="px-3 py-4 whitespace-nowrap text-center text-xs">
                                  <span className={`inline-flex px-2 py-1 text-xs font-medium rounded-full ${
                                    data.variance_analysis?.confidence === 'Very High' ? 'bg-green-100 text-green-800' :
                                    data.variance_analysis?.confidence === 'High' ? 'bg-blue-100 text-blue-800' :
                                    data.variance_analysis?.confidence === 'Medium' ? 'bg-yellow-100 text-yellow-800' :
                                    'bg-gray-100 text-gray-800'
                                  }`}>
                                    {data.variance_analysis?.confidence || 'N/A'}
                                  </span>
                                </td>
                              </tr>
                            ))}
                          </tbody>
                        </table>
                      </div>
                      
                      {/* Explanation */}
                      <div className="mt-4 p-4 bg-blue-50 rounded-lg">
                        <h5 className="text-sm font-semibold text-blue-900 mb-2">📋 Performance Differential Explanation</h5>
                        <div className="text-xs text-blue-800 space-y-1">
                          <p><strong>Positive values (green):</strong> Team performs better with this referee</p>
                          <p><strong>Negative values (red):</strong> Team performs worse with this referee</p>
                          <p><strong>Variance Confidence:</strong> Statistical reliability of the variance analysis</p>
                          <p><strong>Calculation:</strong> Each value shows the difference between average performance with this referee vs all other referees</p>
                        </div>
                      </div>
                    </div>
                  )}}
                </div>
              </>
            )}
          </div>
        )}
      </div>
    </div>
  );
}

export default App;