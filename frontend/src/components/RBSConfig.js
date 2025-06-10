import React from 'react';
import { DEFAULT_RBS_CONFIG } from '../analysis-components';
import { ConfigurationList } from '../advanced-features';

const RBSConfig = ({
  rbsConfig,
  setRbsConfig,
  rbsConfigName,
  setRbsConfigName,
  allRbsConfigs,
  setAllRbsConfigs,
  loadingRbsConfigs,
  setLoadingRbsConfigs,
  savingRbsConfig,
  setSavingRbsConfig,
  saveRBSConfig,
  loadRBSConfig,
  deleteRBSConfig,
  fetchAllRBSConfigs
}) => {

  const handleRbsConfigChange = (parameter, value) => {
    setRbsConfig(prev => ({
      ...prev,
      [parameter]: parseFloat(value) || value
    }));
  };

  const handleSaveRbsConfig = async () => {
    if (!rbsConfigName.trim()) {
      alert('Please enter a configuration name');
      return;
    }

    setSavingRbsConfig(true);
    try {
      await saveRBSConfig(rbsConfigName, rbsConfig);
      await fetchAllRBSConfigs(); // Refresh the list
      alert(`✅ RBS Configuration "${rbsConfigName}" saved successfully!`);
    } catch (error) {
      console.error('Error saving RBS configuration:', error);
      alert(`❌ Error saving RBS configuration: ${error.response?.data?.detail || error.message}`);
    } finally {
      setSavingRbsConfig(false);
    }
  };

  const handleLoadRbsConfig = async (selectedConfigName) => {
    setLoadingRbsConfigs(true);
    try {
      const config = await loadRBSConfig(selectedConfigName);
      setRbsConfig(config);
      setRbsConfigName(selectedConfigName);
      alert(`✅ RBS Configuration "${selectedConfigName}" loaded successfully!`);
    } catch (error) {
      console.error('Error loading RBS configuration:', error);
      alert(`❌ Error loading RBS configuration: ${error.response?.data?.detail || error.message}`);
    } finally {
      setLoadingRbsConfigs(false);
    }
  };

  const handleDeleteRbsConfig = async (selectedConfigName) => {
    if (!window.confirm(`Are you sure you want to delete the RBS configuration "${selectedConfigName}"?`)) {
      return;
    }

    try {
      await deleteRBSConfig(selectedConfigName);
      await fetchAllRBSConfigs(); // Refresh the list
      alert(`✅ RBS Configuration "${selectedConfigName}" deleted successfully!`);
    } catch (error) {
      console.error('Error deleting RBS configuration:', error);
      alert(`❌ Error deleting RBS configuration: ${error.response?.data?.detail || error.message}`);
    }
  };

  const resetRbsToDefaults = () => {
    if (window.confirm('Reset all RBS parameters to default values?')) {
      setRbsConfig({...DEFAULT_RBS_CONFIG});
      setRbsConfigName('');
    }
  };

  const rbsParameters = [
    {
      category: 'Card Decision Weights',
      params: [
        { key: 'yellow_card_weight', label: 'Yellow Card Weight', min: 0, max: 2, step: 0.1, description: 'Impact of yellow card decisions on bias score' },
        { key: 'red_card_weight', label: 'Red Card Weight', min: 0, max: 5, step: 0.2, description: 'Impact of red card decisions on bias score' },
        { key: 'second_yellow_weight', label: 'Second Yellow Weight', min: 0, max: 3, step: 0.1, description: 'Impact of second yellow card decisions' }
      ]
    },
    {
      category: 'Foul Decision Weights',
      params: [
        { key: 'fouls_committed_weight', label: 'Fouls Committed Weight', min: 0, max: 1, step: 0.05, description: 'Weight for fouls called against team' },
        { key: 'fouls_drawn_weight', label: 'Fouls Drawn Weight', min: 0, max: 1, step: 0.05, description: 'Weight for fouls called in favor of team' },
        { key: 'foul_differential_multiplier', label: 'Foul Differential Multiplier', min: 1, max: 3, step: 0.1, description: 'Amplifier for foul count differences' }
      ]
    },
    {
      category: 'Penalty Decision Weights',
      params: [
        { key: 'penalties_awarded_weight', label: 'Penalties Awarded Weight', min: 0, max: 5, step: 0.2, description: 'Impact of penalty decisions awarded' },
        { key: 'penalties_conceded_weight', label: 'Penalties Conceded Weight', min: 0, max: 5, step: 0.2, description: 'Impact of penalty decisions against' },
        { key: 'penalty_conversion_factor', label: 'Penalty Conversion Factor', min: 0.5, max: 1.5, step: 0.05, description: 'Adjustment for penalty conversion rates' }
      ]
    },
    {
      category: 'Statistical Thresholds',
      params: [
        { key: 'minimum_matches_threshold', label: 'Minimum Matches Threshold', min: 1, max: 20, step: 1, description: 'Minimum matches required for RBS calculation' },
        { key: 'confidence_threshold', label: 'Confidence Threshold', min: 0.5, max: 0.99, step: 0.05, description: 'Statistical significance threshold' },
        { key: 'variance_sensitivity', label: 'Variance Sensitivity', min: 0.1, max: 2, step: 0.1, description: 'Sensitivity to statistical variance' }
      ]
    },
    {
      category: 'Advanced Parameters',
      params: [
        { key: 'time_decay_factor', label: 'Time Decay Factor', min: 0.8, max: 1, step: 0.01, description: 'Decay rate for historical data' },
        { key: 'home_away_adjustment', label: 'Home/Away Adjustment', min: 0.8, max: 1.2, step: 0.05, description: 'Adjustment for venue-specific bias' },
        { key: 'league_normalization', label: 'League Normalization', min: 0.5, max: 1.5, step: 0.1, description: 'Cross-league comparison adjustment' }
      ]
    }
  ];

  return (
    <div className="space-y-6">
      <div className="bg-white p-6 rounded-lg shadow-lg border border-gray-200">
        <h2 className="text-xl font-bold mb-4" style={{color: '#002629'}}>⚖️ Referee Bias Score (RBS) Configuration</h2>
        <p className="mb-6" style={{color: '#002629', opacity: 0.8}}>
          Configure the weights and parameters used to calculate Referee Bias Scores for fair and accurate analysis.
        </p>

        {/* RBS Configuration Management */}
        <div className="mb-6 p-4 rounded-lg border-2" style={{backgroundColor: '#F2E9E4', borderColor: '#12664F'}}>
          <h3 className="font-semibold mb-4" style={{color: '#002629'}}>💾 RBS Configuration Management</h3>
          
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-4">
            <div>
              <label className="block text-sm font-medium mb-2" style={{color: '#002629'}}>Configuration Name</label>
              <input
                type="text"
                value={rbsConfigName}
                onChange={(e) => setRbsConfigName(e.target.value)}
                placeholder="Enter RBS configuration name..."
                className="form-input w-full"
              />
            </div>
            <div className="flex items-end space-x-2">
              <button
                onClick={handleSaveRbsConfig}
                disabled={!rbsConfigName.trim() || savingRbsConfig}
                className="px-4 py-2 text-white font-medium rounded hover:opacity-90 disabled:opacity-50 disabled:cursor-not-allowed flex items-center space-x-2"
                style={{backgroundColor: '#12664F'}}
              >
                {savingRbsConfig ? (
                  <>
                    <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white"></div>
                    <span>Saving...</span>
                  </>
                ) : (
                  <>
                    <span>💾</span>
                    <span>Save Config</span>
                  </>
                )}
              </button>
              <button
                onClick={resetRbsToDefaults}
                className="px-4 py-2 text-white font-medium rounded hover:opacity-90 transition-opacity"
                style={{backgroundColor: '#002629'}}
              >
                🔄 Reset to Defaults
              </button>
            </div>
          </div>

          {/* Saved RBS Configurations List */}
          <ConfigurationList
            configurations={allRbsConfigs}
            type="RBS"
            onLoad={handleLoadRbsConfig}
            onDelete={handleDeleteRbsConfig}
            loading={loadingRbsConfigs}
          />
        </div>

        {/* RBS Parameter Configuration */}
        <div className="space-y-6">
          {rbsParameters.map(category => (
            <div key={category.category} className="p-4 rounded-lg border-2" style={{backgroundColor: '#A3D9FF', borderColor: '#12664F'}}>
              <h3 className="font-semibold mb-4" style={{color: '#002629'}}>{category.category}</h3>
              
              <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
                {category.params.map(param => (
                  <div key={param.key} className="bg-white p-4 rounded border">
                    <div className="flex items-center justify-between mb-2">
                      <label className="font-medium text-sm" style={{color: '#002629'}}>{param.label}</label>
                      <div className="flex items-center space-x-2">
                        <input
                          type="number"
                          min={param.min}
                          max={param.max}
                          step={param.step}
                          value={rbsConfig[param.key] || 0}
                          onChange={(e) => handleRbsConfigChange(param.key, e.target.value)}
                          className="w-20 px-2 py-1 text-sm border rounded"
                        />
                        <span className="text-xs" style={{color: '#002629', opacity: 0.7}}>
                          [{param.min}-{param.max}]
                        </span>
                      </div>
                    </div>
                    
                    <input
                      type="range"
                      min={param.min}
                      max={param.max}
                      step={param.step}
                      value={rbsConfig[param.key] || 0}
                      onChange={(e) => handleRbsConfigChange(param.key, e.target.value)}
                      className="w-full mb-2"
                    />
                    
                    <p className="text-xs" style={{color: '#002629', opacity: 0.6}}>{param.description}</p>
                  </div>
                ))}
              </div>
            </div>
          ))}
        </div>

        {/* RBS Configuration Summary */}
        <div className="mt-6 p-4 rounded-lg" style={{backgroundColor: '#A3D9FF'}}>
          <h3 className="font-semibold mb-3" style={{color: '#002629'}}>📋 Current RBS Configuration Summary</h3>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
            <div>
              <div className="font-medium" style={{color: '#002629'}}>Card Weights</div>
              <div style={{color: '#002629', opacity: 0.8}}>
                Yellow: {rbsConfig.yellow_card_weight || 0} | 
                Red: {rbsConfig.red_card_weight || 0}
              </div>
            </div>
            <div>
              <div className="font-medium" style={{color: '#002629'}}>Foul Weights</div>
              <div style={{color: '#002629', opacity: 0.8}}>
                Committed: {rbsConfig.fouls_committed_weight || 0} | 
                Drawn: {rbsConfig.fouls_drawn_weight || 0}
              </div>
            </div>
            <div>
              <div className="font-medium" style={{color: '#002629'}}>Penalty Weights</div>
              <div style={{color: '#002629', opacity: 0.8}}>
                Awarded: {rbsConfig.penalties_awarded_weight || 0} | 
                Conceded: {rbsConfig.penalties_conceded_weight || 0}
              </div>
            </div>
            <div>
              <div className="font-medium" style={{color: '#002629'}}>Thresholds</div>
              <div style={{color: '#002629', opacity: 0.8}}>
                Min Matches: {rbsConfig.minimum_matches_threshold || 0} | 
                Confidence: {rbsConfig.confidence_threshold || 0}
              </div>
            </div>
          </div>
          
          <div className="mt-4 p-3 rounded" style={{backgroundColor: 'white'}}>
            <h4 className="font-medium mb-2" style={{color: '#002629'}}>🧮 RBS Calculation Formula</h4>
            <div className="text-xs font-mono" style={{color: '#002629', opacity: 0.8}}>
              RBS = (Yellow Cards × {rbsConfig.yellow_card_weight || 0}) + (Red Cards × {rbsConfig.red_card_weight || 0}) + 
              (Foul Differential × {rbsConfig.foul_differential_multiplier || 0}) + 
              (Penalty Differential × {rbsConfig.penalties_awarded_weight || 0})
            </div>
            <div className="text-xs mt-1" style={{color: '#002629', opacity: 0.6}}>
              Adjusted for time decay ({rbsConfig.time_decay_factor || 0}), home/away bias ({rbsConfig.home_away_adjustment || 0}), 
              and league normalization ({rbsConfig.league_normalization || 0})
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default RBSConfig;