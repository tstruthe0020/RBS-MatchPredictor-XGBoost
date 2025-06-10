import React from 'react';
import { DEFAULT_PREDICTION_CONFIG } from '../analysis-components';
import { ConfigurationList } from '../advanced-features';

const PredictionConfig = ({
  predictionConfig,
  setPredictionConfig,
  configName,
  setConfigName,
  allPredictionConfigs,
  setAllPredictionConfigs,
  loadingConfigs,
  setLoadingConfigs,
  savingConfig,
  setSavingConfig,
  savePredictionConfig,
  loadPredictionConfig,
  deletePredictionConfig,
  fetchAllPredictionConfigs
}) => {

  const handleConfigChange = (parameter, value) => {
    setPredictionConfig(prev => ({
      ...prev,
      [parameter]: parseFloat(value) || value
    }));
  };

  const handleSaveConfig = async () => {
    if (!configName.trim()) {
      alert('Please enter a configuration name');
      return;
    }

    setSavingConfig(true);
    try {
      await savePredictionConfig(configName, predictionConfig);
      await fetchAllPredictionConfigs(); // Refresh the list
      alert(`✅ Configuration "${configName}" saved successfully!`);
    } catch (error) {
      console.error('Error saving configuration:', error);
      alert(`❌ Error saving configuration: ${error.response?.data?.detail || error.message}`);
    } finally {
      setSavingConfig(false);
    }
  };

  const handleLoadConfig = async (selectedConfigName) => {
    setLoadingConfigs(true);
    try {
      const config = await loadPredictionConfig(selectedConfigName);
      setPredictionConfig(config);
      setConfigName(selectedConfigName);
      alert(`✅ Configuration "${selectedConfigName}" loaded successfully!`);
    } catch (error) {
      console.error('Error loading configuration:', error);
      alert(`❌ Error loading configuration: ${error.response?.data?.detail || error.message}`);
    } finally {
      setLoadingConfigs(false);
    }
  };

  const handleDeleteConfig = async (selectedConfigName) => {
    if (!window.confirm(`Are you sure you want to delete the configuration "${selectedConfigName}"?`)) {
      return;
    }

    try {
      await deletePredictionConfig(selectedConfigName);
      await fetchAllPredictionConfigs(); // Refresh the list
      alert(`✅ Configuration "${selectedConfigName}" deleted successfully!`);
    } catch (error) {
      console.error('Error deleting configuration:', error);
      alert(`❌ Error deleting configuration: ${error.response?.data?.detail || error.message}`);
    }
  };

  const resetToDefaults = () => {
    if (window.confirm('Reset all parameters to default values?')) {
      setPredictionConfig({...DEFAULT_PREDICTION_CONFIG});
      setConfigName('');
    }
  };

  const parameters = [
    {
      category: 'Team Performance Weights',
      params: [
        { key: 'team_form_weight', label: 'Team Form Weight', min: 0, max: 2, step: 0.1, description: 'Recent team performance impact' },
        { key: 'home_advantage_weight', label: 'Home Advantage Weight', min: 0, max: 2, step: 0.1, description: 'Home field advantage multiplier' },
        { key: 'head_to_head_weight', label: 'Head-to-Head Weight', min: 0, max: 2, step: 0.1, description: 'Historical matchup importance' },
        { key: 'league_position_weight', label: 'League Position Weight', min: 0, max: 2, step: 0.1, description: 'Current league standing impact' }
      ]
    },
    {
      category: 'Statistical Factors',
      params: [
        { key: 'goals_scored_weight', label: 'Goals Scored Weight', min: 0, max: 2, step: 0.1, description: 'Offensive capability weight' },
        { key: 'goals_conceded_weight', label: 'Goals Conceded Weight', min: 0, max: 2, step: 0.1, description: 'Defensive weakness weight' },
        { key: 'xg_weight', label: 'Expected Goals Weight', min: 0, max: 2, step: 0.1, description: 'xG statistical importance' },
        { key: 'possession_weight', label: 'Possession Weight', min: 0, max: 2, step: 0.1, description: 'Ball control impact' }
      ]
    },
    {
      category: 'External Factors',
      params: [
        { key: 'referee_bias_weight', label: 'Referee Bias Weight', min: 0, max: 2, step: 0.1, description: 'RBS impact on predictions' },
        { key: 'injury_impact_weight', label: 'Injury Impact Weight', min: 0, max: 2, step: 0.1, description: 'Player absence penalty' },
        { key: 'weather_factor', label: 'Weather Factor', min: 0, max: 1, step: 0.05, description: 'Weather condition influence' },
        { key: 'crowd_factor', label: 'Crowd Factor', min: 0, max: 1, step: 0.05, description: 'Fan attendance impact' }
      ]
    },
    {
      category: 'Model Parameters',
      params: [
        { key: 'confidence_threshold', label: 'Confidence Threshold', min: 0.5, max: 0.95, step: 0.05, description: 'Minimum prediction confidence' },
        { key: 'learning_rate', label: 'Learning Rate', min: 0.01, max: 0.3, step: 0.01, description: 'Model learning speed' },
        { key: 'regularization_strength', label: 'Regularization Strength', min: 0, max: 1, step: 0.1, description: 'Overfitting prevention' }
      ]
    }
  ];

  return (
    <div className="space-y-6">
      <div className="bg-white p-6 rounded-lg shadow-lg border border-gray-200">
        <h2 className="text-xl font-bold mb-4" style={{color: '#002629'}}>⚙️ Prediction Configuration</h2>
        <p className="mb-6" style={{color: '#002629', opacity: 0.8}}>
          Fine-tune prediction algorithm parameters to optimize model performance for different scenarios.
        </p>

        {/* Configuration Management */}
        <div className="mb-6 p-4 rounded-lg border-2" style={{backgroundColor: '#F2E9E4', borderColor: '#1C5D99'}}>
          <h3 className="font-semibold mb-4" style={{color: '#002629'}}>💾 Configuration Management</h3>
          
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-4">
            <div>
              <label className="block text-sm font-medium mb-2" style={{color: '#002629'}}>Configuration Name</label>
              <input
                type="text"
                value={configName}
                onChange={(e) => setConfigName(e.target.value)}
                placeholder="Enter configuration name..."
                className="form-input w-full"
              />
            </div>
            <div className="flex items-end space-x-2">
              <button
                onClick={handleSaveConfig}
                disabled={!configName.trim() || savingConfig}
                className="px-4 py-2 text-white font-medium rounded hover:opacity-90 disabled:opacity-50 disabled:cursor-not-allowed flex items-center space-x-2"
                style={{backgroundColor: '#1C5D99'}}
              >
                {savingConfig ? (
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
                onClick={resetToDefaults}
                className="px-4 py-2 text-white font-medium rounded hover:opacity-90 transition-opacity"
                style={{backgroundColor: '#002629'}}
              >
                🔄 Reset to Defaults
              </button>
            </div>
          </div>

          {/* Saved Configurations List */}
          <ConfigurationList
            configurations={allPredictionConfigs}
            type="prediction"
            onLoad={handleLoadConfig}
            onDelete={handleDeleteConfig}
            loading={loadingConfigs}
          />
        </div>

        {/* Parameter Configuration */}
        <div className="space-y-6">
          {parameters.map(category => (
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
                          value={predictionConfig[param.key] || 0}
                          onChange={(e) => handleConfigChange(param.key, e.target.value)}
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
                      value={predictionConfig[param.key] || 0}
                      onChange={(e) => handleConfigChange(param.key, e.target.value)}
                      className="w-full mb-2"
                    />
                    
                    <p className="text-xs" style={{color: '#002629', opacity: 0.6}}>{param.description}</p>
                  </div>
                ))}
              </div>
            </div>
          ))}
        </div>

        {/* Configuration Summary */}
        <div className="mt-6 p-4 rounded-lg" style={{backgroundColor: '#A3D9FF'}}>
          <h3 className="font-semibold mb-3" style={{color: '#002629'}}>📋 Current Configuration Summary</h3>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
            <div>
              <div className="font-medium" style={{color: '#002629'}}>Team Factors</div>
              <div style={{color: '#002629', opacity: 0.8}}>
                Form: {predictionConfig.team_form_weight || 0} | 
                Home: {predictionConfig.home_advantage_weight || 0}
              </div>
            </div>
            <div>
              <div className="font-medium" style={{color: '#002629'}}>Statistical</div>
              <div style={{color: '#002629', opacity: 0.8}}>
                Goals: {predictionConfig.goals_scored_weight || 0} | 
                xG: {predictionConfig.xg_weight || 0}
              </div>
            </div>
            <div>
              <div className="font-medium" style={{color: '#002629'}}>External</div>
              <div style={{color: '#002629', opacity: 0.8}}>
                Referee: {predictionConfig.referee_bias_weight || 0} | 
                Injury: {predictionConfig.injury_impact_weight || 0}
              </div>
            </div>
            <div>
              <div className="font-medium" style={{color: '#002629'}}>Model</div>
              <div style={{color: '#002629', opacity: 0.8}}>
                Confidence: {predictionConfig.confidence_threshold || 0} | 
                Learning: {predictionConfig.learning_rate || 0}
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default PredictionConfig;