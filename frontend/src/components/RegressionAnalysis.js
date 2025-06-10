import React from 'react';
import { VARIABLE_CATEGORIES } from '../analysis-components';

const RegressionAnalysis = ({
  regressionData,
  setRegressionData,
  selectedVariables,
  setSelectedVariables,
  selectedTarget,
  setSelectedTarget,
  loadingRegression,
  setLoadingRegression,
  runRegressionAnalysis
}) => {

  const handleVariableToggle = (variable) => {
    setSelectedVariables(prev => {
      const isSelected = prev.includes(variable);
      if (isSelected) {
        return prev.filter(v => v !== variable);
      } else {
        return [...prev, variable];
      }
    });
  };

  const handleSelectAllCategory = (category) => {
    const categoryVariables = VARIABLE_CATEGORIES[category];
    setSelectedVariables(prev => {
      const currentCategoryVars = categoryVariables.filter(v => prev.includes(v));
      
      if (currentCategoryVars.length === categoryVariables.length) {
        // All selected, deselect all
        return prev.filter(v => !categoryVariables.includes(v));
      } else {
        // Some or none selected, select all
        const newVars = [...prev];
        categoryVariables.forEach(v => {
          if (!newVars.includes(v)) {
            newVars.push(v);
          }
        });
        return newVars;
      }
    });
  };

  const handleRunRegression = async () => {
    if (selectedVariables.length === 0) {
      alert('Please select at least one variable');
      return;
    }
    if (!selectedTarget) {
      alert('Please select a target variable');
      return;
    }

    setLoadingRegression(true);
    try {
      const result = await runRegressionAnalysis(selectedVariables, selectedTarget);
      setRegressionData(result);
    } catch (error) {
      console.error('Error running regression:', error);
      alert(`❌ Regression Error: ${error.response?.data?.detail || error.message}`);
    } finally {
      setLoadingRegression(false);
    }
  };

  const clearSelection = () => {
    setSelectedVariables([]);
    setSelectedTarget('');
    setRegressionData(null);
  };

  return (
    <div className="space-y-6">
      <div className="bg-white p-6 rounded-lg shadow-lg border border-gray-200">
        <h2 className="text-xl font-bold mb-4" style={{color: '#002629'}}>📈 Regression Analysis</h2>
        <p className="mb-6" style={{color: '#002629', opacity: 0.8}}>
          Analyze statistical relationships between variables to understand what factors most influence match outcomes.
        </p>

        {/* Variable Selection */}
        <div className="mb-6">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-lg font-semibold" style={{color: '#002629'}}>Select Variables for Analysis</h3>
            <div className="flex space-x-2">
              <span className="text-sm" style={{color: '#002629', opacity: 0.7}}>
                {selectedVariables.length} variables selected
              </span>
              <button
                onClick={clearSelection}
                className="text-sm px-3 py-1 rounded hover:opacity-90 transition-opacity"
                style={{backgroundColor: '#002629', color: 'white'}}
              >
                Clear All
              </button>
            </div>
          </div>

          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            {Object.entries(VARIABLE_CATEGORIES).map(([category, variables]) => {
              const selectedInCategory = variables.filter(v => selectedVariables.includes(v));
              const allSelected = selectedInCategory.length === variables.length;
              const someSelected = selectedInCategory.length > 0;

              return (
                <div key={category} className="border-2 rounded-lg p-4" style={{borderColor: '#1C5D99', backgroundColor: '#F2E9E4'}}>
                  <div className="flex items-center justify-between mb-3">
                    <h4 className="font-semibold" style={{color: '#002629'}}>{category}</h4>
                    <button
                      onClick={() => handleSelectAllCategory(category)}
                      className={`text-xs px-3 py-1 rounded transition-opacity ${
                        allSelected 
                          ? 'bg-red-500 hover:bg-red-600 text-white' 
                          : 'bg-green-500 hover:bg-green-600 text-white'
                      }`}
                    >
                      {allSelected ? 'Deselect All' : 'Select All'}
                    </button>
                  </div>
                  
                  <div className="grid grid-cols-2 gap-2">
                    {variables.map(variable => (
                      <label key={variable} className="flex items-center space-x-2 cursor-pointer">
                        <input
                          type="checkbox"
                          checked={selectedVariables.includes(variable)}
                          onChange={() => handleVariableToggle(variable)}
                          className="form-checkbox"
                        />
                        <span className="text-sm" style={{color: '#002629'}}>{variable}</span>
                      </label>
                    ))}
                  </div>
                  
                  {someSelected && (
                    <div className="mt-2 text-xs" style={{color: '#1C5D99'}}>
                      {selectedInCategory.length} of {variables.length} selected
                    </div>
                  )}
                </div>
              );
            })}
          </div>
        </div>

        {/* Target Variable Selection */}
        <div className="mb-6">
          <h3 className="text-lg font-semibold mb-4" style={{color: '#002629'}}>Select Target Variable</h3>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
            {['home_goals', 'away_goals', 'total_goals', 'goal_difference', 'home_win', 'draw', 'away_win'].map(target => (
              <label key={target} className="flex items-center space-x-2 cursor-pointer p-3 rounded border-2 transition-colors" 
                     style={{
                       borderColor: selectedTarget === target ? '#1C5D99' : '#E5E5E5',
                       backgroundColor: selectedTarget === target ? '#A3D9FF' : 'white'
                     }}>
                <input
                  type="radio"
                  name="target"
                  value={target}
                  checked={selectedTarget === target}
                  onChange={(e) => setSelectedTarget(e.target.value)}
                  className="form-radio"
                />
                <span className="text-sm font-medium" style={{color: '#002629'}}>{target.replace(/_/g, ' ')}</span>
              </label>
            ))}
          </div>
        </div>

        {/* Run Analysis Button */}
        <div className="mb-6">
          <button
            onClick={handleRunRegression}
            disabled={selectedVariables.length === 0 || !selectedTarget || loadingRegression}
            className="px-6 py-3 text-white font-medium rounded-lg hover:opacity-90 disabled:opacity-50 disabled:cursor-not-allowed flex items-center space-x-2 transition-opacity"
            style={{backgroundColor: '#1C5D99'}}
          >
            {loadingRegression ? (
              <>
                <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-white"></div>
                <span>Running Analysis...</span>
              </>
            ) : (
              <>
                <span>📊</span>
                <span>Run Regression Analysis</span>
              </>
            )}
          </button>
        </div>

        {/* Regression Results */}
        {regressionData && (
          <div className="bg-white border-2 rounded-lg p-6" style={{borderColor: '#1C5D99'}}>
            <h3 className="text-xl font-bold mb-4" style={{color: '#002629'}}>📈 Analysis Results</h3>
            
            {/* Model Summary */}
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-6">
              <div className="stat-card">
                <div className="stat-card-number">{(regressionData.r2_score * 100).toFixed(1)}%</div>
                <div className="stat-card-label">R² Score</div>
                <div className="text-xs mt-1" style={{color: '#002629', opacity: 0.6}}>Variance explained</div>
              </div>
              <div className="stat-card">
                <div className="stat-card-number">{regressionData.mean_squared_error?.toFixed(3) || 'N/A'}</div>
                <div className="stat-card-label">MSE</div>
                <div className="text-xs mt-1" style={{color: '#002629', opacity: 0.6}}>Mean Squared Error</div>
              </div>
              <div className="stat-card">
                <div className="stat-card-number">{regressionData.feature_count || selectedVariables.length}</div>
                <div className="stat-card-label">Features</div>
                <div className="text-xs mt-1" style={{color: '#002629', opacity: 0.6}}>Variables used</div>
              </div>
            </div>

            {/* Feature Importance */}
            {regressionData.feature_importance && (
              <div className="mb-6">
                <h4 className="font-semibold mb-4" style={{color: '#002629'}}>🎯 Feature Importance</h4>
                <div className="space-y-2">
                  {Object.entries(regressionData.feature_importance)
                    .sort(([,a], [,b]) => Math.abs(b) - Math.abs(a))
                    .slice(0, 10)
                    .map(([feature, importance]) => {
                      const absImportance = Math.abs(importance);
                      const maxImportance = Math.max(...Object.values(regressionData.feature_importance).map(Math.abs));
                      const percentage = (absImportance / maxImportance) * 100;
                      
                      return (
                        <div key={feature} className="flex items-center space-x-3">
                          <div className="w-32 text-sm font-medium" style={{color: '#002629'}}>{feature}</div>
                          <div className="flex-1 relative">
                            <div className="w-full bg-gray-200 rounded-full h-4">
                              <div 
                                className="h-4 rounded-full transition-all duration-300"
                                style={{
                                  width: `${percentage}%`,
                                  backgroundColor: importance >= 0 ? '#12664F' : '#002629'
                                }}
                              ></div>
                            </div>
                          </div>
                          <div className={`w-16 text-sm font-bold text-right ${importance >= 0 ? 'text-green-600' : 'text-red-600'}`}>
                            {importance >= 0 ? '+' : ''}{importance.toFixed(3)}
                          </div>
                        </div>
                      );
                    })}
                </div>
              </div>
            )}

            {/* Coefficients */}
            {regressionData.coefficients && (
              <div className="mb-6">
                <h4 className="font-semibold mb-4" style={{color: '#002629'}}>📋 Regression Coefficients</h4>
                <div className="overflow-x-auto">
                  <table className="min-w-full border-collapse">
                    <thead>
                      <tr className="border-b">
                        <th className="text-left py-2 px-3 font-medium" style={{color: '#002629'}}>Variable</th>
                        <th className="text-right py-2 px-3 font-medium" style={{color: '#002629'}}>Coefficient</th>
                        <th className="text-right py-2 px-3 font-medium" style={{color: '#002629'}}>Impact</th>
                      </tr>
                    </thead>
                    <tbody>
                      {Object.entries(regressionData.coefficients)
                        .sort(([,a], [,b]) => Math.abs(b) - Math.abs(a))
                        .map(([variable, coefficient]) => (
                          <tr key={variable} className="border-b border-gray-100">
                            <td className="py-2 px-3 text-sm" style={{color: '#002629'}}>{variable}</td>
                            <td className={`py-2 px-3 text-sm font-mono text-right ${coefficient >= 0 ? 'text-green-600' : 'text-red-600'}`}>
                              {coefficient >= 0 ? '+' : ''}{coefficient.toFixed(4)}
                            </td>
                            <td className="py-2 px-3 text-xs text-right" style={{color: '#002629', opacity: 0.7}}>
                              {Math.abs(coefficient) > 0.1 ? 'High' : Math.abs(coefficient) > 0.01 ? 'Medium' : 'Low'}
                            </td>
                          </tr>
                        ))}
                    </tbody>
                  </table>
                </div>
              </div>
            )}

            {/* Model Interpretation */}
            <div className="p-4 rounded-lg" style={{backgroundColor: '#A3D9FF'}}>
              <h4 className="font-semibold mb-2" style={{color: '#002629'}}>🧠 Model Interpretation</h4>
              <div className="text-sm space-y-1" style={{color: '#002629'}}>
                <p>
                  <strong>R² Score:</strong> {((regressionData.r2_score || 0) * 100).toFixed(1)}% of the variance in {selectedTarget.replace(/_/g, ' ')} is explained by the selected variables.
                </p>
                {regressionData.r2_score > 0.7 && (
                  <p className="text-green-700">✅ Strong predictive relationship detected</p>
                )}
                {regressionData.r2_score <= 0.3 && (
                  <p className="text-yellow-700">⚠️ Weak relationship - consider additional variables</p>
                )}
                <p>
                  <strong>Top Factor:</strong> {regressionData.feature_importance ? 
                    Object.entries(regressionData.feature_importance)
                      .sort(([,a], [,b]) => Math.abs(b) - Math.abs(a))[0]?.[0] || 'N/A'
                    : 'N/A'} has the strongest influence on {selectedTarget.replace(/_/g, ' ')}.
                </p>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default RegressionAnalysis;