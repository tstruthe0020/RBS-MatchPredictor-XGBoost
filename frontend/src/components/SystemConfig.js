import React from 'react';

const SystemConfig = ({
  mlStatus,
  ensembleModelStatus,
  trainingModels,
  setTrainingModels,
  trainingResults,
  setTrainingResults,
  reloadingModels,
  setReloadingModels,
  checkMLStatus,
  trainMLModels,
  reloadMLModels,
  trainEnsembleModels,
  getEnsembleModelStatus,
  systemStatus,
  setSystemStatus,
  fetchSystemStatus,
  defaultDecayPreset,
  setDefaultDecayPreset,
  defaultFormation,
  setDefaultFormation,
  decayPresets,
  availableFormations,
  saveSystemConfig,
  loadingSystemStatus,
  setLoadingSystemStatus
}) => {

  const handleTrainMLModels = async () => {
    if (!window.confirm('🏋️ Train ML Models?\n\nThis will retrain all XGBoost models using the current dataset. This process may take several minutes.')) {
      return;
    }

    setTrainingModels(true);
    try {
      const result = await trainMLModels();
      setTrainingResults(result);
      await checkMLStatus(); // Refresh status
      if (result?.success) {
        alert('✅ ML models trained successfully!');
      } else {
        alert('⚠️ Training completed but some models may need more data for optimal performance.');
      }
    } catch (error) {
      console.error('Error training ML models:', error);
      alert(`❌ Error training ML models: ${error.response?.data?.detail || error.message}`);
    } finally {
      setTrainingModels(false);
    }
  };

  const handleReloadModels = async () => {
    setReloadingModels(true);
    try {
      await reloadMLModels();
      await checkMLStatus(); // Refresh status
      alert('✅ Models reloaded successfully!');
    } catch (error) {
      console.error('Error reloading models:', error);
      alert(`❌ Error reloading models: ${error.response?.data?.detail || error.message}`);
    } finally {
      setReloadingModels(false);
    }
  };

  const handleTrainEnsembleModels = async () => {
    if (!window.confirm('🤖 Train Ensemble Models?\n\nThis will train multiple ML models including Random Forest, Gradient Boosting, Neural Networks, and Logistic Regression. This process may take several minutes.')) {
      return;
    }

    setTrainingModels(true);
    try {
      const result = await trainEnsembleModels();
      await getEnsembleModelStatus(); // Refresh status
      if (result?.success) {
        alert('✅ Ensemble models trained successfully!');
      } else {
        alert('⚠️ Training completed but some models may need more data for optimal performance.');
      }
    } catch (error) {
      console.error('Error training ensemble models:', error);
      alert(`❌ Error training ensemble models: ${error.response?.data?.detail || error.message}`);
    } finally {
      setTrainingModels(false);
    }
  };

  const handleFetchSystemStatus = async () => {
    setLoadingSystemStatus(true);
    try {
      const status = await fetchSystemStatus();
      setSystemStatus(status);
    } catch (error) {
      console.error('Error fetching system status:', error);
    } finally {
      setLoadingSystemStatus(false);
    }
  };

  const handleSaveSystemConfig = async () => {
    try {
      await saveSystemConfig({
        default_decay_preset: defaultDecayPreset,
        default_formation: defaultFormation
      });
      alert('✅ System configuration saved successfully!');
    } catch (error) {
      console.error('Error saving system config:', error);
      alert(`❌ Error saving configuration: ${error.response?.data?.detail || error.message}`);
    }
  };

  return (
    <div className="space-y-6">
      <div className="bg-white p-6 rounded-lg shadow-lg border border-gray-200">
        <h2 className="text-xl font-bold mb-4" style={{color: '#002629'}}>🔧 System Configuration</h2>
        <p className="mb-6" style={{color: '#002629', opacity: 0.8}}>
          Manage machine learning models, system settings, and global configuration parameters.
        </p>

        {/* ML Model Management */}
        <div className="mb-6 p-4 rounded-lg border-2" style={{backgroundColor: '#A3D9FF', borderColor: '#1C5D99'}}>
          <div className="flex items-center justify-between mb-4">
            <div>
              <h3 className="text-lg font-semibold" style={{color: '#002629'}}>🧠 XGBoost Models Management</h3>
              <div className="flex items-center space-x-2 mt-2">
                <span className={`inline-block w-3 h-3 rounded-full ${mlStatus?.models_loaded ? 'bg-green-500' : 'bg-red-500'}`}></span>
                <span className="text-sm font-medium" style={{color: '#002629'}}>
                  {mlStatus?.models_loaded ? 'Loaded' : 'Not Loaded'}
                </span>
                <span className="text-xs" style={{color: '#002629', opacity: 0.7}}>
                  ({mlStatus?.feature_columns_count || 0} features)
                </span>
              </div>
            </div>
            <button
              onClick={checkMLStatus}
              className="px-3 py-2 text-white text-sm font-medium rounded hover:opacity-90 transition-opacity"
              style={{backgroundColor: '#1C5D99'}}
            >
              🔄 Refresh Status
            </button>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div className="stat-card">
              <div className="stat-card-number">{mlStatus?.models_count || 0}</div>
              <div className="stat-card-label">Models Loaded</div>
            </div>
            <div className="stat-card">
              <div className="stat-card-number">{mlStatus?.feature_columns_count || 0}</div>
              <div className="stat-card-label">Feature Columns</div>
            </div>
            <div className="stat-card">
              <div className="stat-card-number">{mlStatus?.training_data_size || 0}</div>
              <div className="stat-card-label">Training Records</div>
            </div>
          </div>

          <div className="flex space-x-4 mt-4">
            <button
              onClick={handleTrainMLModels}
              disabled={trainingModels}
              className="px-4 py-2 text-white font-medium rounded hover:opacity-90 disabled:opacity-50 disabled:cursor-not-allowed flex items-center space-x-2"
              style={{backgroundColor: '#12664F'}}
            >
              {trainingModels ? (
                <>
                  <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white"></div>
                  <span>Training...</span>
                </>
              ) : (
                <>
                  <span>🏋️</span>
                  <span>Train Models</span>
                </>
              )}
            </button>

            <button
              onClick={handleReloadModels}
              disabled={reloadingModels}
              className="px-4 py-2 text-white font-medium rounded hover:opacity-90 disabled:opacity-50 disabled:cursor-not-allowed flex items-center space-x-2"
              style={{backgroundColor: '#002629'}}
            >
              {reloadingModels ? (
                <>
                  <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white"></div>
                  <span>Reloading...</span>
                </>
              ) : (
                <>
                  <span>🔄</span>
                  <span>Reload Models</span>
                </>
              )}
            </button>
          </div>
        </div>

        {/* Ensemble Models Management */}
        <div className="mb-6 p-4 rounded-lg border-2" style={{backgroundColor: '#F2E9E4', borderColor: '#12664F'}}>
          <div className="flex items-center justify-between mb-4">
            <div>
              <h3 className="text-lg font-semibold" style={{color: '#002629'}}>🤖 Ensemble Models Management</h3>
              <div className="text-sm mt-1" style={{color: '#002629', opacity: 0.8}}>
                Random Forest, Gradient Boosting, Neural Networks, Logistic Regression
              </div>
            </div>
            <button
              onClick={getEnsembleModelStatus}
              className="px-3 py-2 text-white text-sm font-medium rounded hover:opacity-90 transition-opacity"
              style={{backgroundColor: '#12664F'}}
            >
              🔄 Check Status
            </button>
          </div>

          {ensembleModelStatus && (
            <div className="grid grid-cols-2 md:grid-cols-5 gap-3 mb-4">
              {Object.entries(ensembleModelStatus.models_available || {}).map(([modelType, status]) => (
                <div key={modelType} 
                     className="p-3 rounded border-2 text-center"
                     style={{
                       borderColor: status.available ? '#12664F' : '#002629',
                       backgroundColor: status.available ? '#A3D9FF' : 'white'
                     }}>
                  <div className="text-lg mb-1">
                    {status.available ? '✅' : '❌'}
                  </div>
                  <div className="text-xs font-medium" style={{color: '#002629'}}>
                    {modelType.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase())}
                  </div>
                </div>
              ))}
            </div>
          )}

          <button
            onClick={handleTrainEnsembleModels}
            disabled={trainingModels}
            className="px-4 py-2 text-white font-medium rounded hover:opacity-90 disabled:opacity-50 disabled:cursor-not-allowed flex items-center space-x-2"
            style={{backgroundColor: '#12664F'}}
          >
            {trainingModels ? (
              <>
                <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white"></div>
                <span>Training...</span>
              </>
            ) : (
              <>
                <span>🤖</span>
                <span>Train Ensemble Models</span>
              </>
            )}
          </button>
        </div>

        {/* System Settings */}
        <div className="mb-6 p-4 rounded-lg border-2" style={{backgroundColor: '#F2E9E4', borderColor: '#002629'}}>
          <div className="flex items-center justify-between mb-4">
            <div>
              <h3 className="text-lg font-semibold" style={{color: '#002629'}}>⚙️ System Settings</h3>
              <p className="text-sm mt-1" style={{color: '#002629', opacity: 0.8}}>
                Configure global system parameters and default values
              </p>
            </div>
            <button
              onClick={handleSaveSystemConfig}
              className="px-4 py-2 text-white font-medium rounded hover:opacity-90 transition-opacity"
              style={{backgroundColor: '#002629'}}
            >
              💾 Save Settings
            </button>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            {/* Time Decay Settings */}
            <div>
              <h4 className="font-medium mb-3" style={{color: '#002629'}}>⏰ Time Decay Settings</h4>
              <div className="space-y-3">
                <div>
                  <label className="block text-sm font-medium mb-2" style={{color: '#002629'}}>Default Decay Preset</label>
                  <select
                    value={defaultDecayPreset}
                    onChange={(e) => setDefaultDecayPreset(e.target.value)}
                    className="form-select w-full"
                  >
                    {decayPresets.map(preset => (
                      <option key={preset.name} value={preset.name}>
                        {preset.display_name} - {preset.description}
                      </option>
                    ))}
                  </select>
                </div>
                <div className="flex items-center">
                  <input
                    type="checkbox"
                    checked={true}
                    readOnly
                    className="mr-2"
                  />
                  <span className="text-sm" style={{color: '#002629'}}>Enable time decay by default</span>
                </div>
              </div>
            </div>

            {/* Formation Settings */}
            <div>
              <h4 className="font-medium mb-3" style={{color: '#002629'}}>⚽ Formation Settings</h4>
              <div className="space-y-3">
                <div>
                  <label className="block text-sm font-medium mb-2" style={{color: '#002629'}}>Default Formation</label>
                  <select
                    value={defaultFormation}
                    onChange={(e) => setDefaultFormation(e.target.value)}
                    className="form-select w-full"
                  >
                    {availableFormations.map(formation => (
                      <option key={formation} value={formation}>{formation}</option>
                    ))}
                  </select>
                </div>
                <div className="text-sm" style={{color: '#002629', opacity: 0.7}}>
                  Available formations: {availableFormations.join(', ')}
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* System Status */}
        <div className="mb-6">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-lg font-semibold" style={{color: '#002629'}}>📊 System Status</h3>
            <button
              onClick={handleFetchSystemStatus}
              disabled={loadingSystemStatus}
              className="px-3 py-2 text-white text-sm font-medium rounded hover:opacity-90 disabled:opacity-50 disabled:cursor-not-allowed flex items-center space-x-1"
              style={{backgroundColor: '#1C5D99'}}
            >
              {loadingSystemStatus ? (
                <>
                  <div className="animate-spin rounded-full h-3 w-3 border-b-2 border-white"></div>
                  <span>Loading...</span>
                </>
              ) : (
                <>
                  <span>🔄</span>
                  <span>Refresh</span>
                </>
              )}
            </button>
          </div>

          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            <div className="stat-card">
              <div className="stat-card-number">{mlStatus?.models_loaded ? '✅' : '❌'}</div>
              <div className="stat-card-label">XGBoost Models</div>
            </div>
            <div className="stat-card">
              <div className="stat-card-number">
                {ensembleModelStatus ? 
                  Object.values(ensembleModelStatus.models_available || {}).filter(m => m.available).length : 0
                }/5
              </div>
              <div className="stat-card-label">Ensemble Models</div>
            </div>
            <div className="stat-card">
              <div className="stat-card-number">{systemStatus?.total_teams || 30}</div>
              <div className="stat-card-label">Teams</div>
            </div>
            <div className="stat-card">
              <div className="stat-card-number">{systemStatus?.total_referees || 50}</div>
              <div className="stat-card-label">Referees</div>
            </div>
          </div>
        </div>

        {/* Training Results */}
        {trainingResults && (
          <div className="p-4 rounded-lg border-2" style={{backgroundColor: '#A3D9FF', borderColor: '#12664F'}}>
            <h3 className="font-semibold mb-3" style={{color: '#002629'}}>📈 Latest Training Results</h3>
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
              <div>
                <div className="font-medium" style={{color: '#002629'}}>Status</div>
                <div className={trainingResults.success ? 'text-green-600' : 'text-red-600'}>
                  {trainingResults.success ? '✅ Success' : '❌ Failed'}
                </div>
              </div>
              <div>
                <div className="font-medium" style={{color: '#002629'}}>Models Trained</div>
                <div style={{color: '#002629'}}>{trainingResults.models_trained || 'N/A'}</div>
              </div>
              <div>
                <div className="font-medium" style={{color: '#002629'}}>Training Time</div>
                <div style={{color: '#002629'}}>{trainingResults.training_time || 'N/A'}</div>
              </div>
              <div>
                <div className="font-medium" style={{color: '#002629'}}>Accuracy</div>
                <div style={{color: '#002629'}}>{trainingResults.accuracy || 'N/A'}</div>
              </div>
            </div>
            {trainingResults.message && (
              <div className="mt-2 text-sm" style={{color: '#002629', opacity: 0.8}}>
                {trainingResults.message}
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
};

export default SystemConfig;