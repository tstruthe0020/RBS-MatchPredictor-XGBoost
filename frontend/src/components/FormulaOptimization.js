import React from 'react';
import { OptimizationResults, formatOptimizationResults } from '../advanced-features';

const FormulaOptimization = ({
  optimizationResults,
  setOptimizationResults,
  loadingOptimization,
  setLoadingOptimization,
  optimizationHistory,
  setOptimizationHistory,
  selectedOptimizationType,
  setSelectedOptimizationType,
  runAdvancedOptimization,
  runRBSOptimizationAnalysis,
  runPredictorAnalysis,
  runXGBoostHyperparameterOptimization,
  fetchOptimizationHistory
}) => {

  const optimizationTypes = [
    {
      id: 'prediction_config',
      name: '🎯 Prediction Config Optimization',
      description: 'Optimize prediction parameters using genetic algorithms and performance metrics',
      category: 'Algorithm Tuning'
    },
    {
      id: 'rbs_formula',
      name: '⚖️ RBS Formula Optimization',
      description: 'Optimize referee bias scoring weights and thresholds for maximum accuracy',
      category: 'Bias Analysis'
    },
    {
      id: 'predictor_analysis',
      name: '🔬 Predictor Analysis',
      description: 'Analyze feature importance and variable relationships for model improvement',
      category: 'Feature Engineering'
    },
    {
      id: 'xgboost_hyperparameters',
      name: '🚀 XGBoost Model Optimization',
      description: 'Hyperparameter tuning for XGBoost models using Bayesian optimization',
      category: 'Model Tuning'
    }
  ];

  const handleOptimization = async () => {
    if (!selectedOptimizationType) {
      alert('Please select an optimization type');
      return;
    }

    setLoadingOptimization(true);
    try {
      let result;
      
      switch (selectedOptimizationType) {
        case 'prediction_config':
          result = await runAdvancedOptimization('prediction_config');
          break;
        case 'rbs_formula':
          result = await runRBSOptimizationAnalysis();
          break;
        case 'predictor_analysis':
          result = await runPredictorAnalysis();
          break;
        case 'xgboost_hyperparameters':
          result = await runXGBoostHyperparameterOptimization();
          break;
        default:
          throw new Error('Unknown optimization type');
      }

      setOptimizationResults(result);
      
      // Refresh optimization history
      const history = await fetchOptimizationHistory();
      setOptimizationHistory(history);

      alert('✅ Optimization completed successfully!');
    } catch (error) {
      console.error('Error running optimization:', error);
      alert(`❌ Optimization Error: ${error.response?.data?.detail || error.message}`);
    } finally {
      setLoadingOptimization(false);
    }
  };

  const handleRefreshHistory = async () => {
    try {
      const history = await fetchOptimizationHistory();
      setOptimizationHistory(history);
    } catch (error) {
      console.error('Error fetching optimization history:', error);
    }
  };

  return (
    <div className="space-y-6">
      <div className="bg-white p-6 rounded-lg shadow-lg border border-gray-200">
        <h2 className="text-xl font-bold mb-4" style={{color: '#002629'}}>🔧 Advanced Formula Optimization</h2>
        <p className="mb-6" style={{color: '#002629', opacity: 0.8}}>
          AI-powered optimization tools for improving prediction accuracy, bias scoring, and model performance through advanced algorithms.
        </p>

        {/* Optimization Type Selection */}
        <div className="mb-6">
          <h3 className="text-lg font-semibold mb-4" style={{color: '#002629'}}>🎯 Select Optimization Type</h3>
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
            {optimizationTypes.map(type => (
              <div
                key={type.id}
                onClick={() => setSelectedOptimizationType(type.id)}
                className={`p-4 rounded-lg border-2 cursor-pointer transition-all ${
                  selectedOptimizationType === type.id
                    ? 'border-blue-500 bg-blue-50'
                    : 'border-gray-200 bg-white hover:border-blue-300'
                }`}
              >
                <div className="flex items-start justify-between mb-2">
                  <div className="font-semibold" style={{color: '#002629'}}>{type.name}</div>
                  <span className={`px-2 py-1 rounded text-xs font-medium ${
                    selectedOptimizationType === type.id
                      ? 'bg-blue-100 text-blue-800'
                      : 'bg-gray-100 text-gray-600'
                  }`}>
                    {type.category}
                  </span>
                </div>
                <p className="text-sm" style={{color: '#002629', opacity: 0.8}}>{type.description}</p>
              </div>
            ))}
          </div>
        </div>

        {/* Optimization Controls */}
        <div className="mb-6 p-4 rounded-lg border-2" style={{backgroundColor: '#F2E9E4', borderColor: '#1C5D99'}}>
          <div className="flex items-center justify-between">
            <div>
              <h3 className="font-semibold" style={{color: '#002629'}}>🚀 Run Optimization</h3>
              <p className="text-sm mt-1" style={{color: '#002629', opacity: 0.8}}>
                {selectedOptimizationType 
                  ? `Execute ${optimizationTypes.find(t => t.id === selectedOptimizationType)?.name || 'optimization'}`
                  : 'Select an optimization type to begin'
                }
              </p>
            </div>
            <button
              onClick={handleOptimization}
              disabled={!selectedOptimizationType || loadingOptimization}
              className="px-6 py-3 text-white font-medium rounded-lg hover:opacity-90 disabled:opacity-50 disabled:cursor-not-allowed flex items-center space-x-2 transition-opacity"
              style={{backgroundColor: '#1C5D99'}}
            >
              {loadingOptimization ? (
                <>
                  <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-white"></div>
                  <span>Optimizing...</span>
                </>
              ) : (
                <>
                  <span>🔧</span>
                  <span>Start Optimization</span>
                </>
              )}
            </button>
          </div>
        </div>

        {/* Optimization Results */}
        {optimizationResults && (
          <div className="mb-6">
            <OptimizationResults 
              results={optimizationResults} 
              optimizationType={selectedOptimizationType}
            />
          </div>
        )}

        {/* Optimization History */}
        <div className="mb-6">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-lg font-semibold" style={{color: '#002629'}}>📈 Optimization History</h3>
            <button
              onClick={handleRefreshHistory}
              className="px-3 py-2 text-white text-sm font-medium rounded hover:opacity-90 transition-opacity"
              style={{backgroundColor: '#12664F'}}
            >
              🔄 Refresh
            </button>
          </div>

          {optimizationHistory && optimizationHistory.length > 0 ? (
            <div className="space-y-3">
              {optimizationHistory.slice(0, 10).map((entry, index) => (
                <div key={index} className="p-4 rounded-lg border-2" style={{backgroundColor: '#A3D9FF', borderColor: '#12664F'}}>
                  <div className="flex items-center justify-between mb-2">
                    <div className="font-medium" style={{color: '#002629'}}>{entry.optimization_type}</div>
                    <div className="text-sm" style={{color: '#002629', opacity: 0.7}}>
                      {new Date(entry.timestamp).toLocaleString()}
                    </div>
                  </div>
                  
                  <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
                    <div>
                      <div className="text-xs" style={{color: '#002629', opacity: 0.7}}>Improvement</div>
                      <div className={`font-bold ${entry.improvement >= 0 ? 'text-green-600' : 'text-red-600'}`}>
                        {entry.improvement >= 0 ? '+' : ''}{entry.improvement}%
                      </div>
                    </div>
                    <div>
                      <div className="text-xs" style={{color: '#002629', opacity: 0.7}}>Runtime</div>
                      <div className="font-medium" style={{color: '#002629'}}>
                        {entry.runtime ? `${entry.runtime.toFixed(1)}s` : 'N/A'}
                      </div>
                    </div>
                    <div>
                      <div className="text-xs" style={{color: '#002629', opacity: 0.7}}>Method</div>
                      <div className="font-medium" style={{color: '#002629'}}>
                        {entry.method || 'Standard'}
                      </div>
                    </div>
                    <div>
                      <div className="text-xs" style={{color: '#002629', opacity: 0.7}}>Status</div>
                      <div className={`font-medium ${entry.status === 'success' ? 'text-green-600' : 'text-red-600'}`}>
                        {entry.status === 'success' ? '✅ Success' : '❌ Failed'}
                      </div>
                    </div>
                  </div>

                  {entry.parameters_optimized && (
                    <div className="mt-2 text-xs" style={{color: '#002629', opacity: 0.6}}>
                      Optimized: {Object.keys(entry.parameters_optimized).join(', ')}
                    </div>
                  )}
                </div>
              ))}
            </div>
          ) : (
            <div className="text-center py-8" style={{color: '#002629', opacity: 0.6}}>
              No optimization history available. Run an optimization to see results here.
            </div>
          )}
        </div>

        {/* AI Suggestions */}
        <div className="p-4 rounded-lg border-2" style={{backgroundColor: '#A3D9FF', borderColor: '#002629'}}>
          <h3 className="font-semibold mb-3" style={{color: '#002629'}}>🤖 AI Optimization Suggestions</h3>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-sm">
            <div className="bg-white p-3 rounded">
              <div className="font-medium mb-1" style={{color: '#002629'}}>📊 Performance Boost</div>
              <div style={{color: '#002629', opacity: 0.8}}>
                Run Predictor Analysis to identify underperforming features and optimize model accuracy.
              </div>
            </div>
            <div className="bg-white p-3 rounded">
              <div className="font-medium mb-1" style={{color: '#002629'}}>⚖️ Bias Reduction</div>
              <div style={{color: '#002629', opacity: 0.8}}>
                Optimize RBS formula weights to improve referee bias detection sensitivity.
              </div>
            </div>
            <div className="bg-white p-3 rounded">
              <div className="font-medium mb-1" style={{color: '#002629'}}>🎯 Algorithm Tuning</div>
              <div style={{color: '#002629', opacity: 0.8}}>
                Use XGBoost hyperparameter optimization for improved prediction confidence.
              </div>
            </div>
            <div className="bg-white p-3 rounded">
              <div className="font-medium mb-1" style={{color: '#002629'}}>🔄 Continuous Improvement</div>
              <div style={{color: '#002629', opacity: 0.8}}>
                Regularly run prediction config optimization to adapt to new data patterns.
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default FormulaOptimization;