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
  
  // New state for referee-based navigation
  const [refereeSummary, setRefereeSummary] = useState([]);
  const [selectedRefereeDetails, setSelectedRefereeDetails] = useState(null);
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

  // Fetch initial data
  useEffect(() => {
    fetchStats();
    fetchTeams();
    fetchReferees();
    fetchRefereeSummary();
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

  const fetchRefereeDetails = async (refereeName) => {
    try {
      console.log('Fetching referee details for:', refereeName);
      const response = await axios.get(`${API}/referee/${encodeURIComponent(refereeName)}`);
      console.log('Referee details response:', response.data);
      setSelectedRefereeDetails(response.data);
      setViewingReferee(refereeName);
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
      const response = await axios.post(`${API}/predict-match`, predictionForm);
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
            {['dashboard', 'upload', 'predict', 'results'].map((tab) => (
              <button
                key={tab}
                onClick={() => {
                  setActiveTab(tab);
                  if (tab === 'results') {
                    console.log('Results tab clicked, fetching referee summary...');
                    fetchRefereeSummary();
                  }
                }}
                className={`py-4 px-1 border-b-2 font-medium text-sm capitalize ${
                  activeTab === tab
                    ? 'border-blue-500 text-blue-600'
                    : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                }`}
              >
                {tab === 'predict' ? 'Match Prediction' : tab}
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
              <h2 className="text-xl font-bold text-gray-900 mb-4">RBS Formula Explanation</h2>
              <div className="text-gray-700 space-y-2">
                <p><strong>RBS (Referee Bias Score)</strong> measures how a specific referee influences a team's performance compared to that team's performance with other referees.</p>
                <p><strong>Formula:</strong> RBS(team,referee) = (1/N) × Σ[TeamStat(vs referee) - TeamStat(vs others)] × weight</p>
                <div className="mt-4 grid grid-cols-2 gap-4 text-sm">
                  <div>
                    <h4 className="font-semibold">Statistics & Weights:</h4>
                    <ul className="mt-2 space-y-1">
                      <li>• Yellow cards: 0.3</li>
                      <li>• Red cards: 0.5</li>
                      <li>• Fouls committed: 0.1</li>
                      <li>• Fouls drawn: 0.1</li>
                    </ul>
                  </div>
                  <div>
                    <h4 className="font-semibold">Additional Factors:</h4>
                    <ul className="mt-2 space-y-1">
                      <li>• Penalties awarded: 0.5</li>
                      <li>• xG difference: 0.4</li>
                      <li>• Possession %: 0.2</li>
                    </ul>
                  </div>
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
                  <p className="text-sm text-gray-600 mb-4">Required columns: match_id, player_name, team_name, is_home, goals, assists, yellow_cards, fouls_committed, fouls_drawn, xg</p>
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
                                <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">RBS Score</th>
                                <th className="px-3 py-3 text-center text-xs font-medium text-gray-500 uppercase tracking-wider">Yellow Cards</th>
                                <th className="px-3 py-3 text-center text-xs font-medium text-gray-500 uppercase tracking-wider">Red Cards</th>
                                <th className="px-3 py-3 text-center text-xs font-medium text-gray-500 uppercase tracking-wider">Fouls</th>
                                <th className="px-3 py-3 text-center text-xs font-medium text-gray-500 uppercase tracking-wider">Fouls Drawn</th>
                                <th className="px-3 py-3 text-center text-xs font-medium text-gray-500 uppercase tracking-wider">Penalties</th>
                                <th className="px-3 py-3 text-center text-xs font-medium text-gray-500 uppercase tracking-wider">xG Diff</th>
                                <th className="px-3 py-3 text-center text-xs font-medium text-gray-500 uppercase tracking-wider">Possession</th>
                                <th className="px-3 py-3 text-center text-xs font-medium text-gray-500 uppercase tracking-wider">Matches</th>
                                <th className="px-3 py-3 text-center text-xs font-medium text-gray-500 uppercase tracking-wider">Confidence</th>
                              </tr>
                            </thead>
                            <tbody className="bg-white divide-y divide-gray-200">
                              {selectedRefereeDetails.rbs_results?.map((result, index) => (
                                <tr key={index} className="hover:bg-gray-50">
                                  <td className="px-4 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                                    {result.team_name}
                                  </td>
                                  <td className="px-4 py-4 whitespace-nowrap">
                                    <span className={`inline-flex px-2 py-1 text-xs font-semibold rounded-full ${getRBSColor(result.rbs_score)}`}>
                                      {result.rbs_score > 0 ? '+' : ''}{result.rbs_score}
                                    </span>
                                  </td>
                                  <td className="px-3 py-4 whitespace-nowrap text-center text-xs">
                                    <span className={`inline-flex px-1 py-0.5 rounded text-xs ${
                                      result.stats_breakdown?.yellow_cards > 0.05 ? 'bg-red-100 text-red-700' :
                                      result.stats_breakdown?.yellow_cards < -0.05 ? 'bg-green-100 text-green-700' :
                                      'bg-gray-100 text-gray-600'
                                    }`}>
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
                                  <td className="px-3 py-4 whitespace-nowrap text-center text-sm text-gray-900">
                                    {result.matches_with_ref}
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