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

  // Fetch initial data
  useEffect(() => {
    fetchStats();
    fetchTeams();
    fetchReferees();
    fetchRBSResults();
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

  const fetchRBSResults = async () => {
    try {
      const params = {};
      if (selectedTeam) params.team = selectedTeam;
      if (selectedReferee) params.referee = selectedReferee;
      
      const response = await axios.get(`${API}/rbs-results`, { params });
      setRbsResults(response.data.results || []);
    } catch (error) {
      console.error('Error fetching RBS results:', error);
    }
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
      fetchRBSResults();
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

  // Apply filters when team/referee selection changes
  useEffect(() => {
    fetchRBSResults();
  }, [selectedTeam, selectedReferee]);

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
            {['dashboard', 'upload', 'results'].map((tab) => (
              <button
                key={tab}
                onClick={() => setActiveTab(tab)}
                className={`py-4 px-1 border-b-2 font-medium text-sm capitalize ${
                  activeTab === tab
                    ? 'border-blue-500 text-blue-600'
                    : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                }`}
              >
                {tab}
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
            {/* Filters */}
            <div className="bg-white p-6 rounded-lg shadow-sm border">
              <h2 className="text-xl font-bold text-gray-900 mb-4">Filter Results</h2>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">Team</label>
                  <select
                    value={selectedTeam}
                    onChange={(e) => setSelectedTeam(e.target.value)}
                    className="w-full p-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  >
                    <option value="">All Teams</option>
                    {teams.map(team => (
                      <option key={team} value={team}>{team}</option>
                    ))}
                  </select>
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">Referee</label>
                  <select
                    value={selectedReferee}
                    onChange={(e) => setSelectedReferee(e.target.value)}
                    className="w-full p-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  >
                    <option value="">All Referees</option>
                    {referees.map(referee => (
                      <option key={referee} value={referee}>{referee}</option>
                    ))}
                  </select>
                </div>
              </div>
            </div>

            {/* Results Table */}
            <div className="bg-white rounded-lg shadow-sm border overflow-hidden">
              <div className="px-6 py-4 border-b">
                <h2 className="text-xl font-bold text-gray-900">RBS Results ({rbsResults.length})</h2>
                <p className="text-sm text-gray-600 mt-1">Positive scores indicate referee favors the team, negative scores indicate bias against</p>
              </div>
              
              <div className="overflow-x-auto">
                <table className="min-w-full divide-y divide-gray-200">
                  <thead className="bg-gray-50">
                    <tr>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Team</th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Referee</th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">RBS Score</th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Interpretation</th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Matches</th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Confidence</th>
                    </tr>
                  </thead>
                  <tbody className="bg-white divide-y divide-gray-200">
                    {rbsResults.map((result, index) => (
                      <tr key={index} className="hover:bg-gray-50">
                        <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                          {result.team_name}
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                          {result.referee}
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap">
                          <span className={`inline-flex px-2 py-1 text-xs font-semibold rounded-full ${getRBSColor(result.rbs_score)}`}>
                            {result.rbs_score > 0 ? '+' : ''}{result.rbs_score}
                          </span>
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                          {getRBSInterpretation(result.rbs_score)}
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                          {result.matches_with_ref}
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap">
                          <span className={`inline-flex px-2 py-1 text-xs font-medium rounded-full ${
                            result.confidence_level === 'high' ? 'bg-green-100 text-green-800' :
                            result.confidence_level === 'medium' ? 'bg-yellow-100 text-yellow-800' :
                            'bg-red-100 text-red-800'
                          }`}>
                            {result.confidence_level}
                          </span>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
                
                {rbsResults.length === 0 && (
                  <div className="text-center py-12">
                    <p className="text-gray-500">No RBS results found. Upload data and calculate scores first.</p>
                  </div>
                )}
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}

export default App;