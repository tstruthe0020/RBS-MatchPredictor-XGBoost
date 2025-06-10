import React from 'react';

const Navigation = ({ activeTab, setActiveTab }) => {
  const tabs = [
    { id: 'dashboard', name: '📊 Dashboard', icon: '📊' },
    { id: 'upload', name: '📁 Upload Data', icon: '📁' },
    { id: 'predict', name: '🎯 Standard Predict', icon: '🎯' },
    { id: 'xgboost', name: '🚀 Enhanced XGBoost', icon: '🚀' },
    { id: 'ensemble', name: '🤖 Ensemble Predictions', icon: '🤖' },
    { id: 'regression', name: '📈 Regression Analysis', icon: '📈' },
    { id: 'prediction-config', name: '⚙️ Prediction Config', icon: '⚙️' },
    { id: 'rbs-config', name: '⚖️ RBS Config', icon: '⚖️' },
    { id: 'optimization', name: '🔧 Formula Optimization', icon: '🔧' },
    { id: 'results', name: '📋 Results', icon: '📋' },
    { id: 'config', name: '🔧 System Config', icon: '🔧' }
  ];

  return (
    <div style={{backgroundColor: '#12664F'}} className="shadow-sm">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <nav className="flex space-x-8 overflow-x-auto">
          {tabs.map(tab => (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id)}
              className={`py-4 px-6 text-sm font-medium border-b-2 whitespace-nowrap transition-colors ${
                activeTab === tab.id
                  ? 'text-white border-white'
                  : 'border-transparent hover:border-white/50'
              }`}
              style={{
                color: activeTab === tab.id ? '#FFFFFF' : '#A3D9FF'
              }}
            >
              <span className="mr-2">{tab.icon}</span>
              {tab.name}
            </button>
          ))}
        </nav>
      </div>
    </div>
  );
};

export default Navigation;