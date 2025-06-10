import React, { useState, useEffect } from 'react';
import axios from 'axios';
import Header from './components/Header';
import Navigation from './components/Navigation';
import Dashboard from './components/Dashboard';
import UploadData from './components/UploadData';
import StandardPredict from './components/StandardPredict';
import EnhancedXGBoost from './components/EnhancedXGBoost';
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
        checkRBSStatus()
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